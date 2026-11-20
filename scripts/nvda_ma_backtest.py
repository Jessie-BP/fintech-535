#!/usr/bin/env python3
"""Backtest the nightly NVDA 20/50-day moving-average rule on LSEG daily bars.

The simulation mirrors what the live system does each night:
  * after the close of day t, run signal_from_closes() on closes up to t;
  * the order is a market order for day t+1, so it fills at t+1's open.

Each day's return is split at the open. The overnight leg (previous close to
open) is held with the position from before the open; the intraday leg (open
to close) is held with the position the order just set. No costs, no slippage,
no dividends (NVDA's are negligible). Prices are LSEG split-adjusted.

Writes gh-pages/helios/orders/backtest.json for the orders page.

    python scripts/nvda_ma_backtest.py            # pull from LSEG
    python scripts/nvda_ma_backtest.py --csv f    # reuse a saved Date,OPEN_PRC,TRDPRC_1 file
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "gh-pages" / "helios" / "orders" / "backtest.json"
START = "2020-11-01"

_spec = importlib.util.spec_from_file_location("nvda_orders", Path(__file__).with_name("nvda_orders.py"))
orders = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(orders)


def fetch_bars() -> list[tuple[date, float, float]]:
    import lseg.data as ld
    import pandas as pd

    session = ld.session.platform.Definition(
        app_key=orders.credential("app_key"),
        grant=ld.session.platform.GrantPassword(
            username=orders.credential("username"), password=orders.credential("password")
        ),
        signon_control=True,
    ).get_session()
    session.open()
    ld.session.set_default(session)
    try:
        frame = ld.get_history(
            universe=orders.RIC, fields=["OPEN_PRC", "TRDPRC_1"], interval="daily",
            start=START, end=date.today().isoformat(),
        )
    finally:
        ld.close_session()
    frame = frame.apply(pd.to_numeric, errors="coerce").dropna()
    return [(pd.Timestamp(i).date(), float(r.OPEN_PRC), float(r.TRDPRC_1)) for i, r in frame.iterrows()]


def read_csv(path: Path) -> list[tuple[date, float, float]]:
    with path.open() as f:
        rows = list(csv.reader(f))
    out = []
    for row in rows[1:]:
        try:
            out.append((date.fromisoformat(row[0][:10]), float(row[1]), float(row[2])))
        except (ValueError, IndexError):
            continue
    return out


def max_drawdown(curve: list[float]) -> float:
    peak, worst = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


def stats(curve: list[float], days: list[date], daily: list[float]) -> dict:
    years = (days[-1] - days[0]).days / 365.25
    mean = sum(daily) / len(daily)
    vol = math.sqrt(sum((r - mean) ** 2 for r in daily) / (len(daily) - 1)) * math.sqrt(252)
    return {
        "total_return": curve[-1] / curve[0] - 1,
        "cagr": (curve[-1] / curve[0]) ** (1 / years) - 1,
        "vol": vol,
        "sharpe": mean * 252 / vol if vol else None,
        "max_drawdown": max_drawdown(curve),
    }


def backtest(bars: list[tuple[date, float, float]]) -> dict:
    bars = sorted(bars)
    closes = [c for _, _, c in bars]
    # target[t]: position chosen after the close of day t (None before 50 closes exist).
    target = [None] * len(bars)
    for t in range(49, len(bars)):
        target[t] = orders.signal_from_closes(closes[: t + 1])[2] > 0

    first = 50  # first day an order can fill: the open after the 50th close
    days, strat, hold, s_daily, h_daily = [], [1.0], [1.0], [], []
    trades, entry = [], None
    for t in range(first, len(bars)):
        day, open_, close = bars[t]
        prev_close = bars[t - 1][2]
        before = bool(target[t - 2]) if t - 2 >= 49 else False
        after = target[t - 1]
        overnight, intraday = open_ / prev_close, close / open_
        if t == first:
            s = intraday if after else 1.0
            h = intraday  # buy and hold enters at the same first open
        else:
            s = (overnight if before else 1.0) * (intraday if after else 1.0)
            h = overnight * intraday
        if after and not before:
            entry = (day, open_)
        elif before and not after and entry:
            trades.append({"entry": entry[0].isoformat(), "entry_px": round(entry[1], 2),
                           "exit": day.isoformat(), "exit_px": round(open_, 2),
                           "return": open_ / entry[1] - 1})
            entry = None
        days.append(day)
        strat.append(strat[-1] * s)
        hold.append(hold[-1] * h)
        s_daily.append(s - 1)
        h_daily.append(h - 1)
    if entry:
        trades.append({"entry": entry[0].isoformat(), "entry_px": round(entry[1], 2),
                       "exit": None, "exit_px": round(bars[-1][2], 2),
                       "return": bars[-1][2] / entry[1] - 1})

    strat, hold = strat[1:], hold[1:]
    span = [bars[first - 1][0]] + days  # include the start point for CAGR
    closed = [tr for tr in trades if tr["exit"]]
    in_market = sum(1 for t in range(first, len(bars)) if target[t - 1]) / len(days)
    return {
        "rule": "Long 1 NVDA share when the 20-day mean close is above the 50-day mean; "
                "otherwise flat. Signal at the close, market order at the next open.",
        "source": "LSEG NVDA.O daily OPEN_PRC and TRDPRC_1, split-adjusted",
        "start": days[0].isoformat(),
        "end": days[-1].isoformat(),
        "costs": "none",
        "strategy": {**stats([1.0] + strat, span, s_daily), "time_in_market": in_market,
                     "round_trips": len(closed),
                     "win_rate": sum(tr["return"] > 0 for tr in closed) / len(closed) if closed else None},
        "buy_hold": stats([1.0] + hold, span, h_daily),
        "series": [{"d": d.isoformat(), "s": round(a, 5), "h": round(b, 5)} for d, a, b in zip(days, strat, hold)],
        "trades": trades,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, help="Date,OPEN_PRC,TRDPRC_1 file instead of LSEG")
    args = ap.parse_args()
    bars = read_csv(args.csv) if args.csv else fetch_bars()
    if len(bars) < 300:
        raise SystemExit(f"Only {len(bars)} bars; need a longer history")
    result = backtest(bars)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    s, h = result["strategy"], result["buy_hold"]
    print(f"{result['start']} -> {result['end']}")
    for name, m in (("MA 20/50", s), ("Buy&hold", h)):
        print(f"  {name:9} total {m['total_return']:+.1%}  CAGR {m['cagr']:+.1%}  vol {m['vol']:.1%}  "
              f"Sharpe {m['sharpe']:.2f}  maxDD {m['max_drawdown']:.1%}")
    print(f"  in market {s['time_in_market']:.0%}, {s['round_trips']} round trips, win rate {s['win_rate']:.0%}")


if __name__ == "__main__":
    main()
