window.HELIOS_BOOK = {
  "underlying": "NVDA",
  "startCash": 25000,
  "initPct": 0.5,
  "maintPct": 0.25,
  "blotter": [
    {
      "id": "t1",
      "ts": "2026-06-08 10:00 ET",
      "side": "BUY",
      "qty": 100,
      "instrument": "NVDA.O",
      "occ": "NVDA.O",
      "asset": "STK",
      "strike": null,
      "expiry": null,
      "limit": 206.2799,
      "fill": 206.2799,
      "multiplier": 1,
      "notes": "Monday combo · stock leg. Limit = 10:00 ET open print. Decrease cash. Rule: if flat, buy 100."
    },
    {
      "id": "t2",
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
      "notes": "Monday combo · call leg. Nearest OTM 207.5C. Limit = mid. Cash +100×mid."
    },
    {
      "id": "t3",
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
      "notes": "Friday OTM: close $205.21 ≤ 207.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t4",
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
      "notes": "Still long · Monday rewrite 215C. Limit = mid."
    },
    {
      "id": "t5",
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
      "notes": "Friday OTM: close $191.71 ≤ 215C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t6",
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
      "id": "t7",
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
      "notes": "Friday ITM: close $210.96 > 197.5C. Exit = wait; short call assigned."
    },
    {
      "id": "t8",
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
      "id": "t9",
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
      "id": "t10",
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
      "id": "t11",
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
      "notes": "Friday OTM: close $202.69 ≤ 210C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t12",
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
      "id": "t13",
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
      "notes": "Friday OTM: close $207.06 ≤ 207.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t14",
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
      "id": "t15",
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
      "notes": "Friday OTM: close $200.80 ≤ 202.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t16",
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
      "notes": "Still long · Monday rewrite 222.5C. Limit = mid."
    },
    {
      "id": "t17",
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
      "notes": "Friday ITM: close $225.18 > 222.5C. Exit = wait; short call assigned."
    },
    {
      "id": "t18",
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
      "id": "t19",
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
      "id": "t20",
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
      "id": "t21",
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
      "notes": "Friday OTM: close $214.73 ≤ 227.5C. Exit = wait; keep shares and premium."
    },
    {
      "id": "t22",
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
      "id": "t23",
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
      "notes": "Friday ITM: close $217.57 > 210C. Exit = wait; short call assigned."
    },
    {
      "id": "t24",
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
    }
  ],
  "ledger": [
    {
      "date": "2026-06-08 10:00 ET",
      "cash": 4752.01,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/12 207.5C",
      "stockPx": 206.2799,
      "optPx": 3.8,
      "lmv": 20627.99,
      "optMv": -380,
      "nav": 25000,
      "init": 10313.99,
      "maint": 5157,
      "available": 14686.01,
      "excess": 19843
    },
    {
      "date": "2026-06-12 16:00 ET",
      "cash": 4752.01,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 205.21,
      "optPx": 0,
      "lmv": 20521,
      "optMv": 0,
      "nav": 25273.01,
      "init": 10260.5,
      "maint": 5130.25,
      "available": 15012.51,
      "excess": 20142.76
    },
    {
      "date": "2026-06-15 10:00 ET",
      "cash": 4752.01,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 208.8,
      "optPx": 0,
      "lmv": 20880,
      "optMv": 0,
      "nav": 25632.01,
      "init": 10440,
      "maint": 5220,
      "available": 15192.01,
      "excess": 20412.01
    },
    {
      "date": "2026-06-22 10:00 ET",
      "cash": 5035.51,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "6/26 215C",
      "stockPx": 213.08,
      "optPx": 2.835,
      "lmv": 21308,
      "optMv": -283.5,
      "nav": 26060.01,
      "init": 10654,
      "maint": 5327,
      "available": 15406.01,
      "excess": 20733.01
    },
    {
      "date": "2026-06-26 16:00 ET",
      "cash": 5035.51,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 191.71,
      "optPx": 0,
      "lmv": 19171,
      "optMv": 0,
      "nav": 24206.51,
      "init": 9585.5,
      "maint": 4792.75,
      "available": 14621.01,
      "excess": 19413.76
    },
    {
      "date": "2026-06-29 10:00 ET",
      "cash": 5035.51,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 193.31,
      "optPx": 0,
      "lmv": 19331,
      "optMv": 0,
      "nav": 24366.51,
      "init": 9665.5,
      "maint": 4832.75,
      "available": 14701.01,
      "excess": 19533.76
    },
    {
      "date": "2026-07-06 10:00 ET",
      "cash": 5328.01,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/10 197.5C",
      "stockPx": 196.28,
      "optPx": 2.925,
      "lmv": 19628,
      "optMv": -292.5,
      "nav": 24663.51,
      "init": 9814,
      "maint": 4907,
      "available": 14849.51,
      "excess": 19756.51
    },
    {
      "date": "2026-07-10 16:00 ET",
      "cash": 25078.01,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 210.96,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 25078.01,
      "init": 0,
      "maint": 0,
      "available": 25078.01,
      "excess": 25078.01
    },
    {
      "date": "2026-07-13 10:00 ET",
      "cash": 4533.11,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/17 210C",
      "stockPx": 208.724,
      "optPx": 3.275,
      "lmv": 20872.4,
      "optMv": -327.5,
      "nav": 25078.01,
      "init": 10436.2,
      "maint": 5218.1,
      "available": 14641.81,
      "excess": 19859.91
    },
    {
      "date": "2026-07-17 16:00 ET",
      "cash": 4533.11,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 202.69,
      "optPx": 0,
      "lmv": 20269,
      "optMv": 0,
      "nav": 24802.11,
      "init": 10134.5,
      "maint": 5067.25,
      "available": 14667.61,
      "excess": 19734.86
    },
    {
      "date": "2026-07-20 10:00 ET",
      "cash": 4870.61,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/24 207.5C",
      "stockPx": 205.84,
      "optPx": 3.375,
      "lmv": 20584,
      "optMv": -337.5,
      "nav": 25117.11,
      "init": 10292,
      "maint": 5146,
      "available": 14825.11,
      "excess": 19971.11
    },
    {
      "date": "2026-07-24 16:00 ET",
      "cash": 4870.61,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 207.055,
      "optPx": 0,
      "lmv": 20705.5,
      "optMv": 0,
      "nav": 25576.11,
      "init": 10352.75,
      "maint": 5176.38,
      "available": 15223.36,
      "excess": 20399.74
    },
    {
      "date": "2026-07-27 10:00 ET",
      "cash": 5270.61,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "7/31 202.5C",
      "stockPx": 201.76,
      "optPx": 4,
      "lmv": 20176,
      "optMv": -400,
      "nav": 25046.61,
      "init": 10088,
      "maint": 5044,
      "available": 14958.61,
      "excess": 20002.61
    },
    {
      "date": "2026-07-31 16:00 ET",
      "cash": 5270.61,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 200.8,
      "optPx": 0,
      "lmv": 20080,
      "optMv": 0,
      "nav": 25350.61,
      "init": 10040,
      "maint": 5020,
      "available": 15310.61,
      "excess": 20330.61
    },
    {
      "date": "2026-08-03 10:00 ET",
      "cash": 5270.61,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 202.26,
      "optPx": 0,
      "lmv": 20226,
      "optMv": 0,
      "nav": 25496.61,
      "init": 10113,
      "maint": 5056.5,
      "available": 15383.61,
      "excess": 20440.11
    },
    {
      "date": "2026-08-10 10:00 ET",
      "cash": 5615.61,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/14 222.5C",
      "stockPx": 222.09,
      "optPx": 3.45,
      "lmv": 22209,
      "optMv": -345,
      "nav": 27479.61,
      "init": 11104.5,
      "maint": 5552.25,
      "available": 16375.11,
      "excess": 21927.36
    },
    {
      "date": "2026-08-14 16:00 ET",
      "cash": 27865.61,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 225.18,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 27865.61,
      "init": 0,
      "maint": 0,
      "available": 27865.61,
      "excess": 27865.61
    },
    {
      "date": "2026-08-17 10:00 ET",
      "cash": 5516.61,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/21 227.5C",
      "stockPx": 226.17,
      "optPx": 2.68,
      "lmv": 22617,
      "optMv": -268,
      "nav": 27865.61,
      "init": 11308.5,
      "maint": 5654.25,
      "available": 16557.11,
      "excess": 22211.36
    },
    {
      "date": "2026-08-21 16:00 ET",
      "cash": 5516.61,
      "shares": 100,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 214.73,
      "optPx": 0,
      "lmv": 21473,
      "optMv": 0,
      "nav": 26989.61,
      "init": 10736.5,
      "maint": 5368.25,
      "available": 16253.11,
      "excess": 21621.36
    },
    {
      "date": "2026-08-24 10:00 ET",
      "cash": 6134.11,
      "shares": 100,
      "shortCalls": -1,
      "callLabel": "8/28 210C",
      "stockPx": 209.665,
      "optPx": 6.175,
      "lmv": 20966.5,
      "optMv": -617.5,
      "nav": 26483.11,
      "init": 10483.25,
      "maint": 5241.62,
      "available": 15999.86,
      "excess": 21241.49
    },
    {
      "date": "2026-08-28 16:00 ET",
      "cash": 27134.11,
      "shares": 0,
      "shortCalls": 0,
      "callLabel": "—",
      "stockPx": 217.57,
      "optPx": 0,
      "lmv": 0,
      "optMv": 0,
      "nav": 27134.11,
      "init": 0,
      "maint": 0,
      "available": 27134.11,
      "excess": 27134.11
    }
  ],
  "rics": [
    {
      "label": "NVDA 2026-06-12 207.5 call (expired)",
      "ric": "NVDAF122620750.U^F26"
    },
    {
      "label": "NVDA 2026-07-10 197.5 call (expired)",
      "ric": "NVDAG102619750.U^G26"
    },
    {
      "label": "NVDA 2026-08-14 222.5 call (expired)",
      "ric": "NVDAH142622250.U^H26"
    },
    {
      "label": "NVDA 2026-08-28 210 call (expired)",
      "ric": "NVDAH282621000.U^H26"
    }
  ],
  "writeup": {
    "title": "NVDA Friday weeklies — nearest OTM at 10:00 ET",
    "fill": "At each eligible Monday 10:00 ET timestamp, the stock leg fills at the hourly opening print. Among actual listed calls with both BID and ASK, the rule selects the smallest strike strictly above spot; ATM is allowed only when spot exactly equals a listed strike. The call limit and simulated fill equal (BID+ASK)/2 at that same timestamp. Because expired chain constituents are unavailable, candidate RICs are reconstructed and accepted only when LSEG returns real history; otherwise the week is skipped.",
    "roll": "No roll and no buy-to-close. The short call is held through Friday expiry. OTM or ATM calls EXPIRE and the shares remain. ITM calls ASSIGN; 100 shares are delivered at strike and the position becomes flat.",
    "pin": "Nine weeks produced valid two-sided entry quotes: six calls expired and three were assigned. Five candidate weeks were skipped under the no-quote rule. Ending equity was $27,134.11 from $25,000.",
    "regT": "The account starts with $25,000. NAV = cash + stock LMV + option MV, with the short call recorded as a negative asset. Reg T is used because its 50% stock initial requirement and 25% maintenance requirement are transparent and reproducible without a broker-specific portfolio-margin engine; the covered short call adds $0. Available funds and excess remained positive throughout the test.",
    "analysis": "The midpoint regression uses 81 synchronized Monday 10:00 ET observations across the near-the-money chain. Its high R² supports mid as a reproducible fill assumption, while the fitted slope below one shows that prints did not sit perfectly on quoted midpoints. Assignment capped upside in three weeks; skipped weeks show the cost of requiring real two-sided quotes instead of inventing fills. A next version would add commissions and spread-based slippage, compare nearest OTM with a fixed-delta strike rule, and test whether entering on the first session after a Monday holiday improves results without weakening the rule."
  },
  "midVsTrade": {
    "points": [
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
      }
    ],
    "slope": 0.9544382252100735,
    "intercept": -0.23612590246452728,
    "r2": 0.9366193867955619,
    "n": 81,
    "displayedPoints": 81
  }
};
