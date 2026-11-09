#!/usr/bin/env python3
"""Install the cumulative Magalanadu campaign, unrest, and secession engine changes."""
from pathlib import Path
import sys

from patch_unciv_v4_5_1 import once
from patch_unciv_v4_6 import apply as apply_v4_6


def apply(root: Path):
    root = root.resolve()
    apply_v4_6(root)
    engine = root / 'core/src/com/unciv'
    popups = engine / 'ui/popups'
    payloads = {
        'MagalanaduSecession.kt': engine / 'logic/civilization',
        'MagalanaduUnrestMenu.kt': popups,
    }
    for name, directory in payloads.items():
        source = Path(__file__).with_name(name).read_bytes()
        destination = directory / name
        if destination.exists():
            if destination.read_bytes() != source:
                raise RuntimeError(f'Unexpected existing secession code: {destination}')
        else:
            destination.write_bytes(source)

    game = engine / 'logic/GameInfo.kt'
    once(game,
         '    val civMap by lazy { civilizations.associateBy { it.civID } }\n',
         '''    val civMap by lazy { civilizations.associateByTo(HashMap()) { it.civID } }

    // MAGALANADU_V4_7_SECESSION: register new civs in both the serialized roster and the live lookup.
    internal fun registerMagalanaduBreakaway(civ: Civilization) {
        check(getCivilizationOrNull(civ.civID) == null)
        val index = civMap
        civilizations.add(civ)
        index[civ.civID] = civ
    }

''')
    anchor = '        popup.addButton("COVERT TREASURY: extract actual Gold") {'
    once(popups / 'MagalanaduDirectorate.kt', anchor,
         """        if (!user.gameInfo.gameParameters.isOnlineMultiplayer) {
            popup.addButton("UNREST AND SECESSION: destabilize foreign cities") {
                popup.close()
                MagalanaduUnrestMenu.open(user)
            }.row()
        }
""" + anchor)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_7.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
