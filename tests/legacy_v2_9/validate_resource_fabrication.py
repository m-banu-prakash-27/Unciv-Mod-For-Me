#!/usr/bin/env python3
"""Verify terrain-independent tile-resource fabrication without overwriting base resources."""
import json,re
from collections import Counter
from pathlib import Path
r=Path(__file__).resolve().parents[1]
j=r/'jsons'
read=lambda p:json.loads((j/p).read_text('utf8'))
u=read('Units.json');im=read('TileImprovements.json')
f=json.loads((r/'compatibility/balance_manifest.json').read_text('utf8'))
units={x['name']:x for x in u};imps={x['name']:x for x in im}
assert 'TileResources.json' not in [p.name for p in j.glob('*.json')], 'MUST NOT rewrite vanilla world generation'
assert len(f['newResourceUnits'])==5 and len(f['newResourceImprovements'])==35
for name in f['newResourceImprovements']:
    x=imps[name]
    assert x['uniqueTo']=='Magalanadu'
    assert 'Land' in x['terrainsCanBeBuiltOn'] and 'Water' in x['terrainsCanBeBuiltOn']
    assert all(t in x['terrainsCanBeBuiltOn'] for t in ['Forest','Jungle','Marsh','Mountain','Ice','Fallout'])
    assert re.match(r'^Provides \[\d+\] \[[^]]+\]$',x['uniques'][0]),name
    assert (r/'Images'/'ImprovementIcons'/f'{name}.png').is_file()
for name in f['newResourceUnits']:
    assert name in units
    assert units[name]['uniqueTo']=='Magalanadu'
    assert (r/'Images'/'UnitIcons'/f'{name}.png').is_file()
coverage=Counter()
for name in f['newResourceUnits']:
    for unique in units[name]['uniques']:
        m=re.match(r'Can instantly construct a \[([^]]+)\] improvement <for \[1\] movement>',unique)
        if m:
            assert m.group(1) in f['newResourceImprovements'], (name,m.group(1))
            coverage[m.group(1)]+=1
assert set(coverage)==set(f['newResourceImprovements']) and all(v==1 for v in coverage.values())
direct=units['Magalanadu Natural Deposit Surveyor']
assert sum(x.startswith('Add [') and x.endswith('] to this tile <for [1] movement>') for x in direct['uniques'])==35
assert len(imps)==9+35 and len(u)==60+5
print(f'PASS: {len(coverage)} all-terrain tile resource fabricators; 35 terrain-limited native deposit actions; original resources untouched')
print('RUNTIME CAVEAT: natural deposits remain terrain limited. Mountain/ice access and 4.22.16 actions still need in-game testing.')
