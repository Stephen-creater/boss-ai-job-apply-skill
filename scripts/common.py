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
os.makedirs(D, exist_ok=True)
