#!/usr/bin/env python3
"""Check v4.7 installation and repeatability on patched Unciv source."""
from pathlib import Path
import sys

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / 'engine_patch'))
from patch_unciv_v4_7 import apply

root = Path(sys.argv[1]).resolve()
engine = root / 'core/src/com/unciv'
game = engine / 'logic/GameInfo.kt'
directorate = engine / 'ui/popups/MagalanaduDirectorate.kt'
core = engine / 'logic/civilization/MagalanaduSecession.kt'
menu = engine / 'ui/popups/MagalanaduUnrestMenu.kt'
files = {path: path.read_bytes() for path in (game, directorate, core, menu)}
for payload in (core, menu):
    assert files[payload] == (repo / 'engine_patch' / payload.name).read_bytes()
assert game.read_text().count('internal fun registerMagalanaduBreakaway(') == 1
assert 'civilizations.add(civ)\n        index[civ.civID] = civ' in game.read_text()
for label in (
    'UNREST AND SECESSION', 'CAMPAIGN OBJECTIVES', 'ACQUIRE ALL RESOURCES', 'MILITARY LOGISTICS'
):
    assert directorate.read_text().count(f'"{label}:') == 1, label
apply(root)
assert all(path.read_bytes() == content for path, content in files.items())
print('PASS: secession registry, menu, prior features and repeatable patch.')
