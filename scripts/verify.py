"""End-of-day verification for the current round. usage: verify.py [history_rounds_glob]
Checks: count, unique links, overlap with earlier rounds, cities, salary rules, toast evidence, delays, past employers."""
import json, glob, os, re, sys
from datetime import datetime
from common import W, CFG, BLOCK, CITY_CODE, EXTRA_CITIES, EXTRA_RATIO
st = json.load(open(W + '/boss-state.json')); S = st['success']
base = os.path.dirname(W); prev = set()
for f in glob.glob(base + '/round-*/decisions.jsonl'):
    if os.path.dirname(f) == W: continue
    for l in open(f):
        try:
            d = json.loads(l)
            if d.get('decision') == 'success': prev.add(d['href'])
        except Exception: pass
bad = []
ex = sum(s['city'] in EXTRA_CITIES for s in S)
if ex > (len(S) - ex) * EXTRA_RATIO: bad.append(('补充城市', ex, f'超过主力城市的 {EXTRA_RATIO} 倍'))
for s in S:
    sal = s['salary']; m = re.match(r'(\d+)-(\d+)K', sal); d = re.match(r'(\d+)-(\d+)元/天', sal)
    if '实习' in s['employmentType']:
        if not d or int(d.group(1)) < 200: bad.append((s['company'], sal, '实习日薪'))
    elif not m or not (12 <= int(m.group(2)) <= 30): bad.append((s['company'], sal, '正职月薪'))
    if s['city'] not in CITY_CODE: bad.append((s['company'], s['city'], '城市'))
    if re.search(BLOCK, s['company']): bad.append((s['company'], '过往公司'))
ts = sorted(datetime.fromisoformat(s['time'].replace('Z', '+00:00')) for s in S if 'T' in s['time'])
gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:])]
cities = {}
for s in S: cities[s['city']] = cities.get(s['city'], 0) + 1
out = dict(round=CFG['round'], success=len(S), unique=len({s['href'] for s in S}), overlap_prev=len({s['href'] for s in S} & prev),
           cities=cities, intern=sum('实习' in s['employmentType'] for s in S), toast_all=all(s['evidence'] == '已向BOSS发送消息' for s in S),
           min_gap_s=round(min(gaps), 1) if gaps else None, violations=bad)
print(json.dumps(out, ensure_ascii=False, indent=1))
