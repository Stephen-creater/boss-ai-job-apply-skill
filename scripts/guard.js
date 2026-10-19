// Page-state guard injected before every browser script. Any sign of logout / verification / restriction => stop.
async function loginOK(p){
  const s = await p.evaluate(()=>{ const t=document.body?.innerText||''; const dlg=[...document.querySelectorAll('.boss-login-dialog-content')].some(d=>d.offsetParent);
    return { nav: !!document.querySelector('.nav-figure'), dlg, lock: /登录查看完整内容/.test(t), restrict: /访问受限|异常行为|安全验证|操作频繁|请完成验证|滑块/.test(t) }; });
  if (s.restrict) { console.log("RESTRICT"); return false; }
  return s.nav && !s.dlg && !s.lock;
}
function rnd(a,b){ return a+Math.floor(Math.random()*(b-a)); }
