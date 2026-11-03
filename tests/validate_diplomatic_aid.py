#!/usr/bin/env python3
"""Static checks for v2.1 recipient-activated units (Unciv 4.22.16)."""
import json, re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
units=json.loads((R/'jsons'/'Units.json').read_text())
manifest=json.loads((R/'compatibility'/'balance_manifest.json').read_text())
new={u['name']:u for u in units if u['name'] in manifest['newDiplomaticAidUnits']}
assert len(new)==len(manifest['newDiplomaticAidUnits'])==len(set(manifest['newDiplomaticAidUnits']))
for name,u in new.items():
    assert u['uniqueTo']=='Magalanadu' and u['cost']>=100 and u['movement']>0
    assert u.get('requiredTech')
    assert (R/'Images'/'UnitIcons'/f'{name}.png').exists()
for u in new.values():
    if u['name'].startswith('Magalanadu Blueprint - '):
        tech=u['name'].split(' - ',1)[1]
        assert u['requiredTech']==tech
        assert f'Discover [{tech}] <by consuming this unit>' in u['uniques']
        assert 'Can hurry technology research' in u['uniques']
assert 'Free Technology <by consuming this unit>' in new['Magalanadu Technology Ambassador']['uniques']
assert 'Gain [650] [Science] <by consuming this unit>' in new['Magalanadu Science Envoy']['uniques']
assert new['Magalanadu Foreign Aid Battalion']['strength']<=50
print(f'PASS: {len(new)} custom diplomatic aid units, with {sum(k.startswith("Magalanadu Blueprint - ") for k in new)} exact-tech blueprints')
print('Caveat: Unit gifting requires FRIENDLY major-civ territory, and AI cannot be assumed to activate custom technology actions.')
