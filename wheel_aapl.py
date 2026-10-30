"""AAPL wheel backtest (cash-secured puts -> covered calls) on point-in-time LSEG data.

Selection uses the previous session's daily TR.DELTA. Execution uses the first
session's 10:00 ET hourly BID/ASK each week: short options are sold at the bid.
Options are held to the Friday expiry and settled against the official close
(assignment at the strike), so there are no early closes. Data is fetched once
into wheel_aapl_data.json; the simulation reruns offline with --from-cache.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import lseg.data as ld

import pmcc_aapl as base

ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "wheel_aapl_data.json"
OUTPUT_PATH = ROOT / "wheel_aapl_output.json"
base.GREEKS_CACHE_PATH = ROOT / "wheel_greeks_cache.json"

UNDERLYING = base.UNDERLYING
OPTION_ROOT = base.OPTION_ROOT
START = base.START
END = base.END
STRIKE_STEP = 2.5
STARTING_CASH = 50_000.0
COMMISSION = 0.65
PUT_TARGET = 0.25  # |delta| of the cash-secured put
CALL_TARGET = 0.25  # delta of the covered call
DELTA_TOLERANCE = 0.10
BAR_BAND = (0.08, 0.95)  # |delta| range for which quote history is downloaded (ITM strikes are needed for rolls)
PROFIT_TAKE = 0.50  # buy a short back once its ask is <= 50% of the credit received
ROLL_ITM = True  # roll an ITM short into next week's same strike if the roll is a net credit
ENTRY_HOUR_UTC = base.ENTRY_HOUR_UTC


def option_ric(kind: str, expiry: date, strike: float, as_of: date) -> str:
    month = chr(ord("A") + expiry.month - 1)
    code = month if kind == "CALL" else chr(ord(month) + 12)
    ric = f"{OPTION_ROOT}{code}{expiry.day:02d}{expiry.year % 100:02d}{int(round(strike * 100)):05d}.U"
    return f"{ric}^{month}{expiry.year % 100:02d}" if expiry < as_of else ric


def candidates(kind: str, expiry: date, strikes: list[float]) -> list[dict[str, Any]]:
    today = date.today()
    return [
        {"ric": option_ric(kind, expiry, k, today), "strike": k, "expiry": expiry.isoformat(), "kind": kind}
        for k in strikes
        if k > 0
    ]


# --------------------------------------------------------------------------- fetch
def fetch_dataset() -> dict[str, Any]:
    ld.open_session()
    try:
        stock = base.fetch_history(UNDERLYING, ["OPEN_PRC", "HIGH_1", "LOW_1", "TRDPRC_1"], START - timedelta(days=7), END)
        schedule = base.trading_schedule(stock)
        weekly = []
        for index, week in enumerate(schedule, start=1):
            spot = float(week["spot"])
            expiry = date.fromisoformat(week["expiry"])
            put_c = candidates("PUT", expiry, base.grid(spot * 0.86, spot * 1.03, STRIKE_STEP))
            call_c = candidates("CALL", expiry, base.grid(spot * 0.97, spot * 1.16, STRIKE_STEP))
            puts = base.fetch_daily_greeks(put_c, week["deltaAsOf"])
            calls = base.fetch_daily_greeks(call_c, week["deltaAsOf"])
            for row in puts:
                row["kind"] = "PUT"
            for row in calls:
                row["kind"] = "CALL"
            chosen = [
                row for row in puts + calls
                if BAR_BAND[0] <= abs(row["delta"]) <= BAR_BAND[1]
            ]
            for row in chosen:
                row["bars"] = base.fetch_history(
                    row["ric"], ["BID", "ASK", "TRDPRC_1"], date.fromisoformat(week["deltaAsOf"]), expiry
                )
            print(
                f"Week {index}/{len(schedule)} {week['entryDate']}: {len(puts)} put / {len(calls)} call Deltas, "
                f"{len(chosen)} quote series",
                flush=True,
            )
            weekly.append({**week, "puts": puts, "calls": calls})
        payload = {
            "source": "LSEG Workspace",
            "fetchedAt": datetime.now().isoformat(timespec="seconds"),
            "underlying": UNDERLYING,
            "start": START.isoformat(),
            "end": END.isoformat(),
            "stock": stock,
            "schedule": schedule,
            "weekly": weekly,
        }
        CACHE_PATH.write_text(json.dumps(payload), encoding="utf-8")
        return payload
    finally:
        ld.close_session()


# ---------------------------------------------------------------------- simulation
def quote_at(bars: list[dict[str, Any]], timestamp: str):
    return base.quote_at(bars, timestamp)


def pick(rows: list[dict[str, Any]], target: float, predicate) -> dict[str, Any] | None:
    eligible = [r for r in rows if predicate(r)]
    best = min(eligible, key=lambda r: (abs(abs(r["delta"]) - target), r["strike"]), default=None)
    if best is None or abs(abs(best["delta"]) - target) > DELTA_TOLERANCE:
        return None
    return best


def official_close(stock_by_time: dict[str, Any], day: str) -> tuple[str, float]:
    times = sorted(t for t in stock_by_time if t.startswith(day) and stock_by_time[t].get("close") is not None)
    if not times:
        raise RuntimeError(f"No AAPL bars on {day}")
    return times[-1], float(stock_by_time[times[-1]]["close"])


def run_backtest(data: dict[str, Any], fill_mode: str = "bid", roll: bool = True, take_profit: float = PROFIT_TAKE) -> dict[str, Any]:
    """fill_mode: 'bid' = sell short options at the bid (base case); 'mid' = sensitivity."""
    ROLL_ITM, PROFIT_TAKE = roll, take_profit
    stock_by_time = {r["time"]: r for r in data["stock"]}
    stock_times = sorted(t for t in stock_by_time if data["schedule"][0]["entryTime"] <= t)
    cash = STARTING_CASH
    shares = 0
    short: dict[str, Any] | None = None  # open option, with its bars
    basis_prem = 0.0  # premium collected in the current cycle ($)
    basis_strike = None
    blotter: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    cycles = 0

    def log(time_, action, leg, opt, qty, fill, fee, cash_change, rule, bid=None, ask=None, delta=None, tag=None):
        blotter.append(
            {
                "id": len(blotter) + 1,
                "time": time_,
                "action": action,
                "leg": leg,
                "ric": opt["ric"] if opt else UNDERLYING,
                "strike": opt["strike"] if opt else None,
                "expiry": opt["expiry"] if opt else None,
                "qty": qty,
                "delta": delta,
                "bid": bid,
                "ask": ask,
                "fill": fill,
                "fee": fee,
                "cashChange": round(cash_change, 2),
                "tag": tag,
                "rule": rule,
            }
        )

    def snap(time_, event, px):
        nonlocal cash
        opt_mv = 0.0
        if short:
            q = last_quote(short, time_)
            opt_mv = -100 * (float(q["ask"]) if q else 0.0)
        row = {
            "time": time_,
            "event": event,
            "cash": round(cash, 2),
            "shares": shares,
            "stockPx": round(px, 4),
            "stockMv": round(shares * px, 2),
            "short": None
            if not short
            else {"ric": short["ric"], "kind": short["kind"], "strike": short["strike"], "expiry": short["expiry"], "mv": round(opt_mv, 2)},
            "optMv": round(opt_mv, 2),
            "nav": round(cash + shares * px + opt_mv, 2),
            "collateral": round(short["strike"] * 100, 2) if short and short["kind"] == "PUT" else 0.0,
        }
        ledger.append(row)

    def last_quote(opt, time_):
        best = None
        for bar in opt["bars"]:
            if bar["time"] <= time_ and bar.get("bid") is not None and bar.get("ask") is not None:
                best = bar
        return best

    weeks = data["weekly"]
    for wi, week in enumerate(weeks):
        entry = week["entryTime"]
        spot = float(week["spot"])
        decision = {k: week[k] for k in ("entryDate", "entryTime", "deltaAsOf", "expiry", "spot")}
        decision["state"] = "SHARES" if shares else "CASH"
        q = None
        fill = None
        rolled_in = short is not None  # a roll last Friday already opened this week's short
        # ---- open
        if rolled_in:
            decision.update(status="TRADE", shortRic=short["ric"], kind=short["kind"], strike=short["strike"],
                            delta=short.get("delta"), fill=short["fill"], tag="ROLLED IN")
            snap(entry, "HOLD ROLLED SHORT", spot)
            fill = short["fill"]
        elif shares == 0:
            rows = week["puts"]
            chosen = pick(rows, PUT_TARGET, lambda r: r["delta"] < 0 and "bars" in r)
            if chosen is None:
                near = min(rows, key=lambda r: abs(abs(r["delta"]) - PUT_TARGET), default=None)
                decision.update(status="DATA_GAP" if not rows else "NO_TARGET")
                decision["reason"] = "No put Delta returned" if not rows else (
                    f"Nearest |Delta| {abs(near['delta']):.4f}" + ("" if "bars" in near else " (no quote series)")
                )
                decisions.append(decision)
                snap(entry, "NO TRADE", spot)
                continue
            q = quote_at(chosen["bars"], entry)
            if not base.valid_quote(q):
                decision.update(status="DATA_GAP", reason="Missing valid BID/ASK at entry")
                decisions.append(decision)
                snap(entry, "NO TRADE", spot)
                continue
            if cash < chosen["strike"] * 100 + COMMISSION:
                decision.update(status="NO_CASH", reason="Cash does not secure the strike")
                decisions.append(decision)
                snap(entry, "NO TRADE", spot)
                continue
            fill = float(q["bid"]) if fill_mode == "bid" else (float(q["bid"]) + float(q["ask"])) / 2
            prem = fill * 100 - COMMISSION
            cash += prem
            basis_prem += fill * 100
            short = {**chosen, "fill": round(fill, 4)}
            log(entry, "SELL", "PUT", chosen, -1, round(fill, 4), COMMISSION, prem,
                f"Cash-secured put, previous-close |Delta| nearest {PUT_TARGET:.2f}; fill at {fill_mode}",
                q["bid"], q["ask"], chosen["delta"], tag="OPEN")
            snap(entry, "PUT SOLD", spot)
        else:
            rows = week["calls"]
            floor = (basis_strike * 100 - basis_prem) / 100  # net cost basis per share
            chosen = pick(rows, CALL_TARGET, lambda r: r["delta"] > 0 and "bars" in r and r["strike"] >= floor)
            if chosen is None:
                if not rows:
                    decision.update(status="DATA_GAP", reason="No call Delta returned")
                else:
                    decision.update(status="NO_CALL", reason=f"No call near Delta {CALL_TARGET:.2f} at or above basis ${floor:.2f}")
                decisions.append(decision)
                snap(entry, "HOLD SHARES (NO CALL)", spot)
                continue
            q = quote_at(chosen["bars"], entry)
            if not base.valid_quote(q):
                decision.update(status="DATA_GAP", reason="Missing valid BID/ASK at entry")
                decisions.append(decision)
                snap(entry, "HOLD SHARES (NO CALL)", spot)
                continue
            fill = float(q["bid"]) if fill_mode == "bid" else (float(q["bid"]) + float(q["ask"])) / 2
            prem = fill * 100 - COMMISSION
            cash += prem
            basis_prem += fill * 100
            short = {**chosen, "fill": round(fill, 4)}
            log(entry, "SELL", "CALL", chosen, -1, round(fill, 4), COMMISSION, prem,
                f"Covered call, previous-close Delta nearest {CALL_TARGET:.2f}, strike >= net basis ${floor:.2f}; fill at {fill_mode}",
                q["bid"], q["ask"], chosen["delta"], tag="OPEN")
            snap(entry, "CALL SOLD", spot)
        if not rolled_in:
            decision.update(status="TRADE", shortRic=short["ric"], kind=short["kind"], strike=short["strike"],
                            delta=short["delta"], bid=q["bid"], ask=q["ask"], fill=round(fill, 4), tag="OPEN")
        expiry_day = week["expiry"]
        settle_time = f"{expiry_day} 20:00:00"
        roll_time = f"{expiry_day} 19:00:00"  # 15:00 ET on expiry day
        leg = short["kind"]

        # ---- profit-take: buy back once the ask has decayed to PROFIT_TAKE x credit
        closed = False
        if PROFIT_TAKE:
            for bar in short["bars"]:
                hour_utc = int(bar["time"][11:13])
                # only act inside the 10:00-15:00 ET window (14-19 UTC); earlier bars are pre-open quotes
                if bar["time"] <= entry or bar["time"] >= roll_time or not 14 <= hour_utc <= 19:
                    continue
                if bar.get("ask") is None or bar.get("bid") is None or bar["ask"] < bar["bid"]:
                    continue
                if float(bar["ask"]) <= PROFIT_TAKE * short["fill"]:
                    cost = float(bar["ask"]) * 100 + COMMISSION
                    cash -= cost
                    log(bar["time"], "BTC", leg, short, 1, float(bar["ask"]), COMMISSION, -cost,
                        f"Profit-take: ask {bar['ask']:.2f} <= {PROFIT_TAKE:.0%} of the {short['fill']:.2f} credit",
                        bar["bid"], bar["ask"], tag="CLOSE")
                    if leg == "PUT":
                        basis_prem = 0.0
                    else:
                        basis_prem -= float(bar["ask"]) * 100
                    px_now = stock_by_time[bar["time"]]["close"] if stock_by_time.get(bar["time"], {}).get("close") is not None else spot
                    short = None
                    snap(bar["time"], "SHORT CLOSED (PROFIT-TAKE)", float(px_now))
                    decision["outcome"] = "CLOSED_EARLY"
                    closed = True
                    break
        if closed:
            decisions.append(decision)
            continue

        # ---- roll: ITM at 15:00 ET on expiry day -> buy back, sell next week's same strike for a net credit
        close_time, close_px = official_close(stock_by_time, expiry_day)
        decision["officialClose"] = round(close_px, 4)
        spot_15 = stock_by_time.get(roll_time, {}).get("open")
        itm_15 = spot_15 is not None and (float(spot_15) < short["strike"] if leg == "PUT" else float(spot_15) > short["strike"])
        if ROLL_ITM and itm_15 and wi + 1 < len(weeks):
            nxt = weeks[wi + 1]
            rows = nxt["puts"] if leg == "PUT" else nxt["calls"]
            target = next((r for r in rows if "bars" in r and math.isclose(r["strike"], short["strike"])), None)
            old_q = quote_at(short["bars"], roll_time)
            new_q = quote_at(target["bars"], roll_time) if target else None
            if base.valid_quote(old_q) and base.valid_quote(new_q) and nxt["expiry"] > expiry_day:
                new_fill = float(new_q["bid"]) if fill_mode == "bid" else (float(new_q["bid"]) + float(new_q["ask"])) / 2
                net = new_fill * 100 - float(old_q["ask"]) * 100 - 2 * COMMISSION
                if net > 0:
                    cash -= float(old_q["ask"]) * 100 + COMMISSION
                    log(roll_time, "BTC", leg, short, 1, float(old_q["ask"]), COMMISSION, -(float(old_q["ask"]) * 100 + COMMISSION),
                        f"Roll: {leg.lower()} ITM at 15:00 ET (AAPL {float(spot_15):.2f}); buy back at the ask",
                        old_q["bid"], old_q["ask"], tag="ROLL CLOSE")
                    cash += new_fill * 100 - COMMISSION
                    basis_prem += new_fill * 100 - float(old_q["ask"]) * 100
                    new_short = {**target, "fill": round(new_fill, 4)}
                    log(roll_time, "SELL", leg, target, -1, round(new_fill, 4), COMMISSION, new_fill * 100 - COMMISSION,
                        f"Roll: sell next week's {target['strike']} at the {fill_mode}; net credit ${net:.2f} after fees",
                        new_q["bid"], new_q["ask"], target["delta"], tag="ROLL OPEN")
                    decision.update(outcome="ROLLED", rollNetCredit=round(net, 2), rollTo=target["ric"])
                    short = new_short
                    snap(roll_time, f"{leg} ROLLED", float(spot_15))
                    decisions.append(decision)
                    continue
                decision["rollSkipped"] = f"Roll would be a ${net:.2f} net debit"
            else:
                decision["rollSkipped"] = "No valid quotes to roll"

        # ---- settle at expiry
        decision["officialClose"] = round(close_px, 4)
        if leg == "PUT":
            if close_px < short["strike"]:
                cash -= short["strike"] * 100
                shares = 100
                basis_strike = short["strike"]
                log(settle_time, "ASSIGN", "PUT", short, -1, short["strike"], 0.0, -short["strike"] * 100,
                    f"Put ITM (close {close_px:.2f} < {short['strike']}): buy 100 AAPL at the strike", tag="ASSIGN")
                decision["outcome"] = "ASSIGNED"
                ev = "PUT ASSIGNED"
            else:
                log(settle_time, "EXPIRE", "PUT", short, 0, 0.0, 0.0, 0.0,
                    f"Put OTM (close {close_px:.2f} >= {short['strike']}): expires worthless, keep premium", tag="EXPIRE")
                decision["outcome"] = "EXPIRED_OTM"
                ev = "PUT EXPIRES"
                basis_prem = 0.0
        else:
            if close_px > short["strike"]:
                cash += short["strike"] * 100
                shares = 0
                log(settle_time, "ASSIGN", "CALL", short, -1, short["strike"], 0.0, short["strike"] * 100,
                    f"Call ITM (close {close_px:.2f} > {short['strike']}): 100 AAPL called away at the strike", tag="ASSIGN")
                decision["outcome"] = "CALLED_AWAY"
                ev = "CALL ASSIGNED"
                cycles += 1
                basis_prem = 0.0
                basis_strike = None
            else:
                log(settle_time, "EXPIRE", "CALL", short, 0, 0.0, 0.0, 0.0,
                    f"Call OTM (close {close_px:.2f} <= {short['strike']}): expires worthless, keep shares and premium", tag="EXPIRE")
                decision["outcome"] = "EXPIRED_OTM"
                ev = "CALL EXPIRES"
        short = None
        snap(settle_time, ev, close_px)
        decisions.append(decision)

    # ---- timeline: portfolio at every hourly bar, rebuilt from the blotter
    first = next(d["entryTime"] for d in decisions if d["status"] == "TRADE")
    stock_times = [t for t in stock_times if t >= first]  # score both sides from the first executed trade
    timeline = build_timeline(data, blotter, stock_times)
    final_time, final_px = official_close(stock_by_time, END.isoformat())
    final_nav = cash + shares * final_px
    navs = [STARTING_CASH] + [p["nav"] for p in timeline]
    peak, mdd = navs[0], 0.0
    for v in navs:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1)

    weekly_nav = week_end_navs(timeline)
    returns = [b / a - 1 for a, b in zip(weekly_nav, weekly_nav[1:])]
    mean = statistics.fmean(returns)
    sd = statistics.stdev(returns)
    down = math.sqrt(sum(min(r, 0) ** 2 for r in returns) / len(returns))
    sharpe = mean / sd * math.sqrt(52) if sd else None
    sortino = mean / down * math.sqrt(52) if down else None

    entry_px = float(stock_by_time[first]["open"])
    bh_nav = STARTING_CASH + (final_px - entry_px) * 100
    bh_path = [STARTING_CASH + (float(stock_by_time[p["time"]]["close"]) - entry_px) * 100
               for p in timeline if stock_by_time.get(p["time"], {}).get("close") is not None]
    bh_weekly = [STARTING_CASH] + [
        STARTING_CASH + (float(stock_by_time[t]["close"]) - entry_px) * 100
        for t in week_end_times(timeline) if stock_by_time[t].get("close") is not None
    ]
    bh_returns = [b / a - 1 for a, b in zip(bh_weekly, bh_weekly[1:])]
    bh_sd = statistics.stdev(bh_returns)
    bh_down = math.sqrt(sum(min(r, 0) ** 2 for r in bh_returns) / len(bh_returns))
    bh_peak, bh_mdd = bh_path[0], 0.0
    for v in bh_path:
        bh_peak = max(bh_peak, v)
        bh_mdd = min(bh_mdd, v / bh_peak - 1)

    opens = [b for b in blotter if b["action"] == "SELL"]
    cash_check = STARTING_CASH + sum(b["cashChange"] for b in blotter)
    if not math.isclose(cash, cash_check, abs_tol=0.02):
        raise AssertionError("Blotter does not reconcile to cash")
    if len(opens) != sum(b["action"] in ("EXPIRE", "ASSIGN", "BTC") for b in blotter):
        raise AssertionError("Every opened short needs exactly one terminal event")
    premium = sum(b["fill"] * 100 for b in opens)
    ended_in_stock = shares == 100
    return {
        "strategy": "AAPL wheel",
        "fillMode": fill_mode,
        "source": data["source"],
        "start": data["start"],
        "end": data["end"],
        "startingCash": STARTING_CASH,
        "commissionPerContract": COMMISSION,
        "putTargetDelta": PUT_TARGET,
        "callTargetDelta": CALL_TARGET,
        "deltaTolerance": DELTA_TOLERANCE,
        "firstTradeTime": first,
        "decisions": decisions,
        "blotter": blotter,
        "ledger": ledger,
        "timeline": timeline,
        "endingNav": round(final_nav, 2),
        "endingShares": shares,
        "returnPct": round((final_nav / STARTING_CASH - 1) * 100, 4),
        "maxDrawdownPct": round(mdd * 100, 4),
        "sharpe": None if sharpe is None else round(sharpe, 4),
        "sortino": None if sortino is None else round(sortino, 4),
        "weeklyVolPct": round(sd * 100, 4),
        "premiumCollected": round(premium, 2),
        "putsSold": sum(b["leg"] == "PUT" and b["tag"] == "OPEN" for b in opens),
        "callsSold": sum(b["leg"] == "CALL" and b["tag"] == "OPEN" for b in opens),
        "putAssignments": sum(b["action"] == "ASSIGN" and b["leg"] == "PUT" for b in blotter),
        "callAssignments": sum(b["action"] == "ASSIGN" and b["leg"] == "CALL" for b in blotter),
        "expiredWorthless": sum(b["action"] == "EXPIRE" for b in blotter),
        "profitTakeCloses": sum(b["tag"] == "CLOSE" for b in blotter),
        "rolls": sum(b["tag"] == "ROLL OPEN" for b in blotter),
        "rolledSettings": {"rollItm": ROLL_ITM, "profitTake": PROFIT_TAKE},
        "completedCycles": cycles,
        "tradeWeeks": sum(d["status"] == "TRADE" for d in decisions),
        "skippedWeeks": sum(d["status"] != "TRADE" for d in decisions),
        "feesPaid": round(sum(b["fee"] for b in blotter), 2),
        "benchmark": {
            "name": "AAPL buy-and-hold (100 shares + residual cash)",
            "entry": round(entry_px, 4),
            "exit": round(final_px, 4),
            "endingNav": round(bh_nav, 2),
            "returnPct": round((bh_nav / STARTING_CASH - 1) * 100, 4),
            "maxDrawdownPct": round(bh_mdd * 100, 4),
            "sharpe": round(statistics.fmean(bh_returns) / bh_sd * math.sqrt(52), 4),
            "sortino": round(statistics.fmean(bh_returns) / bh_down * math.sqrt(52), 4) if bh_down else None,
            "stockReturnPct": round((final_px / entry_px - 1) * 100, 4),
        },
        "cashBenchmark": {"name": "Cash (0%)", "returnPct": 0.0},
        "endedInStock": ended_in_stock,
    }


def _mark_week_end(*args, **kwargs):  # kept for symmetry; weekly NAV comes from the timeline
    return None


def build_timeline(data, blotter, stock_times):
    """Replay the blotter against hourly bars to get the exact portfolio at every bar."""
    events = sorted(blotter, key=lambda b: b["time"])
    weekly_bars = {}
    for wk in data["weekly"]:
        for kind in ("puts", "calls"):
            for row in wk[kind]:
                if "bars" in row:
                    weekly_bars[row["ric"]] = row["bars"]
    stock_by_time = {r["time"]: r for r in data["stock"]}
    cash, shares = STARTING_CASH, 0
    short = None
    i = 0
    out = []
    last_px = None
    for t in stock_times:
        while i < len(events) and events[i]["time"] <= t:
            ev = events[i]
            cash += ev["cashChange"]
            if ev["action"] == "SELL":
                short = {"ric": ev["ric"], "kind": ev["leg"], "strike": ev["strike"], "expiry": ev["expiry"], "fill": ev["fill"]}
            elif ev["action"] in ("EXPIRE", "BTC"):
                short = None
            elif ev["action"] == "ASSIGN":
                shares = 100 if ev["leg"] == "PUT" else 0
                short = None
            i += 1
        bar = stock_by_time[t]
        px = bar.get("close")
        if px is None:
            continue
        px = float(px)
        last_px = px
        opt = None
        opt_mv = 0.0
        if short:
            best = None
            for ob in weekly_bars.get(short["ric"], []):
                if ob["time"] <= t and ob.get("bid") is not None and ob.get("ask") is not None:
                    best = ob
            bid = best["bid"] if best else None
            ask = best["ask"] if best else None
            opt_mv = -100 * float(ask) if ask is not None else 0.0
            opt = {**short, "bid": bid, "ask": ask, "mv": round(opt_mv, 2)}
        out.append(
            {
                "time": t,
                "stockPx": round(px, 4),
                "cash": round(cash, 2),
                "shares": shares,
                "stockMv": round(shares * px, 2),
                "short": opt,
                "optMv": round(opt_mv, 2),
                "nav": round(cash + shares * px + opt_mv, 2),
                "collateral": round(short["strike"] * 100, 2) if short and short["kind"] == "PUT" else 0.0,
            }
        )
    return out


def week_end_times(timeline):
    by_week = {}
    for p in timeline:
        d = datetime.fromisoformat(p["time"]).date()
        by_week[d.isocalendar()[:2]] = p["time"]
    return list(by_week.values())


def week_end_navs(timeline):
    ends = set(week_end_times(timeline))
    return [STARTING_CASH] + [p["nav"] for p in timeline if p["time"] in ends]


def fill_stats(data) -> dict[str, Any]:
    """Evidence for the fill assumption: quoted spreads and prints at the entry bar."""
    spreads, pct, inside, with_trade, half = [], [], 0, 0, []
    for wk in data["weekly"]:
        for kind in ("puts", "calls"):
            for row in wk[kind]:
                if "bars" not in row or not (0.15 <= abs(row["delta"]) <= 0.35):
                    continue
                q = quote_at(row["bars"], wk["entryTime"])
                if not base.valid_quote(q) or q["ask"] <= 0:
                    continue
                mid = (q["bid"] + q["ask"]) / 2
                spreads.append(q["ask"] - q["bid"])
                pct.append((q["ask"] - q["bid"]) / mid * 100 if mid else 0)
                half.append((q["ask"] - q["bid"]) / 2 * 100)
                trade = next((b for b in row["bars"] if b["time"] == wk["entryTime"]), {}).get("close")
                if trade is not None:
                    with_trade += 1
                    inside += q["bid"] - 0.005 <= trade <= q["ask"] + 0.005
    return {
        "contracts": len(spreads),
        "medianSpread": round(statistics.median(spreads), 4) if spreads else None,
        "medianSpreadPctOfMid": round(statistics.median(pct), 2) if pct else None,
        "medianHalfSpreadPerContract": round(statistics.median(half), 2) if half else None,
        "withTradePrint": with_trade,
        "tradeInsideQuote": inside,
    }


def run_all(data) -> dict[str, Any]:
    base_run = run_backtest(data, "bid")
    mid_run = run_backtest(data, "mid")
    plain = run_backtest(data, "bid", roll=False, take_profit=0.0)
    output = {
        **base_run,
        "variants": {
            "withRules": {k: base_run[k] for k in ("endingNav", "returnPct", "sharpe", "sortino", "maxDrawdownPct", "premiumCollected")},
            "holdToExpiry": {k: plain[k] for k in ("endingNav", "returnPct", "sharpe", "sortino", "maxDrawdownPct", "premiumCollected")},
        },
        "sensitivity": {
            "mid": {k: mid_run[k] for k in ("endingNav", "returnPct", "sharpe", "sortino", "maxDrawdownPct")},
            "bid": {k: base_run[k] for k in ("endingNav", "returnPct", "sharpe", "sortino", "maxDrawdownPct")},
        },
        "fillStats": fill_stats(data),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-cache", action="store_true")
    args = parser.parse_args()
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if args.from_cache else fetch_dataset()
    out = run_all(data)
    print(
        f"NAV ${out['endingNav']:,.2f} ({out['returnPct']:.2f}%) vs benchmark {out['benchmark']['returnPct']:.2f}% · "
        f"puts {out['putsSold']} calls {out['callsSold']} closes {out['profitTakeCloses']} rolls {out['rolls']} · assignments P{out['putAssignments']}/C{out['callAssignments']} · "
        f"skipped weeks {out['skippedWeeks']}"
    )


if __name__ == "__main__":
    main()
