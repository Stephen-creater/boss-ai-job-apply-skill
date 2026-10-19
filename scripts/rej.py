import json,sys,subprocess
from common import SK,D as T
reads={}
for l in open(sys.argv[1]):
  try: r=json.loads(l); reads[r['url']]=r
  except: pass
out=[]
for a in sys.argv[2:]:
  p,why=a.split('|',1); h=[k for k in reads if k.startswith('/job_detail/'+p)][0]; r=reads[h]
  out.append({"href":h,"decision":"reject","title":r['name'],"company":(r.get('comp') or '').split('\n')[0] or r.get('title','').split('_')[-1].replace('招聘',''),"city":r['city'],"salary":r['salary'],"reason":why})
print(subprocess.run(['python3',SK+'/log.py',json.dumps(out,ensure_ascii=False)],capture_output=True,text=True,cwd=T).stdout.strip())
