#!/usr/bin/env python3
"""Validate v2.5's 35 repeatable resource facilities and cumulative Nation triggers."""
from pathlib import Path
import json,re
from collections import Counter
R=Path(__file__).resolve().parents[1]
load=lambda n:json.loads((R/'jsons'/n).read_text('utf8'))
manifest=json.loads((R/'compatibility/balance_manifest.json').read_text('utf8'))
B=load('Buildings.json');N=load('Nations.json')
assert len(B)==59 and len(N)==1
expected=manifest['newResourceBuildings'];assert len(expected)==35 and len(set(expected))==35
buildings={b['name']:b for b in B}
assert all(b in buildings for b in expected)
nation=N[0]['uniques'];duration=manifest['resourceBuildingDurationTurns']
assert duration>=999999 and len(nation)==84
counts=Counter()
for name in expected:
    b=buildings[name]
    assert name not in [v['name'] for v in B[:24]]
    assert b['uniqueTo']=='Magalanadu'
    assert b['uniques']==[f'Remove [{name}] [in this city]'],(name,b['uniques'])
    assert not b.get('isWonder',False) and not b.get('isNationalWonder',False)
    assert b['cost']>=100
    assert not any(x in b for x in ('food','gold','production')),'lasting yields must not vanish on self-removal'
    cat,res=next((a,c) for a,c in [('Strategic',r) for r in ['Horses','Iron','Coal','Oil','Aluminum','Uranium']]+[('Luxury',r) for r in ['Citrus','Copper','Cotton','Crab','Dyes','Furs','Gems','Gold Ore','Incense','Ivory','Jewelry','Marble','Pearls','Porcelain','Salt','Silk','Silver','Spices','Sugar','Truffles','Whales','Wine']]+[('Bonus',r) for r in ['Bananas','Cattle','Deer','Fish','Sheep','Stone','Wheat']] if name.startswith(c+' '))
    counts[cat]+=1
    trigger=f'Provides [100] [{res}] <upon constructing [{name}]> <for [{duration}] turns>'
    assert nation.count(trigger)==1,(name,trigger)
    stat='Production' if cat=='Strategic' or res=='Stone' else 'Gold' if cat=='Luxury' else 'Food'
    assert nation.count(f'[+2 {stat}] [in capital] <upon constructing [{name}]> <for [{duration}] turns>')==1
    assert (R/'Images/BuildingIcons'/(name+'.png')).is_file(),name
    assert f'BuildingIcons/{name}\n' in (R/'MagalanaduResourceBuildings.atlas').read_text('utf8')
    assert b['quote'].startswith('Resource Supply')
assert counts=={'Strategic':6,'Luxury':22,'Bonus':7}
assert len([x for x in nation if ' <upon constructing [' in x and 'Provides [100]' in x])==35
assert len([x for x in nation if ' <upon constructing [' in x and '[+2 ' in x])==35
assert len([x for x in B if x['name'] not in expected])==24
print('PASS: All 35 repeatable buildings trigger +100 nation-owned resource supply and self-remove.')
print('PASS: Each permanent-style income stacks, 35 resource names first, 35 icon atlas matches.')
print('NOTE: Official game runtime still required to confirm save/reload and supply accounting.')
