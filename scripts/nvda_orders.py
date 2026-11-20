#!/usr/bin/env python3
"""Turn LSEG NVDA closes and Sanji's position book into next-session orders."""

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
TARGET_SHARES = 1


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
            start=(today - timedelta(days=150)).isoformat(),
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


def share_count(book: object) -> int:
    """Accept a flat initial book or common keyed/list position shapes; reject ambiguity."""
    if book in ({}, [], None):
        return 0
    if isinstance(book, dict):
        items = book.get("positions", book.get("holdings", book))
        if items in ({}, [], None):
            return 0
        if isinstance(items, dict):
            if str(CONID) in items:
                item = items[str(CONID)]
                if isinstance(item, (int, float)) and not isinstance(item, bool):
                    return int(item)
                if isinstance(item, dict) and "conid" not in item and "underlying" not in item:
                    item = {**item, "conid": CONID}
                items = [item]
            elif "conid" in items or "underlying" in items:
                items = [items]
            else:
                items = list(items.values())
    else:
        items = book
    if not isinstance(items, list):
        raise ValueError("Unrecognized positions.json structure")
    total = 0
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Unrecognized position entry")
        asset = item.get("conid", item.get("underlying"))
        if asset is None:
            raise ValueError("Position entry has no conid")
        if str(asset) != str(CONID) or item.get("contract", "underlying") != "underlying":
            continue
        qty = item.get("qty", item.get("quantity", item.get("shares")))
        if isinstance(qty, bool) or not isinstance(qty, (int, float)) or not float(qty).is_integer():
            raise ValueError("NVDA position has no integral share quantity")
        total += int(qty)
    if total < 0:
        raise ValueError("This long-only strategy cannot manage short NVDA shares")
    return total


def signal_from_closes(prices: list[float]) -> tuple[float, float, int]:
    """The whole trading rule. Shared by the nightly order run and the backtest.

    Long TARGET_SHARES when the 20-day mean close is above the 50-day mean, else flat.
    """
    ma20 = sum(prices[-20:]) / 20
    ma50 = sum(prices[-50:]) / 50
    return ma20, ma50, TARGET_SHARES if ma20 > ma50 else 0


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


def plan(closes: list[tuple[date, float]], held: int, now: datetime) -> tuple[list[dict], dict]:
    last = latest_session(now)
    # Drop any partial bar for a session still trading (manual run during market hours).
    clean = sorted((day, price) for day, price in closes if day <= last and math.isfinite(price) and price > 0)
    if len(clean) < 50 or len({day for day, _ in clean}) != len(clean):
        raise ValueError("Need at least 50 distinct, valid daily closes")
    if clean[-1][0] != last:
        raise ValueError(f"Latest LSEG price is stale: {clean[-1][0]}, expected {last}")
    ma20, ma50, target = signal_from_closes([price for _, price in clean])
    session = next_session(now)
    delta = target - held
    orders = []
    if delta:
        action = "BUY" if delta > 0 else "SEL"
        orders.append({
            "id": f"nvda-ma20-50-{action.lower()}-{session.isoformat()}",
            "for": session.isoformat(),
            "order_type": "mkt",
            "action": action,
            "qty": abs(delta),
            "underlying": CONID,
            "contract": "underlying",
            "ref": "open",
        })
    signal = {
        "strategy": "NVDA 20/50-day moving average",
        "as_of": clean[-1][0].isoformat(),
        "for": session.isoformat(),
        "close": round(clean[-1][1], 2),
        "ma20": round(ma20, 4),
        "ma50": round(ma50, 4),
        "target_shares": target,
        "held_shares": held,
        "orders": orders,
    }
    return orders, signal


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def main() -> None:
    now = datetime.now(ZoneInfo("UTC"))
    book_path = ROOT / "mkt" / "positions.json"
    book = json.loads(book_path.read_text()) if book_path.exists() else {}
    orders, signal = plan(fetch_closes(), share_count(book), now)
    # The assignment requests a root file; Sanji's published schema reads mkt/.
    write_json(ROOT / "open_orders.json", orders)
    write_json(ROOT / "mkt" / "open_orders.json", orders)
    write_json(ROOT / "gh-pages" / "helios" / "orders" / "signal.json", signal)
    print(f"NVDA {signal['as_of']} close={signal['close']} MA20={signal['ma20']} MA50={signal['ma50']}; {len(orders)} order(s) for {signal['for']}")


if __name__ == "__main__":
    main()
