# filt.py ms.json out.txt [allow_intern]
import json,re,sys
from common import D as T
d=json.load(open(sys.argv[1])); kn=set(json.load(open(T+'/known.json')))
intern = len(sys.argv)>3
good=re.compile(r'AI|Ai|ai|Agent|agent|智能体|大模型|AIGC|LLM|RAG|FDE|Dify|Coze|MCP|数字员工|知识库|提示词|解决方案')
bad=re.compile(r'销售|算法|测试|标注|运维|训练|讲师|教师|老师|推理|电商|游戏|医疗|医药|金融|银行|证券|保险|直播|短剧|招商|客服|主播|运营|跨境|教育|招投标|健康|设计师|UI|美术|视频|图像|原画|摄影|总监|合伙人|嵌入式|硬件|芯片|渠道|商务|BD|市场|营销|品牌|电销|动画|供应链|物流|审计|课程|教培|量化|建筑|医学|广告|政务|政府|药|财务|税|基金|生物|儿童|采购|算力|评测|质检|测评|C\+\+|\.NET|前端|GIS|外派|驻场|法律|律师|地产|房|酒店|旅游|能源|电力|号池|翻译|数据开发|ETL|爬虫|培训|宠物|剧本|部署|AI辅助|AI编程|AI Coding|vibe|Vibe'+('' if intern else '|实习'))
out=[]
for h,x in d.items():
  if h in kn: continue
  t=re.split(r'[-]',x['t'])[0]; loc=x['t'].split(' ')[-1]
  if good.search(t) and not bad.search(x['t']) and re.search(r'(杭州|上海)(·|$)',loc): out.append(h)
open(sys.argv[2],'w').write('\n'.join(out)+'\n'); print(len(d),len(out))
