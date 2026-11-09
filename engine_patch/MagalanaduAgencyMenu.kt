package com.unciv.ui.popups

import com.unciv.GUI
import com.unciv.logic.city.City
import com.unciv.logic.civilization.AgencyGroup
import com.unciv.logic.civilization.AgencyMission
import com.unciv.logic.civilization.AgencyTarget
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.MagalanaduAgency as Agency
import com.unciv.logic.civilization.MagalanaduSecession

object MagalanaduAgencyMenu {
    fun open(player: Civilization) {
        val popup = menu("INTELLIGENCE AGENCY")
        val active = player.magalanaduAgency?.operations?.size ?: 0
        popup.addGoodSizedLabel("$active / ${Agency.Slots} active operations. ${player.gold} Gold available.").row()
        button(popup, "Active operations") { showActive(player) }
        button(popup, "Network dossiers") { showNetworks(player) }
        button(popup, "Operation reports") { showReports(player) }
        for (group in AgencyGroup.entries)
            button(popup, group.title) { selectMission(player, group) }
        show(popup)
    }

    private fun selectMission(player: Civilization, group: AgencyGroup) {
        val popup = menu(group.title)
        for (mission in AgencyMission.entries.filter { it.group == group }) {
            button(popup, mission.title) { selectTarget(player, mission) }
        }
        button(popup, "Back to Agency") { open(player) }
        show(popup)
    }

    private fun selectTarget(player: Civilization, mission: AgencyMission) {
        val popup = menu(mission.title)
        popup.addGoodSizedLabel(mission.effect).row()
        popup.addGoodSizedLabel("Requires ${mission.access} access and ${mission.leverage} leverage.").row()
        val targets = Agency.targets(player).filter { target ->
            when {
                mission.target == AgencyTarget.Pair -> Agency.partners(player, target).isNotEmpty()
                mission == AgencyMission.Coup || mission == AgencyMission.Unrest || mission == AgencyMission.Secession ->
                    target.isMajorCiv && target.cities.isNotEmpty()
                mission.target == AgencyTarget.City -> target.cities.isNotEmpty()
                else -> true
            }
        }
        if (targets.isEmpty()) popup.addGoodSizedLabel("No known civilization can be selected.").row()
        for (target in targets) {
            val net = Agency.network(player, target)
            button(popup, "${target.civName}  |  Access ${net.access}  Leverage ${net.leverage}  Heat ${net.heat}") {
                when (mission.target) {
                    AgencyTarget.Country -> confirm(player, mission, target)
                    AgencyTarget.City, AgencyTarget.Secession -> selectCity(player, mission, target)
                    AgencyTarget.Pair -> selectPartner(player, mission, target)
                }
            }
        }
        button(popup, "Back to missions") { selectMission(player, mission.group) }
        show(popup)
    }

    private fun selectCity(player: Civilization, mission: AgencyMission, target: Civilization) {
        val popup = menu("Choose a city in ${target.civName}")
        val cities = target.cities.filter {
            when (mission) {
                AgencyMission.Coup -> !it.isCapital() && it.isInResistance()
                AgencyMission.Secession -> MagalanaduSecession.canSecede(target, it)
                else -> true
            }
        }.sortedBy { it.name }
        if (cities.isEmpty()) popup.addGoodSizedLabel("No eligible city. Coup and secession require an eligible city in resistance.").row()
        for (city in cities) {
            button(popup, city.name) {
                if (mission.target == AgencyTarget.Secession) selectNation(player, mission, target, city)
                else confirm(player, mission, target, city)
            }
        }
        button(popup, "Back to targets") { selectTarget(player, mission) }
        show(popup)
    }

    private fun selectPartner(player: Civilization, mission: AgencyMission, target: Civilization) {
        val popup = menu("Choose the second civilization")
        for (other in Agency.partners(player, target))
            button(popup, other.civName) { confirm(player, mission, target, secondary = other.civID, secondaryName = other.civName) }
        button(popup, "Back to targets") { selectTarget(player, mission) }
        show(popup)
    }

    private fun selectNation(player: Civilization, mission: AgencyMission, target: Civilization, city: City) {
        val popup = menu("Choose a breakaway identity")
        val nations = Agency.eligibleNations(player)
        if (nations.isEmpty()) popup.addGoodSizedLabel("No unused nation identities remain.").row()
        for (nation in nations) {
            val type = if (nation.isCityState) "City-State" else "major civilization"
            button(popup, "${nation.name} ($type)") {
                confirm(player, mission, target, city, nation.name, nation.name)
            }
        }
        button(popup, "Back to cities") { selectCity(player, mission, target) }
        show(popup)
    }

    private fun confirm(
        player: Civilization, mission: AgencyMission, target: Civilization, city: City? = null,
        secondary: String = "", secondaryName: String = ""
    ) {
        val popup = menu(mission.title)
        val net = Agency.network(player, target)
        val names = listOf(target.civName, city?.name.orEmpty(), secondaryName).filter { it.isNotBlank() }
        popup.addGoodSizedLabel(names.joinToString(" / ")).row()
        popup.addGoodSizedLabel(mission.effect).row()
        popup.addGoodSizedLabel("Estimates use current network strength. Gold is spent when you launch.").row()
        for (careful in listOf(false, true)) {
            val name = if (careful) "Careful" else "Standard"
            val label = "$name  |  ${Agency.cost(mission, careful)} Gold  |  ${Agency.duration(mission, careful)} turns\n" +
                "${Agency.chance(mission, net, careful)}% success  |  ${Agency.exposure(mission, net, careful)}% exposure"
            button(popup, label) {
                val screen = GUI.getWorldScreen()
                val error = if (!screen.canChangeState) "Wait for your turn."
                    else Agency.queue(player, mission, target, city, secondary, careful)
                screen.shouldUpdate = true
                val result = menu(error ?: "Operation queued")
                button(result, "Back to Agency") { open(player) }
                show(result)
            }
        }
        button(popup, "Back to targets") { selectTarget(player, mission) }
        show(popup)
    }

    private fun showActive(player: Civilization) {
        val popup = menu("ACTIVE OPERATIONS")
        val data = player.magalanaduAgency
        if (data == null || data.operations.isEmpty()) popup.addGoodSizedLabel("No active operations.").row()
        for (op in data?.operations.orEmpty()) {
            val target = player.gameInfo.getCivilizationOrNull(op.civId)?.civName ?: op.civId
            val turns = (op.readyTurn - player.gameInfo.turns).coerceAtLeast(0)
            val name = op.mission()?.title ?: op.missionId
            button(popup, "$name  |  $target  |  $turns turns left") {
                val detail = menu(name)
                detail.addGoodSizedLabel("$target. Ready in $turns turns.").row()
                if (!op.postponed) {
                    button(detail, "Lay low (delay 2 turns, reduce heat by up to 15)") {
                        if (GUI.getWorldScreen().canChangeState) Agency.layLow(player, op.serial)
                        showActive(player)
                    }
                }
                button(detail, "Abort operation (Gold already spent)") {
                    if (GUI.getWorldScreen().canChangeState) Agency.abort(player, op.serial)
                    showActive(player)
                }
                button(detail, "Back") { showActive(player) }
                show(detail)
            }
        }
        button(popup, "Back to Agency") { open(player) }
        show(popup)
    }

    private fun showNetworks(player: Civilization) {
        val popup = menu("NETWORK DOSSIERS")
        for (target in Agency.targets(player)) {
            val net = Agency.network(player, target)
            val facilities = listOfNotNull(
                "station".takeIf { net.station }, "route".takeIf { net.route }, "captive".takeIf { net.captive }
            ).joinToString()
            popup.addGoodSizedLabel("${target.civName}\nAccess ${net.access}  Cover ${net.cover}  Heat ${net.heat}  Leverage ${net.leverage}" +
                if (facilities.isEmpty()) "" else "\n$facilities").row()
        }
        button(popup, "Back to Agency") { open(player) }
        show(popup)
    }

    private fun showReports(player: Civilization) {
        val popup = menu("OPERATION REPORTS")
        val reports = player.magalanaduAgency?.reports.orEmpty()
        if (reports.isEmpty()) popup.addGoodSizedLabel("No reports yet.").row()
        for (report in reports) popup.addGoodSizedLabel(report).row()
        button(popup, "Back to Agency") { open(player) }
        show(popup)
    }

    private fun menu(title: String) = Popup(GUI.getWorldScreen(), Popup.Scrollability.All).also {
        it.addGoodSizedLabel(title).row()
    }

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
