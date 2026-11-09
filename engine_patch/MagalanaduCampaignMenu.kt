package com.unciv.ui.popups

import com.unciv.GUI
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.MagalanaduDefenseObjective as Defense
import com.unciv.logic.civilization.MagalanaduDefenseObjective.Status

object MagalanaduCampaignMenu {
    fun open(player: Civilization) {
        val popup = menu("CAMPAIGN OBJECTIVES")
        val objective = player.magalanaduDefenseObjective
        if (objective != null) {
            popup.addGoodSizedLabel("Defend ${objective.cityName} (${objective.defenderName}) against ${objective.rivalName}.").row()
            val status = when (objective.status) {
                Status.Active -> "${(objective.deadline - player.gameInfo.turns).coerceAtLeast(0)} turns remaining. Reward: ${Defense.Reward} Gold."
                Status.Succeeded -> "Completed. ${Defense.Reward} Gold awarded."
                Status.CityLost -> "Failed. The defender lost the city."
                Status.NeutralityBroken -> "Failed. Magalanadu went to war with one of the participants."
                Status.Cancelled -> "Cancelled."
            }
            popup.addGoodSizedLabel(status).row()
        }

        if (objective?.status == Status.Active) {
            popup.addButton("Cancel objective") {
                popup.close()
                val confirmation = menu("Cancel this objective?")
                confirmation.addButton("Confirm cancellation") {
                    Defense.cancel(player)
                    confirmation.close()
                    open(player)
                }.row()
                confirmation.addButton("Back") {
                    confirmation.close()
                    open(player)
                }.row()
                show(confirmation)
            }.row()
        } else {
            popup.addGoodSizedLabel("Keep a foreign city under its current owner for ${Defense.Duration} turns. Stay at peace with the defender and its chosen rival. You may send aid, and the objective continues if they make peace.").row()
            popup.addButton("Start a city-defense objective") {
                popup.close()
                selectDefender(player)
            }.row()
        }
        show(popup)
    }

    private fun selectDefender(player: Civilization) {
        val popup = menu("Choose the civilization to defend")
        val known = player.getKnownCivs().sortedBy { it.civName }.toList()
        val choices = known.map { defender ->
            defender to known.filter { rival -> Defense.canStart(player, defender, rival) }
        }.filter { (defender, rivals) -> defender.cities.isNotEmpty() && rivals.isNotEmpty() }
        if (choices.isEmpty())
            popup.addGoodSizedLabel("No eligible war. Meet two major civilizations at war with each other while at peace with both.").row()
        for ((defender, rivals) in choices) {
            popup.addButton(defender.civName) {
                popup.close()
                selectRival(player, defender, rivals)
            }.row()
        }
        show(popup)
    }

    private fun selectRival(player: Civilization, defender: Civilization, rivals: List<Civilization>) {
        val popup = menu("Choose the rival of ${defender.civName}")
        for (rival in rivals) {
            popup.addButton(rival.civName) {
                popup.close()
                selectCity(player, defender, rival)
            }.row()
        }
        show(popup)
    }

    private fun selectCity(player: Civilization, defender: Civilization, rival: Civilization) {
        val popup = menu("Choose a city to defend against ${rival.civName}")
        for (city in defender.cities.sortedBy { it.name }) {
            popup.addButton(city.name) {
                popup.close()
                val confirmation = menu("Defend ${city.name} for ${Defense.Duration} turns?")
                confirmation.addGoodSizedLabel("Keep the city under ${defender.civName} and stay at peace with both participants. Reward: ${Defense.Reward} Gold.").row()
                confirmation.addButton("Start objective") {
                    confirmation.close()
                    if (Defense.start(player, defender, rival, city)) open(player)
                    else show(menu("This city or war is no longer eligible."))
                }.row()
                show(confirmation)
            }.row()
        }
        show(popup)
    }

    private fun menu(title: String) = Popup(GUI.getWorldScreen(), Popup.Scrollability.All).also {
        it.addGoodSizedLabel(title).row()
    }

    private fun show(popup: Popup) {
        popup.addCloseButton().row()
        popup.open()
    }
}
