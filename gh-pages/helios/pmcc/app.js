(() => {
  const BOOK = window.PMCC_BOOK || { pending: true };
  const money = (n) => `$${Number(n).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`;
  const num = (n,d=2) => n == null ? "—" : Number(n).toFixed(d);
  const esc = (s) => String(s ?? "—").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  if (BOOK.pending) {
    document.getElementById("pending").hidden = false;
    document.querySelectorAll(".data-panel").forEach(node => node.hidden = true);
    return;
  }

  const combos = BOOK.combinations;
  const best = combos.reduce((a, b) => (b.endingNav > a.endingNav ? b : a), combos[0]);
  const picker = document.getElementById("combo");
  picker.innerHTML = combos.map(b => `<option value="${esc(b.combinationId)}">Long ${num(b.longTargetDelta)} / short ${num(b.shortTargetDelta)}${b.combinationId === best.combinationId ? " (best)" : ""}</option>`).join("");
  picker.value = best.combinationId;

  // Built from the book, so the numbers stay right whenever the backtest is rerun.
  (() => {
    const nWeeks = best.decisions.length;
    const word = (n) => ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"][n] ?? String(n);
    const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);
    const plural = (n, one, many) => `${word(n)} ${n === 1 ? one : many}`;
    const bench = best.benchmark.returnPct;
    const label = (c) => `long ${num(c.longTargetDelta)} / short ${num(c.shortTargetDelta)}`;
    const values = (key) => [...new Set(combos.map(c => c[key]))].sort((a, b) => a - b);
    const longs = values("longTargetDelta"), shorts = values("shortTargetDelta");
    const worst = combos.reduce((a, b) => (b.returnPct < a.returnPct ? b : a), combos[0]);
    const rises = (by, other) => values(other).every(o => {
      const line = combos.filter(c => c[other] === o).sort((a, b) => a[by] - b[by]);
      return line.every((c, i) => i === 0 || c.returnPct >= line[i - 1].returnPct);
    });
    const beat = combos.filter(c => c.returnPct > bench).length;
    const beatText = beat === 0 ? `None of the ${combos.length} beat buy and hold.`
      : beat === combos.length ? `All ${combos.length} beat buy and hold.`
      : `Only ${word(beat)} of the ${combos.length} beat buy and hold.`;
    const gaps = best.decisions.filter(d => d.status === "DATA_GAP");
    const noTarget = best.decisions.filter(d => d.status === "NO_TARGET");

    const combosText = [
      `We ran ${combos.length} combinations: ${word(longs.length)} long-call Delta targets (${num(longs[0])} to ${num(longs[longs.length - 1])}) against ${word(shorts.length)} weekly short-call targets (${num(shorts[0])} to ${num(shorts[shorts.length - 1])}).`,
      `The best was ${label(best)}, which ended at ${money(best.endingNav)}, a return of ${num(best.returnPct)}% against ${num(bench)}% for just holding AAPL over the same dates.`,
      `The weakest was ${label(worst)} at ${num(worst.returnPct)}%.`,
      rises("longTargetDelta", "shortTargetDelta") && rises("shortTargetDelta", "longTargetDelta")
        ? "Returns went up as the long call got deeper in the money and as the short call moved closer to the money, so the best one sits in that corner of the grid." : "",
      beatText,
      `The best and worst are ${num(best.returnPct - worst.returnPct, 1)} points apart on a single ${nWeeks}-week window, so this tells us which setting did best here, not which one is right.`,
    ].filter(Boolean).join(" ");

    const dataText = [
      `${best.tradeWeeks} of the ${nWeeks} weeks actually traded.`,
      gaps.length ? `${cap(plural(gaps.length, "week", "weeks"))} (entered ${gaps.map(d => d.entryDate).join(" and ")}) are data gaps: for those expiries LSEG gave us no Delta for any strike we asked about, so there was nothing to pick a short call from. We skipped them instead of making up a number, and the account just kept the long call.` : "",
      noTarget.length ? `${cap(plural(noTarget.length, "more week", "more weeks"))} had Deltas but none close enough to the target, so no short call was sold.` : "",
    ].filter(Boolean).join(" ");

    const strikeText = "We search short strikes every $2.50, not every $5. Some AAPL weeklies only list strikes on that spacing, and a $5 search finds nothing for those weeks.";
    document.getElementById("analysis").innerHTML = [combosText, dataText, strikeText].map(t => `<p>${esc(t)}</p>`).join("");
  })();

  document.getElementById("comparison").innerHTML = combos.map(b => `<tr data-combo="${esc(b.combinationId)}" class="${b.combinationId === best.combinationId ? 'best' : ''}"><td class="mono">${esc(b.combinationId)}${b.combinationId === best.combinationId ? ' <span class="best-tag">BEST</span>' : ''}</td><td>${num(b.long.delta,4)}</td><td class="${b.returnPct >= 0 ? 'good' : 'bad'}">${num(b.returnPct)}%</td><td>${num(b.pnlOnLongDebitPct)}%</td><td>${money(b.endingNav)}</td><td>${num(b.maxDrawdownPct)}%</td><td>${b.tradeWeeks}/${b.decisions.length}</td><td class="${b.assignments ? 'bad' : 'good'}">${b.assignments}</td><td>${b.dataGapWeeks}</td><td>${num(b.benchmark.returnPct)}%</td></tr>`).join("");

  function render(B) {
    const cards = [
      ["Specification", `L ${num(B.longTargetDelta)} / S ${num(B.shortTargetDelta)}`],
      ["Ending NAV", money(B.endingNav)],
      ["PMCC return", `${num(B.returnPct)}%`],
      ["AAPL buy & hold", `${num(B.benchmark.returnPct)}%`],
      ["Event max drawdown", `${num(B.maxDrawdownPct)}%`],
      ["P&L / long debit", `${num(B.pnlOnLongDebitPct)}%`],
      ["Actual long Delta", num(B.long.delta,4)],
      ["Verified weeks", `${B.tradeWeeks}/${B.decisions.length}`],
      ["Bought back", B.shortsBoughtBack],
      ["Expired OTM", B.shortsExpiredOtm],
      ["Assignments", B.assignments],
    ];
    document.getElementById("metrics").innerHTML = cards.map(([k,v])=>`<div class="metric"><label>${k}</label><strong>${v}</strong></div>`).join("");
    document.querySelectorAll("#comparison tr").forEach(row => row.classList.toggle("selected", row.dataset.combo === B.combinationId));
    document.getElementById("decisions").innerHTML = B.decisions.map(r=>`<tr><td class="mono">${esc(r.entryTime)}</td><td class="mono">${esc(r.deltaAsOf)}</td><td class="mono">${esc(r.expiry)}</td><td>${num(r.spot)}</td><td class="${r.status==='TRADE'?'good':'bad'}">${esc(r.status)}</td><td class="mono">${esc(r.shortRic)}</td><td>${num(r.shortDelta,4)}</td><td>${num(r.entryBid,3)}</td><td>${num(r.exitAsk,3)}</td><td class="${r.expiryOutcome==='ASSIGNED'?'bad':(r.status==='TRADE'?'good':'')}">${esc(r.expiryOutcome)}</td></tr>`).join("");
    document.getElementById("blotter").innerHTML = B.blotter.map(r=>`<tr><td class="mono">${esc(r.time)}</td><td class="${r.action==='SELL'?'good':''}">${esc(r.action)}</td><td>${esc(r.leg)}</td><td class="mono">${esc(r.ric)}</td><td>${esc(r.deltaAsOf)}</td><td>${num(r.delta,4)}</td><td>${num(r.bid,3)}</td><td>${num(r.ask,3)}</td><td>${num(r.fill,3)}</td><td>${money(r.fee)}</td><td>${money(r.cashChange)}</td></tr>`).join("");
    document.getElementById("ledger").innerHTML = B.ledger.map(r=>`<tr><td class="mono">${esc(r.time)}</td><td>${esc(r.event)}</td><td>${money(r.cash)}</td><td>${num(r.longBid,3)}</td><td>${money(r.longMv)}</td><td>${num(r.shortAsk,3)}</td><td>${money(r.shortMv)}</td><td class="good">${money(r.nav)}</td></tr>`).join("");

    const rows=B.ledger,W=960,H=270,L=64,R=15,T=16,D=34,values=rows.map(r=>r.nav),lo=Math.min(...values)*.98,hi=Math.max(...values)*1.02;
    const x=i=>L+i/Math.max(rows.length-1,1)*(W-L-R), y=v=>T+(hi-v)/(hi-lo||1)*(H-T-D);
    const path=values.map((v,i)=>`${i?'L':'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(' ');
    const grid=[0,.5,1].map(t=>{const v=lo+(hi-lo)*t,yy=y(v);return `<line class="axis" x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}"/><text x="${L-8}" y="${yy+4}" text-anchor="end" fill="#8aa099" font-size="10">${Math.round(v).toLocaleString()}</text>`}).join('');
    document.getElementById("chart").innerHTML=`<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="PMCC liquidation NAV">${grid}<path class="navline" d="${path}"/>${values.map((v,i)=>`<circle class="dot" cx="${x(i)}" cy="${y(v)}" r="2.5"/>`).join('')}<text x="${L}" y="${H-8}" fill="#8aa099" font-size="10">${esc(rows[0].time)}</text><text x="${W-R}" y="${H-8}" text-anchor="end" fill="#8aa099" font-size="10">${esc(rows.at(-1).time)}</text></svg>`;
    document.getElementById("chart-note").textContent=`${B.combinationId} · AAPL benchmark ${num(B.benchmark.returnPct)}%`;
  }

  const choose = id => render(combos.find(b => b.combinationId === id) || combos[0]);
  picker.addEventListener("change", () => choose(picker.value));
  document.querySelectorAll("#comparison tr").forEach(row => row.addEventListener("click", () => { picker.value = row.dataset.combo; choose(row.dataset.combo); }));
  choose(picker.value);
})();
