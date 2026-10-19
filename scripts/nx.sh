#!/bin/zsh
# nx.sh <queue.txt> <reads.jsonl> [N=5] [chars=220]
# Read the next N unread candidates in the search-page right panel, show JDs, auto-log hard-rule rejects.
SK="${0:A:h}"
D=$(cd "$SK" && python3 -c "from common import D; print(D)")
cd "$D" || exit 1
Q=$1; R=$2; N=${3:-5}
[ -f "$R" ] || : > "$R"; [ -f badcomp.txt ] || : > badcomp.txt
H=$(python3 - "$Q" "$R" "$N" <<'PY'
import json,sys,re
Q,R,N=sys.argv[1],sys.argv[2],int(sys.argv[3])
done=set()
for l in open(R):
  try: done.add(json.loads(l)['url'])
  except: pass
kn=set(json.load(open('known.json'))); ms=json.load(open('msall.json'))
bad=[x.strip() for x in open('badcomp.txt') if x.strip()]
q=[]
for x in open(Q):
  x=x.strip()
  if not x or x in done or x in kn or x not in ms: continue
  t=ms[x]['t']
  if any(b in t for b in bad): continue
  if re.search(r'销|客户经理|拓展|战略|标注|数据项目|客服|编导|剪辑|策划|猎头|招聘|审核', re.split(r'[-]',t)[0]): continue
  q.append(x)
q.sort(key=lambda h:(ms[h]['q'],ms[h]['c'],ms[h].get('sal','')))
print(','.join(f"{h}|{ms[h]['q']}|{ms[h]['c']}|{ms[h].get('sal','')}" for h in q[:N])); print(len(q)-min(len(q),N),file=sys.stderr)
PY
)
[ -z "$H" ] && { echo EMPTY; exit; }
python3 "$SK/run.py" pread "$H" > last.raw 2>&1; grep -E "LOGOUT|RESTRICT|READERR|NOCARD|MISMATCH|上限|停止|休息|!!!" last.raw | cut -c1-160
grep '^{' last.raw > last.jsonl; cat last.jsonl >> "$R"
grep -qE "LOGOUT|RESTRICT|!!!|已停止|上限|休息" last.raw && { echo "!!! 已停止（见上一行原因）"; exit 1; }
python3 "$SK/show2.py" ${4:-220} < last.jsonl; python3 "$SK/log.py" "$(cat auto.json)" >/dev/null
