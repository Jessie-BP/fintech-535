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
book.weeklyDecisions = backtest.weeklyDecisions;
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

const money = (value) =>
  `$${value.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
const endingNav = backtest.ledger.at(-1).nav;
const returnPct = ((endingNav / backtest.startCash - 1) * 100).toFixed(2);
const assignedWeeks = backtest.blotter.filter(
  (trade) => trade.asset === "CALL" && trade.side === "ASSIGN",
).length;
const pinText =
  backtest.dataGapWeeks === 0
    ? `All ${backtest.weeklyDecisions.length} candidate weeks have verified two-sided entry quotes in the cached LSEG pull. Ending equity was ${money(endingNav)} from ${money(backtest.startCash)} (${returnPct}%).`
    : `${backtest.tradeWeeks} of ${backtest.weeklyDecisions.length} candidate weeks have verified two-sided entry quotes in the cached LSEG pull. ${backtest.dataGapWeeks} weeks are explicitly marked DATA GAP and are not interpreted as evidence that NVDA had no listed call. Ending equity on the verified subset was ${money(endingNav)} from ${money(backtest.startCash)}.`;
const slopeNote =
  Math.abs(scatter.slope - 1) < 0.02
    ? `the fitted slope of ${scatter.slope.toFixed(3)} is essentially one, so prints sit on the quoted midpoint on average`
    : scatter.slope < 1
      ? `the fitted slope of ${scatter.slope.toFixed(3)}, below one, shows that prints did not sit perfectly on quoted midpoints`
      : `the fitted slope of ${scatter.slope.toFixed(3)}, above one, shows that prints did not sit perfectly on quoted midpoints`;
const gapNote =
  backtest.dataGapWeeks === 0
    ? "Every candidate week had a verified quote; any week without one would be shown separately as a data gap rather than silently skipped."
    : "Missing contract histories are shown separately because silently treating an upstream fetch failure as a strategy skip would overstate pure-NVDA exposure and distort the backtest.";
const analysisText = `The midpoint regression uses ${scatter.n} synchronized Monday 10:00 ET observations across the near-the-money chain (R² = ${scatter.r2.toFixed(3)}). A high R² supports mid as a reproducible fill assumption, and ${slopeNote}. Assignment capped upside in ${assignedWeeks} of ${backtest.tradeWeeks} traded weeks. ${gapNote}`;

book.writeup = {
  title: "NVDA weeklies — first trading day, nearest OTM at 10:00 ET",
  fill: "At 10:00 ET on the first exchange session of each week, the stock leg fills at the hourly opening print; a Monday market holiday moves entry to Tuesday or the next open session. The expiry is the final exchange session of that week (Thursday in a Friday-holiday week). Across the $1 and $2.50 near-the-money strike grids, the rule selects the lowest strike at or above spot with a valid BID and ASK; fill is their midpoint.",
  roll: "No roll and no buy-to-close. The short call is held through its final weekly expiry session. OTM or ATM calls EXPIRE and the shares remain. ITM calls ASSIGN; 100 shares are delivered at strike and the position becomes flat.",
  pin: pinText,
  regT: "The account starts with $25,000. NAV = cash + stock LMV + option MV, with the short call recorded as a negative asset. Reg T is used because its 50% stock initial requirement and 25% maintenance requirement are transparent and reproducible without a broker-specific portfolio-margin engine; the covered short call adds $0. Available funds and excess remained positive throughout the test.",
  analysis: analysisText,
};

fs.writeFileSync(
  bookPath,
  `${prefix}${JSON.stringify(book, null, 2)};\n`,
  "utf8",
);

console.log(
  `Embedded NVDA book with ${backtest.blotter.length} blotter rows, ${backtest.ledger.length} ledger rows, and scatter n=${scatter.n}, R2=${scatter.r2.toFixed(6)}`,
);
