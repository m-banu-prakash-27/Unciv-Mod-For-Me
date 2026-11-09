#!/usr/bin/env python3
"""Check native spy integration against the patched 4.22.16 source files."""
from pathlib import Path
import re
import sys

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'engine_patch'))
from patch_unciv_v4_9 import apply, native_agency

root = Path(sys.argv[1]).resolve()
engine = root / 'core/src/com/unciv'
spy = engine / 'models/Spy.kt'
espionage = engine / 'ui/screens/espionage/EspionageScreen.kt'
menu = espionage.with_name('MagalanaduSpyMenu.kt')
logic = engine / 'logic/civilization/MagalanaduAgency.kt'
data = logic.with_name('MagalanaduAgencyData.kt')
civ = logic.with_name('Civilization.kt')
game = engine / 'logic/GameInfo.kt'
directorate = engine / 'ui/popups/MagalanaduDirectorate.kt'
snapshot = {p: p.read_bytes() for p in (spy, espionage, menu, logic, data, civ, game, directorate)}
assert logic.read_text() == native_agency()
assert len(re.findall(r'^    \w+\(AgencyGroup\.', data.read_text(), re.MULTILINE)) == 34
assert 'spyBound: Boolean = false' in data.read_text()
assert 'spyBound = true' in logic.read_text()
assert 'it.getCityOrNull() == posting' in logic.read_text()
assert 'val city = spy.getCityOrNull()' in logic.read_text()
assert 'city.id != op.cityId' in logic.read_text()
assert 'val Slots' not in logic.read_text()
assert 'manager.addSpy()' in espionage.read_text()
assert espionage.read_text().count('MagalanaduAgency.canRecruit(civInfo)') == 2
assert 'MagalanaduSpyMenu.open(this, spy, ::update)' in espionage.read_text()
assert 'MagalanaduAgency.abort(civInfo, it.serial)' in espionage.read_text()
assert 'toReturn.magalanaduOperationSerial = magalanaduOperationSerial' in spy.read_text()
assert 'magalanaduOperationSerial = null' in spy.read_text()
assert 'activeOperation(this) != null) return' in spy.read_text()
assert 'toReturn.magalanaduAgency = magalanaduAgency?.copy()' in civ.read_text()
assert game.read_text().count('MagalanaduAgency.processTurn(player)') == 1
assert 'EspionageScreen(user, world)' in directorate.read_text()
assert 'MagalanaduAgencyMenu.open(user)' not in directorate.read_text()
apply(root)
assert all(path.read_bytes() == content for path, content in snapshot.items())
print('PASS: native spy screen, exclusive recruitment, spy binding, movement and clone hooks, 34 missions, repeatable patch.')
