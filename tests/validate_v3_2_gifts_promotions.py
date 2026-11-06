from pathlib import Path
import json,re
root=Path(__file__).resolve().parents[1]
load=lambda n: json.loads((root/'jsons'/f'{n}.json').read_text('utf-8'))
units=load('Units');n=load('Nations');promo=load('UnitPromotions');b=load('Buildings');im=load('TileImprovements')
m=json.loads((root/'compatibility'/'v3_2_promotion_and_gift_manifest.json').read_text())
assert (len(units),len(n),len(b),len(im),len(promo))==(53,1,24,44,3)
assert len(m['standardRelevantPromotions'])==91
assert len(set(m['standardRelevantPromotions']))==91
assert len(n[0]['uniques'])==162+91
promos={p['name'] for p in promo}
for u in units:
 assert set(u['promotions'])>=promos,u['name']
 assert 'May enter foreign tiles without open borders' in u.get('uniques',[]),u['name']
for p in m['standardRelevantPromotions']:
 expected=f'All newly-trained [relevant] units [in all cities] receive the [{p}] promotion'
 assert expected in n[0]['uniques'],p
assert m['majorCivNoOpenBordersGiftRequiresEnginePatch'] is True
assert not any(x['name'].startswith('Magalanadu Resource Supply') for x in b)
assert any(i['name']=='Omni Resource Generator' and len([z for z in i['uniques'] if z.startswith('Provides [50]')])==35 for i in im)
assert next(x for x in units if x['name']=='Super Cheat Settler')['movement']==300
print('PASS v3.2 gifts/promotion manifest (promotions for 53 units + 91 relevant newly-trained promotions)')
