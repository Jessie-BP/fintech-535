import importlib.util
import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "nvda_orders", Path(__file__).resolve().parents[1] / "scripts" / "nvda_orders.py"
)
orders = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orders)

FOR = date(2026, 11, 17)
NVDA = 4815747


class OrderPlanningTests(unittest.TestCase):
    def setUp(self):
        self.today = date(2026, 11, 16)
        self.rising = [(self.today - timedelta(days=70 - i), 100 + i) for i in range(70)]
        self.falling = [(day, 200 - i) for i, (day, _) in enumerate(self.rising)]

    def plan(self, closes, book):
        with patch.object(orders, "latest_session", return_value=closes[-1][0]), patch.object(
            orders, "next_session", return_value=FOR
        ):
            return orders.plan(closes, book, self.today)

    def test_flat_book_uptrend_writes_cash_secured_put(self):
        generated, signal = self.plan(self.rising, {})
        self.assertEqual(generated, [{
            "id": "nvda-csp-2026-11-17",
            "for": "2026-11-17",
            "order_type": "mkt",
            "action": "SHT",
            "qty": 1,
            "underlying": NVDA,
            "contract": "put",
            "expiry": "5DTE+",
            "strike": "otm:1",
            "ref": "open",
        }])
        self.assertEqual(signal["trend"], "up")
        # Chart history: one point per session that has a 50-day mean, newest last.
        self.assertEqual(len(signal["history"]), 70 - 49)
        self.assertEqual(signal["history"][-1]["c"], 169)
        self.assertEqual(signal["history"][-1]["m20"], signal["ma20"])

    def test_flat_book_downtrend_stays_out(self):
        generated, signal = self.plan(self.falling, {})
        self.assertEqual(generated, [])
        self.assertEqual(signal["trend"], "down")

    def test_assigned_shares_uptrend_writes_covered_call(self):
        book = {"positions": [{"conid": NVDA, "contract": "underlying", "qty": 100}]}
        generated, _ = self.plan(self.rising, book)
        self.assertEqual(len(generated), 1)
        o = generated[0]
        self.assertEqual((o["id"], o["action"], o["qty"], o["contract"], o["strike"]),
                         ("nvda-cc-2026-11-17", "SHT", 1, "call", "otm:1"))

    def test_shares_downtrend_sells_shares(self):
        book = {"positions": [{"conid": NVDA, "qty": 100}]}
        generated, _ = self.plan(self.falling, book)
        self.assertEqual([(o["action"], o["qty"], o["contract"]) for o in generated],
                         [("SEL", 100, "underlying")])
        self.assertNotIn("strike", generated[0])
        self.assertNotIn("expiry", generated[0])

    def test_open_short_option_waits(self):
        for book in (
            {"positions": [{"underlying": NVDA, "contract": "put", "qty": -1}]},
            {"positions": [{"underlying": NVDA, "contract": "call", "qty": 1, "side": "short"},
                           {"conid": NVDA, "qty": 100}]},
        ):
            for closes in (self.rising, self.falling):
                self.assertEqual(self.plan(closes, book)[0], [], book)

    def test_odd_lot_is_sold_before_calls(self):
        generated, _ = self.plan(self.rising, {"positions": [{"conid": NVDA, "qty": 101}]})
        self.assertEqual([(o["action"], o["qty"], o["contract"]) for o in generated],
                         [("SEL", 1, "underlying"), ("SHT", 1, "call")])
        self.assertEqual(len({o["id"] for o in generated}), 2)

    def test_not_enough_cash_skips_the_put(self):
        generated, signal = self.plan(self.rising, {"cash": 1000.0, "positions": []})
        self.assertEqual(generated, [])
        self.assertIn("does not secure a put", signal["reason"])

    def test_sessions_follow_the_clock_not_the_date(self):
        try:
            import pandas_market_calendars  # noqa: F401
        except ImportError:
            self.skipTest("pandas_market_calendars not installed")
        utc = ZoneInfo("UTC")
        cases = [
            # On time: 03:00 UTC Tue = 22:00 Mon New York.
            (datetime(2026, 11, 17, 3, 0, tzinfo=utc), date(2026, 11, 16), date(2026, 11, 17)),
            # GitHub started it late: 06:32 Tue New York, before the open.
            (datetime(2026, 11, 17, 11, 32, tzinfo=utc), date(2026, 11, 16), date(2026, 11, 17)),
            # Mid-session manual run: plan tomorrow off yesterday's close.
            (datetime(2026, 11, 17, 16, 0, tzinfo=utc), date(2026, 11, 16), date(2026, 11, 18)),
            # Friday night plans Monday.
            (datetime(2026, 11, 21, 3, 0, tzinfo=utc), date(2026, 11, 20), date(2026, 11, 23)),
        ]
        for now, last, nxt in cases:
            self.assertEqual(orders.latest_session(now), last, now)
            self.assertEqual(orders.next_session(now), nxt, now)

    def test_book_parser_and_invalid_data(self):
        state = orders.book_state
        self.assertEqual(state({})["shares"], 0)
        self.assertEqual(state({"positions": [{"conid": NVDA, "qty": 100}]})["shares"], 100)
        self.assertEqual(state({"positions": {str(NVDA): {"qty": 200}}})["shares"], 200)
        self.assertEqual(state({str(NVDA): 100, "cash": 5e4})["shares"], 100)
        self.assertEqual(state({"cash": 5e4})["cash"], 5e4)
        # Other underlyings are ignored.
        self.assertEqual(state([{"conid": 3691937, "qty": 100}])["shares"], 0)
        with self.assertRaises(ValueError):
            self.plan(self.rising[:49], {})
        with patch.object(orders, "latest_session", return_value=self.today):
            with self.assertRaisesRegex(ValueError, "stale"):
                orders.plan(self.rising, {}, self.today)
        with self.assertRaises(ValueError):
            state({"positions": [{"conid": NVDA, "qty": "1"}]})
        with self.assertRaises(ValueError):
            state({"positions": [{"conid": NVDA, "qty": -5}]})
        with self.assertRaises(ValueError):
            state({"positions": [{"conid": NVDA, "contract": "future", "qty": 1}]})


if __name__ == "__main__":
    unittest.main()
