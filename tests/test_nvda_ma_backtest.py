import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "nvda_ma_backtest", Path(__file__).resolve().parents[1] / "scripts" / "nvda_ma_backtest.py"
)
bt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bt)


class BacktestTimingTests(unittest.TestCase):
    def test_signal_at_close_fills_at_next_open(self):
        # 60 flat days, then a steady rise: MA20 crosses above MA50 on the first up day.
        start = date(2024, 1, 1)
        closes = [100.0] * 60 + [100.0 + i for i in range(1, 41)]
        bars = [(start + timedelta(days=i), c - 0.5, c) for i, c in enumerate(closes)]
        result = bt.backtest(bars)
        first = result["trades"][0]
        signal_day = next(i for i in range(49, len(bars))
                          if bt.orders.signal_from_closes(closes[: i + 1])[2])
        self.assertEqual(first["entry"], bars[signal_day + 1][0].isoformat())
        self.assertEqual(first["entry_px"], round(bars[signal_day + 1][1], 2))
        # Flat before the signal: the strategy curve does not move.
        self.assertTrue(all(p["s"] == 1.0 for p in result["series"][: signal_day - 50 + 1]))


if __name__ == "__main__":
    unittest.main()
