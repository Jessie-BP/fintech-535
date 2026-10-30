(() => {
  const BOOK = window.WHEEL_BOOK || { pending: true };
  const money = (n) => n == null ? "—" : `${n < 0 ? "-" : ""}$${Math.abs(Number(n)).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`;
  const num = (n,d=2) => n == null ? "—" : Number(n).toFixed(d);
  const esc = (s) => String(s ?? "—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const el = (id) => document.getElementById(id);
  if (BOOK.pending) {
    el("pending").hidden = false;
    document.querySelectorAll(".data-panel,.thesis").forEach(n => n.hidden = true);
    return;
  }
  const B = BOOK, bm = B.benchmark, tl = B.timeline;

  el("metrics").innerHTML = [
    ["Ending NAV", money(B.endingNav)],
    ["Wheel return", `${num(B.returnPct)}%`],
    ["AAPL buy & hold", `${num(bm.returnPct)}%`],
    ["Sharpe (wheel / B&H)", `${num(B.sharpe)} / ${num(bm.sharpe)}`],
    ["Sortino (wheel / B&H)", `${num(B.sortino)} / ${num(bm.sortino)}`],
    ["Max drawdown (wheel / B&H)", `${num(B.maxDrawdownPct)}% / ${num(bm.maxDrawdownPct)}%`],
    ["Premium collected", money(B.premiumCollected)],
    ["Puts sold / assigned", `${B.putsSold} / ${B.putAssignments}`],
    ["Calls sold / called away", `${B.callsSold} / ${B.callAssignments}`],
    ["Closes / rolls", `${B.profitTakeCloses} / ${B.rolls}`],
    ["Expired worthless", B.expiredWorthless],
    ["Weeks traded / skipped", `${B.tradeWeeks} / ${B.skippedWeeks}`],
    ["Commissions", money(B.feesPaid)],
  ].map(([k,v]) => `<div class="metric"><label>${k}</label><strong>${v}</strong></div>`).join("");

  // ---- thesis written before the run; verdict computed from the numbers
  const beat = B.returnPct > bm.returnPct, betterSharpe = B.sharpe > bm.sharpe, lessDD = B.maxDrawdownPct > bm.maxDrawdownPct;
  const said = (c, y, n) => c ? y : n;
  el("thesis").innerHTML = [
    "<p><b>Thesis.</b> Weekly option prices usually embed more volatility than AAPL then delivers, so a seller collects more premium than the average payout. The wheel turns that premium into a steady income stream: a 0.25-Delta put is an order to buy AAPL below the market and get paid to wait, and a covered call struck at or above the net cost basis can never lock in a loss on the shares. We expect higher return per unit of risk (Sharpe) than owning the shares, with smaller drawdowns, but lower return in a strong rally because the calls cap the upside.</p>",
    `<p><b>Result.</b> The wheel ended at ${money(B.endingNav)}, a return of ${num(B.returnPct)}%, against ${num(bm.returnPct)}% for holding 100 AAPL shares with the same ${money(B.startingCash)} (AAPL itself moved ${num(bm.stockReturnPct)}%). ${said(beat, "It beat the benchmark.", "It did not beat the benchmark.")} Sharpe was ${num(B.sharpe)} against ${num(bm.sharpe)}: ${said(betterSharpe, "better risk-adjusted performance", "worse risk-adjusted performance")}. Max drawdown was ${num(B.maxDrawdownPct)}% against ${num(bm.maxDrawdownPct)}%: ${said(lessDD, "smaller, as expected", "not smaller")}.</p>`,
    `<p><b>Why.</b> ${esc(B.putAssignments)} of ${esc(B.putsSold)} puts were assigned and ${esc(B.callAssignments)} of ${esc(B.callsSold)} calls were called away; ${esc(B.premiumCollected ? money(B.premiumCollected) : "$0")} of premium was collected before ${money(B.feesPaid)} of commissions. ${B.skippedWeeks ? `${B.skippedWeeks} of ${B.tradeWeeks + B.skippedWeeks} weeks had no trade (data gaps or no suitable strike), which are listed in the weekly audit instead of being filled in.` : ""} ${B.endedInStock ? "The account ended the window holding shares." : "The account ended the window in cash."} This is ${B.tradeWeeks + B.skippedWeeks} weeks in one market regime, so it is evidence about this window, not proof the wheel works.</p>`,
  ].join("");

  // ---- chart: wheel NAV vs buy and hold with cursor
  const entryPx = bm.entry, start = B.startingCash;
  const W = 960, H = 290, L = 64, R = 15, T = 16, D = 34;
  const wheel = tl.map(p => p.nav), hold = tl.map(p => start + (p.stockPx - entryPx) * 100);
  const lo = Math.min(...wheel, ...hold) * .99, hi = Math.max(...wheel, ...hold) * 1.01;
  const x = i => L + i / Math.max(tl.length - 1, 1) * (W - L - R), y = v => T + (hi - v) / (hi - lo || 1) * (H - T - D);
  const line = (vals) => vals.map((v,i)=>`${i?'L':'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
  const grid = [0,.5,1].map(t=>{const v=lo+(hi-lo)*t,yy=y(v);return `<line class="axis" x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}"/><text x="${L-8}" y="${yy+4}" text-anchor="end" fill="#8aa099" font-size="10">${Math.round(v).toLocaleString()}</text>`}).join('');
  const idxOf = (time) => { let k = tl.findIndex(p => p.time >= time); return k < 0 ? tl.length - 1 : k; };
  const marks = B.blotter.filter(b => b.action === "SELL").map(b => { const i = idxOf(b.time); return `<circle class="${b.leg==='PUT'?'mk-put':'mk-call'}" cx="${x(i)}" cy="${y(tl[i].nav)}" r="3.5"><title>${esc(b.time)} sell ${esc(b.leg)} ${b.strike}</title></circle>`; }).join('');
  el("chart").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Wheel NAV vs buy and hold">${grid}<path class="bhline" d="${line(hold)}"/><path class="navline" d="${line(wheel)}"/>${marks}<line id="cursor" class="cursor" y1="${T}" y2="${H-D}"/><text x="${L}" y="${H-8}" fill="#8aa099" font-size="10">${esc(tl[0].time)}</text><text x="${W-R}" y="${H-8}" text-anchor="end" fill="#8aa099" font-size="10">${esc(tl.at(-1).time)}</text></svg>`;
  el("chart-note").textContent = "Solid = wheel · dashed = buy & hold · dots: yellow = put sold, blue = call sold";

  // ---- portfolio viewer
  const slider = el("slider"); slider.max = tl.length - 1;
  const eventIdx = [...new Set(B.blotter.map(b => idxOf(b.time)))].sort((a,b)=>a-b);
  function show(i) {
    i = Math.max(0, Math.min(tl.length - 1, i)); slider.value = i;
    const p = tl[i], s = p.short;
    el("when").textContent = p.time + " UTC";
    const cur = el("cursor"); cur.setAttribute("x1", x(i)); cur.setAttribute("x2", x(i));
    const done = B.blotter.filter(b => b.time <= p.time).length;
    const cards = [
      ["Cash", money(p.cash), p.collateral ? `of which ${money(p.collateral)} secures the short put` : "no put collateral"],
      ["Shares", `${p.shares}`, p.shares ? `${money(p.stockMv)} at ${num(p.stockPx)}` : `AAPL ${num(p.stockPx)}`],
      ["Short put", s && s.kind === "PUT" ? `1 × ${s.strike}P` : "none", s && s.kind === "PUT" ? `${esc(s.ric)}<br>bid ${num(s.bid)} / ask ${num(s.ask)} · exp ${esc(s.expiry)}<br>liability ${money(p.optMv)}` : ""],
      ["Covered call", s && s.kind === "CALL" ? `1 × ${s.strike}C` : "none", s && s.kind === "CALL" ? `${esc(s.ric)}<br>bid ${num(s.bid)} / ask ${num(s.ask)} · exp ${esc(s.expiry)}<br>liability ${money(p.optMv)}` : ""],
      ["Liquidation NAV", money(p.nav), `${num((p.nav / start - 1) * 100)}% since start · ${done} of ${B.blotter.length} blotter rows done`],
    ];
    el("portfolio").innerHTML = cards.map(([k,v,n]) => `<div class="metric"><label>${k}</label><strong>${v}</strong><small>${n}</small></div>`).join("");
    el("pf-note").textContent = "Short options are marked at the ask (cost to close). Stock is marked at the hourly close. Option quotes carry forward when an hour has no update.";
  }
  slider.addEventListener("input", () => show(+slider.value));
  el("prev").onclick = () => show(+slider.value - 1); el("next").onclick = () => show(+slider.value + 1);
  el("prev-ev").onclick = () => show([...eventIdx].reverse().find(i => i < +slider.value) ?? 0);
  el("next-ev").onclick = () => show(eventIdx.find(i => i > +slider.value) ?? tl.length - 1);
  show(0);

  // ---- assumptions
  const fs = B.fillStats, sn = B.sensitivity;
  el("assumptions").innerHTML = [
    `<p><b>Short options are sold at the bid.</b> A seller who hits the quote receives the bid. Across ${fs.contracts} contracts with Delta between 0.15 and 0.35 at the entry bar, the median bid-ask spread was ${money(fs.medianSpread)} (${num(fs.medianSpreadPctOfMid,1)}% of the mid), so selling at the bid costs about ${money(fs.medianHalfSpreadPerContract)} per contract versus the mid. We do not assume mid fills: a mid price is a quote nobody has to honour. In the entry bar, ${fs.withTradePrint} of those ${fs.contracts} contracts also had a last-trade price, and ${fs.tradeInsideQuote} (${num(fs.tradeInsideQuote/Math.max(fs.withTradePrint,1)*100,0)}%) of those prints sat inside the bid-ask, so the quote brackets where trades happen and the bid is the conservative end of it. The trade field can be a carried-forward print, so it supports the range but does not prove a fill</p>`,
    `<p><b>Sensitivity.</b> Filling at the mid instead gives ${money(sn.mid.endingNav)} (${num(sn.mid.returnPct)}%) against ${money(sn.bid.endingNav)} (${num(sn.bid.returnPct)}%) at the bid, so the spread assumption ${Math.abs(sn.mid.returnPct - sn.bid.returnPct) < 0.5 ? "barely changes" : "matters for"} the conclusion.</p>`,
    "<p><b>Selection.</b> Put and call strikes come from the prior session's daily Delta (target 0.25, within ±0.10). Covered calls must be at or above the net cost basis (assignment strike minus premiums collected in the cycle). If the chosen contract has no valid bid/ask at 10:00 ET, the week is a data gap and no trade is made; we do not substitute a neighbouring strike.</p>",
    `<p><b>Closes and rolls.</b> Close: a short is bought back at the ask as soon as any hourly quote shows the ask at or below ${num(B.rolledSettings.profitTake*100,0)}% of the credit received (profit-take). Roll: if a short is in the money at 15:00 ET on expiry day, we buy it back at the ask and sell next week's same strike at the bid, but only if that is a net credit after both commissions; otherwise the option is left to settle. Both rules were fixed before the run, and the table below shows what they changed.</p>`,
    `<p><b>Settlement.</b> Anything still open settles on the official close of the expiry session: a put is assigned if the close is below the strike (buy 100 shares at the strike), a call if the close is above it (sell 100 shares at the strike). Commission is ${money(B.commissionPerContract)} per option contract traded; assignments carry no fee and nothing earns interest. Cash starts at ${money(B.startingCash)}, enough to secure one contract. Both the wheel and the buy-and-hold benchmark are scored from the first executed trade (${esc(B.firstTradeTime)}), because the first week had no usable put data.</p>`,
    `<p><b>Effect of the rules.</b> Hold to expiry only: ${money(B.variants.holdToExpiry.endingNav)} (${num(B.variants.holdToExpiry.returnPct)}%, Sharpe ${num(B.variants.holdToExpiry.sharpe)}, max drawdown ${num(B.variants.holdToExpiry.maxDrawdownPct)}%). With closes and rolls: ${money(B.variants.withRules.endingNav)} (${num(B.variants.withRules.returnPct)}%, Sharpe ${num(B.variants.withRules.sharpe)}, max drawdown ${num(B.variants.withRules.maxDrawdownPct)}%).</p>`,
  ].join("");

  // ---- tables
  el("decisions").innerHTML = B.decisions.map(r => `<tr><td class="mono">${esc(r.entryTime)}</td><td class="mono">${esc(r.expiry)}</td><td>${esc(r.state)}</td><td class="${r.status==='TRADE'?'good':'bad'}">${esc(r.status)}${r.reason?` <span title="${esc(r.reason)}">ⓘ</span>`:''}</td><td class="mono">${esc(r.shortRic)}</td><td>${num(r.strike)}</td><td>${num(r.delta,4)}</td><td>${num(r.bid,3)}</td><td>${num(r.ask,3)}</td><td>${num(r.fill,3)}</td><td>${num(r.officialClose)}</td><td class="${/ASSIGNED|CALLED/.test(r.outcome||'')?'bad':'good'}">${esc(r.outcome || r.reason)}</td></tr>`).join("");
  el("blotter").innerHTML = B.blotter.map(r => `<tr><td>${r.id}</td><td class="mono">${esc(r.time)}</td><td class="${r.action==='SELL'?'sell':r.action==='ASSIGN'?'assign':''}">${esc(r.action)}</td><td>${esc(r.tag)}</td><td>${esc(r.leg)}</td><td class="mono">${esc(r.ric)}</td><td>${num(r.strike)}</td><td>${num(r.delta,4)}</td><td>${num(r.bid,3)}</td><td>${num(r.ask,3)}</td><td>${num(r.fill,3)}</td><td>${money(r.fee)}</td><td>${money(r.cashChange)}</td><td class="wrap">${esc(r.rule)}</td></tr>`).join("");
  el("ledger").innerHTML = B.ledger.map(r => `<tr><td class="mono">${esc(r.time)}</td><td>${esc(r.event)}</td><td>${money(r.cash)}</td><td>${r.shares}</td><td>${num(r.stockPx)}</td><td>${money(r.stockMv)}</td><td class="mono">${r.short?esc(r.short.ric):'—'}</td><td>${money(r.optMv)}</td><td>${money(r.collateral)}</td><td class="good">${money(r.nav)}</td></tr>`).join("");
})();
