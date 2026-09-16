const fs = require("fs");
const path = require("path");

const root = __dirname;
const bookPath = path.join(root, "gh-pages", "helios", "book.js");
const scatterPath = path.join(root, "nvda_mid_vs_trade_web.json");
const backtestPath = path.join(root, "nvda_backtest_output.json");

const source = fs.readFileSync(bookPath, "utf8").trim();
const prefix = "window.HELIOS_BOOK = ";

if (!source.startsWith(prefix) || !source.endsWith(";")) {
  throw new Error("Unexpected gh-pages/helios/book.js format");
}

const book = JSON.parse(source.slice(prefix.length, -1));
const scatter = JSON.parse(fs.readFileSync(scatterPath, "utf8"));
const backtest = JSON.parse(fs.readFileSync(backtestPath, "utf8"));

book.underlying = backtest.underlying;
book.startCash = backtest.startCash;
book.initPct = backtest.initPct;
book.maintPct = backtest.maintPct;
book.blotter = backtest.blotter;
book.ledger = backtest.ledger;
book.midVsTrade = scatter;
const soldCalls = backtest.blotter.filter(
  (trade) => trade.asset === "CALL" && trade.side === "SELL",
);
const assignedRics = new Set(
  backtest.blotter
    .filter((trade) => trade.asset === "CALL" && trade.side === "ASSIGN")
    .map((trade) => trade.instrument),
);
book.rics = soldCalls
  .filter(
    (trade, index) =>
      index === 0 ||
      index === soldCalls.length - 1 ||
      assignedRics.has(trade.instrument),
  )
  .map((trade) => ({
    label: `NVDA ${trade.expiry} ${trade.strike} call (expired)`,
    ric: trade.instrument,
  }));
book.writeup = {
  title: "NVDA Friday weeklies — nearest OTM at 10:00 ET",
  fill: "At each eligible Monday 10:00 ET timestamp, the stock leg fills at the hourly opening print. Among actual listed calls with both BID and ASK, the rule selects the smallest strike strictly above spot; ATM is allowed only when spot exactly equals a listed strike. The call limit and simulated fill equal (BID+ASK)/2 at that same timestamp. Because expired chain constituents are unavailable, candidate RICs are reconstructed and accepted only when LSEG returns real history; otherwise the week is skipped.",
  roll: "No roll and no buy-to-close. The short call is held through Friday expiry. OTM or ATM calls EXPIRE and the shares remain. ITM calls ASSIGN; 100 shares are delivered at strike and the position becomes flat.",
  pin: `Nine weeks produced valid two-sided entry quotes: six calls expired and three were assigned. Five candidate weeks were skipped under the no-quote rule. Ending equity was $${backtest.ledger.at(-1).nav.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})} from $${backtest.startCash.toLocaleString()}.`,
  regT: "The account starts with $25,000. NAV = cash + stock LMV + option MV, with the short call recorded as a negative asset. Reg T is used because its 50% stock initial requirement and 25% maintenance requirement are transparent and reproducible without a broker-specific portfolio-margin engine; the covered short call adds $0. Available funds and excess remained positive throughout the test.",
  analysis: "The midpoint regression uses 81 synchronized Monday 10:00 ET observations across the near-the-money chain. Its high R² supports mid as a reproducible fill assumption, while the fitted slope below one shows that prints did not sit perfectly on quoted midpoints. Assignment capped upside in three weeks; skipped weeks show the cost of requiring real two-sided quotes instead of inventing fills. A next version would add commissions and spread-based slippage, compare nearest OTM with a fixed-delta strike rule, and test whether entering on the first session after a Monday holiday improves results without weakening the rule.",
};

fs.writeFileSync(
  bookPath,
  `${prefix}${JSON.stringify(book, null, 2)};\n`,
  "utf8",
);

console.log(
  `Embedded NVDA book with ${backtest.blotter.length} blotter rows, ${backtest.ledger.length} ledger rows, and scatter n=${scatter.n}, R2=${scatter.r2.toFixed(6)}`,
);
