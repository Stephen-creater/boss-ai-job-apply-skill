"""Hard anti-risk limits. Every browser action goes through check()/record(); any anomaly writes a HALT file
that blocks the rest of the (Beijing) day. See docs/防风控规则.md."""
import json, os, sys, time
from datetime import datetime, timezone, timedelta
from common import D, CFG
BJ = timezone(timedelta(hours=8))
L = {'day_sends': 50, 'day_pages': 250, 'day_searches': 15, 'hour_pages': 60, 'hour_sends': 20,
     'session_minutes': 45, 'rest_minutes': 30, 'sessions_per_day': 3}
L.update(CFG.get('limits', {}))
def today(): return datetime.now(BJ).strftime('%Y-%m-%d')
def _p(): os.makedirs(D + '/usage', exist_ok=True); return f"{D}/usage/{today()}.json"
def _load():
    try: return json.load(open(_p()))
    except Exception: return {'events': []}
def halt_file(): return f"{D}/usage/HALT-{today()}"
def halted():
    return open(halt_file()).read() if os.path.exists(halt_file()) else None
def halt(reason):
    os.makedirs(D + '/usage', exist_ok=True)
    open(halt_file(), 'w').write(f"{datetime.now(BJ).isoformat()} {reason}\n")
def _sum(ev, kind, since):
    return sum(e['n'] for e in ev if e['k'] == kind and e['t'] >= since)
def sessions(ev):
    ts = sorted(e['t'] for e in ev); out = []
    for t in ts:
        if out and t - out[-1][1] <= L['rest_minutes'] * 60: out[-1][1] = t
        else: out.append([t, t])
    return out
def check(kind, n=1):
    """Raise SystemExit with a Chinese reason if doing n more of `kind` would break a rule."""
    bu = CFG.get('blocked_until')
    if bu and today() < bu: sys.exit(f"已停止：账号风控冷却期，{bu} 之前不操作 BOSS。")
    ramp = CFG.get('ramp_day_sends', {}).get(today())
    if ramp is not None: L['day_sends'] = min(L['day_sends'], ramp)
    h = halted()
    if h: sys.exit(f"已停止：今天出现过异常（{h.strip()}），按规则当天不再操作。")
    ev = _load()['events']; now = time.time(); day0 = 0; hr = now - 3600
    caps = {'send': ('day_sends', 'hour_sends'), 'page': ('day_pages', 'hour_pages'), 'search': ('day_searches', None)}
    dk, hk = caps[kind]
    if _sum(ev, kind, day0) + n > L[dk]: sys.exit(f"已到每日上限：{kind} {_sum(ev, kind, day0)}/{L[dk]}，今天停止。")
    if hk and _sum(ev, kind, hr) + n > L[hk]: sys.exit(f"已到每小时上限：{kind} {_sum(ev, kind, hr)}/{L[hk]}，请稍后再继续。")
    ss = sessions(ev)
    if ss and now - ss[-1][1] <= L['rest_minutes'] * 60:          # still inside current session
        if now - ss[-1][0] > L['session_minutes'] * 60:
            sys.exit(f"本段已连续操作超过 {L['session_minutes']} 分钟，请休息至少 {L['rest_minutes']} 分钟。")
    elif len(ss) >= L['sessions_per_day']:
        sys.exit(f"今天已操作 {len(ss)} 段，达到每日段数上限，今天停止。")
def record(kind, n=1):
    d = _load(); d['events'].append({'t': time.time(), 'k': kind, 'n': n}); json.dump(d, open(_p(), 'w'))
def summary():
    ev = _load()['events']; now = time.time()
    return {k: (_sum(ev, k, 0), _sum(ev, k, now - 3600)) for k in ('send', 'page', 'search')} | {'sessions': len(sessions(ev)), 'halt': halted()}
if __name__ == '__main__':
    print(json.dumps(summary(), ensure_ascii=False))
