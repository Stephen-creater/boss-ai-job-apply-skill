"""Shared paths/config. SK = script dir (in the skill); D = private data dir (never committed)."""
import json, os
SK = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SK)
_cfgp = os.path.join(ROOT, 'config.local.json')
CFG = json.load(open(_cfgp if os.path.exists(_cfgp) else os.path.join(ROOT, 'config.example.json')))
D = os.path.expanduser(CFG['state_dir'])            # known.json / msall.json / reads.jsonl / usage ...
W = os.path.join(os.path.expanduser(CFG['work_dir']), CFG['round'])  # boss-state.json / decisions.jsonl ...
T = D  # backward-compatible name used by older helpers
BLOCK = '|'.join(CFG.get('past_employers', [])) or '(?!x)x'
# 主力城市（大头）和补充城市（只作补充：补充城市成功数 ≤ 主力城市成功数的一半）
MAIN_CITIES = CFG.get('main_cities', {'杭州': '101210100', '上海': '101020100'})
EXTRA_CITIES = CFG.get('extra_cities', {'北京': '101010100', '深圳': '101280600', '广州': '101280100'})
CITY_CODE = {**MAIN_CITIES, **EXTRA_CITIES}
EXTRA_RATIO = CFG.get('extra_ratio', 0.5)   # 补充城市成功数 ≤ 主力城市成功数 × 这个比例
os.makedirs(D, exist_ok=True)
