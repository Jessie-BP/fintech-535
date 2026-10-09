window.HELIOS_BOOK = {
  "underlying": "NVDA",
  "startCash": 25000,
  "initPct": 0.5,
  "maintPct": 0.25,
  "blotter": [
    {
      "id": "t1",
      "ts": "2026-06-01 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 219.17,
      "fill": 219.17,
      "multiplier": 1,
      "notes": "Monday combo · stock leg. Limit = 10:00 ET open print. Decrease cash. Rule: if flat, buy 100."
    },
    {
      "id": "t2",
      "ts": "2026-06-01 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAF052622000.U^F26",
      "occ": "NVDA 6/5 220 C",
      "asset": "CALL",
      "strike": 220,
      "expiry": "2026-06-05",
      "limit": 4.35,
      "fill": 4.35,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 220C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t3",
      "ts": "2026-06-05 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAF052622000.U^F26",
      "occ": "NVDA 6/5 220 C",
      "asset": "CALL",
      "strike": 220,
      "expiry": "2026-06-05",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $205.11 ≤ 220C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t4",
      "ts": "2026-06-08 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAF122620750.U^F26",
      "occ": "NVDA 6/12 207.5 C",
      "asset": "CALL",
      "strike": 207.5,
      "expiry": "2026-06-12",
      "limit": 3.8,
      "fill": 3.8,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 207.5C. Limit = mid."
    },
    {
      "id": "t5",
      "ts": "2026-06-12 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAF122620750.U^F26",
      "occ": "NVDA 6/12 207.5 C",
      "asset": "CALL",
      "strike": 207.5,
      "expiry": "2026-06-12",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $205.14 ≤ 207.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t6",
      "ts": "2026-06-15 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAF182621000.U^F26",
      "occ": "NVDA 6/18 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-06-18",
      "limit": 2.7649999999999997,
      "fill": 2.7649999999999997,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 210C. Limit = mid."
    },
    {
      "id": "t7",
      "ts": "2026-06-18 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAF182621000.U^F26",
      "occ": "NVDA 6/18 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-06-18",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $210.20 > 210C. Exit = wait; short call assigned."
    },
    {
      "id": "t8",
      "ts": "2026-06-18 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 210,
      "expiry": "2026-06-18",
      "limit": 210,
      "fill": 210,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $210. Cash +$21,000; now flat."
    },
    {
      "id": "t9",
      "ts": "2026-06-22 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 213.08,
      "fill": 213.08,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t10",
      "ts": "2026-06-22 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAF262621500.U^F26",
      "occ": "NVDA 6/26 215 C",
      "asset": "CALL",
      "strike": 215,
      "expiry": "2026-06-26",
      "limit": 2.835,
      "fill": 2.835,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 215C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t11",
      "ts": "2026-06-26 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAF262621500.U^F26",
      "occ": "NVDA 6/26 215 C",
      "asset": "CALL",
      "strike": 215,
      "expiry": "2026-06-26",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $191.71 ≤ 215C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t12",
      "ts": "2026-06-29 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAG022619500.U^G26",
      "occ": "NVDA 7/2 195 C",
      "asset": "CALL",
      "strike": 195,
      "expiry": "2026-07-02",
      "limit": 2.4850000000000003,
      "fill": 2.4850000000000003,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 195C. Limit = mid."
    },
    {
      "id": "t13",
      "ts": "2026-07-02 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAG022619500.U^G26",
      "occ": "NVDA 7/2 195 C",
      "asset": "CALL",
      "strike": 195,
      "expiry": "2026-07-02",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $194.52 ≤ 195C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t14",
      "ts": "2026-07-06 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAG102619750.U^G26",
      "occ": "NVDA 7/10 197.5 C",
      "asset": "CALL",
      "strike": 197.5,
      "expiry": "2026-07-10",
      "limit": 2.925,
      "fill": 2.925,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 197.5C. Limit = mid."
    },
    {
      "id": "t15",
      "ts": "2026-07-10 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAG102619750.U^G26",
      "occ": "NVDA 7/10 197.5 C",
      "asset": "CALL",
      "strike": 197.5,
      "expiry": "2026-07-10",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $210.94 > 197.5C. Exit = wait; short call assigned."
    },
    {
      "id": "t16",
      "ts": "2026-07-10 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 197.5,
      "expiry": "2026-07-10",
      "limit": 197.5,
      "fill": 197.5,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $197.5. Cash +$19,750; now flat."
    },
    {
      "id": "t17",
      "ts": "2026-07-13 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 208.724,
      "fill": 208.724,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t18",
      "ts": "2026-07-13 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAG172621000.U^G26",
      "occ": "NVDA 7/17 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-07-17",
      "limit": 3.275,
      "fill": 3.275,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 210C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t19",
      "ts": "2026-07-17 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAG172621000.U^G26",
      "occ": "NVDA 7/17 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-07-17",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $202.64 ≤ 210C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t20",
      "ts": "2026-07-20 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAG242620750.U^G26",
      "occ": "NVDA 7/24 207.5 C",
      "asset": "CALL",
      "strike": 207.5,
      "expiry": "2026-07-24",
      "limit": 3.375,
      "fill": 3.375,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 207.5C. Limit = mid."
    },
    {
      "id": "t21",
      "ts": "2026-07-24 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAG242620750.U^G26",
      "occ": "NVDA 7/24 207.5 C",
      "asset": "CALL",
      "strike": 207.5,
      "expiry": "2026-07-24",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $206.96 ≤ 207.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t22",
      "ts": "2026-07-27 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAG312620250.U^G26",
      "occ": "NVDA 7/31 202.5 C",
      "asset": "CALL",
      "strike": 202.5,
      "expiry": "2026-07-31",
      "limit": 4,
      "fill": 4,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 202.5C. Limit = mid."
    },
    {
      "id": "t23",
      "ts": "2026-07-31 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAG312620250.U^G26",
      "occ": "NVDA 7/31 202.5 C",
      "asset": "CALL",
      "strike": 202.5,
      "expiry": "2026-07-31",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $200.80 ≤ 202.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t24",
      "ts": "2026-08-03 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAH072620250.U^H26",
      "occ": "NVDA 8/7 202.5 C",
      "asset": "CALL",
      "strike": 202.5,
      "expiry": "2026-08-07",
      "limit": 3.9000000000000004,
      "fill": 3.9000000000000004,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 202.5C. Limit = mid."
    },
    {
      "id": "t25",
      "ts": "2026-08-07 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAH072620250.U^H26",
      "occ": "NVDA 8/7 202.5 C",
      "asset": "CALL",
      "strike": 202.5,
      "expiry": "2026-08-07",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $223.89 > 202.5C. Exit = wait; short call assigned."
    },
    {
      "id": "t26",
      "ts": "2026-08-07 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 202.5,
      "expiry": "2026-08-07",
      "limit": 202.5,
      "fill": 202.5,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $202.5. Cash +$20,250; now flat."
    },
    {
      "id": "t27",
      "ts": "2026-08-10 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 222.09,
      "fill": 222.09,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t28",
      "ts": "2026-08-10 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAH142622250.U^H26",
      "occ": "NVDA 8/14 222.5 C",
      "asset": "CALL",
      "strike": 222.5,
      "expiry": "2026-08-14",
      "limit": 3.45,
      "fill": 3.45,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 222.5C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t29",
      "ts": "2026-08-14 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAH142622250.U^H26",
      "occ": "NVDA 8/14 222.5 C",
      "asset": "CALL",
      "strike": 222.5,
      "expiry": "2026-08-14",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $225.21 > 222.5C. Exit = wait; short call assigned."
    },
    {
      "id": "t30",
      "ts": "2026-08-14 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 222.5,
      "expiry": "2026-08-14",
      "limit": 222.5,
      "fill": 222.5,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $222.5. Cash +$22,250; now flat."
    },
    {
      "id": "t31",
      "ts": "2026-08-17 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 226.17,
      "fill": 226.17,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t32",
      "ts": "2026-08-17 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAH212622750.U^H26",
      "occ": "NVDA 8/21 227.5 C",
      "asset": "CALL",
      "strike": 227.5,
      "expiry": "2026-08-21",
      "limit": 2.68,
      "fill": 2.68,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 227.5C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t33",
      "ts": "2026-08-21 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAH212622750.U^H26",
      "occ": "NVDA 8/21 227.5 C",
      "asset": "CALL",
      "strike": 227.5,
      "expiry": "2026-08-21",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $214.74 ≤ 227.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t34",
      "ts": "2026-08-24 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAH282621000.U^H26",
      "occ": "NVDA 8/28 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-08-28",
      "limit": 6.175000000000001,
      "fill": 6.175000000000001,
      "multiplier": 100,
      "notes": "Still long · Monday rewrite 210C. Limit = mid."
    },
    {
      "id": "t35",
      "ts": "2026-08-28 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAH282621000.U^H26",
      "occ": "NVDA 8/28 210 C",
      "asset": "CALL",
      "strike": 210,
      "expiry": "2026-08-28",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $217.54 > 210C. Exit = wait; short call assigned."
    },
    {
      "id": "t36",
      "ts": "2026-08-28 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 210,
      "expiry": "2026-08-28",
      "limit": 210,
      "fill": 210,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $210. Cash +$21,000; now flat."
    },
    {
      "id": "t37",
      "ts": "2026-08-31 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 218.87,
      "fill": 218.87,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t38",
      "ts": "2026-08-31 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAI042622000.U^I26",
      "occ": "NVDA 9/4 220 C",
      "asset": "CALL",
      "strike": 220,
      "expiry": "2026-09-04",
      "limit": 2.98,
      "fill": 2.98,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 220C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t39",
      "ts": "2026-09-04 16:00 ET",
      "side": "ASSIGN",
      "qty": 1,
      "instrument": "NVDAI042622000.U^I26",
      "occ": "NVDA 9/4 220 C",
      "asset": "CALL",
      "strike": 220,
      "expiry": "2026-09-04",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session ITM: close $230.34 > 220C. Exit = wait; short call assigned."
    },
    {
      "id": "t40",
      "ts": "2026-09-04 16:00 ET",
      "side": "SELL",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": 220,
      "expiry": "2026-09-04",
      "limit": 220,
      "fill": 220,
      "multiplier": 1,
      "notes": "Assignment delivery: sell 100 at $220. Cash +$22,000; now flat."
    },
    {
      "id": "t41",
      "ts": "2026-09-08 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 229.592,
      "fill": 229.592,
      "multiplier": 1,
      "notes": "Flat after assignment. Monday combo stock leg · buy 100 at the 10:00 ET open print."
    },
    {
      "id": "t42",
      "ts": "2026-09-08 10:00 ET",
      "side": "SELL",
      "qty": 1,
      "instrument": "NVDAI112623000.U^I26",
      "occ": "NVDA 9/11 230 C",
      "asset": "CALL",
      "strike": 230,
      "expiry": "2026-09-11",
      "limit": 3.175,
      "fill": 3.175,
      "multiplier": 100,
      "notes": "Monday combo · call leg. Nearest OTM 230C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t43",
      "ts": "2026-09-11 16:00 ET",
      "side": "EXPIRE",
      "qty": 1,
      "instrument": "NVDAI112623000.U^I26",
      "occ": "NVDA 9/11 230 C",
      "asset": "CALL",
      "strike": 230,
      "expiry": "2026-09-11",
      "limit": null,
      "fill": 0,
      "multiplier": 100,
      "notes": "Expiry-session OTM: close $218.18 ≤ 230C. Exit = wait; keep shares and premium."
    }
  ],
  "ledger": [
    {
      "date": "2026-06-01 10:00 ET",
      "event": "ENTRY",
      "cash": 3518,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/5 220C",
      "stockPx": 219.17,
      "optPx": 4.35,
      "lmv": 21917,
      "optMv": -435,
      "nav": 25000,
      "init": 10958.5,
      "maint": 5479.25,
      "available": 14041.5,
      "excess": 19520.75
    },
    {
      "date": "2026-06-05 16:00 ET",
      "event": "EXPIRE",
      "cash": 3518,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 205.11,
      "optPx": 0,
      "lmv": 20511,
      "optMv": 0,
      "nav": 24029,
      "init": 10255.5,
      "maint": 5127.75,
      "available": 13773.5,
      "excess": 18901.25
    },
    {
      "date": "2026-06-08 10:00 ET",
      "event": "ENTRY",
      "cash": 3898,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/12 207.5C",
      "stockPx": 206.2799,
      "optPx": 3.8,
      "lmv": 20627.99,
      "optMv": -380,
      "nav": 24145.99,
      "init": 10313.99,
      "maint": 5157,
      "available": 13831.99,
      "excess": 18988.99
    },
    {
      "date": "2026-06-12 16:00 ET",
      "event": "EXPIRE",
      "cash": 3898,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 205.14,
      "optPx": 0,
      "lmv": 20514,
      "optMv": 0,
      "nav": 24412,
      "init": 10257,
      "maint": 5128.5,
      "available": 14155,
      "excess": 19283.5
    },
    {
      "date": "2026-06-15 10:00 ET",
      "event": "ENTRY",
      "cash": 4174.5,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/18 210C",
      "stockPx": 208.77,
      "optPx": 2.765,
      "lmv": 20877,
      "optMv": -276.5,
      "nav": 24775,
      "init": 10438.5,
      "maint": 5219.25,
      "available": 14336.5,
      "excess": 19555.75
    },
    {
      "date": "2026-06-18 16:00 ET",
      "event": "ASSIGN",
      "cash": 25174.5,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 210.2,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 25174.5,
      "init": 0,
      "maint": 0,
      "available": 25174.5,
      "excess": 25174.5
    },
    {
      "date": "2026-06-22 10:00 ET",
      "event": "ENTRY",
      "cash": 4150,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/26 215C",
      "stockPx": 213.08,
      "optPx": 2.835,
      "lmv": 21308,
      "optMv": -283.5,
      "nav": 25174.5,
      "init": 10654,
      "maint": 5327,
      "available": 14520.5,
      "excess": 19847.5
    },
    {
      "date": "2026-06-26 16:00 ET",
      "event": "EXPIRE",
      "cash": 4150,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 191.71,
      "optPx": 0,
      "lmv": 19171,
      "optMv": 0,
      "nav": 23321,
      "init": 9585.5,
      "maint": 4792.75,
      "available": 13735.5,
      "excess": 18528.25
    },
    {
      "date": "2026-06-29 10:00 ET",
      "event": "ENTRY",
      "cash": 4398.5,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/2 195C",
      "stockPx": 193.33,
      "optPx": 2.485,
      "lmv": 19333,
      "optMv": -248.5,
      "nav": 23483,
      "init": 9666.5,
      "maint": 4833.25,
      "available": 13816.5,
      "excess": 18649.75
    },
    {
      "date": "2026-07-02 16:00 ET",
      "event": "EXPIRE",
      "cash": 4398.5,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 194.52,
      "optPx": 0,
      "lmv": 19452,
      "optMv": 0,
      "nav": 23850.5,
      "init": 9726,
      "maint": 4863,
      "available": 14124.5,
      "excess": 18987.5
    },
    {
      "date": "2026-07-06 10:00 ET",
      "event": "ENTRY",
      "cash": 4691,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/10 197.5C",
      "stockPx": 196.28,
      "optPx": 2.925,
      "lmv": 19628,
      "optMv": -292.5,
      "nav": 24026.5,
      "init": 9814,
      "maint": 4907,
      "available": 14212.5,
      "excess": 19119.5
    },
    {
      "date": "2026-07-10 16:00 ET",
      "event": "ASSIGN",
      "cash": 24441,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 210.94,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 24441,
      "init": 0,
      "maint": 0,
      "available": 24441,
      "excess": 24441
    },
    {
      "date": "2026-07-13 10:00 ET",
      "event": "ENTRY",
      "cash": 3896.1,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/17 210C",
      "stockPx": 208.724,
      "optPx": 3.275,
      "lmv": 20872.4,
      "optMv": -327.5,
      "nav": 24441,
      "init": 10436.2,
      "maint": 5218.1,
      "available": 14004.8,
      "excess": 19222.9
    },
    {
      "date": "2026-07-17 16:00 ET",
      "event": "EXPIRE",
      "cash": 3896.1,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 202.64,
      "optPx": 0,
      "lmv": 20264,
      "optMv": 0,
      "nav": 24160.1,
      "init": 10132,
      "maint": 5066,
      "available": 14028.1,
      "excess": 19094.1
    },
    {
      "date": "2026-07-20 10:00 ET",
      "event": "ENTRY",
      "cash": 4233.6,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/24 207.5C",
      "stockPx": 205.8536,
      "optPx": 3.375,
      "lmv": 20585.36,
      "optMv": -337.5,
      "nav": 24481.46,
      "init": 10292.68,
      "maint": 5146.34,
      "available": 14188.78,
      "excess": 19335.12
    },
    {
      "date": "2026-07-24 16:00 ET",
      "event": "EXPIRE",
      "cash": 4233.6,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 206.96,
      "optPx": 0,
      "lmv": 20696,
      "optMv": 0,
      "nav": 24929.6,
      "init": 10348,
      "maint": 5174,
      "available": 14581.6,
      "excess": 19755.6
    },
    {
      "date": "2026-07-27 10:00 ET",
      "event": "ENTRY",
      "cash": 4633.6,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/31 202.5C",
      "stockPx": 201.76,
      "optPx": 4,
      "lmv": 20176,
      "optMv": -400,
      "nav": 24409.6,
      "init": 10088,
      "maint": 5044,
      "available": 14321.6,
      "excess": 19365.6
    },
    {
      "date": "2026-07-31 16:00 ET",
      "event": "EXPIRE",
      "cash": 4633.6,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 200.8,
      "optPx": 0,
      "lmv": 20080,
      "optMv": 0,
      "nav": 24713.6,
      "init": 10040,
      "maint": 5020,
      "available": 14673.6,
      "excess": 19693.6
    },
    {
      "date": "2026-08-03 10:00 ET",
      "event": "ENTRY",
      "cash": 5023.6,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/7 202.5C",
      "stockPx": 202.26,
      "optPx": 3.9,
      "lmv": 20226,
      "optMv": -390,
      "nav": 24859.6,
      "init": 10113,
      "maint": 5056.5,
      "available": 14746.6,
      "excess": 19803.1
    },
    {
      "date": "2026-08-07 16:00 ET",
      "event": "ASSIGN",
      "cash": 25273.6,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 223.89,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 25273.6,
      "init": 0,
      "maint": 0,
      "available": 25273.6,
      "excess": 25273.6
    },
    {
      "date": "2026-08-10 10:00 ET",
      "event": "ENTRY",
      "cash": 3409.6,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/14 222.5C",
      "stockPx": 222.09,
      "optPx": 3.45,
      "lmv": 22209,
      "optMv": -345,
      "nav": 25273.6,
      "init": 11104.5,
      "maint": 5552.25,
      "available": 14169.1,
      "excess": 19721.35
    },
    {
      "date": "2026-08-14 16:00 ET",
      "event": "ASSIGN",
      "cash": 25659.6,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 225.21,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 25659.6,
      "init": 0,
      "maint": 0,
      "available": 25659.6,
      "excess": 25659.6
    },
    {
      "date": "2026-08-17 10:00 ET",
      "event": "ENTRY",
      "cash": 3310.6,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/21 227.5C",
      "stockPx": 226.17,
      "optPx": 2.68,
      "lmv": 22617,
      "optMv": -268,
      "nav": 25659.6,
      "init": 11308.5,
      "maint": 5654.25,
      "available": 14351.1,
      "excess": 20005.35
    },
    {
      "date": "2026-08-21 16:00 ET",
      "event": "EXPIRE",
      "cash": 3310.6,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 214.741,
      "optPx": 0,
      "lmv": 21474.1,
      "optMv": 0,
      "nav": 24784.7,
      "init": 10737.05,
      "maint": 5368.53,
      "available": 14047.65,
      "excess": 19416.18
    },
    {
      "date": "2026-08-24 10:00 ET",
      "event": "ENTRY",
      "cash": 3928.1,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/28 210C",
      "stockPx": 209.665,
      "optPx": 6.175,
      "lmv": 20966.5,
      "optMv": -617.5,
      "nav": 24277.1,
      "init": 10483.25,
      "maint": 5241.62,
      "available": 13793.85,
      "excess": 19035.48
    },
    {
      "date": "2026-08-28 16:00 ET",
      "event": "ASSIGN",
      "cash": 24928.1,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 217.54,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 24928.1,
      "init": 0,
      "maint": 0,
      "available": 24928.1,
      "excess": 24928.1
    },
    {
      "date": "2026-08-31 10:00 ET",
      "event": "ENTRY",
      "cash": 3339.1,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "9/4 220C",
      "stockPx": 218.87,
      "optPx": 2.98,
      "lmv": 21887,
      "optMv": -298,
      "nav": 24928.1,
      "init": 10943.5,
      "maint": 5471.75,
      "available": 13984.6,
      "excess": 19456.35
    },
    {
      "date": "2026-09-04 16:00 ET",
      "event": "ASSIGN",
      "cash": 25339.1,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 230.345,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 25339.1,
      "init": 0,
      "maint": 0,
      "available": 25339.1,
      "excess": 25339.1
    },
    {
      "date": "2026-09-08 10:00 ET",
      "event": "ENTRY",
      "cash": 2697.4,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "9/11 230C",
      "stockPx": 229.592,
      "optPx": 3.175,
      "lmv": 22959.2,
      "optMv": -317.5,
      "nav": 25339.1,
      "init": 11479.6,
      "maint": 5739.8,
      "available": 13859.5,
      "excess": 19599.3
    },
    {
      "date": "2026-09-11 16:00 ET",
      "event": "EXPIRE",
      "cash": 2697.4,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 218.18,
      "optPx": 0,
      "lmv": 21818,
      "optMv": 0,
      "nav": 24515.4,
      "init": 10909,
      "maint": 5454.5,
      "available": 13606.4,
      "excess": 19060.9
    }
  ],
  "rics": [
    {
      "label": "NVDA 2026-06-05 220 call (expired)",
      "ric": "NVDAF052622000.U^F26"
    },
    {
      "label": "NVDA 2026-06-18 210 call (expired)",
      "ric": "NVDAF182621000.U^F26"
    },
    {
      "label": "NVDA 2026-07-10 197.5 call (expired)",
      "ric": "NVDAG102619750.U^G26"
    },
    {
      "label": "NVDA 2026-08-07 202.5 call (expired)",
      "ric": "NVDAH072620250.U^H26"
    },
    {
      "label": "NVDA 2026-08-14 222.5 call (expired)",
      "ric": "NVDAH142622250.U^H26"
    },
    {
      "label": "NVDA 2026-08-28 210 call (expired)",
      "ric": "NVDAH282621000.U^H26"
    },
    {
      "label": "NVDA 2026-09-04 220 call (expired)",
      "ric": "NVDAI042622000.U^I26"
    },
    {
      "label": "NVDA 2026-09-11 230 call (expired)",
      "ric": "NVDAI112623000.U^I26"
    }
  ],
  "writeup": {
    "title": "NVDA weeklies — first trading day, nearest OTM at 10:00 ET",
    "fill": "At 10:00 ET on the first exchange session of each week, the stock leg fills at the hourly opening print; a Monday market holiday moves entry to Tuesday or the next open session. The expiry is the final exchange session of that week (Thursday in a Friday-holiday week). Across the $1 and $2.50 near-the-money strike grids, the rule selects the lowest strike at or above spot with a valid BID and ASK; fill is their midpoint.",
    "roll": "No roll and no buy-to-close. The short call is held through its final weekly expiry session. OTM or ATM calls EXPIRE and the shares remain. ITM calls ASSIGN; 100 shares are delivered at strike and the position becomes flat.",
    "pin": "All 15 candidate weeks have verified two-sided entry quotes in the cached LSEG pull. Ending equity was $24,515.40 from $25,000.00 (-1.94%).",
    "regT": "The account starts with $25,000. NAV = cash + stock LMV + option MV, with the short call recorded as a negative asset. Reg T is used because its 50% stock initial requirement and 25% maintenance requirement are transparent and reproducible without a broker-specific portfolio-margin engine; the covered short call adds $0. Available funds and excess remained positive throughout the test.",
    "analysis": "The midpoint regression uses 108 synchronized Monday 10:00 ET observations across the near-the-money chain (R² = 0.898). A high R² supports mid as a reproducible fill assumption, and the fitted slope of 1.005 is essentially one, so prints sit on the quoted midpoint on average. Assignment capped upside in 6 of 15 traded weeks. Every candidate week had a verified quote; any week without one would be shown separately as a data gap rather than silently skipped."
  },
  "midVsTrade": {
    "points": [
      {
        "mid": 10.25,
        "trade": 11.93
      },
      {
        "mid": 8.275,
        "trade": 9.9
      },
      {
        "mid": 6.6,
        "trade": 7.64
      },
      {
        "mid": 5.05,
        "trade": 6.15
      },
      {
        "mid": 3.8,
        "trade": 4.63
      },
      {
        "mid": 2.735,
        "trade": 3.39
      },
      {
        "mid": 1.93,
        "trade": 2.39
      },
      {
        "mid": 1.35,
        "trade": 1.65
      },
      {
        "mid": 0.925,
        "trade": 1.13
      },
      {
        "mid": 9.225,
        "trade": 6.22
      },
      {
        "mid": 7.15,
        "trade": 4.6
      },
      {
        "mid": 5.45,
        "trade": 3.29
      },
      {
        "mid": 4.025,
        "trade": 2.25
      },
      {
        "mid": 2.835,
        "trade": 1.49
      },
      {
        "mid": 1.9,
        "trade": 0.95
      },
      {
        "mid": 1.245,
        "trade": 0.6
      },
      {
        "mid": 0.805,
        "trade": 0.37
      },
      {
        "mid": 0.51,
        "trade": 0.24
      },
      {
        "mid": 9.675,
        "trade": 9.4
      },
      {
        "mid": 7.625,
        "trade": 7.35
      },
      {
        "mid": 5.75,
        "trade": 5.45
      },
      {
        "mid": 4.2,
        "trade": 3.9
      },
      {
        "mid": 2.925,
        "trade": 2.66
      },
      {
        "mid": 1.945,
        "trade": 1.71
      },
      {
        "mid": 1.215,
        "trade": 1.06
      },
      {
        "mid": 0.75,
        "trade": 0.63
      },
      {
        "mid": 0.46,
        "trade": 0.36
      },
      {
        "mid": 9.85,
        "trade": 8.59
      },
      {
        "mid": 7.8,
        "trade": 6.5
      },
      {
        "mid": 6.05,
        "trade": 5.05
      },
      {
        "mid": 4.525,
        "trade": 3.65
      },
      {
        "mid": 3.275,
        "trade": 2.58
      },
      {
        "mid": 2.285,
        "trade": 1.69
      },
      {
        "mid": 1.535,
        "trade": 1.09
      },
      {
        "mid": 0.985,
        "trade": 0.64
      },
      {
        "mid": 0.625,
        "trade": 0.4
      },
      {
        "mid": 9.775,
        "trade": 9.54
      },
      {
        "mid": 7.85,
        "trade": 7.1
      },
      {
        "mid": 6.075,
        "trade": 5.42
      },
      {
        "mid": 4.65,
        "trade": 4.05
      },
      {
        "mid": 3.375,
        "trade": 2.88
      },
      {
        "mid": 2.345,
        "trade": 1.97
      },
      {
        "mid": 1.54,
        "trade": 1.27
      },
      {
        "mid": 1.005,
        "trade": 0.82
      },
      {
        "mid": 0.635,
        "trade": 0.49
      },
      {
        "mid": 10.8,
        "trade": 9.35
      },
      {
        "mid": 8.825,
        "trade": 7.48
      },
      {
        "mid": 7,
        "trade": 5.85
      },
      {
        "mid": 5.35,
        "trade": 4.41
      },
      {
        "mid": 4,
        "trade": 3.2
      },
      {
        "mid": 2.845,
        "trade": 2.25
      },
      {
        "mid": 1.94,
        "trade": 1.52
      },
      {
        "mid": 1.29,
        "trade": 0.98
      },
      {
        "mid": 0.84,
        "trade": 0.62
      },
      {
        "mid": 10.425,
        "trade": 8.5
      },
      {
        "mid": 8.325,
        "trade": 6.3
      },
      {
        "mid": 6.45,
        "trade": 4.65
      },
      {
        "mid": 4.775,
        "trade": 3.25
      },
      {
        "mid": 3.45,
        "trade": 2.2
      },
      {
        "mid": 2.33,
        "trade": 1.4
      },
      {
        "mid": 1.545,
        "trade": 0.85
      },
      {
        "mid": 0.985,
        "trade": 0.52
      },
      {
        "mid": 0.61,
        "trade": 0.34
      },
      {
        "mid": 9.475,
        "trade": 9.56
      },
      {
        "mid": 7.3,
        "trade": 7.41
      },
      {
        "mid": 5.425,
        "trade": 5.52
      },
      {
        "mid": 3.9,
        "trade": 3.95
      },
      {
        "mid": 2.68,
        "trade": 2.68
      },
      {
        "mid": 1.76,
        "trade": 1.74
      },
      {
        "mid": 1.075,
        "trade": 1.09
      },
      {
        "mid": 0.645,
        "trade": 0.65
      },
      {
        "mid": 0.38,
        "trade": 0.38
      },
      {
        "mid": 12.25,
        "trade": 12.24
      },
      {
        "mid": 10.45,
        "trade": 10.55
      },
      {
        "mid": 8.9,
        "trade": 9.05
      },
      {
        "mid": 7.5,
        "trade": 7.4
      },
      {
        "mid": 6.175,
        "trade": 6.2
      },
      {
        "mid": 5.075,
        "trade": 5.05
      },
      {
        "mid": 4.125,
        "trade": 4.08
      },
      {
        "mid": 3.3,
        "trade": 3.29
      },
      {
        "mid": 2.635,
        "trade": 2.62
      },
      {
        "mid": 10.45,
        "trade": 10.81
      },
      {
        "mid": 8.4,
        "trade": 8.85
      },
      {
        "mid": 6.925,
        "trade": 7.1
      },
      {
        "mid": 5.625,
        "trade": 5.6
      },
      {
        "mid": 4.35,
        "trade": 4.32
      },
      {
        "mid": 3.425,
        "trade": 3.29
      },
      {
        "mid": 2.595,
        "trade": 2.48
      },
      {
        "mid": 1.95,
        "trade": 1.83
      },
      {
        "mid": 1.455,
        "trade": 1.33
      },
      {
        "mid": 10.75,
        "trade": 14.55
      },
      {
        "mid": 8.7,
        "trade": 12.1
      },
      {
        "mid": 6.975,
        "trade": 10
      },
      {
        "mid": 5.275,
        "trade": 7.99
      },
      {
        "mid": 3.9,
        "trade": 6.28
      },
      {
        "mid": 2.765,
        "trade": 4.7
      },
      {
        "mid": 1.875,
        "trade": 3.45
      },
      {
        "mid": 1.25,
        "trade": 2.46
      },
      {
        "mid": 0.72,
        "trade": 1.67
      },
      {
        "mid": 9.775,
        "trade": 10.34
      },
      {
        "mid": 7.65,
        "trade": 8.2
      },
      {
        "mid": 5.85,
        "trade": 6.28
      },
      {
        "mid": 4.25,
        "trade": 4.55
      },
      {
        "mid": 2.98,
        "trade": 3.25
      },
      {
        "mid": 2.025,
        "trade": 2.16
      },
      {
        "mid": 1.325,
        "trade": 1.39
      },
      {
        "mid": 0.855,
        "trade": 0.89
      },
      {
        "mid": 0.55,
        "trade": 0.55
      }
    ],
    "slope": 1.0045490418218086,
    "intercept": -0.12805319972732263,
    "r2": 0.8982846084877436,
    "n": 108,
    "displayedPoints": 108
  },
  "weeklyDecisions": [
    {
      "entry_time": "2026-06-01 14:00:00",
      "expiry": "2026-06-05",
      "spot": 219.17,
      "ric": "NVDAF052622000.U^F26",
      "strike": 220,
      "bid": 4.3,
      "ask": 4.4,
      "mid": 4.35,
      "expiry_stock_close": 205.11,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-06-08 14:00:00",
      "expiry": "2026-06-12",
      "spot": 206.2799,
      "ric": "NVDAF122620750.U^F26",
      "strike": 207.5,
      "bid": 3.75,
      "ask": 3.85,
      "mid": 3.8,
      "expiry_stock_close": 205.14,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-06-15 14:00:00",
      "expiry": "2026-06-18",
      "spot": 208.77,
      "ric": "NVDAF182621000.U^F26",
      "strike": 210,
      "bid": 2.73,
      "ask": 2.8,
      "mid": 2.7649999999999997,
      "expiry_stock_close": 210.2,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-06-22 14:00:00",
      "expiry": "2026-06-26",
      "spot": 213.08,
      "ric": "NVDAF262621500.U^F26",
      "strike": 215,
      "bid": 2.82,
      "ask": 2.85,
      "mid": 2.835,
      "expiry_stock_close": 191.71,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-06-29 14:00:00",
      "expiry": "2026-07-02",
      "spot": 193.33,
      "ric": "NVDAG022619500.U^G26",
      "strike": 195,
      "bid": 2.48,
      "ask": 2.49,
      "mid": 2.4850000000000003,
      "expiry_stock_close": 194.52,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-07-06 14:00:00",
      "expiry": "2026-07-10",
      "spot": 196.28,
      "ric": "NVDAG102619750.U^G26",
      "strike": 197.5,
      "bid": 2.9,
      "ask": 2.95,
      "mid": 2.925,
      "expiry_stock_close": 210.94,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-07-13 14:00:00",
      "expiry": "2026-07-17",
      "spot": 208.724,
      "ric": "NVDAG172621000.U^G26",
      "strike": 210,
      "bid": 3.25,
      "ask": 3.3,
      "mid": 3.275,
      "expiry_stock_close": 202.64,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-07-20 14:00:00",
      "expiry": "2026-07-24",
      "spot": 205.8536,
      "ric": "NVDAG242620750.U^G26",
      "strike": 207.5,
      "bid": 3.35,
      "ask": 3.4,
      "mid": 3.375,
      "expiry_stock_close": 206.96,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-07-27 14:00:00",
      "expiry": "2026-07-31",
      "spot": 201.76,
      "ric": "NVDAG312620250.U^G26",
      "strike": 202.5,
      "bid": 3.95,
      "ask": 4.05,
      "mid": 4,
      "expiry_stock_close": 200.8,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-08-03 14:00:00",
      "expiry": "2026-08-07",
      "spot": 202.26,
      "ric": "NVDAH072620250.U^H26",
      "strike": 202.5,
      "bid": 3.85,
      "ask": 3.95,
      "mid": 3.9000000000000004,
      "expiry_stock_close": 223.89,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-08-10 14:00:00",
      "expiry": "2026-08-14",
      "spot": 222.09,
      "ric": "NVDAH142622250.U^H26",
      "strike": 222.5,
      "bid": 3.4,
      "ask": 3.5,
      "mid": 3.45,
      "expiry_stock_close": 225.21,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-08-17 14:00:00",
      "expiry": "2026-08-21",
      "spot": 226.17,
      "ric": "NVDAH212622750.U^H26",
      "strike": 227.5,
      "bid": 2.66,
      "ask": 2.7,
      "mid": 2.68,
      "expiry_stock_close": 214.741,
      "status": "TRADE",
      "outcome": "EXPIRE"
    },
    {
      "entry_time": "2026-08-24 14:00:00",
      "expiry": "2026-08-28",
      "spot": 209.665,
      "ric": "NVDAH282621000.U^H26",
      "strike": 210,
      "bid": 6.15,
      "ask": 6.2,
      "mid": 6.175000000000001,
      "expiry_stock_close": 217.54,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-08-31 14:00:00",
      "expiry": "2026-09-04",
      "spot": 218.87,
      "ric": "NVDAI042622000.U^I26",
      "strike": 220,
      "bid": 2.96,
      "ask": 3,
      "mid": 2.98,
      "expiry_stock_close": 230.345,
      "status": "TRADE",
      "outcome": "ASSIGN"
    },
    {
      "entry_time": "2026-09-08 14:00:00",
      "expiry": "2026-09-11",
      "spot": 229.592,
      "ric": "NVDAI112623000.U^I26",
      "strike": 230,
      "bid": 3.15,
      "ask": 3.2,
      "mid": 3.175,
      "expiry_stock_close": 218.18,
      "status": "TRADE",
      "outcome": "EXPIRE"
    }
  ]
};
