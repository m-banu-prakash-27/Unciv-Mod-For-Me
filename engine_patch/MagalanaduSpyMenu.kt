package com.unciv.ui.screens.espionage

import com.unciv.logic.civilization.AgencyGroup
import com.unciv.logic.civilization.AgencyMission
import com.unciv.logic.civilization.AgencyTarget
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.MagalanaduAgency as Agency
import com.unciv.logic.civilization.MagalanaduSecession
import com.unciv.models.Spy
import com.unciv.ui.popups.Popup

object MagalanaduSpyMenu {
    fun open(screen: EspionageScreen, spy: Spy, refresh: () -> Unit) {
        val player = screen.civInfo
        val city = spy.getCityOrNull() ?: return
        if (!screen.worldScreen.canChangeState || !Agency.isReady(player, spy)) return
        val operation = Agency.activeOperation(spy)
        val popup = menu(screen, "${spy.name} in ${city.name}")
        if (operation != null) {
            val target = player.gameInfo.getCivilizationOrNull(operation.civId)?.civName ?: operation.civId
            val turns = (operation.readyTurn - player.gameInfo.turns).coerceAtLeast(0)
            popup.addGoodSizedLabel("${operation.mission()?.title ?: "Operation"} against $target. $turns turns remaining.").row()
            popup.addGoodSizedLabel("Reassigning this spy cancels the mission. Funding was paid at launch.").row()
            if (!operation.postponed) {
                button(popup, "Lay low (+2 turns, -15 heat)") {
                    if (screen.worldScreen.canChangeState) Agency.layLow(player, operation.serial)
                    refresh()
                }
            }
            button(popup, "Abort mission") {
                if (screen.worldScreen.canChangeState) Agency.abort(player, operation.serial)
                refresh()
            }
        } else {
            val domestic = city.civ == player
            if (!domestic) {
                val network = Agency.network(player, city.civ)
                popup.addGoodSizedLabel("Access ${network.access}  |  Cover ${network.cover}  |  Leverage ${network.leverage}  |  Heat ${network.heat}").row()
            }
            for (group in AgencyGroup.entries) {
                val missions = AgencyMission.entries.filter { it.group == group && Agency.isDomestic(it) == domestic }
                if (missions.isNotEmpty())
                    button(popup, group.title) { selectMission(screen, spy, group, missions, refresh) }
            }
        }
        show(popup)
    }

    private fun selectMission(
        screen: EspionageScreen, spy: Spy, group: AgencyGroup, missions: List<AgencyMission>, refresh: () -> Unit
    ) {
        val popup = menu(screen, group.title)
        val city = spy.getCityOrNull() ?: return
        val player = screen.civInfo
        for (mission in missions) {
            button(popup, mission.title) {
                if (Agency.isDomestic(mission)) {
                    val targets = Agency.targets(player).filter {
                        mission !in listOf(AgencyMission.Interrogate, AgencyMission.TurnAgent) || Agency.network(player, it).captive
                    }
                    choose(screen, spy, mission, "Choose rival", targets.map { it.civName to it.civID }, refresh) { id, _ ->
                        val target = player.gameInfo.getCivilizationOrNull(id)
                        if (target != null) confirm(screen, spy, mission, target, refresh)
                    }
                } else when (mission.target) {
                    AgencyTarget.Pair -> {
                        val partners = Agency.partners(player, city.civ)
                        choose(screen, spy, mission, "Choose the second civilization",
                            partners.map { it.civName to it.civID }, refresh) { id, name ->
                            confirm(screen, spy, mission, city.civ, refresh, id, name)
                        }
                    }
                    AgencyTarget.Secession -> {
                        val choices = if (MagalanaduSecession.canSecede(city.civ, city))
                            Agency.eligibleNations(player).map {
                                val type = if (it.isCityState) "City-State" else "major civilization"
                                "${it.name} ($type)" to it.name
                            } else emptyList()
                        choose(screen, spy, mission, "Choose a breakaway identity", choices, refresh) { id, name ->
                            confirm(screen, spy, mission, city.civ, refresh, id, name)
                        }
                    }
                    else -> confirm(screen, spy, mission, city.civ, refresh)
                }
            }
        }
        button(popup, "Back to operations") { open(screen, spy, refresh) }
        show(popup)
    }

    private fun choose(
        screen: EspionageScreen, spy: Spy, mission: AgencyMission, title: String,
        choices: List<Pair<String, String>>, refresh: () -> Unit, onChoice: (String, String) -> Unit
    ) {
        val popup = menu(screen, title)
        popup.addGoodSizedLabel(mission.effect).row()
        if (choices.isEmpty()) popup.addGoodSizedLabel("No eligible target at this posting.").row()
        for ((name, id) in choices)
            button(popup, name) { onChoice(id, name) }
        button(popup, "Back to operations") { open(screen, spy, refresh) }
        show(popup)
    }

    private fun confirm(
        screen: EspionageScreen, spy: Spy, mission: AgencyMission, target: Civilization,
        refresh: () -> Unit, secondary: String = "", secondaryName: String = ""
    ) {
        val popup = menu(screen, mission.title)
        val net = Agency.network(screen.civInfo, target)
        val location = spy.getCityOrNull() ?: return
        val parties = listOf(location.name, target.civName, secondaryName).filter { it.isNotBlank() }
        popup.addGoodSizedLabel("${spy.name}  |  ${parties.joinToString(" / ")}").row()
        popup.addGoodSizedLabel(mission.effect).row()
        popup.addGoodSizedLabel("Requires ${mission.access} access and ${mission.leverage} leverage.").row()
        for (careful in listOf(false, true)) {
            val style = if (careful) "Careful" else "Standard"
            val price = Agency.cost(mission, careful)
            val time = Agency.duration(mission, careful)
            val chance = Agency.operativeChance(mission, net, careful, spy)
            val exposure = Agency.exposure(mission, net, careful)
            button(popup, "$style  |  $price Gold  |  $time turns\n$chance% success  |  $exposure% exposure") {
                val error = if (screen.worldScreen.canChangeState)
                    Agency.queue(screen.civInfo, spy, mission, target, secondary, careful)
                else "Wait for your turn."
                refresh()
                if (error != null) {
                    val message = menu(screen, error)
                    button(message, "Back to operations") { open(screen, spy, refresh) }
                    show(message)
                }
            }
        }
        button(popup, "Back to operations") { open(screen, spy, refresh) }
        show(popup)
    }

    fun showReports(screen: EspionageScreen) {
        val popup = menu(screen, "SPY REPORTS")
        val reports = screen.civInfo.magalanaduAgency?.reports.orEmpty()
        if (reports.isEmpty()) popup.addGoodSizedLabel("No special operation reports yet.").row()
        for (report in reports) popup.addGoodSizedLabel(report).row()
        show(popup)
    }

    private fun menu(screen: EspionageScreen, title: String) =
        Popup(screen, Popup.Scrollability.All).also { it.addGoodSizedLabel(title).row() }

    private fun button(popup: Popup, label: String, action: () -> Unit) {
        popup.addButton(label) {
            popup.close()
            action()
        }.row()
    }

    private fun show(popup: Popup) {
        popup.addCloseButton().row()
        popup.open()
    }
}
