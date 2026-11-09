#!/usr/bin/env python3
"""Install the Agency inside the native Unciv 4.22.16 espionage screen."""
from pathlib import Path
import sys

from patch_unciv_v4_5_1 import once
from patch_unciv_v4_7 import apply as apply_v4_7

AGENCY = 'com.unciv.logic.civilization.MagalanaduAgency'
MENU = 'com.unciv.ui.screens.espionage.MagalanaduSpyMenu'
SOURCE = Path(__file__).resolve().parent


def replace(text, before, after):
    if text.count(before) != 1:
        raise RuntimeError(f'Unexpected v4.8 Agency source: {before}')
    return text.replace(before, after, 1)


def install(path, content):
    if path.exists() and path.read_text(encoding='utf-8') != content:
        raise RuntimeError(f'Unexpected file {path}. Use a fresh Unciv 4.22.16 checkout.')
    if not path.exists():
        path.write_text(content, encoding='utf-8')


def native_agency():
    code = (SOURCE / 'MagalanaduAgency.kt').read_text(encoding='utf-8')
    code = replace(code, 'import com.unciv.models.SpyAction', 'import com.unciv.models.Spy\nimport com.unciv.models.SpyAction')
    code = replace(code, '    const val Slots = 3\n', '')
    code = replace(code, '&& !player.gameInfo.gameParameters.isOnlineMultiplayer',
                   '&& !player.gameInfo.gameParameters.isOnlineMultiplayer && player.gameInfo.isEspionageEnabled()')
    code = replace(code, '    fun targets(player: Civilization)', '''    fun canRecruit(player: Civilization) = isAvailable(player) && player.isCurrentPlayer()

    fun isDomestic(mission: AgencyMission) = when (mission) {
        AgencyMission.Counterintel, AgencyMission.Expel, AgencyMission.Interrogate, AgencyMission.TurnAgent -> true
        else -> false
    }

    fun isReady(player: Civilization, spy: Spy) =
        canRecruit(player) && spy in player.espionageManager.spyList && spy.isAlive() &&
            spy.isSetUp() && spy.action != SpyAction.Coup && spy.getCityOrNull() != null

    fun activeOperation(spy: Spy): AgencyOperation? {
        val serial = spy.magalanaduOperationSerial ?: return null
        return spy.civInfo.magalanaduAgency?.operations?.firstOrNull { it.serial == serial && it.spyBound }
    }

    fun operativeChance(mission: AgencyMission, network: AgencyNetwork, careful: Boolean, spy: Spy) =
        (chance(mission, network, careful) + (spy.getEffectiveRank() - 1).coerceIn(0, 10) * 3).coerceAtMost(97)

    fun targets(player: Civilization)''')
    code = replace(code,
        '''        player: Civilization, mission: AgencyMission, target: Civilization, city: City?,
        secondary: String, careful: Boolean''',
        '''        player: Civilization, spy: Spy, mission: AgencyMission, target: Civilization,
        secondary: String, careful: Boolean''')
    code = replace(code,
        '''        val data = player.magalanaduAgency ?: MagalanaduAgencyData().also { player.magalanaduAgency = it }
        if (data.operations.size >= Slots) return "All three operation slots are occupied."
        if (data.operations.any { it.civId == target.civID }) return "An operation is already active in this civilization."''',
        '''        if (!isReady(player, spy) || activeOperation(spy) != null)
            return "This spy is unavailable. Establish a network or finish their current operation."
        val city = spy.getCityOrNull() ?: return "Station this spy in a city first."
        if (if (isDomestic(mission)) city.civ != player else city.civ != target)
            return "This mission is unavailable at the spy's current posting."
        val data = player.magalanaduAgency ?: MagalanaduAgencyData().also { player.magalanaduAgency = it }''')
    code = replace(code, '            (city == null || !MagalanaduSecession.canTarget(player, target) ||',
                   '            (!MagalanaduSecession.canTarget(player, target) ||')
    code = replace(code,
        '''            data.serial, mission.name, target.civID, city?.id.orEmpty(), secondary, careful,
            player.gameInfo.turns + duration(mission, careful)
        ))''',
        '''            data.serial, mission.name, target.civID, city.id, secondary, careful,
            player.gameInfo.turns + duration(mission, careful), spyBound = true
        ))
        spy.magalanaduOperationSerial = data.serial''')
    code = replace(code, '        data.operations.remove(op)\n        report(player, data,',
        '''        data.operations.remove(op)
        player.espionageManager.spyList.firstOrNull { it.magalanaduOperationSerial == serial }
            ?.magalanaduOperationSerial = null
        report(player, data,''')
    code = replace(code,
        '''        val due = data.operations.filter { it.readyTurn <= player.gameInfo.turns }''',
        '''        val spiesByOperation = player.espionageManager.spyList
            .mapNotNull { spy -> spy.magalanaduOperationSerial?.let { it to spy } }.toMap()
        val due = data.operations.filter {
            !it.spyBound || it.readyTurn <= player.gameInfo.turns || it.serial !in spiesByOperation
        }''')
    code = replace(code,
        '''            val target = player.gameInfo.getCivilizationOrNull(op.civId)
            val label = "${mission.title} in ${target?.civName ?: op.civId}"
            val city = target?.cities?.firstOrNull { it.id == op.cityId }
            val needsCity = mission.target == AgencyTarget.City || mission.target == AgencyTarget.Secession
            if (target == null || target.isDefeated() || (needsCity && city == null)) {
                report(player, data, "$label aborted. Target changed before execution.")
                continue
            }''',
        '''            if (!op.spyBound) {
                player.addGold(cost(mission, op.careful))
                report(player, data, "${mission.title} refunded. Assign a stationed spy to relaunch it.")
                continue
            }
            val spy = spiesByOperation[op.serial]
            spy?.magalanaduOperationSerial = null
            val target = player.gameInfo.getCivilizationOrNull(op.civId)
            val label = "${spy?.name ?: "Spy"}: ${mission.title} against ${target?.civName ?: op.civId}"
            val city = spy?.getCityOrNull()
            if (spy == null || !isReady(player, spy) || target == null || target.isDefeated() ||
                city == null || city.id != op.cityId || city.civ != (if (isDomestic(mission)) player else target)) {
                report(player, data, "$label aborted. The assigned spy or their posting was lost.")
                continue
            }''')
    code = replace(code, 'random.nextInt(100) < chance(mission, net, op.careful)',
                   'random.nextInt(100) < operativeChance(mission, net, op.careful, spy)')
    code = replace(code, 'sweep(player, target, net, mission)', 'sweep(city!!, target, net, mission)')
    code = replace(code, 'fun sweep(player: Civilization, target:', 'fun sweep(posting: City, target:')
    code = replace(code, 'it.getCityOrNull()?.civ == player', 'it.getCityOrNull() == posting')
    code = replace(code, 'The sweep found no active spy in Magalanadu.',
                   'The sweep found no rival spy in this city.')
    code = replace(code, '            val random = Random(', '''            val unavailable = when (mission) {
                AgencyMission.Interrogate, AgencyMission.TurnAgent -> !net.captive
                AgencyMission.Counterintel -> net.captive
                AgencyMission.Station -> net.station
                AgencyMission.Smuggling -> net.route
                else -> false
            }
            if (unavailable) {
                report(player, data, "$label aborted. The required asset changed before execution.")
                continue
            }
            val random = Random(''')
    return code


def apply(root):
    root = root.resolve()
    apply_v4_7(root)
    engine = root / 'core/src/com/unciv'
    civ = engine / 'logic/civilization'
    spy = engine / 'models/Spy.kt'
    popups = engine / 'ui/popups'
    screen = engine / 'ui/screens/espionage'
    data = replace((SOURCE / 'MagalanaduAgencyData.kt').read_text(encoding='utf-8'),
                   'val readyTurn: Int = 0, val postponed: Boolean = false',
                   'val readyTurn: Int = 0, val postponed: Boolean = false, val spyBound: Boolean = false')
    install(civ / 'MagalanaduAgencyData.kt', data)
    install(civ / 'MagalanaduAgency.kt', native_agency())
    install(screen / 'MagalanaduSpyMenu.kt', (SOURCE / 'MagalanaduSpyMenu.kt').read_text(encoding='utf-8'))

    # Keep the upstream private setter attached to gold.
    once(civ / 'Civilization.kt',
         '    var gold = 0\n        private set\n',
         '    var gold = 0\n        private set\n\n'
         '    var magalanaduAgency: MagalanaduAgencyData? = null\n')
    once(civ / 'Civilization.kt',
         '        toReturn.gold = gold\n',
         '        toReturn.gold = gold\n        toReturn.magalanaduAgency = magalanaduAgency?.copy()\n')
    anchor = '        com.unciv.logic.civilization.MagalanaduDefenseObjective.checkTurn(player)\n'
    once(engine / 'logic/GameInfo.kt', anchor, anchor + f'        {AGENCY}.processTurn(player)\n')

    once(spy, '    private var progressTowardsStealingTech = 0\n',
         '    private var progressTowardsStealingTech = 0\n    internal var magalanaduOperationSerial: Int? = null\n')
    once(spy, '        toReturn.progressTowardsStealingTech = progressTowardsStealingTech\n',
         '        toReturn.progressTowardsStealingTech = progressTowardsStealingTech\n'
         '        toReturn.magalanaduOperationSerial = magalanaduOperationSerial\n')
    once(spy, '    fun endTurn() {\n',
         '    fun endTurn() {\n'
         f'        if (magalanaduOperationSerial != null && {AGENCY}.activeOperation(this) != null) return\n')
    once(spy, '    fun moveTo(city: City?) {\n',
         '    fun moveTo(city: City?) {\n        magalanaduOperationSerial = null\n')

    espionage = screen / 'EspionageScreen.kt'
    once(espionage, '        initSpyHeader()\n',
         f'''        if ({AGENCY}.canRecruit(civInfo) && worldScreen.canChangeState) {{
            val recruit = "Recruit spy".toTextButton()
            recruit.onClick {{
                if (worldScreen.canChangeState && {AGENCY}.canRecruit(civInfo)) {{
                    manager.addSpy()
                    resetSelection()
                    update()
                }}
            }}
            spySelectionTable.add(recruit).colspan(4).left()
            val reports = "Spy reports".toTextButton()
            reports.onClick {{ {MENU}.showReports(this) }}
            spySelectionTable.add(reports).colspan(3).left().row()
        }}
        initSpyHeader()
''')
    once(espionage, '        val actionString = if (spy.action.showTurns)\n',
         f'''        val operation = {AGENCY}.activeOperation(spy)
        val actionString = if (operation != null)
            "${{operation.mission()?.title ?: "Operation"}} (${{(operation.readyTurn - civInfo.gameInfo.turns).coerceAtLeast(0)}})"
        else if (spy.action.showTurns)
''')
    once(espionage, '        spySelectionTable.add(moveSpyButton).minWidth(moveButtonWidth).row()\n',
         f'''        spySelectionTable.add(moveSpyButton).minWidth(moveButtonWidth)
        if (worldScreen.canChangeState && {AGENCY}.isReady(civInfo, spy)) {{
            val operations = (if (operation == null) "Operations" else "Manage operation").toTextButton()
            operations.onClick {{ {MENU}.open(this, spy, ::update) }}
            spySelectionTable.add(operations).padLeft(4f)
        }}
        spySelectionTable.row()
''')
    once(espionage, '            selectedSpy!!.moveTo(location)\n',
         f'''            val spy = selectedSpy!!
            {AGENCY}.activeOperation(spy)?.let {{ {AGENCY}.abort(civInfo, it.serial) }}
            spy.moveTo(location)
''')
    once(espionage, 'spy != null && spy.canDoCoup()) {',
         f'spy != null && spy.canDoCoup() && {AGENCY}.activeOperation(spy) == null) {{')
    anchor = '        popup.addButton("PROXY WAR: A declares war on B") {'
    once(popups / 'MagalanaduDirectorate.kt', anchor,
         f'''        if ({AGENCY}.canRecruit(user)) {{
            popup.addButton("ESPIONAGE: open native spy screen") {{
                popup.close()
                val world = GUI.getWorldScreen()
                world.game.pushScreen {{ com.unciv.ui.screens.espionage.EspionageScreen(user, world) }}
            }}.row()
        }}
''' + anchor)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_9.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
