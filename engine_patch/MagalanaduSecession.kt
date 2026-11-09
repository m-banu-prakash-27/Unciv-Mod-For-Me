package com.unciv.logic.civilization

import com.unciv.logic.city.City
import com.unciv.logic.city.CityFlags
import com.unciv.models.ruleset.nation.Nation
import kotlin.random.Random

/** Foreign city operations use the same resistance and ownership data as the base game. */
object MagalanaduSecession {
    const val ResistanceTurns = 8

    fun canTarget(player: Civilization, parent: Civilization): Boolean =
        player.civName == "Magalanadu" && player.isHuman() && player.isCurrentPlayer()
            && !player.isDefeated() && !player.gameInfo.gameParameters.isOnlineMultiplayer
            && parent != player && parent.isMajorCiv && !parent.isDefeated()
            && player.knows(parent) && parent.cities.isNotEmpty()

    fun foment(player: Civilization, parent: Civilization, cities: List<City>): Int {
        if (!canTarget(player, parent)) return 0
        val affected = cities.distinct().filter { it in parent.cities }
        for (city in affected) {
            val previous = if (city.isInResistance()) city.getFlag(CityFlags.Resistance) else 0
            city.setFlag(CityFlags.Resistance, maxOf(previous, ResistanceTurns))
            city.cityStats.update()
            parent.addNotification(
                "Unrest has erupted in [${city.name}].",
                city.location, NotificationCategory.Cities
            )
        }
        parent.updateStatsForNextTurn()
        return affected.size
    }

    fun canSecede(parent: Civilization, city: City): Boolean =
        parent.cities.size > 1 && city in parent.cities && city.isInResistance() && !city.isOriginalCapital

    fun availableNations(player: Civilization, asCityState: Boolean): List<Nation> {
        val game = player.gameInfo
        val usedNames = game.civilizations.map { it.civName }.toSet()
        val usedIds = game.civilizations.map { it.civID }.toSet()
        return game.ruleset.nations.values.filter { nation ->
            val eligibleType = if (asCityState)
                nation.cityStateType?.let { it in game.ruleset.cityStateTypes } == true
            else nation.isMajorCiv
            eligibleType && nation.name !in usedNames && nation.name !in usedIds
        }.sortedBy { it.name }
    }

    fun secede(
        player: Civilization, parent: Civilization, city: City, nation: Nation, asCityState: Boolean
    ): Boolean {
        if (!canTarget(player, parent) || !canSecede(parent, city) ||
            nation !in availableNations(player, asCityState)) return false

        val game = player.gameInfo
        val breakaway = Civilization(nation)
        breakaway.gameInfo = game
        if (asCityState && !breakaway.cityStateFunctions.initCityState(
                game.ruleset, game.gameParameters.startingEra,
                game.civilizations.asSequence().filter { it.isMajorCiv }.map { it.nation },
                Random(city.id.hashCode() xor game.turns)
            )) return false

        // Copy completed technologies only. Research, troops, trades and alliances belong to the parent.
        breakaway.tech.techsResearched.addAll(parent.tech.techsResearched.filter { it in game.ruleset.technologies })
        breakaway.hasEverOwnedOriginalCapital = true
        breakaway.citiesCreated = 1
        breakaway.cache.updateState()
        breakaway.setTransients()
        game.registerMagalanaduBreakaway(breakaway)

        // Native ownership transfer moves the city, its tiles and eligible buildings, and assigns the palace.
        city.moveToCiv(breakaway)
        city.foundingCivObject = breakaway
        city.isOriginalCapital = true
        city.isPuppet = false
        city.removeFlag(CityFlags.Resistance)
        city.reassignAllPopulation()
        city.cityConstructions.removeAll()
        city.cityStats.update()

        for (contact in listOf(player, parent))
            if (!breakaway.knows(contact)) breakaway.diplomacyFunctions.makeCivilizationsMeet(contact)

        val center = city.getCenterTile()
        for (unit in center.getUnits().toList())
            if (unit.civ != breakaway) unit.movement.teleportToClosestMoveableTile()
        for (unit in city.getTiles().flatMap { it.getUnits() }.toList())
            if (!unit.movement.canPassThrough(unit.currentTile))
                unit.movement.teleportToClosestMoveableTile()

        for (civ in listOf(parent, breakaway)) {
            civ.cache.updateCitiesConnectedToCapital()
            civ.updateStatsForNextTurn()
        }
        val message = "[${city.name}] has seceded from [${parent.civName}] and formed [${breakaway.civName}]."
        player.addNotification(message, city.location, NotificationCategory.Diplomacy)
        parent.addNotification(message, city.location, NotificationCategory.Diplomacy)
        return true
    }
}
