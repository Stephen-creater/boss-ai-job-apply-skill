// read JDs in the search page right panel (no separate detail page). ENV.H = "href|q|c|sal,href|q|c|sal"
const fs = await import("node:fs");
const task = await takeOverTaskSpace(ENV.SPACE); const p = task.page(ENV.PS);
const dec = s => (s||'').replace(/[\ue031-\ue03a]/g, ch => String(ch.charCodeAt(0)-0xe031));
for (const item of ENV.H.split(",")) { try {
  const [H,q,c,sal] = item.split("|");
  const want = "query="+encodeURIComponent(q)+"&city="+c+(sal?"&salary="+sal:"");
  let url = await p.url();
  if (!url.includes("city="+c) || !decodeURIComponent(url).includes("query="+q) || (sal && !url.includes("salary="+sal)) || (!sal && url.includes("salary="))) {
    try { await p.goto("https://www.zhipin.com/web/geek/jobs?"+want); } catch(e) {} await p.waitForTimeout(rnd(2500,4500));
  }
  if (!(await loginOK(p))) { console.log("LOGOUT"); process.exit(0); }
  let ok=false;
  for (let i=0;i<14;i++){ ok = await p.evaluate(h=>!!document.querySelector('a[href^="'+h+'"]'), H); if(ok) break; await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight)); await p.waitForTimeout(rnd(1800,3500)); }
  if (!ok) { console.log("NOCARD", H); continue; }
  await p.evaluate(h=>{document.querySelectorAll('[data-pick]').forEach(e=>e.removeAttribute('data-pick')); const card=document.querySelector('a[href^="'+h+'"]').closest('.job-card-box, .job-card-wrap'); card.setAttribute('data-pick','1'); card.scrollIntoView({block:'center'});}, H);
  await p.waitForTimeout(rnd(600,1400));
  await p.click('[data-pick="1"] a[href^="'+H+'"]', {label:"open job card"});
  await p.waitForTimeout(rnd(5000,15000));
  await p.evaluate(()=>{const b=document.querySelector('.job-detail-body')||document.querySelector('.job-detail-container'); b?.scrollBy?.(0,400);});
  const r = await p.evaluate(()=>{ const d=document.querySelector('.job-detail-container'); const q=s=>d?.querySelector(s)?.textContent?.trim();
    const card=document.querySelector('[data-pick="1"]');
    return { activeHref: document.querySelector('.job-card-box.active a, .job-card-wrap.active a')?.getAttribute('href')?.replace(/\?.*/,''),
      name:q('.job-name'), salaryRaw:q('.job-salary'), tags:q('.tag-list'), btn:d?.querySelector('.op-btn-chat')?.innerText.trim(),
      desc:d?.querySelector('.desc')?.innerText?.trim(), loc:q('.job-address-desc'), boss:q('.boss-info-attr'), card: card?.innerText.replace(/\s+/g,' ').slice(0,160) }; });
  if (!(await loginOK(p))) { console.log("LOGOUT"); process.exit(0); }
  if (!r.desc && await panelFail(p)) { console.log("LOADFAIL"); process.exit(0); }
  if (r.activeHref!==H) { console.log("MISMATCH", H, r.activeHref); continue; }
  const cardTxt = r.card||''; const parts = cardTxt.split(' ');
  const out = { url:H, name:r.name, salary:dec(r.salaryRaw).replace(/\s+/g,''), city:(r.loc||cardTxt).match(/杭州|上海|北京|深圳|广州|南京|苏州|宁波|成都|武汉/)?.[0]||'', loc:r.loc,
    btn:r.btn, desc:(r.desc||'').replace(/\n{2,}/g,'\n').slice(0,1300), comp:(r.boss||'').split('·')[0].trim(), card:dec(cardTxt), via:'panel', readAt:new Date().toISOString() };
  console.log(JSON.stringify(out));
  fs.appendFileSync(ENV.T+"/reads.jsonl", JSON.stringify(out)+"\n");
} catch(e) { console.log("READERR", item.slice(0,60), String(e).slice(0,100)); } }
