package com.unciv.ui.popups

import com.unciv.GUI
import com.unciv.logic.city.City
import com.unciv.logic.civilization.Civilization
import com.unciv.logic.map.HexCoord
import com.unciv.logic.map.tile.Tile
import com.unciv.models.ruleset.unit.BaseUnit

/**
 * Magalanadu military logistics for Unciv 4.22.16.
 * Permanent assignment is stored on City.magalanaduDepotPosition, so it survives saves.
 * Ordinary production still uses UnitManager's normal placement and gain-unit triggers.
 */
object MagalanaduLogistics {
    private const val CIV = "Magalanadu"
    private const val BUILDING = "Magalanadu Armament Depot"
    private const val IMPROVEMENT = "Arms Depot"
    private const val PAGE_SIZE = 12

    /** Used by the standard unit-construction pipeline. No permanent global state. */
    fun productionSpawnPosition(city: City, baseUnit: BaseUnit): HexCoord? {
        if (city.civ.civName != CIV) return null
        // A naval unit should remain at its originating coastal city. The stock
        // placement algorithm handles a nearby legal water tile from there.
        if (baseUnit.isWaterUnit) return city.location
        return getAssignedOrDefaultDepot(city)?.position
    }

    private fun isDepotImprovement(tile: Tile, city: City): Boolean =
        tile.getCity() == city && tile.improvement == IMPROVEMENT && !tile.improvementIsPillaged

    private fun hasDepotBuilding(city: City): Boolean =
        BUILDING in city.cityConstructions.builtBuildings

    private fun getSites(city: City): List<Tile> {
        val sites = city.getTiles().filter { isDepotImprovement(it, city) }.toMutableList()
        if (hasDepotBuilding(city) && sites.none { it == city.getCenterTile() })
            sites.add(0, city.getCenterTile())
        return sites.sortedBy { it.getCenterTileDistance(city) }
    }

    private fun Tile.getCenterTileDistance(city: City): Int =
        aerialDistanceTo(city.getCenterTile())

    private fun getAssignedOrDefaultDepot(city: City): Tile? {
        val sites = getSites(city)
        val selected = city.magalanaduDepotPosition
        return if (selected == null) sites.firstOrNull()
        else sites.firstOrNull { it.position == selected } ?: sites.firstOrNull()
    }

    private fun popup(title: String): Popup =
        Popup(GUI.getWorldScreen(), Popup.Scrollability.All).also {
            it.addGoodSizedLabel(title).row()
        }

    private fun notice(message: String) {
        val dialog = popup("MAGALANADU MILITARY LOGISTICS")
        dialog.addGoodSizedLabel(message).row()
        dialog.addCloseButton().row()
        dialog.open()
    }

    fun open(user: Civilization) {
        if (user.civName != CIV || !user.isCurrentPlayer()) return
        val dialog = popup("ARMAMENT DEPOTS AND GLOBAL DEPLOYMENT")
        dialog.addGoodSizedLabel(
            "Choose a city and depot. The city building supports spawning at the city; an Arms Depot improvement supports spawning at its tile. Built units use the assigned depot."
        ).row()
        if (user.cities.isEmpty()) dialog.addGoodSizedLabel("No cities available.").row()
        for (city in user.cities.sortedBy { it.name }) {
            val sites = getSites(city)
            dialog.addButton("${city.name}: ${sites.size} active depot(s)") {
                dialog.close()
                showCity(user, city)
            }.row()
        }
        dialog.addCloseButton().row()
        dialog.open()
    }

    private fun showCity(user: Civilization, city: City) {
        val dialog = popup("DEPOT CONTROL: ${city.name}")
        if (city.civ != user) {
            dialog.addGoodSizedLabel("City no longer belongs to Magalanadu.").row()
        } else {
            val sites = getSites(city)
            val assigned = getAssignedOrDefaultDepot(city)
            dialog.addGoodSizedLabel(
                "Active depots: ${sites.size}. Current production destination: ${assigned?.position ?: "None"}."
            ).row()
            if (sites.isEmpty()) {
                dialog.addGoodSizedLabel(
                    "Build Magalanadu Armament Depot in the city, or construct an Arms Depot improvement on a tile belonging to this city."
                ).row()
            }
            for (site in sites) {
                val desc = if (site == city.getCenterTile()) "CITY ARMAMENT DEPOT" else "ARMS DEPOT"
                dialog.addButton("SELECT $desc at ${site.position}") {
                    city.magalanaduDepotPosition = site.position
                    dialog.close()
                    showDepot(user, city, site)
                }.row()
            }
        }
        dialog.addCloseButton().row()
        dialog.open()
    }

    private fun showDepot(user: Civilization, city: City, site: Tile) {
        if (city.civ != user || site !in getSites(city)) {
            notice("This depot is no longer available. Select an active depot.")
            return
        }
        val dialog = popup("DEPOT: ${city.name}, ${site.position}")
        dialog.addGoodSizedLabel(
            "Units produced by ${city.name} will now start here if placement is legal. Choose instant deployment to create units immediately at or near this depot."
        ).row()
        for (category in listOf("Land military", "Naval military", "Air", "Civilian", "All units")) {
            dialog.addButton("SPAWN: $category") {
                dialog.close()
                chooseUnit(user, city, site, category, 0)
            }.row()
        }
        dialog.addButton("CHANGE DEPOT") { dialog.close(); showCity(user, city) }.row()
        dialog.addCloseButton().row()
        dialog.open()
    }

    private fun chooseUnit(user: Civilization, city: City, site: Tile, category: String, page: Int) {
        if (city.civ != user || site !in getSites(city)) {
            notice("Depot is no longer valid.")
            return
        }
        val all = user.gameInfo.ruleset.units.values.asSequence()
            .filter { unit -> when (category) {
                "Land military" -> unit.isLandUnit && unit.isMilitary
                "Naval military" -> unit.isWaterUnit && unit.isMilitary
                "Air" -> unit.isAirUnit()
                "Civilian" -> unit.isCivilian()
                else -> true
            } }
            .sortedBy { it.name }.toList()
        val from = (page * PAGE_SIZE).coerceAtMost(all.size)
        val to = (from + PAGE_SIZE).coerceAtMost(all.size)
        val dialog = popup("$category: units ${from + 1}-$to of ${all.size}")
        for (unit in all.subList(from, to)) {
            dialog.addButton(unit.name) {
                dialog.close()
                chooseQuantity(user, city, site, unit, category, page)
            }.row()
        }
        if (page > 0) dialog.addButton("PREVIOUS PAGE") {
            dialog.close(); chooseUnit(user, city, site, category, page - 1)
        }.row()
        if (to < all.size) dialog.addButton("NEXT PAGE") {
            dialog.close(); chooseUnit(user, city, site, category, page + 1)
        }.row()
        dialog.addCloseButton().row()
        dialog.open()
    }

    private fun chooseQuantity(
        user: Civilization, city: City, site: Tile, unit: BaseUnit, category: String, page: Int
    ) {
        val dialog = popup("DEPLOY ${unit.name}")
        dialog.addGoodSizedLabel(
            "Spawn immediately at ${site.position}, or the nearest legal tile. A stacked or impassable depot may force placement on a neighboring tile. No production or Gold is charged."
        ).row()
        for (quantity in listOf(1, 5, 10)) dialog.addButton("SPAWN $quantity") {
            dialog.close()
            val spawned = spawn(user, city, site, unit, quantity)
            notice("${unit.name}: $spawned of $quantity units deployed around ${site.position}. " +
                if (spawned < quantity) "Remaining units could not find legal space." else "Deployment completed.")
        }.row()
        dialog.addButton("BACK TO UNIT LIST") { dialog.close(); chooseUnit(user, city, site, category, page) }.row()
        dialog.addCloseButton().row()
        dialog.open()
    }

    private fun spawn(user: Civilization, city: City, site: Tile, baseUnit: BaseUnit, quantity: Int): Int {
        if (user.civName != CIV || !user.isCurrentPlayer() || city.civ != user || site !in getSites(city)) return 0
        var count = 0
        for (index in 0 until quantity.coerceIn(1, 10)) {
            user.units.placeUnitNearTile(site.position, baseUnit) ?: break
            count++
        }
        // Stock unit placement handles ownership, resource upkeep and starting promotions.
        GUI.getWorldScreen().shouldUpdate = true
        return count
    }
}
