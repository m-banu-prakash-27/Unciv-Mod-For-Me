#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((ROOT/'jsons'/p).read_text('utf-8'))
B=read('Buildings.json');N=read('Nations.json')[0]['uniques']
M=json.loads((ROOT/'compatibility/balance_manifest.json').read_text('utf-8'))
assert len(B)==59
assert M['purchaseSystemVersion']=='v2.7'
for stat in ['Gold','Culture','Faith']:
    u=f'May buy [All] buildings for [10] [{stat}] [in all cities] at an increasing price ([10])'
    assert N.count(u)==1,(stat,u)
n_wonders=0
names=set()
for b in B:
    name=b['name'];names.add(name)
    uniques=b.get('uniques',[])
    assert b['uniqueTo']=='Magalanadu'
    assert b['cost']==5
    assert 'Cannot be purchased' not in uniques,name
    for currency in ['Gold','Culture','Faith']:
        assert uniques.count(f'Can be purchased with [{currency}] [in all cities]')==1,(name,currency)
    assert uniques.count('Cost increases by [5] when built')==1,name
    if b.get('isWonder') or b.get('isNationalWonder'):
        n_wonders+=1
        assert 'Can be purchased with [Gold] [in all cities]' in uniques,name
    remove=f'Remove [{name}] [in this city]'
    if remove in uniques: assert uniques[-1]==remove,name
assert len(names)==59 and n_wonders==14,n_wonders
for name in M['newRepeatableProjects']+M['newResourceBuildings']:
    assert any(b['name']==name and b['uniques'][-1]==f'Remove [{name}] [in this city]' for b in B)
# In Unciv 4.22.16, cost increases are quadratic, not fixed +10.
# Standard-speed prices: (10+10/2*(n*n+n)) rounded down to 10.
prices=[int((10+10/2*(n*n+n))/10)*10 for n in range(5)]
assert prices==[10,20,40,70,110],prices
print('PASS: All 59 Magalanadu buildings have 5 Production base cost and 5-per-completion growth rule')
print('PASS: All can be purchased for Gold/Culture/Faith with increasing-cost national uniques')
print('PASS: all 59 buildings explicitly permit Gold/Culture/Faith, including 14 special wonders and 45 repeatable projects')
print('PASS: expected Standard-speed purchase prices:',prices)
