"""Embed the verified wheel backtest output in the static GitHub Pages app."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "wheel_aapl_output.json"
TARGET = ROOT / "gh-pages" / "helios" / "wheel" / "book.js"


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    required = {"blotter", "ledger", "timeline", "decisions", "benchmark", "fillStats", "sensitivity"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"Wheel output is missing: {', '.join(sorted(missing))}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("window.WHEEL_BOOK = " + json.dumps(payload, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Built {TARGET} with {len(payload['blotter'])} blotter rows and {len(payload['timeline'])} timeline bars")


if __name__ == "__main__":
    main()
