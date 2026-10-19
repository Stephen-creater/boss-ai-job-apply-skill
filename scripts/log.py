import json,sys
from common import D as T,W
recs=json.loads(sys.argv[1]); recs = recs if isinstance(recs,list) else [recs]
st=json.load(open(W+"/boss-state.json")); rv=json.load(open(W+"/reviews.json")); known=set(json.load(open(T+"/known.json")))
for r in recs:
  h=r["href"]
  if r["decision"]=="success":
    assert h not in {x["href"] for x in st["success"]}, "dup "+h
    n=len(st["success"])+1
    st["success"].append({"href":h,"title":r["title"],"company":r["company"],"city":r["city"],"salary":r["salary"],"salaryDecoded":r["salary"],"query":r.get("query"),"time":r["time"],"evidence":"已向BOSS发送消息","nextDelayMs":r.get("delay"),"employmentType":r.get("type","正职"),"note":r.get("note",""),"entry":"搜索页右侧详情面板-立即沟通"})
    with open(W+"/checkpoint.md","a") as f: f.write(f"- 第{n}条确认成功：{r['company']}｜{r['title']}｜{r['city']}｜{r['salary']}。{r.get('note','')} 弹窗“已向BOSS发送消息”，{r['time']}；等待{r.get('delay',0)/1000:.3f}秒后关闭。\n")
  with open(W+"/decisions.jsonl","a") as f: f.write(json.dumps({**r,"fullJDReviewed":True},ensure_ascii=False)+"\n")
  rv[h]=r; known.add(h)
st["currentSuccess"]=len(st["success"]); st["status"]="in_progress"
json.dump(st,open(W+"/boss-state.json","w"),ensure_ascii=False,indent=1)
json.dump(rv,open(W+"/reviews.json","w"),ensure_ascii=False,indent=1)
json.dump(sorted(known),open(T+"/known.json","w"))
pc=json.load(open(T+"/prevcomp.json"))
for x in st["success"]: pc.setdefault(x["company"],[]); x["title"] in pc[x["company"]] or pc[x["company"]].append(x["title"])
json.dump(pc,open(T+"/prevcomp.json","w"),ensure_ascii=False)
print("success", len(st["success"]))
