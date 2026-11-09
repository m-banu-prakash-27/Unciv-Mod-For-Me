#!/usr/bin/env python3
"""Apply Magalanadu campaign objectives on top of the cumulative v4.5.1 patch."""
from pathlib import Path
import sys

from patch_unciv_v4_5_1 import apply as apply_v4_5_1, once

OBJECTIVE = 'com.unciv.logic.civilization.MagalanaduDefenseObjective'


def apply(root: Path):
    root = root.resolve()
    apply_v4_5_1(root)
    engine = root / 'core/src/com/unciv'
    logic = engine / 'logic'
    civ = logic / 'civilization/Civilization.kt'
    popups = engine / 'ui/popups'
    payloads = {
        'MagalanaduDefenseObjective.kt': civ.parent,
        'MagalanaduCampaignMenu.kt': popups,
    }
    for name, directory in payloads.items():
        source = Path(__file__).with_name(name).read_bytes()
        destination = directory / name
        if destination.exists() and destination.read_bytes() != source:
            raise RuntimeError(f'Unexpected existing campaign code: {destination}')
        destination.write_bytes(source)

    once(civ,
         '    var civID = ""\n\n    var tech = TechManager()',
         '    var civID = ""\n\n'
         '    // MAGALANADU_V4_6_CAMPAIGN: serialized with the owning civilization.\n'
         '    var magalanaduDefenseObjective: MagalanaduDefenseObjective? = null\n\n'
         '    var tech = TechManager()')
    once(civ,
         '        toReturn.civID = civID\n        toReturn.tech = tech.clone()',
         '        toReturn.civID = civID\n'
         '        toReturn.magalanaduDefenseObjective = magalanaduDefenseObjective\n'
         '        toReturn.tech = tech.clone()')

    once(logic / 'GameInfo.kt',
         '        // Starting their turn\n        TurnManager(player).startTurn(progressBar)\n',
         '        // Starting their turn\n        TurnManager(player).startTurn(progressBar)\n'
         f'        {OBJECTIVE}.checkTurn(player)\n')

    once(civ.parent / 'diplomacy/DeclareWar.kt',
         '        onWarDeclared(otherCivDiplomacy, false, declareWarReason.warType)\n',
         '        onWarDeclared(otherCivDiplomacy, false, declareWarReason.warType)\n'
         f'        {OBJECTIVE}.onWarDeclared(civInfo, otherCiv)\n'
         f'        {OBJECTIVE}.onWarDeclared(otherCiv, civInfo)\n')

    once(logic / 'city/managers/CityConquestFunctions.kt',
         '        city.civ = newCiv\n',
         '        city.civ = newCiv\n'
         f'        if (oldCiv != newCiv) {OBJECTIVE}.onCityLost(oldCiv, city)\n')
    once(logic / 'city/City.kt',
         '        civ.cities = civ.cities.withoutItem(this)\n',
         '        civ.cities = civ.cities.withoutItem(this)\n'
         f'        {OBJECTIVE}.onCityLost(civ, this)\n')

    anchor = '        popup.addButton("ARMS CONTRACTS: donate a military unit") {'
    once(popups / 'MagalanaduDirectorate.kt', anchor,
         '''        if (!user.gameInfo.gameParameters.isOnlineMultiplayer) {
            popup.addButton("CAMPAIGN OBJECTIVES: defend a foreign city") {
                popup.close()
                MagalanaduCampaignMenu.open(user)
            }.row()
        }
''' + anchor)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_6.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
