#!/usr/bin/env python3
"""Verify campaign installation and repeatability against patched Unciv source."""
from pathlib import Path
import sys

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'engine_patch'))
from patch_unciv_v4_6 import apply

root = Path(sys.argv[1]).resolve()
engine = root / 'core/src/com/unciv'
hooks = {
    'logic/civilization/Civilization.kt': (
        'var magalanaduDefenseObjective: MagalanaduDefenseObjective? = null',
        'toReturn.magalanaduDefenseObjective = magalanaduDefenseObjective',
    ),
    'logic/GameInfo.kt': ('MagalanaduDefenseObjective.checkTurn(player)',),
    'logic/civilization/diplomacy/DeclareWar.kt': (
        'MagalanaduDefenseObjective.onWarDeclared(civInfo, otherCiv)',
        'MagalanaduDefenseObjective.onWarDeclared(otherCiv, civInfo)',
    ),
    'logic/city/managers/CityConquestFunctions.kt': (
        'if (oldCiv != newCiv) com.unciv.logic.civilization.MagalanaduDefenseObjective.onCityLost(oldCiv, city)',
    ),
    'logic/city/City.kt': ('MagalanaduDefenseObjective.onCityLost(civ, this)',),
    'ui/popups/MagalanaduDirectorate.kt': ('MagalanaduCampaignMenu.open(user)',),
}
snapshot = {}
for relative, anchors in hooks.items():
    path = engine / relative
    text = path.read_text()
    for anchor in anchors:
        assert text.count(anchor) == 1, f'Missing or duplicate hook: {relative}: {anchor}'
    snapshot[path] = path.read_bytes()
for relative in (
    'logic/civilization/MagalanaduDefenseObjective.kt',
    'ui/popups/MagalanaduCampaignMenu.kt',
):
    path = engine / relative
    snapshot[path] = path.read_bytes()
    assert snapshot[path] == (repo / 'engine_patch' / path.name).read_bytes()
apply(root)
assert all(path.read_bytes() == content for path, content in snapshot.items())
print('PASS: campaign save, turn, war, ownership and menu hooks. Patch is repeatable.')
