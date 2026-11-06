#!/usr/bin/env python3
"""Targeted checks for disabled/phantom unit actions after v2.2 cleanup."""
import json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
units=json.loads((R/'jsons/Units.json').read_text())
manifest=json.loads((R/'compatibility/balance_manifest.json').read_text())
by_name={u['name']:u for u in units}
assert len(units)==60+len(manifest.get('newResourceUnits',[])), f"Unexpected number of active units: {len(units)}"
assert len(by_name)==len(units)
for name in manifest['removedUnits']:
    assert name not in by_name
    assert not (R/'Images/UnitIcons'/f'{name}.png').exists()
    assert f'UnitIcons/{name}' not in (R/'game.atlas').read_text()
assert by_name['Corporate Mercenary']['uniqueTo']=='Magalanadu'
for name in ['Super Cheat Worker','Super Cheat Settler']:
    assert 'Can move after attacking' not in by_name[name]['uniques']
for u in units:
    # Direct terrain-changing triggerables must be actions, or a building/tech/event trigger.
    for effect in u.get('uniques',[]):
        if effect.startswith('Turn this tile into'):
            assert '<by consuming this unit>' in effect or '<for [1] movement>' in effect, f'Unusable terraforming ability in {u["name"]}: {effect}'
    if u['name'].startswith('Magalanadu Blueprint - '):
        tech=u['name'].split(' - ',1)[1]
        assert f'Discover [{tech}] <by consuming this unit>' in u['uniques']
for name in ['Magalanadu Arms Dealer','Magalanadu Resource Smuggler','Magalanadu Architect of Wonders']:
    assert any('Can instantly construct a [' in x and '<by consuming this unit>' in x for x in by_name[name]['uniques'])
assert 'Can build [Land] improvements on tiles' in by_name['Super Cheat Worker']['uniques']
print('PASS: functional-unit cleanup / no orphan terraformer, no phantom tile-change action; specialist and research action definitions retained.')
print('CAUTION: this is static validation only, not an in-game action or AI simulation.')
