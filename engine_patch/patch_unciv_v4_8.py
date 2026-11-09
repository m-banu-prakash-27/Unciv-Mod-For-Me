#!/usr/bin/env python3
"""Install the Magalanadu Intelligence Agency on cumulative Unciv 4.22.16."""
from pathlib import Path
import sys

from patch_unciv_v4_5_1 import once
from patch_unciv_v4_7 import apply as apply_v4_7


def apply(root: Path):
    root = root.resolve()
    apply_v4_7(root)
    engine = root / 'core/src/com/unciv'
    civ_dir = engine / 'logic/civilization'
    popups = engine / 'ui/popups'
    for name, directory in (
        ('MagalanaduAgencyData.kt', civ_dir),
        ('MagalanaduAgency.kt', civ_dir),
        ('MagalanaduAgencyMenu.kt', popups),
    ):
        source = Path(__file__).with_name(name).read_bytes()
        destination = directory / name
        if destination.exists():
            if destination.read_bytes() != source:
                raise RuntimeError(f'Unexpected existing Agency code: {destination}')
        else:
            destination.write_bytes(source)

    civ = civ_dir / 'Civilization.kt'
    once(civ,
         '    var gold = 0\n',
         '    var gold = 0\n'
         '    var magalanaduAgency: MagalanaduAgencyData? = null\n')
    once(civ,
         '        toReturn.gold = gold\n',
         '        toReturn.gold = gold\n'
         '        toReturn.magalanaduAgency = magalanaduAgency?.copy()\n')

    game = engine / 'logic/GameInfo.kt'
    anchor = '        com.unciv.logic.civilization.MagalanaduDefenseObjective.checkTurn(player)\n'
    once(game, anchor, anchor + '        com.unciv.logic.civilization.MagalanaduAgency.processTurn(player)\n')

    directorate = popups / 'MagalanaduDirectorate.kt'
    anchor = '        popup.addButton("PROXY WAR: A declares war on B") {'
    once(directorate, anchor,
         '''        if (com.unciv.logic.civilization.MagalanaduAgency.isAvailable(user)) {
            popup.addButton("INTELLIGENCE AGENCY: plan covert missions") {
                popup.close()
                MagalanaduAgencyMenu.open(user)
            }.row()
        }
''' + anchor)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_8.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
