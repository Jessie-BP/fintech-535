"""AAPL poor man's covered call parameter backtest using point-in-time LSEG data.

Selection uses the previous trading session's daily TR.DELTA. Execution uses
the next session's 10:00 ET hourly quote: buy the long call at ask and sell the
short call at bid. Short calls are bought back at ask at 15:00 ET on expiry.
"""

from __future__ import annotations

import argparse
import json
import math
import time
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable

import lseg.data as ld

warnings.filterwarnings("ignore", category=FutureWarning, module=r"lseg\.data\..*")


ROOT = Path(__file__).resolve().parent
CACHE_PATH = ROOT / "pmcc_aapl_data.json"
OUTPUT_PATH = ROOT / "pmcc_aapl_output.json"
GREEKS_CACHE_PATH = ROOT / "pmcc_greeks_cache.json"

UNDERLYING = "AAPL.O"
OPTION_ROOT = "AAPL"
START = date(2026, 6, 1)
END = date(2026, 9, 11)
LONG_MIN_DTE = 270
LONG_MAX_DTE = 450
LONG_TARGET_DTE = 365
ENTRY_HOUR_UTC = 14  # 10:00 ET during this daylight-saving-time sample
EXIT_HOUR_UTC = 19  # 15:00 ET
LONG_TARGET_DELTAS = (0.70, 0.75, 0.80, 0.85, 0.90)
SHORT_TARGET_DELTAS = (0.20, 0.25, 0.30)
LONG_DELTA_TOLERANCE = 0.03
SHORT_DELTA_TOLERANCE = 0.10
SHORT_REFINEMENT_THRESHOLD = 0.03
COMMISSION = 0.65
STARTING_CASH = 25_000.0

CALL_MONTH = {month: chr(ord("A") + month - 1) for month in range(1, 13)}


def call_ric(root: str, expiry: date, strike: float, as_of: date) -> str:
    month = CALL_MONTH[expiry.month]
    yy = f"{expiry.year % 100:02d}"
    strike_token = f"{int(round(strike * 100)):05d}"
    ric = f"{root}{month}{expiry.day:02d}{yy}{strike_token}.U"
    return f"{ric}^{month}{yy}" if expiry < as_of else ric


def num(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def column_key(column: Any) -> str:
    parts = column if isinstance(column, tuple) else (column,)
    return " ".join(str(part).strip().upper() for part in parts if str(part).strip())


def normalize_history(frame: Any) -> list[dict[str, Any]]:
    if frame is None or frame.empty:
        return []
    reset = frame.reset_index()
    time_column = reset.columns[0]
    rows = []
    for _, source in reset.iterrows():
        row: dict[str, Any] = {"time": str(source[time_column])}
        for column, value in source.items():
            key = column_key(column)
            if "OPEN_PRC" in key or key.endswith(" OPEN"):
                row["open"] = num(value)
            elif "HIGH_1" in key or key.endswith(" HIGH"):
                row["high"] = num(value)
            elif "LOW_1" in key or key.endswith(" LOW"):
                row["low"] = num(value)
            elif "TRDPRC_1" in key or key.endswith(" CLOSE"):
                row["close"] = num(value)
            elif key.endswith(" BID") or key == "BID":
                row["bid"] = num(value)
            elif key.endswith(" ASK") or key == "ASK":
                row["ask"] = num(value)
        if any(value is not None for key, value in row.items() if key != "time"):
            rows.append(row)
    return rows


def retry(label: str, operation: Callable[[], Any], attempts: int = 3) -> Any:
    error: Exception | None = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:  # LSEG desktop sessions can fail transiently
            error = exc
            # A bad synthetic RIC is deterministic; retrying it only wastes
            # requests and can trigger the Workspace throttle.
            if "unable to resolve" in str(exc).lower():
                break
            if attempt + 1 < attempts:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"{label} failed after {attempt + 1} attempt(s): {error}") from error


def fetch_history(ric: str, fields: list[str], start: date, end: date) -> list[dict[str, Any]]:
    frame = retry(
        f"history {ric}",
        lambda: ld.get_history(
            universe=ric,
            fields=fields,
            interval="hourly",
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
        ),
    )
    return normalize_history(frame)


def trading_schedule(stock_bars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bars_by_time = {row["time"]: row for row in stock_bars}
    sessions = sorted({datetime.fromisoformat(row["time"]).date() for row in stock_bars})
    by_week: dict[tuple[int, int], list[date]] = {}
    for session in sessions:
        iso = session.isocalendar()
        by_week.setdefault((iso.year, iso.week), []).append(session)

    schedule = []
    for week_sessions in sorted(by_week.values(), key=min):
        entry_date = min(week_sessions)
        expiry = max(week_sessions)
        if entry_date < START or expiry > END or entry_date == expiry:
            continue
        entry_time = f"{entry_date.isoformat()} {ENTRY_HOUR_UTC:02d}:00:00"
        entry_bar = bars_by_time.get(entry_time)
        if not entry_bar or entry_bar.get("open") is None:
            raise RuntimeError(f"Missing underlying entry bar at {entry_time}")
        prior_sessions = [session for session in sessions if session < entry_date]
        if not prior_sessions:
            raise RuntimeError(f"No prior session available for {entry_date}")
        schedule.append(
            {
                "entryDate": entry_date.isoformat(),
                "entryTime": entry_time,
                "deltaAsOf": max(prior_sessions).isoformat(),
                "expiry": expiry.isoformat(),
                "spot": entry_bar["open"],
            }
        )
    return schedule


def grid(low: float, high: float, step: float) -> list[float]:
    first = math.floor(low / step) * step
    last = math.ceil(high / step) * step
    count = int(round((last - first) / step))
    return [round(first + index * step, 2) for index in range(count + 1)]


def candidate_rics(expiry: date, strikes: list[float], as_of: date) -> list[dict[str, Any]]:
    return [
        {
            "ric": call_ric(OPTION_ROOT, expiry, strike, as_of),
            "strike": strike,
            "expiry": expiry.isoformat(),
        }
        for strike in strikes
        if strike > 0
    ]


def discover_long_candidates(spot: float) -> list[dict[str, Any]]:
    """Use the live chain for the still-active LEAPS instead of guessing RICs."""
    min_expiry = START + timedelta(days=LONG_MIN_DTE)
    max_expiry = START + timedelta(days=LONG_MAX_DTE)
    frame = retry(
        "discover active AAPL LEAPS",
        lambda: ld.discovery.search(
            view=ld.discovery.Views.EQUITY_DERIVATIVE_QUOTES,
            filter=(
                "AssetState eq 'AC' and UnderlyingQuoteRIC eq 'AAPL.O' "
                "and RCSAssetClass eq 'OPT' and IsChain eq false "
                f"and ExpiryDate ge {min_expiry.isoformat()} "
                f"and ExpiryDate le {max_expiry.isoformat()}"
            ),
            select="RIC,ExpiryDate,CallPutOption,StrikePrice,UnderlyingQuoteRIC,AssetState",
            top=10_000,
        ),
    )
    candidates = []
    if frame is None or frame.empty:
        return candidates
    for source in frame.to_dict("records"):
        normalized = {str(key).strip().lower(): value for key, value in source.items()}
        ric = str(normalized.get("ric") or "").strip()
        strike = num(normalized.get("strikeprice"))
        cp = str(normalized.get("callputoption") or "").strip().upper()
        expiry_text = str(normalized.get("expirydate") or "")[:10]
        try:
            expiry = date.fromisoformat(expiry_text)
        except ValueError:
            continue
        if not ric or strike is None or not cp.startswith("C"):
            continue
        if not (spot * 0.50 <= strike < spot):
            continue
        dte = (expiry - START).days
        if LONG_MIN_DTE <= dte <= LONG_MAX_DTE:
            candidates.append(
                {"ric": ric, "strike": strike, "expiry": expiry_text, "dteAtEntry": dte}
            )
    unique = {candidate["ric"]: candidate for candidate in candidates}
    return list(unique.values())


def fetch_daily_greeks(
    candidates: list[dict[str, Any]], as_of: str, *, cache_only: bool = False
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        disk_cache = json.loads(GREEKS_CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        disk_cache = {}
    if disk_cache.get("__schemaVersion") != 2:
        # Version 1 wrote null for both deterministic bad RICs and temporary
        # failures. Those nulls cannot safely be treated as permanent misses.
        disk_cache = {key: value for key, value in disk_cache.items() if value is not None}
        disk_cache["__schemaVersion"] = 2
        GREEKS_CACHE_PATH.write_text(json.dumps(disk_cache, indent=2), encoding="utf-8")

    pending = []
    for candidate in candidates:
        cached = disk_cache.get(f"{as_of}|{candidate['ric']}", "MISSING")
        # None means this exact RIC was already rejected as unresolvable.
        if cached == "MISSING":
            pending.append(candidate)
        elif cached is not None:
            records.append(cached)
    candidates = pending
    if cache_only:
        return records
    fields = [
        "TR.CLOSEPRICE.DATE",
        "TR.CLOSEPRICE",
        "TR.IMPLIEDVOLATILITY",
        "TR.DELTA",
    ]
    deterministic_invalid: set[str] = set()
    for offset in range(0, len(candidates), 40):
        chunk = candidates[offset : offset + 40]
        universe = [candidate["ric"] for candidate in chunk]

        def get_frame(items: list[str], label: str):
            return retry(
                label,
                lambda: ld.get_data(
                    universe=items,
                    fields=fields,
                    parameters={"SDate": as_of, "EDate": as_of, "FRQ": "D"},
                ),
            )

        def fetch_resilient(items: list[str]) -> list[Any]:
            """Bisect a rejected batch so valid RIC groups still stay batched."""
            if not items:
                return []
            try:
                frame = get_frame(items, f"daily Greeks {as_of} ({len(items)} RICs)")
                time.sleep(0.22)
                return [frame]
            except RuntimeError as exc:
                time.sleep(0.22)
                if len(items) == 1:
                    if "unable to resolve" in str(exc).lower():
                        deterministic_invalid.add(items[0])
                    return []
                middle = len(items) // 2
                return fetch_resilient(items[:middle]) + fetch_resilient(items[middle:])

        frames = fetch_resilient(universe)

        for frame in frames:
            if frame is None or frame.empty:
                continue
            for source in frame.to_dict("records"):
                normalized = {str(key).strip().lower(): value for key, value in source.items()}
                ric = str(normalized.get("instrument") or "").strip()
                delta = num(normalized.get("delta"))
                returned_date = str(normalized.get("date") or "")[:10]
                if not ric or delta is None or returned_date != as_of:
                    continue
                candidate = next((item for item in chunk if item["ric"] == ric), None)
                if candidate is None:
                    continue
                records.append(
                    {
                        **candidate,
                        "deltaAsOf": returned_date,
                        "delta": delta,
                        "iv": num(normalized.get("implied volatility")),
                        "close": num(normalized.get("close price")),
                    }
                )
        time.sleep(0.25)

    found = {row["ric"]: row for row in records if row.get("deltaAsOf") == as_of}
    for candidate in candidates:
        observation = found.get(candidate["ric"])
        if observation is not None:
            disk_cache[f"{as_of}|{candidate['ric']}"] = observation
        elif candidate["ric"] in deterministic_invalid:
            disk_cache[f"{as_of}|{candidate['ric']}"] = None
    if candidates:
        GREEKS_CACHE_PATH.write_text(json.dumps(disk_cache, indent=2), encoding="utf-8")
    return records


def closest_delta(
    rows: list[dict[str, Any]], target: float, predicate: Callable[[dict[str, Any]], bool]
) -> dict[str, Any] | None:
    eligible = [row for row in rows if 0 < row["delta"] < 1 and predicate(row)]
    return min(eligible, key=lambda row: (abs(row["delta"] - target), row["strike"])) if eligible else None


def covers_targets(
    rows: list[dict[str, Any]], targets: tuple[float, ...], tolerance: float,
    predicate: Callable[[dict[str, Any]], bool] = lambda row: True,
) -> bool:
    return all(
        (selected := closest_delta(rows, target, predicate)) is not None
        and abs(selected["delta"] - target) <= tolerance
        for target in targets
    )


def midpoint_strikes_for_missing_targets(
    rows: list[dict[str, Any]], targets: tuple[float, ...], tolerance: float
) -> list[float]:
    """Return only $2.50 strikes that can improve an uncovered target."""
    ordered = sorted(rows, key=lambda row: row["strike"])
    strikes: set[float] = set()
    for target in targets:
        selected = closest_delta(ordered, target, lambda row: True)
        if selected is not None and abs(selected["delta"] - target) <= tolerance:
            continue
        bracket = next(
            (
                (left, right)
                for left, right in zip(ordered, ordered[1:])
                if (left["delta"] - target) * (right["delta"] - target) <= 0
            ),
            None,
        )
        if bracket is not None:
            midpoint = (float(bracket[0]["strike"]) + float(bracket[1]["strike"])) / 2
            if not math.isclose(midpoint % 5.0, 0.0, abs_tol=1e-9):
                strikes.add(round(midpoint, 2))
    return sorted(strikes)


def integer_strikes_between_spot_and_first_otm(
    rows: list[dict[str, Any]], spot: float
) -> list[float]:
    """Probe possible $1 strikes skipped by a coarse standard-strike grid."""
    otm_strikes = sorted(float(row["strike"]) for row in rows if row["strike"] > spot)
    if not otm_strikes:
        return []
    first_otm = otm_strikes[0]
    first_integer = math.floor(spot) + 1
    return [
        float(strike)
        for strike in range(first_integer, math.ceil(first_otm))
        if spot < strike < first_otm
    ]


def quote_at(bars: list[dict[str, Any]], timestamp: str) -> dict[str, Any] | None:
    quote = next((bar for bar in bars if bar["time"] == timestamp), None)
    if quote and (quote.get("bid") is None or quote.get("ask") is None) and quote.get("close") is not None:
        # Market makers sometimes pull a two-sided quote on an expiring,
        # near-worthless contract while a last trade price still exists.
        # Fall back to that trade price rather than discarding the bar.
        quote = {**quote, "bid": quote["close"], "ask": quote["close"]}
    return quote


def valid_quote(quote: dict[str, Any] | None) -> bool:
    if not quote:
        return False
    bid, ask = quote.get("bid"), quote.get("ask")
    return bid is not None and ask is not None and 0 <= bid <= ask


def fetch_dataset() -> dict[str, Any]:
    ld.open_session()
    try:
        stock = fetch_history(
            UNDERLYING,
            ["OPEN_PRC", "HIGH_1", "LOW_1", "TRDPRC_1"],
            START - timedelta(days=7),
            END,
        )
        schedule = trading_schedule(stock)
        ric_as_of = date.today()

        initial = schedule[0]
        initial_spot = float(initial["spot"])
        long_candidates = discover_long_candidates(initial_spot)
        if not long_candidates:
            raise RuntimeError("LSEG discovery returned no active AAPL LEAPS candidates")
        print(f"Discovered {len(long_candidates)} active long-call candidates", flush=True)
        # Select the expiry first, then the strike. Querying every listed LEAPS
        # causes many point-in-time failures because contracts listed today may
        # not yet have existed on the historical selection date.
        expiry_order = sorted(
            {row["expiry"]: row["dteAtEntry"] for row in long_candidates}.items(),
            key=lambda item: (abs(item[1] - LONG_TARGET_DTE), item[0]),
        )
        long_greeks = []
        selected_expiry = None
        for expiry_text, _ in expiry_order:
            expiry_candidates = [
                row for row in long_candidates
                if row["expiry"] == expiry_text
                and initial_spot * 0.55 <= row["strike"] < initial_spot
            ]
            cached = fetch_daily_greeks(
                expiry_candidates, initial["deltaAsOf"], cache_only=True
            )
            if covers_targets(cached, LONG_TARGET_DELTAS, LONG_DELTA_TOLERANCE):
                long_greeks = cached
            else:
                print(
                    f"Querying {len(expiry_candidates)} historical Delta rows for "
                    f"long expiry {expiry_text}",
                    flush=True,
                )
                long_greeks = fetch_daily_greeks(expiry_candidates, initial["deltaAsOf"])
            if covers_targets(long_greeks, LONG_TARGET_DELTAS, LONG_DELTA_TOLERANCE):
                selected_expiry = expiry_text
                break
        if selected_expiry is None:
            raise RuntimeError(
                "No single eligible long expiry covers all five Delta targets within tolerance"
            )
        print(
            f"Using long expiry {selected_expiry}; {len(long_greeks)} verified Delta rows",
            flush=True,
        )
        eligible_longs = [
            row for row in long_greeks if 0 < row["delta"] < 1 and row["strike"] < initial_spot
        ]
        selected_longs = []
        long_bars_by_ric: dict[str, list[dict[str, Any]]] = {}
        for target in LONG_TARGET_DELTAS:
            selected = min(
                eligible_longs,
                key=lambda row, target=target: (
                    abs(row["delta"] - target),
                    abs(row["dteAtEntry"] - LONG_TARGET_DTE),
                    row["strike"],
                ),
                default=None,
            )
            if selected is None or abs(selected["delta"] - target) > LONG_DELTA_TOLERANCE:
                nearest = "none" if selected is None else f"{selected['delta']:.4f}"
                raise RuntimeError(
                    f"No long call within ±{LONG_DELTA_TOLERANCE:.2f} of target "
                    f"{target:.2f}; nearest was {nearest}"
                )
            chosen = dict(selected)
            if chosen["ric"] not in long_bars_by_ric:
                long_bars_by_ric[chosen["ric"]] = fetch_history(
                    chosen["ric"], ["BID", "ASK", "TRDPRC_1"], START, END
                )
            chosen["bars"] = long_bars_by_ric[chosen["ric"]]
            entry_quote = quote_at(chosen["bars"], initial["entryTime"])
            if not valid_quote(entry_quote):
                raise RuntimeError(
                    f"Long target {target:.2f} ({chosen['ric']}) has no valid 10:00 ET entry quote"
                )
            chosen["targetDelta"] = target
            chosen["entryQuote"] = entry_quote
            chosen["breakeven"] = round(chosen["strike"] + float(entry_quote["ask"]), 4)
            selected_longs.append(chosen)
            print(
                f"Long target {target:.2f}: {chosen['ric']} · expiry {chosen['expiry']} "
                f"· DTE {chosen['dteAtEntry']} · actual delta {chosen['delta']:.4f}",
                flush=True,
            )

        weekly = []
        for index, week in enumerate(schedule, start=1):
            spot = float(week["spot"])
            expiry = date.fromisoformat(week["expiry"])
            print(
                f"Week {index}/{len(schedule)} {week['entryDate']}: selecting shorts...",
                flush=True,
            )
            # LSEG Search does not retain expired equity options. Construct the
            # documented expired RICs, then retain only contracts for which LSEG
            # returns a Delta dated exactly deltaAsOf.
            strikes = grid(spot * 0.96, spot * 1.12, 5.0)
            candidates = candidate_rics(expiry, strikes, ric_as_of)
            # Delta is observed at the prior close. Do not discard that
            # point-in-time selection merely because an overnight move makes
            # its strike slightly ITM by the next morning's execution time.
            eligible_short = lambda row: True
            greeks = fetch_daily_greeks(candidates, week["deltaAsOf"], cache_only=True)
            if not covers_targets(
                greeks, SHORT_TARGET_DELTAS, SHORT_DELTA_TOLERANCE, eligible_short
            ):
                greeks = fetch_daily_greeks(candidates, week["deltaAsOf"])
            selections = {
                target: closest_delta(greeks, target, eligible_short)
                for target in SHORT_TARGET_DELTAS
            }
            needs_finer_grid = any(
                selected is None
                or abs(selected["delta"] - target) > SHORT_REFINEMENT_THRESHOLD
                for target, selected in selections.items()
            )
            if needs_finer_grid:
                supplemental_strikes = sorted(
                    set(
                        midpoint_strikes_for_missing_targets(
                            greeks, SHORT_TARGET_DELTAS, SHORT_REFINEMENT_THRESHOLD
                        )
                        + integer_strikes_between_spot_and_first_otm(greeks, spot)
                    )
                    - {float(candidate["strike"]) for candidate in candidates}
                )
                supplemental = candidate_rics(expiry, supplemental_strikes, ric_as_of)
                extra = fetch_daily_greeks(
                    supplemental, week["deltaAsOf"], cache_only=True
                )
                if not covers_targets(
                    greeks + extra,
                    SHORT_TARGET_DELTAS,
                    SHORT_REFINEMENT_THRESHOLD,
                    eligible_short,
                ):
                    extra = fetch_daily_greeks(supplemental, week["deltaAsOf"])
                greeks.extend(extra)
                candidates.extend(supplemental)
                selections = {
                    target: closest_delta(greeks, target, eligible_short)
                    for target in SHORT_TARGET_DELTAS
                }
            bars_by_ric = {}
            quote_rics = {
                selected["ric"]
                for target, selected in selections.items()
                if selected is not None
                and abs(selected["delta"] - target) <= SHORT_DELTA_TOLERANCE
            }
            if quote_rics:
                print(
                    f"Week {index}/{len(schedule)} {week['entryDate']}: "
                    f"downloading {len(quote_rics)} option quote series...",
                    flush=True,
                )
            for target, selected in selections.items():
                if (
                    selected is not None
                    and abs(selected["delta"] - target) <= SHORT_DELTA_TOLERANCE
                    and selected["ric"] not in bars_by_ric
                ):
                    bars_by_ric[selected["ric"]] = fetch_history(
                        selected["ric"], ["BID", "ASK", "TRDPRC_1"],
                        date.fromisoformat(week["entryDate"]), expiry,
                    )

            targets = {}
            for target, selected in selections.items():
                decision = {**week, "targetDelta": target, "status": "DATA_GAP"}
                on_target = selected is not None and abs(selected["delta"] - target) <= SHORT_DELTA_TOLERANCE
                if on_target:
                    chosen = dict(selected)
                    chosen["bars"] = bars_by_ric[chosen["ric"]]
                    entry_quote = quote_at(chosen["bars"], week["entryTime"])
                    exit_time = f"{week['expiry']} {EXIT_HOUR_UTC:02d}:00:00"
                    exit_quote = quote_at(chosen["bars"], exit_time)
                    if valid_quote(entry_quote):
                        decision.update({
                            "status": "TRADE", "short": chosen,
                            "entryQuote": entry_quote, "exitTime": exit_time,
                            "exitQuote": exit_quote,
                            "entryMoneyness": (
                                "OTM" if chosen["strike"] > spot else "ITM_OR_ATM_AFTER_GAP"
                            ),
                            "exitDataStatus": "OK" if valid_quote(exit_quote) else "DATA_GAP",
                        })
                    else:
                        decision["reason"] = "Missing valid BID/ASK at entry"
                elif not greeks:
                    decision["reason"] = "No candidate RIC returned previous-close Delta"
                elif selected is None:
                    decision["status"] = "NO_TARGET"
                    decision["reason"] = "No valid call Delta was returned"
                else:
                    decision["status"] = "NO_TARGET"
                    decision["reason"] = (
                        f"Nearest OTM Delta was {selected['delta']:.4f}; outside "
                        f"±{SHORT_DELTA_TOLERANCE:.2f} of target {target:.2f}"
                    )
                targets[f"{target:.2f}"] = decision
            weekly.append({**week, "candidateRics": len(candidates), "deltaRows": len(greeks), "targets": targets})
            details = []
            for target in SHORT_TARGET_DELTAS:
                decision = targets[f"{target:.2f}"]
                selected = selections[target]
                if decision["status"] == "TRADE":
                    details.append(f"{target:.2f}→TRADE Δ{selected['delta']:.4f}")
                elif selected is None:
                    details.append(f"{target:.2f}→{decision['status']} (no call Delta)")
                else:
                    details.append(
                        f"{target:.2f}→{decision['status']} "
                        f"(nearest Δ{selected['delta']:.4f})"
                    )
            detail = " · ".join(details)
            print(
                f"Week {index}/{len(schedule)} {week['entryDate']}: "
                f"{len(candidates)} candidate RICs · {len(greeks)} Delta rows · {detail}",
                flush=True,
            )

        payload = {
            "source": "LSEG Workspace",
            "fetchedAt": datetime.now().isoformat(timespec="seconds"),
            "underlying": UNDERLYING,
            "start": START.isoformat(),
            "end": END.isoformat(),
            "stock": stock,
            "schedule": schedule,
            "longs": selected_longs,
            "weekly": weekly,
        }
        CACHE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    finally:
        ld.close_session()


def snapshot(
    timestamp: str,
    event: str,
    cash: float,
    long_ric: str,
    long_quote: dict[str, Any],
    short: dict[str, Any] | None = None,
    short_quote: dict[str, Any] | None = None,
) -> dict[str, Any]:
    long_bid = float(long_quote["bid"])
    short_ask = float(short_quote["ask"]) if short and short_quote else 0.0
    long_mv = 100 * long_bid
    short_mv = -100 * short_ask
    return {
        "time": timestamp,
        "event": event,
        "cash": round(cash, 2),
        "longRic": long_ric,
        "longBid": round(long_bid, 4),
        "longMv": round(long_mv, 2),
        "shortRic": short["ric"] if short else None,
        "shortAsk": round(short_ask, 4),
        "shortMv": round(short_mv, 2),
        "nav": round(cash + long_mv + short_mv, 2),
    }


def run_backtest(
    data: dict[str, Any], long_target: float, short_target: float
) -> dict[str, Any]:
    selected_long = next(
        (row for row in data["longs"] if math.isclose(row["targetDelta"], long_target)),
        None,
    )
    if selected_long is None:
        raise RuntimeError(f"Dataset has no long selection for target {long_target:.2f}")
    if abs(float(selected_long["delta"]) - long_target) > LONG_DELTA_TOLERANCE:
        raise AssertionError(
            f"Long trade violates ±{LONG_DELTA_TOLERANCE:.2f} band around {long_target:.2f}"
        )
    long_bars = selected_long["bars"]
    first = data["schedule"][0]
    long_entry_quote = quote_at(long_bars, first["entryTime"])
    if not valid_quote(long_entry_quote):
        raise RuntimeError("Selected long call has no valid entry BID/ASK")

    cash = STARTING_CASH
    blotter = []
    ledger = []
    long_ask = float(long_entry_quote["ask"])
    long_cost = long_ask * 100 + COMMISSION
    cash -= long_cost
    blotter.append(
        {
            "time": first["entryTime"],
            "action": "BUY",
            "leg": "LONG",
            "ric": selected_long["ric"],
            "strike": selected_long["strike"],
            "expiry": selected_long["expiry"],
            "deltaAsOf": selected_long["deltaAsOf"],
            "delta": selected_long["delta"],
            "bid": long_entry_quote["bid"],
            "ask": long_entry_quote["ask"],
            "fill": long_ask,
            "fee": COMMISSION,
            "cashChange": round(-long_cost, 2),
            "rule": f"Buy previous-close Delta nearest {long_target:.2f} at ask",
        }
    )
    ledger.append(
        snapshot(first["entryTime"], "LONG ENTRY", cash, selected_long["ric"], long_entry_quote)
    )

    decisions = []
    for weekly_set in data["weekly"]:
        week = weekly_set["targets"][f"{short_target:.2f}"]
        decision = {key: value for key, value in week.items() if key not in {"short", "entryQuote", "exitQuote"}}
        if week["status"] != "TRADE":
            decisions.append(decision)
            continue
        short = week["short"]
        if abs(float(short["delta"]) - short_target) > SHORT_DELTA_TOLERANCE:
            raise AssertionError(
                f"Short trade {short['ric']} violates ±{SHORT_DELTA_TOLERANCE:.2f} "
                f"band around {short_target:.2f}"
            )
        if float(short["strike"]) <= float(selected_long["strike"]):
            raise AssertionError("Short strike must be above the long strike")
        entry_quote = week["entryQuote"]
        exit_quote = week["exitQuote"]
        if not valid_quote(exit_quote):
            raise RuntimeError(
                f"Short call {short['ric']} was entered but has no valid exit quote "
                f"at {week['exitTime']}; refusing a look-ahead skip or invented fill"
            )
        premium = float(entry_quote["bid"]) * 100 - COMMISSION
        cash += premium
        blotter.append(
            {
                "time": week["entryTime"],
                "action": "SELL",
                "leg": "SHORT",
                "ric": short["ric"],
                "strike": short["strike"],
                "expiry": short["expiry"],
                "deltaAsOf": short["deltaAsOf"],
                "delta": short["delta"],
                "bid": entry_quote["bid"],
                "ask": entry_quote["ask"],
                "fill": entry_quote["bid"],
                "fee": COMMISSION,
                "cashChange": round(premium, 2),
                "rule": f"Sell previous-close Delta nearest {short_target:.2f} at bid",
            }
        )
        long_entry_mark = quote_at(long_bars, week["entryTime"])
        if not valid_quote(long_entry_mark):
            raise RuntimeError(f"Missing long-call mark at {week['entryTime']}")
        ledger.append(
            snapshot(
                week["entryTime"],
                "SHORT ENTRY",
                cash,
                selected_long["ric"],
                long_entry_mark,
                short,
                entry_quote,
            )
        )

        close_cost = float(exit_quote["ask"]) * 100 + COMMISSION
        cash -= close_cost
        blotter.append(
            {
                "time": week["exitTime"],
                "action": "BTC",
                "leg": "SHORT",
                "ric": short["ric"],
                "strike": short["strike"],
                "expiry": short["expiry"],
                "deltaAsOf": None,
                "delta": None,
                "bid": exit_quote["bid"],
                "ask": exit_quote["ask"],
                "fill": exit_quote["ask"],
                "fee": COMMISSION,
                "cashChange": round(-close_cost, 2),
                "rule": "Close at 15:00 ET on expiry to avoid assignment",
            }
        )
        long_exit_mark = quote_at(long_bars, week["exitTime"])
        if not valid_quote(long_exit_mark):
            raise RuntimeError(f"Missing long-call mark at {week['exitTime']}")
        ledger.append(
            snapshot(week["exitTime"], "SHORT EXIT", cash, selected_long["ric"], long_exit_mark)
        )
        decision.update(
            {
                "shortRic": short["ric"],
                "shortStrike": short["strike"],
                "shortDelta": short["delta"],
                "entryBid": entry_quote["bid"],
                "exitAsk": exit_quote["ask"],
                "shortStrikeBelowLongBreakeven": (
                    float(short["strike"]) < float(selected_long["breakeven"])
                ),
            }
        )
        decisions.append(decision)

    final_time = f"{END.isoformat()} {EXIT_HOUR_UTC:02d}:00:00"
    final_quote = quote_at(long_bars, final_time)
    if not valid_quote(final_quote):
        raise RuntimeError(f"Selected long call has no valid final quote at {final_time}")
    proceeds = float(final_quote["bid"]) * 100 - COMMISSION
    cash += proceeds
    blotter.append(
        {
            "time": final_time,
            "action": "SELL",
            "leg": "LONG",
            "ric": selected_long["ric"],
            "strike": selected_long["strike"],
            "expiry": selected_long["expiry"],
            "deltaAsOf": None,
            "delta": None,
            "bid": final_quote["bid"],
            "ask": final_quote["ask"],
            "fill": final_quote["bid"],
            "fee": COMMISSION,
            "cashChange": round(proceeds, 2),
            "rule": "Close long call at bid at backtest end",
        }
    )
    ledger.append(
        {
            "time": final_time,
            "event": "LONG EXIT",
            "cash": round(cash, 2),
            "longRic": None,
            "longBid": 0.0,
            "longMv": 0.0,
            "shortRic": None,
            "shortAsk": 0.0,
            "shortMv": 0.0,
            "nav": round(cash, 2),
        }
    )

    navs = [STARTING_CASH, *(float(row["nav"]) for row in ledger)]
    peak = navs[0]
    max_drawdown = 0.0
    for nav in navs:
        peak = max(peak, nav)
        max_drawdown = min(max_drawdown, nav / peak - 1)

    short_sales = [row for row in blotter if row["leg"] == "SHORT" and row["action"] == "SELL"]
    short_closes = [row for row in blotter if row["leg"] == "SHORT" and row["action"] == "BTC"]
    if len(short_sales) != len(short_closes):
        raise AssertionError("Every opened short must have exactly one closing trade")
    cash_from_blotter = STARTING_CASH + sum(float(row["cashChange"]) for row in blotter)
    if not math.isclose(cash, cash_from_blotter, abs_tol=0.011):
        raise AssertionError("Blotter cash changes do not reconcile to ending cash")
    premium_collected = sum(float(row["fill"]) * 100 for row in short_sales)
    short_close_cost = sum(float(row["fill"]) * 100 for row in short_closes)

    stock_by_time = {row["time"]: row for row in data["stock"]}
    stock_entry = float(stock_by_time[first["entryTime"]]["open"])
    stock_exit_row = stock_by_time.get(final_time)
    if not stock_exit_row or stock_exit_row.get("close") is None:
        raise RuntimeError(f"Missing AAPL benchmark exit price at {final_time}")
    stock_exit = float(stock_exit_row["close"])
    benchmark_return = stock_exit / stock_entry - 1

    output = {
        "strategy": "AAPL poor man's covered call",
        "combinationId": f"L{long_target:.2f}-S{short_target:.2f}",
        "source": data["source"],
        "start": data["start"],
        "end": data["end"],
        "startingCash": STARTING_CASH,
        "commissionPerContract": COMMISSION,
        "longTargetDelta": long_target,
        "shortTargetDelta": short_target,
        "shortDeltaBand": [
            short_target - SHORT_DELTA_TOLERANCE,
            short_target + SHORT_DELTA_TOLERANCE,
        ],
        "long": {key: value for key, value in selected_long.items() if key != "bars"},
        "decisions": decisions,
        "blotter": blotter,
        "ledger": ledger,
        "endingNav": round(cash, 2),
        "returnPct": round((cash / STARTING_CASH - 1) * 100, 4),
        "pnlOnLongDebitPct": round((cash - STARTING_CASH) / long_cost * 100, 4),
        "maxDrawdownPct": round(max_drawdown * 100, 4),
        "longOpeningDebit": round(long_cost, 2),
        "premiumCollected": round(premium_collected, 2),
        "shortCloseCost": round(short_close_cost, 2),
        "shortNetBeforeFees": round(premium_collected - short_close_cost, 2),
        "tradeWeeks": sum(row["status"] == "TRADE" for row in decisions),
        "dataGapWeeks": sum(row["status"] == "DATA_GAP" for row in decisions),
        "noTargetWeeks": sum(row["status"] == "NO_TARGET" for row in decisions),
        "benchmark": {
            "name": "AAPL buy-and-hold",
            "entry": round(stock_entry, 4),
            "exit": round(stock_exit, 4),
            "returnPct": round(benchmark_return * 100, 4),
        },
    }
    return output


def run_all_backtests(data: dict[str, Any]) -> dict[str, Any]:
    combinations = [
        run_backtest(data, long_target, short_target)
        for long_target in LONG_TARGET_DELTAS
        for short_target in SHORT_TARGET_DELTAS
    ]
    output = {
        "strategy": "AAPL poor man's covered call parameter comparison",
        "source": data["source"],
        "start": data["start"],
        "end": data["end"],
        "method": {
            "longTargetDeltas": list(LONG_TARGET_DELTAS),
            "shortTargetDeltas": list(SHORT_TARGET_DELTAS),
            "longTolerance": LONG_DELTA_TOLERANCE,
            "shortTolerance": SHORT_DELTA_TOLERANCE,
        },
        "combinations": combinations,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--from-cache",
        action="store_true",
        help="Rebuild the backtest from pmcc_aapl_data.json without calling LSEG",
    )
    args = parser.parse_args()
    if args.from_cache:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if "longs" not in data or any("targets" not in row for row in data.get("weekly", [])):
            raise RuntimeError(
                "pmcc_aapl_data.json uses the old single-combination schema; "
                "run once without --from-cache"
            )
    else:
        data = fetch_dataset()
    output = run_all_backtests(data)
    best = max(output["combinations"], key=lambda row: row["endingNav"])
    print(
        f"Saved {CACHE_PATH.name} and {OUTPUT_PATH.name}; "
        f"ran {len(output['combinations'])} combinations; best {best['combinationId']} "
        f"ending NAV ${best['endingNav']:,.2f}, return {best['returnPct']:.2f}%"
    )


if __name__ == "__main__":
    main()
