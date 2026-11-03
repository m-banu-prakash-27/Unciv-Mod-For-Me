#!/usr/bin/env python3
"""v2.7 explicit per-building purchase availability regression check."""
import json, pathlib, sys
R=pathlib.Path(__file__).resolve().parents[1]
mods={p.name:json.loads(p.read_text(encoding='utf8')) for p in (R/'jsons').glob('*.json')}
B=mods['Buildings.json'];U=mods['Units.json'];N=mods['Nations.json'][0]
assert len(B)==59 and len(U)==65
P=[f'Can be purchased with [{c}] [in all cities]' for c in ('Gold','Culture','Faith')]
assert all('Cannot be purchased' not in str(o.get('uniques',[])) for data in mods.values() if isinstance(data,list) for o in data if isinstance(o,dict))
for b in B:
  assert b.get('uniqueTo')=='Magalanadu',b['name']
  for p in P: assert b['uniques'].count(p)==1,(b['name'],p)
  assert b['cost']==5,b['name']
  assert b['uniques'].count('Cost increases by [5] when built')==1,b['name']
  if f'Remove [{b["name"]}] [in this city]' in b['uniques']:
    assert b['uniques'][-1]==f'Remove [{b["name"]}] [in this city]',b['name']
for currency in ['Gold','Culture','Faith']:
  assert f'May buy [All] buildings for [10] [{currency}] [in all cities] at an increasing price ([10])' in N['uniques']
assert all('Cannot be purchased' not in str(u) for u in mods['Units.json'])
print('PASS: zero purchase-blocking uniques across all active mod JSON objects')
print('PASS: all 59 custom buildings explicitly accept Gold, Culture and Faith')
print('PASS: prices, repeatability, city scope, and 65 units retained')
