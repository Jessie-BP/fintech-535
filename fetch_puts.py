"""Add corrected expired UUUU put RICs to an existing calls-only cache."""

from __future__ import annotations

import pickle
import re
import time
from pathlib import Path

import lseg.data as ld
import pandas as pd

SOURCE = Path("option_pipeline_data.calls-only.partial.pkl")
CHECKPOINT = Path("option_pipeline_data.puts.partial.pkl")
OUTPUT = Path("option_pipeline_data.pkl")
RIC = re.compile(r"^(?P<root>[A-Z]+)(?P<call>[A-L])(?P<rest>\d{9}\.U)\^(?P<suffix>[A-L]\d{2})$")


def put_ric(call_ric: str) -> str:
    match = RIC.match(call_ric)
    if not match:
        raise ValueError(f"Unexpected call RIC: {call_ric}")
    put_code = chr(ord(match.group("call")) + 12)
    return f"{match.group('root')}{put_code}{match.group('rest')}^{match.group('suffix')}"


def request_batch(rics: list[str], start: str, end: str) -> pd.DataFrame:
    try:
        frame = ld.get_history(
            universe=rics,
            fields=["TRDPRC_1", "MID_PRICE"],
            start=start,
            end=end,
            interval="daily",
        )
        if len(rics) == 1 and not isinstance(frame.columns, pd.MultiIndex):
            frame.columns = pd.MultiIndex.from_tuples(
                [(rics[0], str(field)) for field in frame.columns],
                names=["RIC", "Field"],
            )
        return frame
    except Exception as error:
        print(f"Batch of {len(rics)} failed: {error}", flush=True)
        return pd.DataFrame()


def main() -> None:
    with SOURCE.open("rb") as handle:
        payload = pickle.load(handle)
    calls = payload["options"]
    call_rics = sorted(set(map(str, calls.columns.get_level_values(0))))
    groups: dict[str, list[str]] = {}
    for call in call_rics:
        put = put_ric(call)
        expiry_key = put.split(".U", 1)[0][-9:-5]
        groups.setdefault(expiry_key, []).append(put)

    frames = [calls]
    if CHECKPOINT.exists():
        with CHECKPOINT.open("rb") as handle:
            frames.extend(pickle.load(handle))

    start = payload["stock"].index.min().strftime("%Y-%m-%d")
    end = payload["stock"].index.max().strftime("%Y-%m-%d")
    existing = {
        str(value)
        for frame in frames[1:]
        if isinstance(frame.columns, pd.MultiIndex)
        for value in frame.columns.get_level_values(0)
    }

    ld.open_session()
    try:
        for expiry, rics in sorted(groups.items()):
            pending = [ric for ric in rics if ric not in existing]
            if not pending:
                continue
            print(f"Fetching expiry {expiry}: {len(pending)} puts", flush=True)
            for offset in range(0, len(pending), 8):
                frame = request_batch(pending[offset : offset + 8], start, end)
                if frame is not None and not frame.empty:
                    frame = frame.dropna(how="all", axis=1)
                    if not frame.empty:
                        frames.append(frame)
                time.sleep(0.5)
            with CHECKPOINT.open("wb") as handle:
                pickle.dump(frames[1:], handle)
    finally:
        ld.close_session()

    normalized = []
    for frame in frames:
        frame = frame.copy()
        if not isinstance(frame.columns, pd.MultiIndex):
            if not all(isinstance(column, tuple) and len(column) == 2 for column in frame.columns):
                print("Skipping legacy checkpoint frame with ambiguous flat field columns", flush=True)
                continue
            frame.columns = pd.MultiIndex.from_tuples(
                list(frame.columns), names=["RIC", "Field"]
            )
        normalized.append(frame)
    options = pd.concat(normalized, axis=1)
    options = options.loc[:, ~options.columns.duplicated()]
    payload["options"] = options
    payload["synthetic"] = False
    payload["fetched_at"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    with OUTPUT.open("wb") as handle:
        pickle.dump(payload, handle)
    print(f"Saved {OUTPUT} with shape {options.shape}", flush=True)


if __name__ == "__main__":
    main()
