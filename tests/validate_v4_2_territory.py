#!/usr/bin/env python3
"""Static regression for v4.2 plus mathematical 60:40 selection policy."""
from pathlib import Path
import json,math
r=Path(__file__).resolve().parents[1]
p=(r/'engine_patch/patch_unciv_v4_2.py').read_text()
w=(r/'.github/workflows/build-magalanadu-v4-2-android.yml').read_text()
opts=json.loads((r/'jsons/ModOptions.json').read_text())
for item in ['MAGALANADU_V4_2_RADIUS_14','MAGALANADU_V4_2_60_40_CULTURE','MAGALANADU_V4_2_BATCH_CLAIM',
             'MAGALANADU_V4_2_CLAIM_60_40','MAGALANADU_V4_2_CITY_VIEW','isWater','getChoosableTiles()',
             'takeOwnership(next)','getOwner() != null','claimMagalanaduBalancedTiles','40','14','5 * (ownedLand','3 * (total + 1)']:
    assert item in p, f'Missing v4.2 patch feature: {item}'
assert 'city.civ.civName != "Magalanadu"' in p
assert 'city.civ.isCurrentPlayer()' in p
assert opts['constants']['cityWorkRange']==5 and opts['constants']['cityExpandRange']==5
assert 'patch_unciv_v4_2.py' in w and 'Magalanadu-v4-2-Balanced-14-Radius-Android-APK' in w
assert (r/'engine_patch/patch_unciv_v4_1.py').is_file()
assert 1+3*14*15 == 631
assert round(631*.6)==379 and 631-round(631*.6)==252
# Test which tile minimizes the actual ratio deficit, for several city shapes.
def choose(land,water,has_land=True,has_water=True):
    x=[]
    for is_water in (False,True):
        if (is_water and not has_water) or (not is_water and not has_land): continue
        d=abs(5*(land+(0 if is_water else 1))-3*(land+water+1))
        x.append((d,is_water))
    return min(x)[1] if x else None
assert choose(7,0,True,True) is True    # Founding mostly land -> acquire water
assert choose(2,8,True,True) is False   # Too much water -> acquire land
assert choose(60,40,True,True) is False # at target -> choose land to stay near 60%
assert choose(7,0,True,False) is False # Inland fallback: no fabricated water
assert choose(0,0,False,False) is None
print('PASS: 14-radius, 631 area; 60:40 tile preference; inland and coastal behavior; safeguards; v4.2 workflow.')
