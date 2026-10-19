const fs = await import("node:fs");
const known = new Set(JSON.parse(fs.readFileSync(ENV.T+"/known.json","utf8")));
const task = await takeOverTaskSpace(ENV.SPACE); const p = task.page(ENV.PS);
const seen = new Set(); const all = {};
for (const item of ENV.LIST.split(";")) {
  const [q,c,sal] = item.split("|");
  try { await p.goto("https://www.zhipin.com/web/geek/jobs?query="+encodeURIComponent(q)+"&city="+c+(sal?"&salary="+sal:"")); } catch(e) {}
  await p.waitForTimeout(rnd(3000,5500));
  if (!(await loginOK(p))) { console.log("LOGOUT"); break; }
  for (let i=0;i<(ENV.SCROLLS||1);i++){ await p.evaluate(()=>window.scrollBy(0, 900+Math.random()*900)); await p.waitForTimeout(rnd(2000,5000)); await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight)); await p.waitForTimeout(rnd(1500,3500)); }
  const r = await p.evaluate(() => [...document.querySelectorAll('.job-card-box, .job-card-wrap')].map(c=>{const a=c.querySelector('a[href*="job_detail"]'); return {href:a?.getAttribute('href')?.replace(/\?.*/,''), t:c.innerText.replace(/\s+/g,' ').slice(0,160)}}).filter(x=>x.href));
  let n=0;
  for (const x of r) { if (known.has(x.href)||seen.has(x.href)) continue; seen.add(x.href); n++; all[x.href]={...x,q,c,sal:sal||''}; }
  console.log("Q",q,c,sal||'',"cards",r.length,"new",n);
}
fs.writeFileSync(ENV.T+"/msearch.json", JSON.stringify(all));
