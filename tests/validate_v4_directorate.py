#!/usr/bin/env python3
"""Verify v4.0 files, exercise patcher idempotence against 4.22.16-style anchors.

Full Kotlin/Android integration must be built via the GitHub Actions Android runner.
"""
from pathlib import Path
import hashlib
import json
import tempfile
import sys

ROOT=Path(__file__).resolve().parents[1]
engine=ROOT/'engine_patch'
sys.path.insert(0,str(engine))
from patch_unciv_v4_0 import apply

v4=(engine/'MagalanaduDirectorate.kt').read_text()
actions=(engine/'patch_unciv_v4_0.py').read_text()
old=(engine/'patch_unciv_4_22_16.py').read_text()

for name in [
    'MAGALANADU STRATEGIC DIRECTORATE','FORCE WAR NOW','FOREIGN RESOURCE RIGHTS',
    'PROXY WAR: A declares war on B','COVERT TREASURY','STEALTH SABOTAGE',
    'SUPREME SEIZURE','DISINFORMATION', 'TradeOfferType.Gold_Per_Turn',
    'TradeOfferType.Strategic_Resource','TradeOfferType.Luxury_Resource',
    'getCivResourceSupply()', 'inProgressConstructions[current]',
    'declareWar()', 'addModifier(DiplomaticModifiers.Denunciation',
    'trade.reverse()', 'CONTRACT_TURNS = 20', 'RESOURCE_TURNS = 30', 'RESOURCE_LONG_TERM_TURNS = 9999',
]:
    assert name in v4, f'Missing functional Directorate mechanic: {name}'
for name in ['MAGALANADU_V4_0_DIRECTORATE_LAUNCHER','MAGALANADU_V4_0_ARMS_EXPORT_CONTRACT','patch_unciv(root)','MagalanaduDirectorate.kt']:
    assert name in actions, f'Missing engine patch integration: {name}'
assert 'MAGALANADU_V3_2_MAJOR_CIV_GIFT_FIX' in old, 'Regressed existing major-civ gifting patch'
assert 'MAGALANADU_V3_2_SPAWN_PROMOTIONS' in old, 'Regressed earlier promotion fix'

# Synthetic source with the EXACT original anchors, used to verify source patch layout.
SOURCE_ACTIONS = '''package com.unciv.logic.map.mapunit.actions
object UnitActions {
    private fun getGiftActions(unit: MapUnit, tile: Tile) = sequence {
        yield(UnitAction(UnitActionType.GiftUnit, action = {}))
    }
    private suspend fun SequenceScope<UnitAction>.addAutomateActions(unit: MapUnit) {}
    private fun all(unit: MapUnit) = sequence {
        yieldAll(UnitActionsUpgrade.getUpgradeActions(unit))
    }
}
'''
SOURCE_MANAGER='''object UnitManager {
    fun placeUnitNearTile() {
        copiedFrom?.copyStatisticsTo(unit)
    }
}
'''
with tempfile.TemporaryDirectory(prefix='magalanadu-v4-engine-test-') as td:
    root=Path(td)
    action_file=root/'core/src/com/unciv/logic/map/mapunit/actions/UnitActions.kt'
    manager=root/'core/src/com/unciv/logic/civilization/managers/UnitManager.kt'
    popup=root/'core/src/com/unciv/ui/popups'
    for f in (action_file,manager):f.parent.mkdir(parents=True,exist_ok=True)
    popup.mkdir(parents=True,exist_ok=True)
    action_file.write_text(SOURCE_ACTIONS)
    manager.write_text(SOURCE_MANAGER)
    apply(root)
    a=action_file.read_text()
    b=manager.read_text()
    c=(popup/'MagalanaduDirectorate.kt').read_text()
    assert all(a.count(x)==1 for x in [
        'MAGALANADU_V3_2_MAJOR_CIV_GIFT_FIX',
        'MAGALANADU_V4_0_DIRECTORATE_LAUNCHER',
        'MAGALANADU_V4_0_ARMS_EXPORT_CONTRACT'])
    assert 'MAGALANADU_V3_2_SPAWN_PROMOTIONS' in b
    assert c==v4
    a_hash=hashlib.sha256(action_file.read_bytes()).digest()
    b_hash=hashlib.sha256(manager.read_bytes()).digest()
    apply(root)
    assert a_hash==hashlib.sha256(action_file.read_bytes()).digest(), 'Patcher not idempotent for UnitActions'
    assert b_hash==hashlib.sha256(manager.read_bytes()).digest(), 'Patcher not idempotent for UnitManager'

wf=(ROOT/'.github/workflows/build-magalanadu-v4-android.yml').read_text()
assert 'python engine_patch/patch_unciv_v4_0.py game' in wf
assert ':android:assembleDebug' in wf
assert 'Magalanadu-v4-Strategic-Directorate-Android-APK' in wf
assert (ROOT/'.github/workflows/build-magalanadu-patched-android.yml').is_file(), 'Old v3.2 fallback missing'
assert '_CANONICAL_HISTORICAL_SOURCE_HASHES' in (ROOT/'tests/validate_v3_0.py').read_text(), 'Earlier Git line-ending safety fix lost'
for s in ['Units','Buildings','Nations','TileImprovements','UnitPromotions']:
    json.loads((ROOT/'jsons'/f'{s}.json').read_text())
print('PASS v4.0: 6 real operations, war/resource/arms contracts, initial v3.2 patch, idempotence, workflows, existing JSON roster')
print('NOTE: This does NOT replace a full Android build and in-game testing')
