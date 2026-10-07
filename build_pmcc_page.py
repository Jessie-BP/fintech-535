"""Embed the verified PMCC backtest output in the static GitHub Pages app."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "pmcc_aapl_output.json"
TARGET = ROOT / "gh-pages" / "helios" / "pmcc" / "book.js"


def main():
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    required = {"combinations", "method", "source", "start", "end"}
    missing = required - payload.keys()
    if missing:
        raise ValueError(f"PMCC output is missing: {', '.join(sorted(missing))}")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        "window.PMCC_BOOK = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )
    if len(payload["combinations"]) != 15:
        raise ValueError("Expected 5 × 3 = 15 PMCC combinations")
    print(f"Built {TARGET} with {len(payload['combinations'])} combinations")


if __name__ == "__main__":
    main()
