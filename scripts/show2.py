import sys,json,re
from common import D as T
n=int(sys.argv[1]) if len(sys.argv)>1 else 220
auto=[]
PREV=json.load(open(T+'/prevcomp.json'))
for l in sys.stdin:
  try: r=json.loads(l)
  except: print(l[:160]); continue
  sal=r.get('salary') or ''; name=r.get('name') or ''
  m=re.match(r'(\d+)-(\d+)K',sal); d=re.match(r'(\d+)-(\d+)元/天',sal)
  why=None
  if not r.get('name'): why=None; print('NOT-LOADED',r['url']); continue
  elif not r.get('btn'): print('NO-BTN(未加载?)',r['url']); continue
  elif r.get('btn')!='立即沟通': why='按钮为'+str(r.get('btn'))+'，已沟通过或不可沟通'
  elif m and int(m.group(2))>30: why=f'上限{m.group(2)}K>30K'
  elif m and int(m.group(2))<12 and '实习' not in name: why=f'正职上限{m.group(2)}K<12K'
  elif d and int(d.group(1))<200: why=f'实习日薪下限{d.group(1)}<200'
  elif not m and not d: why='薪资单位无法确认：'+sal
  elif m and '实习' in name: why='实习以月薪标注，日薪无法确认'
  if why:
    auto.append({"href":r['url'],"decision":"reject","title":name,"company":(r.get('comp') or '').split('\n')[0],"city":r.get('city'),"salary":sal,"reason":why})
    print('AUTO-REJECT',r['url'][12:30],name[:20],sal,why)
  else:
    print('==',r['url'],name,'|',sal,'|',r.get('city'),'|',r.get('loc'),'|',r.get('comp'))
    c=(r.get('comp') or '').split('\n')[0]
    pv=[t for k,v in PREV.items() if k and c and (k in c or c in k) for t in v]
    if pv: print('  !!PREV同公司已投:',pv[:6])
    print((r.get('desc') or '')[:n])
json.dump(auto,open(T+'/auto.json','w'),ensure_ascii=False)
