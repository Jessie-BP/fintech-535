import json
import sys
from math import ceil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "helios" / "python"))

from option_rics import build_call_ric

DATA_PATH = Path("/Users/pang/Downloads/NVDA.O (2).json")
ENTRY_HOUR_UTC = 14  # 14:00 UTC = 10:00 ET during daylight saving time

with DATA_PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)
    
bars = data["bars"]

# Determine the final date covered by the stock dataset.
data_end = max(datetime.fromisoformat(bar["time"]).date() for bar in bars)

entries = []

for bar in bars:
    timestamp = datetime.fromisoformat(bar["time"])
    
    is_monday = timestamp.weekday() == 0
    is_entry_time = (timestamp.hour == ENTRY_HOUR_UTC
                     and timestamp.minute == 0
                     and timestamp.second == 0)
    
    if not (is_monday and is_entry_time):
        continue
    
    # Monday + 4 calendar days = Friday.
    expiry = timestamp.date() + timedelta(days=4)
    
    # Skip incomplete weeks when the dataset does not reach Friday expiry.
    if expiry > data_end:
        continue
    
    entries.append(
        {
            "entry_time": timestamp,
            "stock_fill": float(bar["open"]),
            "expiry": expiry,
        }
    )
    
print(f"{'ENTRY TIME (UTC)':<22} {'STOCK FILL':>12} {'EXPIRY':>12}")
print("-" * 50)

for entry in entries:
    print(
        f"{entry['entry_time']:%Y-%m-%d %H:%M}"
        f"{entry['stock_fill']:>14.4f}     "
        f"{entry['expiry']:%Y-%m-%d}"
    )

print(f"\nComplete entry weeks: {len(entries)}")

candidates = []

for entry in entries:
    spot = entry["stock_fill"]
    expiry = entry["expiry"]

    # Historical option chains are unavailable after expiry, so enumerate a
    # narrow $2.50 grid around spot and let LSEG history validate each RIC.
    strike_step = 2.5
    center_strike = ceil(spot / strike_step) * strike_step
    candidate_strikes = [
        center_strike + offset * strike_step
        for offset in range(-4, 5)
    ]

    for strike in candidate_strikes:
        strike = round(float(strike), 2)
        
        ric = build_call_ric(root="NVDA", expiry=expiry, strike=strike, as_of=date.today(),)
        
        candidates.append({"ric": ric, "strike": strike, "expiry": expiry.isoformat(), "expired": expiry < date.today(),})
        
print("\nOPTION CANDIDATES")
print("-" * 75)

for candidate in candidates:
    print(
        f"{candidate['expiry']}  "
        f"{candidate['strike']:>7.2f}  "
        f"{candidate['ric']}"
    )

print(f"\nCandidate contracts: {len(candidates)}")        

options_request = {
    "op": "options_fetch",
    "ric": "NVDA.O",
    "root": "NVDA",
    "start": data["start"],
    "end": data["end"],
    "interval": data["interval"],
    "candidates": candidates,
}

request_path = PROJECT_ROOT / "NVDA-options-request.json"

with request_path.open("w", encoding="utf-8") as file:
    json.dump(options_request, file, indent=2)

print(f"Options request saved to: {request_path}")

# Select the actual nearest-OTM call from LSEG option history.
options_response_path = PROJECT_ROOT / "NVDA-options-response.json"

with options_response_path.open("r", encoding="utf-8") as file:
    options_response = json.load(file)

contracts_by_expiry = {}
for contract in options_response.get("added", []):
    contract_expiry = contract["expiry"]
    contracts_by_expiry.setdefault(contract_expiry, []).append(contract)

stock_bars_by_time = {bar["time"]: bar for bar in bars}
weekly_decisions = []

for entry in entries:
    entry_time = entry["entry_time"]
    expiry = entry["expiry"]
    spot = entry["stock_fill"]
    entry_timestamp = entry_time.strftime("%Y-%m-%d %H:%M:%S")
    expiry_text = expiry.isoformat()
    valid_otm_quotes = []

    for contract in contracts_by_expiry.get(expiry_text, []):
        strike = float(contract["strike"])

        # Permit ATM only when spot lands exactly on a listed strike.
        if strike < spot:
            continue

        entry_bar = next(
            (
                option_bar
                for option_bar in contract.get("bars", [])
                if option_bar["time"] == entry_timestamp
            ),
            None,
        )
        if entry_bar is None:
            continue

        bid = entry_bar.get("bid")
        ask = entry_bar.get("ask")
        if bid is None or ask is None:
            continue

        bid = float(bid)
        ask = float(ask)
        if bid < 0 or ask < bid:
            continue

        valid_otm_quotes.append(
            {
                "ric": contract["ric"],
                "strike": strike,
                "bid": bid,
                "ask": ask,
                "mid": (bid + ask) / 2,
            }
        )

    if not valid_otm_quotes:
        weekly_decisions.append(
            {
                "entry_time": entry_time,
                "expiry": expiry,
                "spot": spot,
                "status": "SKIP",
                "reason": "No valid OTM call with both BID and ASK.",
            }
        )
        continue

    selected = min(valid_otm_quotes, key=lambda quote: quote["strike"])

    # The 19:00 UTC bar spans the last regular-market hour (15:00-16:00 ET).
    expiry_timestamp = f"{expiry_text} 19:00:00"
    expiry_stock_bar = stock_bars_by_time.get(expiry_timestamp)

    if expiry_stock_bar is None:
        weekly_decisions.append(
            {
                "entry_time": entry_time,
                "expiry": expiry,
                "spot": spot,
                "status": "SKIP",
                "reason": "No Friday regular-session closing stock bar.",
            }
        )
        continue

    expiry_stock_close = float(expiry_stock_bar["close"])
    outcome = (
        "ASSIGN"
        if expiry_stock_close > selected["strike"]
        else "EXPIRE"
    )

    weekly_decisions.append(
        {
            "entry_time": entry_time,
            "expiry": expiry,
            "spot": spot,
            "ric": selected["ric"],
            "strike": selected["strike"],
            "bid": selected["bid"],
            "ask": selected["ask"],
            "mid": selected["mid"],
            "expiry_stock_close": expiry_stock_close,
            "status": "TRADE",
            "outcome": outcome,
        }
    )

print("\nWEEKLY DECISIONS")
print("-" * 110)
print(
    f"{'ENTRY':<18}"
    f"{'EXPIRY':<12}"
    f"{'SPOT':>10}"
    f"{'STRIKE':>10}"
    f"{'BID':>9}"
    f"{'ASK':>9}"
    f"{'MID':>9}"
    f"{'FRI CLOSE':>12}  "
    f"{'RESULT'}"
)

for decision in weekly_decisions:
    if decision["status"] == "SKIP":
        print(
            f"{decision['entry_time']:%Y-%m-%d %H:%M}  "
            f"{decision['expiry']:%Y-%m-%d}  "
            f"{decision['spot']:>8.4f}  "
            f"SKIP - {decision['reason']}"
        )
        continue

    print(
        f"{decision['entry_time']:%Y-%m-%d %H:%M}"
        f"{decision['expiry']:%Y-%m-%d}"
        f"{decision['spot']:>10.4f}"
        f"{decision['strike']:>10.2f}"
        f"{decision['bid']:>9.3f}"
        f"{decision['ask']:>9.3f}"
        f"{decision['mid']:>9.3f}"
        f"{decision['expiry_stock_close']:>12.4f}  "
        f"{decision['outcome']}"
    )

trade_count = sum(
    decision["status"] == "TRADE"
    for decision in weekly_decisions
)
skip_count = sum(
    decision["status"] == "SKIP"
    for decision in weekly_decisions
)

print(f"\nTrade weeks: {trade_count}")
print(f"Skipped weeks: {skip_count}")

# Build the simulated trade blotter and an event-time Reg T ledger.
START_CASH = 25_000.0
INIT_PCT = 0.50
MAINT_PCT = 0.25

cash = START_CASH
shares = 0
short_call = None
blotter = []
ledger = []
stock_buy_count = 0


def add_blotter(
    timestamp,
    side,
    qty,
    instrument,
    asset,
    limit,
    fill,
    multiplier,
    note,
    strike=None,
    expiry=None,
    occ=None,
):
    blotter.append(
        {
            "id": f"t{len(blotter) + 1}",
            "ts": timestamp,
            "side": side,
            "qty": qty,
            "instrument": instrument,
            "occ": occ or instrument,
            "asset": asset,
            "strike": strike,
            "expiry": expiry,
            "limit": limit,
            "fill": fill,
            "multiplier": multiplier,
            "notes": note,
        }
    )


def add_ledger_snapshot(timestamp, stock_price, option_price=0.0):
    if short_call is not None:
        call_expiry = date.fromisoformat(short_call["expiry"])
        call_label = (
            f"{call_expiry.month}/{call_expiry.day} "
            f"{short_call['strike']:g}C"
        )
    else:
        call_label = "—"

    option_market_value = (
        -100.0 * option_price
        if short_call is not None
        else 0.0
    )
    long_market_value = shares * stock_price
    nav = cash + long_market_value + option_market_value
    initial = INIT_PCT * long_market_value
    maintenance = MAINT_PCT * long_market_value

    ledger.append(
        {
            "date": timestamp,
            "cash": round(cash, 2),
            "shares": shares,
            "shortCalls": -1 if short_call is not None else 0,
            "callLabel": call_label,
            "stockPx": round(stock_price, 4),
            "optPx": round(option_price, 4),
            "lmv": round(long_market_value, 2),
            "optMv": round(option_market_value, 2),
            "nav": round(nav, 2),
            "init": round(initial, 2),
            "maint": round(maintenance, 2),
            "available": round(nav - initial, 2),
            "excess": round(nav - maintenance, 2),
        }
    )


for decision in weekly_decisions:
    entry_time = decision["entry_time"]
    entry_timestamp = (
        entry_time.replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("America/New_York"))
        .strftime("%Y-%m-%d %H:%M ET")
    )
    spot = decision["spot"]

    if decision["status"] == "SKIP":
        # A skipped option order is not a blotter event. If shares remain from
        # an earlier expiry, mark them without changing cash.
        if shares:
            add_ledger_snapshot(entry_timestamp, spot)
        continue

    opened_stock_this_week = shares == 0

    if opened_stock_this_week:
        stock_cost = 100 * spot
        cash -= stock_cost
        shares = 100
        stock_note = (
            "Monday combo · stock leg. Limit = 10:00 ET open print. "
            "Decrease cash. Rule: if flat, buy 100."
            if stock_buy_count == 0
            else
            "Flat after assignment. Monday combo stock leg · buy 100 at "
            "the 10:00 ET open print."
        )
        add_blotter(
            timestamp=entry_timestamp,
            side="BUY",
            qty=100,
            instrument="NVDA.O",
            asset="STK",
            limit=spot,
            fill=spot,
            multiplier=1,
            note=stock_note,
        )
        stock_buy_count += 1

    premium = 100 * decision["mid"]
    cash += premium
    call_label = (
        f"NVDA {decision['expiry'].month}/{decision['expiry'].day} "
        f"{decision['strike']:g} C"
    )
    short_call = {
        "ric": decision["ric"],
        "strike": decision["strike"],
        "expiry": decision["expiry"].isoformat(),
    }
    add_blotter(
        timestamp=entry_timestamp,
        side="SELL",
        qty=1,
        instrument=decision["ric"],
        asset="CALL",
        limit=decision["mid"],
        fill=decision["mid"],
        multiplier=100,
        strike=decision["strike"],
        expiry=decision["expiry"].isoformat(),
        occ=call_label,
        note=(
            f"Monday combo · call leg. Nearest OTM {decision['strike']:g}C. "
            "Limit = mid. Cash +100×mid."
            if opened_stock_this_week
            else
            f"Still long · Monday rewrite {decision['strike']:g}C. "
            "Limit = mid."
        ),
    )
    add_ledger_snapshot(entry_timestamp, spot, decision["mid"])

    expiry_timestamp = f"{decision['expiry'].isoformat()} 16:00 ET"

    if decision["outcome"] == "EXPIRE":
        add_blotter(
            timestamp=expiry_timestamp,
            side="EXPIRE",
            qty=1,
            instrument=decision["ric"],
            asset="CALL",
            limit=None,
            fill=0.0,
            multiplier=100,
            strike=decision["strike"],
            expiry=decision["expiry"].isoformat(),
            occ=call_label,
            note=(
                f"Friday OTM: close ${decision['expiry_stock_close']:.2f} "
                f"≤ {decision['strike']:g}C. Exit = wait; keep shares and premium."
            ),
        )
        short_call = None
    else:
        add_blotter(
            timestamp=expiry_timestamp,
            side="ASSIGN",
            qty=1,
            instrument=decision["ric"],
            asset="CALL",
            limit=None,
            fill=0.0,
            multiplier=100,
            strike=decision["strike"],
            expiry=decision["expiry"].isoformat(),
            occ=call_label,
            note=(
                f"Friday ITM: close ${decision['expiry_stock_close']:.2f} "
                f"> {decision['strike']:g}C. Exit = wait; short call assigned."
            ),
        )
        assignment_proceeds = 100 * decision["strike"]
        cash += assignment_proceeds
        shares = 0
        short_call = None
        add_blotter(
            timestamp=expiry_timestamp,
            side="SELL",
            qty=100,
            instrument="NVDA.O",
            asset="STK",
            limit=decision["strike"],
            fill=decision["strike"],
            multiplier=1,
            strike=decision["strike"],
            expiry=decision["expiry"].isoformat(),
            note=(
                f"Assignment delivery: sell 100 at ${decision['strike']:g}. "
                f"Cash +${assignment_proceeds:,.0f}; now flat."
            ),
        )

    add_ledger_snapshot(
        expiry_timestamp,
        decision["expiry_stock_close"],
    )

backtest_output = {
    "underlying": "NVDA",
    "startCash": START_CASH,
    "initPct": INIT_PCT,
    "maintPct": MAINT_PCT,
    "blotter": blotter,
    "ledger": ledger,
    "tradeWeeks": trade_count,
    "skippedWeeks": skip_count,
}

backtest_output_path = PROJECT_ROOT / "nvda_backtest_output.json"
with backtest_output_path.open("w", encoding="utf-8") as file:
    json.dump(backtest_output, file, indent=2)

print("\nBACKTEST ACCOUNT")
print("-" * 60)
print(f"Starting cash: ${START_CASH:,.2f}")
print(f"Ending cash:   ${cash:,.2f}")
print(f"Ending shares: {shares}")
print(f"Blotter rows:  {len(blotter)}")
print(f"Ledger rows:   {len(ledger)}")
print(f"Saved to:      {backtest_output_path}")
