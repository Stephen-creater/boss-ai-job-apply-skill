"""Make sure the configured ego-browser TaskSpace exists before any BOSS action.
If it is gone (ego clears idle spaces during rests), create a new one and check login with ONE page load:
logged in => update config.local.json and continue; not logged in => stop and tell the user (never ask them to log in again)."""
import json, subprocess, sys, re
from common import ROOT, CFG
import limits

NAME = 'BOSS AI投递'

def _run(js):
    r = subprocess.run(['ego-browser', 'nodejs'], input=js, text=True, capture_output=True)
    return r.stdout + r.stderr

def ensure():
    out = _run('const s = await listTaskSpaces(); console.log("SPACES", JSON.stringify(s.map(x=>x.id)));')
    m = re.search(r'SPACES (\[.*\])', out)
    if m and CFG['space'] in json.loads(m.group(1)):
        return CFG['space']
    limits.check('page', 1)
    out = _run(f'''const task = await taskSpace({json.dumps(NAME)}); console.log("SPACE", task.spaceId);
const p = task.page("p1");
try {{ await p.goto("https://www.zhipin.com/web/geek/jobs?city=101210100"); }} catch(e) {{}}
await p.waitForTimeout(4500);
const s = await p.evaluate(()=>({{nav:!!document.querySelector('.nav-figure'), restrict:/访问受限|异常行为|安全验证|操作频繁|请完成验证|滑块/.test(document.body?.innerText||'')}}));
console.log("STATE", JSON.stringify(s));''')
    limits.record('page', 1)
    sid = re.search(r'SPACE (\d+)', out); st = re.search(r'STATE (\{.*\})', out)
    st = json.loads(st.group(1)) if st else {}
    if st.get('restrict'):
        limits.halt('RESTRICT'); sys.exit('!!! 新空间检测到限制/验证提示，已写入当日停止标记，今天不再操作。')
    if not sid or not st.get('nav'):
        sys.exit('已停止：原浏览器空间已消失，新建的空间未登录。按规则不请用户重新登录，请告诉用户。')
    p = ROOT + '/config.local.json'; c = json.load(open(p)); c['space'] = int(sid.group(1)); c['search_tab'] = 'p1'
    json.dump(c, open(p, 'w'), ensure_ascii=False, indent=1)
    print(f'原空间已消失，已新建空间 {sid.group(1)}（已登录），继续。', file=sys.stderr)
    return int(sid.group(1))

if __name__ == '__main__':
    print(ensure())
