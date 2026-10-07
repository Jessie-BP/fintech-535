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

  document.getElementById("comparison").innerHTML = combos.map(b => `<tr data-combo="${esc(b.combinationId)}" class="${b.combinationId === best.combinationId ? 'best' : ''}"><td class="mono">${esc(b.combinationId)}${b.combinationId === best.combinationId ? ' <span class="best-tag">BEST</span>' : ''}</td><td>${num(b.long.delta,4)}</td><td class="${b.returnPct >= 0 ? 'good' : 'bad'}">${num(b.returnPct)}%</td><td>${num(b.pnlOnLongDebitPct)}%</td><td>${money(b.endingNav)}</td><td>${num(b.maxDrawdownPct)}%</td><td>${b.tradeWeeks}/${b.decisions.length}</td><td>${b.dataGapWeeks}</td><td>${num(b.benchmark.returnPct)}%</td></tr>`).join("");

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
    ];
    document.getElementById("metrics").innerHTML = cards.map(([k,v])=>`<div class="metric"><label>${k}</label><strong>${v}</strong></div>`).join("");
    document.querySelectorAll("#comparison tr").forEach(row => row.classList.toggle("selected", row.dataset.combo === B.combinationId));
    document.getElementById("decisions").innerHTML = B.decisions.map(r=>`<tr><td class="mono">${esc(r.entryTime)}</td><td class="mono">${esc(r.deltaAsOf)}</td><td class="mono">${esc(r.expiry)}</td><td>${num(r.spot)}</td><td class="${r.status==='TRADE'?'good':'bad'}">${esc(r.status)}</td><td class="mono">${esc(r.shortRic)}</td><td>${num(r.shortDelta,4)}</td><td>${num(r.entryBid,3)}</td><td>${num(r.exitAsk,3)}</td></tr>`).join("");
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
