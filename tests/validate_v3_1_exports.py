from pathlib import Path
import json,re,subprocess,sys
r=Path(__file__).resolve().parents[1]
get=lambda n:json.loads((r/'jsons'/f'{n}.json').read_text(encoding='utf-8'))
u=get('Units'); n=get('Nations'); b=get('Buildings');imp=get('TileImprovements');p=get('UnitPromotions')
m=json.loads((r/'compatibility'/'unit_export_rewards_v3_1.json').read_text())
assert (len(u),len(n),len(b),len(imp),len(p))==(53,1,25,44,3)
assert len(m['rewardedUnits'])==52 and len(set(v['unit'] for v in m['rewardedUnits']))==52
assert len(m['specialCityStateGiftUnits'])==20
allun=set(n[0]['uniques']);byn={v['name']:v for v in u}
for x in m['rewardedUnits']:
 assert x['rewardUnique'] in allun
 assert x['productionCost']==byn[x['unit']]['cost']
 assert x['exportRewardGold']==2*x['productionCost']
 assert x['rewardUnique'].endswith('<in tiles without [your]> <in tiles without [Unowned]> <in tiles without [Enemy]>')
for name in m['specialCityStateGiftUnits']:
 obj=byn[name]
 assert 'May enter foreign tiles without open borders' in obj['uniques']
 assert sum(x.endswith(' gift to a City-State') and f'[{name}]' in x for x in allun)==1
 assert any('optional Magalanadu Unciv engine patch' in x for x in obj['uniques'])
assert 'Allied City-States provide [Gold] equal to [+50]% of what they produce for themselves' in allun
assert '[+100]% resources gifted by City-States' in allun
assert any('Can instantly construct a [Omni Resource Generator]' in x for x in byn['Super Cheat Worker']['uniques'])
assert byn['Super Cheat Settler']['movement']==300
assert len([x for x in imp if x['name']=='Omni Resource Generator'][0]['uniques'])>=35
print('PASS v3.1 donation eligibility, price-indexed payouts, City-State native yields, all v3.0 core objects')
