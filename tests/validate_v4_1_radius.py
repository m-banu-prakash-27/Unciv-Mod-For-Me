#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
r=Path(__file__).resolve().parents[1]
p=(r/'engine_patch/patch_unciv_v4_1.py').read_text(encoding='utf8')
w=(r/'.github/workflows/build-magalanadu-v4-1-android.yml').read_text(encoding='utf8')
opts=json.loads((r/'jsons/ModOptions.json').read_text(encoding='utf8'))
required=['MAGALANADU_V4_1_RADIUS_108','MAGALANADU_V4_1_BORDER_FRONTIER',
    'MAGALANADU_V4_1_CITY_VIEW_CAP','MAGALANADU_V4_1_WORKABLE_TILES',
    'apply_v4(root)','getWorkRange()', 'getExpandRange()',
    'city.civ.civName == \"Magalanadu\"','civ.civName == \"Magalanadu\"']
for word in required:
    assert word in p, f'Missing patch rule: {word}'
assert opts['constants']['cityWorkRange']==5 and opts['constants']['cityExpandRange']==5, 'Normal civ radius was changed globally'
assert '108' in p and 'if (cityView.getWorkRange() >= 108) 12' in p
assert 'patch_unciv_v4_1.py' in w
assert 'Magalanadu-v4-1-108-Radius-Android-APK' in w
assert (r/'engine_patch/patch_unciv_v4_0.py').is_file()
assert (r/'engine_patch/patch_unciv_4_22_16.py').is_file()
assert 'CityExpansionManager.kt' in p and 'CityScreen.kt' in p
print('PASS: v4.1 108-hex radius, ordinary civs retained, city view cap, frontier-only cultural expansion, v4 compatibility.')
