import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "nvda_orders", Path(__file__).resolve().parents[1] / "scripts" / "nvda_orders.py"
)
orders = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orders)


class OrderPlanningTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 16)
        self.closes = [(self.today - timedelta(days=70 - i), 100 + i) for i in range(70)]

    def plan(self, closes, held):
        with patch.object(orders, "latest_session", return_value=closes[-1][0]), patch.object(
            orders, "next_session", return_value=date(2026, 11, 17)
        ):
            return orders.plan(closes, held, self.today)

    def test_buy_when_short_average_is_higher(self):
        generated, signal = self.plan(self.closes, 0)
        self.assertEqual(generated[0], {
            "id": "nvda-ma20-50-buy-2026-11-17",
            "for": "2026-11-17",
            "order_type": "mkt",
            "action": "BUY",
            "qty": 1,
            "underlying": 4815747,
            "contract": "underlying",
            "ref": "open",
        })
        self.assertEqual(signal["target_shares"], 1)
        self.assertEqual(self.plan(self.closes, 1)[0], [])

    def test_sell_only_existing_shares_when_signal_is_bearish(self):
        bearish = [(day, 200 - i) for i, (day, _) in enumerate(self.closes)]
        generated, signal = self.plan(bearish, 1)
        self.assertEqual((generated[0]["action"], generated[0]["qty"]), ("SEL", 1))
        self.assertEqual(signal["target_shares"], 0)
        self.assertEqual(self.plan(bearish, 0)[0], [])

    def test_position_parser_and_invalid_data(self):
        self.assertEqual(orders.share_count({"positions": [{"conid": 4815747, "qty": 1}]}), 1)
        self.assertEqual(orders.share_count({"positions": {"4815747": {"qty": 1}}}), 1)
        with self.assertRaises(ValueError):
            self.plan(self.closes[:49], 0)
        with patch.object(orders, "latest_session", return_value=self.today):
            with self.assertRaisesRegex(ValueError, "stale"):
                orders.plan(self.closes, 0, self.today)
        with self.assertRaises(ValueError):
            orders.share_count({"positions": [{"conid": 4815747, "qty": "1"}]})


if __name__ == "__main__":
    unittest.main()
