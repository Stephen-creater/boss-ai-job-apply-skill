const fs = await import("node:fs");
const task = await takeOverTaskSpace(ENV.SPACE); const p = task.page(ENV.PS);
const H = ENV.H;
const want = "query="+encodeURIComponent(ENV.Q)+"&city="+ENV.C+(ENV.SAL?"&salary="+ENV.SAL:"");
let url = await p.url();
if (!url.includes("city="+ENV.C) || !decodeURIComponent(url).includes("query="+ENV.Q) || (ENV.SAL && !url.includes("salary="+ENV.SAL)) || (!ENV.SAL && url.includes("salary="))) {
  try { await p.goto("https://www.zhipin.com/web/geek/jobs?"+want); } catch(e) {} await p.waitForTimeout(3000);
}
async function mark(){
  for (let i=0;i<14;i++){ const has = await p.evaluate(h=>!!document.querySelector('a[href^="'+h+'"]'), H); if(has) break; await p.evaluate(()=>window.scrollTo(0,document.body.scrollHeight)); await p.waitForTimeout(1500); }
  return await p.evaluate(h=>{document.querySelectorAll('[data-pick]').forEach(e=>e.removeAttribute('data-pick')); const a=document.querySelector('a[href^="'+h+'"]'); const card=a?.closest('.job-card-box, .job-card-wrap'); if(!card) return null; card.setAttribute('data-pick','1'); return card.innerText.replace(/\s+/g,' ').slice(0,60);}, H);
}
if (!(await loginOK(p))) { console.log("ABORT LOGOUT"); process.exit(0); }
let sel = await mark();
if (!sel) { try { await p.goto("https://www.zhipin.com/web/geek/jobs?"+want); } catch(e) {} await p.waitForTimeout(3000); sel = await mark(); }
if (!sel) { console.log("ABORT card not found"); process.exit(0); }
await p.evaluate(()=>document.querySelector('[data-pick="1"]')?.scrollIntoView({block:'center'})); await p.waitForTimeout(600);
await p.click('[data-pick="1"] a[href^="'+H+'"]', {label:"open job card"});
await p.waitForTimeout(rnd(1500,3000));
const chk = await p.evaluate(() => { const d=document.querySelector('.job-detail-container');
  return { activeHref: document.querySelector('.job-card-box.active a, .job-card-wrap.active a')?.getAttribute('href')?.replace(/\?.*/,''), btn: d?.querySelector('.op-btn-chat')?.innerText.trim() }; });
if (chk.activeHref !== H) { console.log("ABORT active card mismatch", JSON.stringify(chk)); process.exit(0); }
if (chk.btn !== "立即沟通") { if (await panelFail(p)) console.log("LOADFAIL"); console.log("ABORT btn", chk.btn); process.exit(0); }
const t0 = Date.now();
await p.evaluate(()=>document.querySelector('.job-detail-container .op-btn-chat')?.scrollIntoView({block:'center'})); await p.waitForTimeout(rnd(500,1200));
await p.click('.job-detail-container .op-btn-chat', {label:"start chat in detail panel"});
let res = null, notice = "";
for (let i=0;i<28 && !res;i++){ await p.waitForTimeout(500);
  res = await p.evaluate(()=>{ const g=document.querySelector('.greet-boss-dialog'); const t=document.body.innerText;
    if (g && g.innerText.includes('已向BOSS发送消息')) return {ok:true, text:g.innerText.replace(/\s+/g,' ').slice(0,120)};
    if (/今天已与\d+位BOSS沟通/.test(t) && !/沟通上限/.test(t)) return {notice:true, text:t.match(/今天已与\d+位BOSS沟通[^。\n]*/)?.[0]};
    if (/沟通上限|休息一下|安全验证|操作频繁|验证码/.test(t)) return {ok:false, block:true, text: t.match(/.{0,40}(沟通上限|休息一下|安全验证|操作频繁|验证码).{0,40}/)?.[0]};
    return null; });
  if (res && res.notice) { notice = res.text; res = null; try { await p.click('text="好"', {label:"dismiss official notice"}); } catch(e) {} }
}
const ts = new Date().toISOString();
console.log("RESULT", JSON.stringify(res), ts, "ms", Date.now()-t0, "NOTICE", notice);
fs.appendFileSync(ENV.T+"/sends.jsonl", JSON.stringify({h:H, res, ts, notice})+"\n");
if (res?.ok) {
  const delay = rnd(15000,45000);
  console.log("DELAY", delay);
  fs.appendFileSync(ENV.T+"/sends.jsonl", JSON.stringify({h:H, delay})+"\n");
  await p.waitForTimeout(delay);
  try { await p.click('.greet-boss-dialog .close', {label:"close sent dialog"}); } catch(e) {}
  await p.waitForTimeout(800);
  console.log("CLOSED", await p.evaluate(()=>!document.querySelector('.greet-boss-dialog')));
} else {
  const st = await p.evaluate(()=>({btn: document.querySelector('.job-detail-container .op-btn-chat')?.innerText.trim(), dlg: [...document.querySelectorAll('[class*=dialog]')].map(d=>d.innerText.replace(/\s+/g,' ').slice(0,100)).filter(Boolean)}));
  console.log("STATE", JSON.stringify(st));
}
