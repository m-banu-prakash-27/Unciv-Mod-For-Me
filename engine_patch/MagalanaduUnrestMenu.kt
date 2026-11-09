package com.unciv.ui.popups

import com.unciv.GUI
import com.unciv.logic.city.City
import com.unciv.logic.city.CityFlags
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.civilization.MagalanaduSecession

object MagalanaduUnrestMenu {
    fun open(player: Civilization) {
        val popup = menu("UNREST AND SECESSION")
        popup.addGoodSizedLabel("Incite resistance in a foreign civilization. Cities in resistance can break away as independent nations.").row()
        val targets = player.getKnownCivs().filter { MagalanaduSecession.canTarget(player, it) }
            .sortedBy { it.civName }.toList()
        if (targets.isEmpty()) popup.addGoodSizedLabel("Meet a foreign major civilization that owns at least one city.").row()
        for (target in targets)
            button(popup, target.civName) { showCities(player, target) }
        show(popup)
    }

    private fun showCities(player: Civilization, parent: Civilization) {
        val popup = menu(parent.civName)
        popup.addGoodSizedLabel("Original capitals and the last city of a civilization are protected from secession.").row()
        button(popup, "Foment unrest in all ${parent.cities.size} cities") {
            confirmUnrest(player, parent, parent.cities.toList())
        }
        for (city in parent.cities.sortedBy { it.name }) {
            val status = if (city.isInResistance()) " (${city.getFlag(CityFlags.Resistance)} resistance turns)" else ""
            button(popup, city.name + status) { showCity(player, parent, city) }
        }
        button(popup, "Back") { open(player) }
        show(popup)
    }

    private fun showCity(player: Civilization, parent: Civilization, city: City) {
        val popup = menu("${city.name} (${parent.civName})")
        button(popup, "Foment unrest in ${city.name}") { confirmUnrest(player, parent, listOf(city)) }
        if (MagalanaduSecession.canSecede(parent, city)) {
            button(popup, "Create an independent major civilization") { chooseNation(player, parent, city, false) }
            button(popup, "Create an independent City-State") { chooseNation(player, parent, city, true) }
        } else {
            val reason = if (city.isOriginalCapital || parent.cities.size <= 1)
                "This city is protected from secession."
            else "The city must be in resistance before it can secede."
            popup.addGoodSizedLabel(reason).row()
        }
        button(popup, "Back") { showCities(player, parent) }
        show(popup)
    }

    private fun confirmUnrest(player: Civilization, parent: Civilization, cities: List<City>) {
        val popup = menu("Start resistance in ${cities.size} ${if (cities.size == 1) "city" else "cities"}?")
        popup.addGoodSizedLabel("Affected cities will enter resistance for at least ${MagalanaduSecession.ResistanceTurns} turns.").row()
        button(popup, "Confirm unrest") {
            val screen = GUI.getWorldScreen()
            val affected = if (screen.canChangeState) MagalanaduSecession.foment(player, parent, cities) else 0
            screen.shouldUpdate = true
            val result = if (affected > 0) "Unrest started in $affected of ${parent.civName}'s cities."
                else "Unrest could not be started. Check that the cities still belong to ${parent.civName}."
            showResult(player, parent, result)
        }
        button(popup, "Back") { showCities(player, parent) }
        show(popup)
    }

    private fun chooseNation(player: Civilization, parent: Civilization, city: City, asCityState: Boolean) {
        val kind = if (asCityState) "City-State" else "major civilization"
        val popup = menu("Choose an unused $kind for ${city.name}")
        val nations = MagalanaduSecession.availableNations(player, asCityState)
        if (nations.isEmpty())
            popup.addGoodSizedLabel("Every eligible $kind in this ruleset is already in use.").row()
        for (nation in nations) {
            button(popup, nation.name) {
                val confirmation = menu("Make ${city.name} independent as ${nation.name}?")
                confirmation.addGoodSizedLabel("The city and its territory will transfer to a new AI-controlled $kind. It starts at peace with Magalanadu and its former owner.").row()
                button(confirmation, "Confirm secession") {
                    val screen = GUI.getWorldScreen()
                    val success = screen.canChangeState && MagalanaduSecession.secede(player, parent, city, nation, asCityState)
                    screen.shouldUpdate = true
                    val result = if (success) "${city.name} is now independent as ${nation.name}."
                        else "The city or chosen nation is no longer eligible."
                    showResult(player, parent, result)
                }
                button(confirmation, "Back") { chooseNation(player, parent, city, asCityState) }
                show(confirmation)
            }
        }
        button(popup, "Back") { showCity(player, parent, city) }
        show(popup)
    }

    private fun showResult(player: Civilization, parent: Civilization, text: String) {
        val popup = menu(text)
        button(popup, "Back to ${parent.civName}") { showCities(player, parent) }
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
