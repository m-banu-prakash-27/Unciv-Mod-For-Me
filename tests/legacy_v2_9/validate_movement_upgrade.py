#!/usr/bin/env python3
"""Exact v2.7 -> v2.9 movement/air-range transformation checks."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
old=json.loads((R/'compatibility/units_before_movement_v2_7.json').read_text(encoding='utf-8'))
new=json.loads((R/'jsons/Units.json').read_text(encoding='utf-8'))
assert len(old)==len(new)==65
original={x['name']:x for x in old}
current={x['name']:x for x in new}
assert set(current)==set(original), 'Original unit list must be preserved'
assert len(current)==65
AIR_TYPES={'Bomber','Fighter','Missile'}
TRAVEL={
  'All tiles cost 1 movement',
  'May travel on Water tiles without embarking',
  'Can enter ice tiles',
  'Can pass through impassable tiles',
  'May enter foreign tiles without open borders',
}
for name, prev in original.items():
    updated=current[name]
    assert prev['uniqueTo']=='Magalanadu'==updated['uniqueTo']
    if name=='Super Cheat Settler':
        assert updated['movement']==300
        assert updated['replaces']=='Settler'
        assert TRAVEL <= set(updated['uniques'])
        assert set(prev['uniques']) <= set(updated['uniques'])
    else:
        assert updated['movement']==5*prev['movement'], (name, updated['movement'], prev['movement'])
    if prev['unitType'] in AIR_TYPES:
        assert updated['range']==5*prev.get('range',2)
        if 'interceptRange' in prev: assert updated['interceptRange']==5*prev['interceptRange']
    else:
        assert updated.get('range')==prev.get('range')
        assert updated.get('interceptRange')==prev.get('interceptRange')
    # Strictly compare remaining original fields; do not silently alter combat/trade/build/etc.
    allowed={'movement'}
    if name=='Super Cheat Settler': allowed|={'uniques','replaces'}
    if prev['unitType'] in AIR_TYPES: allowed|={'range','interceptRange'}
    assert {k:v for k,v in updated.items() if k not in allowed} == {k:v for k,v in prev.items() if k not in allowed}, name
print('PASS: 64 custom units exactly quintupled; unique Settler 300 and replaces vanilla Settler; four aircraft/missiles quintupled range; other fields unchanged')
print('NOTE: Actual game pathfinding and performance require live gameplay testing.')
