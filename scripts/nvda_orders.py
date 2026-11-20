#!/usr/bin/env python3
"""Trend-filtered NVDA wheel: LSEG closes + Sanji's book -> next-session Sanji orders.

The 20/50-day moving average decides direction. The book decides the wheel step:
  flat, trend up        -> sell 1 cash-secured put   (SHT put 5DTE+ otm:1)
  long 100s, trend up   -> sell covered calls        (SHT call 5DTE+ otm:1)
  long shares, trend down -> sell the shares         (SEL underlying)
  any short option open -> wait for expiry or assignment (Sanji applies both)
"""

from __future__ import annotations

import json
import math
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CONID = 4815747  # NVDA common stock, NASDAQ, USD
RIC = "NVDA.O"
MULTIPLIER = 100
EXPIRY = "5DTE+"   # listed expiry nearest 5 calendar days out, at least 5 days left
STRIKE = "otm:1"   # one listed strike out of the money from ATM at the open
HISTORY_DAYS = 420  # calendar days pulled; enough for ~250 sessions with a 50-day mean
CHART_SESSIONS = 250


def credential(name: str) -> str:
    value = os.environ.get(f"LSEG_{name.upper()}")
    path = Path.home() / ".lseg" / name
    if not value and path.is_file():
        value = path.read_text().strip()
    if not value:
        raise RuntimeError(f"Missing LSEG_{name.upper()}")
    return value


def fetch_closes() -> list[tuple[date, float]]:
    import lseg.data as ld
    import pandas as pd

    today = datetime.now(ZoneInfo("America/New_York")).date()
    session = ld.session.platform.Definition(
        app_key=credential("app_key"),
        grant=ld.session.platform.GrantPassword(
            username=credential("username"), password=credential("password")
        ),
        signon_control=True,
    ).get_session()
    session.open()
    ld.session.set_default(session)
    try:
        frame = ld.get_history(
            universe=RIC,
            fields=["TRDPRC_1"],
            interval="daily",
            start=(today - timedelta(days=HISTORY_DAYS)).isoformat(),
            end=(today + timedelta(days=1)).isoformat(),
        )
    finally:
        ld.close_session()
    if frame is None or frame.empty:
        raise RuntimeError("LSEG returned no NVDA daily prices")
    column = "TRDPRC_1" if "TRDPRC_1" in frame else frame.columns[0]
    series = pd.to_numeric(frame[column], errors="coerce").dropna()
    closes = [(pd.Timestamp(index).date(), float(value)) for index, value in series.items()]
    return sorted(set(closes))


def _qty(item: dict) -> int:
    qty = item.get("qty", item.get("quantity", item.get("position", item.get("shares"))))
    if isinstance(qty, bool) or not isinstance(qty, (int, float)) or not float(qty).is_integer():
        raise ValueError(f"Position entry has no integral quantity: {item}")
    side = str(item.get("side", item.get("action", ""))).lower()
    if side in ("short", "sht", "sell_to_open") and qty > 0:
        qty = -qty
    return int(qty)


def _entries(book: object) -> list[dict]:
    if book in ({}, [], None):
        return []
    items = book.get("positions", book.get("holdings", book)) if isinstance(book, dict) else book
    if isinstance(items, dict):
        if "conid" in items or "underlying" in items:
            items = [items]
        else:  # keyed by conid or by an id; skip scalar fields such as cash
            rows = []
            for key, value in items.items():
                if isinstance(value, dict):
                    rows.append(value if ("conid" in value or "underlying" in value) else {**value, "conid": key})
                elif isinstance(value, (int, float)) and not isinstance(value, bool) and str(key).isdigit():
                    rows.append({"conid": key, "qty": value})
            items = rows
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise ValueError("Unrecognized positions.json structure")
    return items


def book_state(book: object) -> dict:
    """NVDA shares and option positions from Sanji's book.

    Sanji has not published the positions.json shape yet, so this accepts the
    common ones and fails loudly on anything it cannot read. Short positions may
    be negative quantities or carry side/action "short"/"SHT".
    """
    state = {"shares": 0, "short_puts": 0, "short_calls": 0, "long_options": 0, "cash": None}
    if isinstance(book, dict):
        cash = book.get("cash")
        if isinstance(cash, (int, float)) and not isinstance(cash, bool):
            state["cash"] = float(cash)
    for item in _entries(book):
        asset = item.get("underlying", item.get("conid"))
        if asset is None:
            raise ValueError(f"Position entry has no conid: {item}")
        if str(asset) != str(CONID):
            continue
        contract = str(item.get("contract", "underlying")).lower()
        qty = _qty(item)
        if contract == "underlying":
            state["shares"] += qty
        elif contract in ("put", "call"):
            if qty < 0:
                state[f"short_{contract}s"] += -qty
            else:
                state["long_options"] += qty
        else:
            raise ValueError(f"Unknown contract type: {contract}")
    if state["shares"] < 0:
        raise ValueError("This strategy never shorts NVDA shares")
    return state


def signal_from_closes(prices: list[float]) -> tuple[float, float, bool]:
    """The trend filter. Shared by the nightly order run and the backtest.

    Bullish when the 20-day mean close is above the 50-day mean. Ties are not bullish.
    """
    ma20 = sum(prices[-20:]) / 20
    ma50 = sum(prices[-50:]) / 50
    return ma20, ma50, ma20 > ma50


def nasdaq_schedule(now: datetime):
    import pandas_market_calendars as mcal

    day = now.astimezone(ZoneInfo("America/New_York")).date()
    return mcal.get_calendar("NASDAQ").schedule(
        start_date=day - timedelta(days=14), end_date=day + timedelta(days=14)
    )


def next_session(now: datetime) -> date:
    """First session that has not opened yet. Orders cannot target a session already trading."""
    import pandas as pd

    schedule = nasdaq_schedule(now)
    upcoming = schedule[schedule["market_open"] > pd.Timestamp(now)]
    if upcoming.empty:
        raise RuntimeError("No next NASDAQ session found")
    return upcoming.index[0].date()


def latest_session(now: datetime) -> date:
    """Last session that has already closed, so its daily close is final.

    GitHub can start the 03:00 UTC run hours late, e.g. 06:30 New York the next
    morning. Using the calendar date there would treat today's not-yet-open
    session as the latest one and call yesterday's close stale.
    """
    import pandas as pd

    schedule = nasdaq_schedule(now)
    done = schedule[schedule["market_close"] <= pd.Timestamp(now)]
    if done.empty:
        raise RuntimeError("No recent NASDAQ session found")
    return done.index[-1].date()


def wheel_orders(state: dict, bullish: bool, close: float, session: date) -> tuple[list[dict], str]:
    """Pick the wheel step for tomorrow. Returns (orders, reason)."""
    day = session.isoformat()

    def order(kind: str, action: str, qty: int, contract: str) -> dict:
        o = {"id": f"nvda-{kind}-{day}", "for": day, "order_type": "mkt", "action": action,
             "qty": qty, "underlying": CONID, "contract": contract}
        if contract != "underlying":
            o.update(expiry=EXPIRY, strike=STRIKE)
        o["ref"] = "open"
        return o

    shares = state["shares"]
    if state["short_puts"] or state["short_calls"]:
        return [], "A short option is open. Wait for it to expire or be assigned."
    if state["long_options"]:
        return [], "The book holds long NVDA options this strategy did not open. No new orders."
    if not bullish:
        if shares:
            return [order("exit", "SEL", shares, "underlying")], "Trend is down. Sell the shares."
        return [], "Trend is down and the book is flat. Stay out."
    orders, reasons = [], []
    if shares % MULTIPLIER:
        orders.append(order("odd-lot", "SEL", shares % MULTIPLIER, "underlying"))
        reasons.append(f"Sell {shares % MULTIPLIER} odd-lot share(s); calls cover 100 at a time.")
    if shares >= MULTIPLIER:
        orders.append(order("cc", "SHT", shares // MULTIPLIER, "call"))
        reasons.append("Trend is up and the book is long shares. Write covered calls.")
        return orders, " ".join(reasons)
    need = close * MULTIPLIER
    if state["cash"] is not None and state["cash"] < need:
        reasons.append(f"Trend is up, but cash ${state['cash']:,.0f} does not secure a put (about ${need:,.0f}).")
        return orders, " ".join(reasons)
    orders.append(order("csp", "SHT", 1, "put"))
    reasons.append("Trend is up and the book is flat. Write a cash-secured put.")
    return orders, " ".join(reasons)


def plan(closes: list[tuple[date, float]], book: object, now: datetime) -> tuple[list[dict], dict]:
    last = latest_session(now)
    # Drop any partial bar for a session still trading (manual run during market hours).
    clean = sorted((day, price) for day, price in closes if day <= last and math.isfinite(price) and price > 0)
    if len(clean) < 50 or len({day for day, _ in clean}) != len(clean):
        raise ValueError("Need at least 50 distinct, valid daily closes")
    if clean[-1][0] != last:
        raise ValueError(f"Latest LSEG price is stale: {clean[-1][0]}, expected {last}")
    prices = [price for _, price in clean]
    ma20, ma50, bullish = signal_from_closes(prices)
    history = []
    for i in range(max(49, len(clean) - CHART_SESSIONS), len(clean)):
        m20, m50, _ = signal_from_closes(prices[: i + 1])
        history.append({"d": clean[i][0].isoformat(), "c": round(prices[i], 2),
                        "m20": round(m20, 2), "m50": round(m50, 2)})
    session = next_session(now)
    state = book_state(book)
    orders, reason = wheel_orders(state, bullish, clean[-1][1], session)
    signal = {
        "strategy": "NVDA wheel with a 20/50-day trend filter",
        "as_of": clean[-1][0].isoformat(),
        "for": session.isoformat(),
        "close": round(clean[-1][1], 2),
        "ma20": round(ma20, 4),
        "ma50": round(ma50, 4),
        "trend": "up" if bullish else "down",
        "book": state,
        "reason": reason,
        "orders": orders,
        "history": history,
    }
    return orders, signal


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    now = datetime.now(ZoneInfo("UTC"))
    book_path = ROOT / "mkt" / "positions.json"
    book = json.loads(book_path.read_text()) if book_path.exists() else {}
    orders, signal = plan(fetch_closes(), book, now)
    # The assignment requests a root file; Sanji's published schema reads mkt/.
    write_json(ROOT / "open_orders.json", orders)
    write_json(ROOT / "mkt" / "open_orders.json", orders)
    write_json(ROOT / "gh-pages" / "helios" / "orders" / "signal.json", signal)
    print(f"NVDA {signal['as_of']} close={signal['close']} MA20={signal['ma20']} MA50={signal['ma50']} "
          f"trend={signal['trend']}; {len(orders)} order(s) for {signal['for']}: {signal['reason']}")


if __name__ == "__main__":
    main()
