#!/usr/bin/env python3
"""Validate the installed mission catalogue, game hooks and repeatable installation."""
from pathlib import Path
import re
import sys

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'engine_patch'))
from patch_unciv_v4_8 import apply

root = Path(sys.argv[1]).resolve()
engine = root / 'core/src/com/unciv'
civ = engine / 'logic/civilization'
ui = engine / 'ui/popups'
hooks = {
    civ / 'Civilization.kt': (
        'var magalanaduAgency: MagalanaduAgencyData? = null',
        'toReturn.magalanaduAgency = magalanaduAgency?.copy()',
    ),
    engine / 'logic/GameInfo.kt': ('MagalanaduAgency.processTurn(player)',),
    ui / 'MagalanaduDirectorate.kt': (
        'MagalanaduAgencyMenu.open(user)', 'MagalanaduUnrestMenu.open(user)', 'MagalanaduCampaignMenu.open(user)',
    ),
}
payloads = [civ / 'MagalanaduAgencyData.kt', civ / 'MagalanaduAgency.kt', ui / 'MagalanaduAgencyMenu.kt']
civilization = (civ / 'Civilization.kt').read_text()
assert ('    var gold = 0\n        private set\n\n'
        '    var magalanaduAgency: MagalanaduAgencyData? = null\n') in civilization
assert not re.search(r'var magalanaduAgency:[^\n]+\n\s+private set\b', civilization)
snapshot = {path: path.read_bytes() for path in [*hooks, *payloads]}
for path, anchors in hooks.items():
    for anchor in anchors:
        assert path.read_text().count(anchor) == 1, (path, anchor)
for path in payloads:
    assert snapshot[path] == (repo / 'engine_patch' / path.name).read_bytes()

data, logic, menu = (path.read_text() for path in payloads)
missions = re.findall(r'^    (\w+)\(AgencyGroup\.(\w+), "([^"]+)"', data, re.MULTILINE)
assert len(missions) == len({mission[0] for mission in missions}) == 34
assert len({mission[1] for mission in missions}) == 5
handlers = logic.split('return when (mission) {', 1)[1].split('private fun brief', 1)[0]
assert {m[0] for m in missions} == set(re.findall(r'AgencyMission\.(\w+)', handlers))
for _, _, title in missions:
    assert title in (repo / 'V4_8_INTELLIGENCE_AGENCY_GUIDE.md').read_text()
assert 'AgencyMission.entries.filter' in menu
assert 'fun layLow(' in logic and 'Agency.layLow(' in menu
apply(root)
assert all(path.read_bytes() == content for path, content in snapshot.items())
print('PASS: 34 Agency missions across five groups, UI/turn/save hooks and repeatable installation.')
