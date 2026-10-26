"""Run one browser script inside the ego-browser TaskSpace, with anti-risk limits enforced.
usage: run.py msearch "q|city|sal;..."   |  run.py pread "href|q|city|sal,..."  |  run.py psend href q city sal"""
import sys, json, subprocess, re
from common import SK, D, CFG
import limits
f = sys.argv[1]; args = sys.argv[2:]
names = {'pread': ['H'], 'psend': ['H', 'Q', 'C', 'SAL'], 'msearch': ['LIST']}[f]
env = dict(zip(names, args)); env.update(SPACE=CFG['space'], PS=CFG['search_tab'], T=D)
# ---- pre-check limits (estimated page loads) ----
if f == 'msearch':
    nq = len(env['LIST'].split(';')); limits.check('search', nq); limits.check('page', nq * 2)
elif f == 'pread':
    limits.check('page', len(env['H'].split(',')))
elif f == 'psend':
    limits.check('send', 1); limits.check('page', 1)
import space
env['SPACE'] = space.ensure()   # recreate the space if ego cleared it; stop if the new one is not logged in
js = 'const ENV=' + json.dumps(env, ensure_ascii=False) + ';\n' + open(SK + '/guard.js').read() + '\n' + open(f'{SK}/{f}.js').read()
r = subprocess.run(['ego-browser', 'nodejs'], input=js, text=True, capture_output=True)
lines = [l for l in (r.stdout + r.stderr).splitlines() if 'notice' not in l and 'browser-up' not in l]
out = '\n'.join(lines)
# ---- record usage ----
if f == 'msearch':
    q = sum(1 for l in lines if l.startswith('Q ')); limits.record('search', q); limits.record('page', q * 2)
elif f == 'pread':
    limits.record('page', sum(1 for l in lines if l.startswith('{')) + sum(1 for l in lines if l.startswith('NOCARD')))
elif f == 'psend':
    limits.record('page', 1)
    if '"ok":true' in out: limits.record('send', 1)
# ---- “数据加载失败” => pause 60 min (3rd time today => halt the day) ----
if 'LOADFAIL' in out:
    n = limits.loadfail()
    lines.append(f'!!! 页面“数据加载失败”（今天第 {n} 次），' + ('已写入当日停止标记，今天不再操作。' if n >= 3 else '按规则暂停 60 分钟。'))
# ---- anomaly => halt the whole day ----
if re.search(r'LOGOUT|RESTRICT|"block":true|Control of this task space is with the user', out):
    limits.halt(re.search(r'LOGOUT|RESTRICT|"block":true|Control of this task space', out).group(0))
    lines.append('!!! 检测到异常（掉线/验证/限制），已写入当日停止标记，今天不再操作。')
if f == 'psend':
    keep = [re.sub(r'"text":"[^"]*"', '"text":"…"', l)[:220] for l in lines if re.search(r'RESULT|ABORT|DELAY|CLOSED|Error|error|STATE|!!!', l)]
    print(args[0][12:30], ' | '.join(keep) if keep else 'NO-OUTPUT: ' + ' / '.join(lines[-3:]))
else:
    print('\n'.join(lines))
