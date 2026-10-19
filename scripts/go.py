# go.py reads.jsonl ms.json 'prefix|type|note' ...  (<=4 per call)
import json,sys,re,subprocess
from common import SK,D as T,BLOCK
reads={}
for l in open(sys.argv[1]):
  try: r=json.loads(l); reads[r['url']]=r
  except: pass
ms=json.load(open(sys.argv[2]))
for a in sys.argv[3:]:
  p,typ,note=a.split('|',2)
  h=[k for k in reads if k.startswith('/job_detail/'+p)][0]; r=reads[h]; m=ms.get(h,{})
  comp=(r.get('comp') or '').split('\n')[0] or re.sub(r'招聘$','',r.get('title','').split('_')[-1])
  if re.search(BLOCK,comp+r.get('title',''),re.I): print('BLOCKED past employer',h,comp); continue
  q=m.get('q','AI Agent'); c=m.get('c','101210100' if r['city']=='杭州' else '101020100'); sal=m.get('sal','')
  out=subprocess.run(['python3',SK+'/run.py','psend',h,q,c,sal],capture_output=True,text=True); out=(out.stdout+out.stderr).strip(); print(out[:260])
  if 'card not found' in out:
    q=r['name']; sal=''
    out=subprocess.run(['python3',SK+'/run.py','psend',h,q,c,sal],capture_output=True,text=True); out=(out.stdout+out.stderr).strip(); print('RETRY',out[:240])
  if '"ok":true' in out:
    t=re.search(r'\d{4}-\d\d-\d\dT[\d:.]+Z',out).group(0); d=int(re.search(r'DELAY (\d+)',out).group(1))
    rec={"href":h,"decision":"success","title":r['name'],"company":comp,"city":r['city'],"salary":r['salary'],"type":typ,"query":q,"time":t,"delay":d,"note":note}
    print(subprocess.run(['python3',SK+'/log.py',json.dumps(rec,ensure_ascii=False)],capture_output=True,text=True,cwd=T).stdout.strip())
  else:
    print('STOP: not ok'); break
