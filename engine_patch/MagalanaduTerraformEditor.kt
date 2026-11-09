package com.unciv.ui.popups

import com.unciv.logic.map.tile.Tile
import com.unciv.logic.map.tile.TileNormalizer
import com.unciv.logic.map.tile.RoadStatus
import com.unciv.models.ruleset.tile.TerrainType
import com.unciv.models.ruleset.tile.ResourceType
import com.unciv.ui.screens.worldscreen.WorldScreen
import com.unciv.view.TileView

/**
 * Magalanadu v4.3 in-game, live tile editor.
 * The edited Tile fields are the normal Unciv serializable game-map fields;
 * no separate sidecar state is needed to preserve edits in saved games.
 * Only the current human Magalanadu player can enter editor mode.
 * Selection is deliberate: the player arms the editor in Strategic Directorate,
 * then taps a map tile. Editing ends only when Stop is selected.
 */
object MagalanaduTerraformEditor {
    private var armedGameId: String? = null

    fun arm(screen: WorldScreen) {
        if (!isAuthorized(screen)) return
        armedGameId = screen.gameInfo.gameId
        notice(screen, "TERRAFORMING ARMED", "Tap an explored tile on the world map to edit it. Each change is saved with the game. Return here to stop editing.")
    }

    fun disarm() { armedGameId = null }

    /** Called from WorldMapHolder.onTileClicked before ordinary movement selection. */
    fun consumeTileClick(screen: WorldScreen, selectedView: TileView): Boolean {
        if (armedGameId == null || armedGameId != screen.gameInfo.gameId) return false
        if (!isAuthorized(screen)) { disarm(); return false }
        if (!screen.isPlayersTurn || screen.isNextTurnUpdateRunning()) {
            notice(screen, "TERRAFORMING", "Wait until your turn is active before editing the map.")
            return true
        }
        val tile = screen.gameInfo.tileMap[selectedView.position()]
        if (!screen.viewingCiv.hasExplored(tile)) {
            notice(screen, "TERRAFORMING", "You can only edit explored tiles. Explore this area first.")
            return true
        }
        openTile(screen, tile)
        return true
    }

    private fun isAuthorized(screen: WorldScreen) =
        screen.viewingCiv.civName == "Magalanadu" && screen.viewingCiv.isCurrentPlayer()
            && !screen.gameInfo.gameParameters.isOnlineMultiplayer

    private fun popup(screen: WorldScreen, heading: String): Popup {
        val p = Popup(screen, Popup.Scrollability.All)
        p.addGoodSizedLabel(heading).row()
        return p
    }

    private fun notice(screen: WorldScreen, title: String, text: String) {
        val p = popup(screen, title)
        p.addGoodSizedLabel(text).row()
        p.addCloseButton().row()
        p.open()
    }

    private fun summary(tile: Tile): String =
        "Tile ${tile.position}: ${tile.baseTerrain}" +
        (if (tile.terrainFeatures.isEmpty()) "" else " + " + tile.terrainFeatures.joinToString()) +
        (tile.resource?.let { " | Resource: $it" +
            (if (tile.tileResource?.resourceType == ResourceType.Strategic) " (deposit ${tile.resourceAmount})" else "") +
            (if (tile.magalanaduTerraformResource == it) " [terraform]" else "") } ?: "") +
        (tile.naturalWonder?.let { " | Wonder: $it" } ?: "") +
        (tile.improvement?.let { " | Improvement: $it" } ?: "")

    private fun openTile(screen: WorldScreen, tile: Tile) {
        if (!isAuthorized(screen)) { disarm(); return }
        val p = popup(screen, "MAGALANADU LIVE TERRAFORMING")
        p.addGoodSizedLabel(summary(tile)).row()
        p.addGoodSizedLabel("Select an attribute to edit. Effects update this tile's real game data, with immediate world-map refresh attempted.").row()
        p.addButton("BASE TERRAIN: land, plains, hills, coast, ocean...") { p.close(); chooseBaseTerrain(screen, tile) }.row()
        p.addButton("FEATURES: forest, jungle, marsh, oasis...") { p.close(); chooseFeature(screen, tile) }.row()
        p.addButton("RESOURCES: strategic, luxury, bonus, quantity") { p.close(); chooseResource(screen, tile) }.row()
        p.addButton("NATURAL WONDERS: place or remove") { p.close(); chooseWonder(screen, tile) }.row()
        p.addButton("IMPROVEMENTS: place or remove") { p.close(); chooseImprovement(screen, tile) }.row()
        p.addButton("RIVERS: set or clear individual borders") { p.close(); chooseRiver(screen, tile) }.row()
        p.addButton("ROADS: none, road, railroad") { p.close(); chooseRoad(screen, tile) }.row()
        p.addButton("STOP TERRAFORMING") {
            p.close()
            disarm()
            notice(screen, "TERRAFORMING OFF", "Ordinary tile selection is restored. Save your game to keep your edits.")
        }.row()
        p.addCloseButton("CLOSE / SELECT ANOTHER TILE").row()
        p.open()
    }

    private fun chooseBaseTerrain(screen: WorldScreen, tile: Tile) {
        val p = popup(screen, "BASE TERRAIN: ${tile.position}")
        p.addGoodSizedLabel("Changing land into water (or an impassable tile) is blocked under cities and units to avoid invalid game states.").row()
        val types = setOf(TerrainType.Land, TerrainType.Water)
        for (t in screen.gameInfo.ruleset.terrains.values.filter { it.type in types }.sortedBy { it.name }) {
            p.addButton(t.name) {
                p.close()
                if ((tile.isCityCenter() || tile.getUnits().any()) && (tile.isWater != (t.type == TerrainType.Water) || t.impassable)) {
                    notice(screen, "NOT CHANGED", "This tile contains a city or unit. Move units and avoid changing city-center terrain into water or impassable terrain.")
                } else apply(screen, tile, "Terrain changed to ${t.name}") {
                    tile.naturalWonder = null
                    tile.setBaseTerrain(t)
                    tile.setTerrainTransients()
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseFeature(screen: WorldScreen, tile: Tile) {
        val p = popup(screen, "TERRAIN FEATURES: ${tile.position}")
        val features = screen.gameInfo.ruleset.terrains.values
            .filter { it.type == TerrainType.TerrainFeature }.sortedBy { it.name }
        p.addButton("REMOVE ALL TERRAIN FEATURES") {
            p.close()
            apply(screen, tile, "All terrain features removed") { tile.removeTerrainFeatures() }
        }.row()
        for (t in features) {
            val existing = t.name in tile.terrainFeatures
            val valid = t.occursOn.isEmpty() || tile.baseTerrain in t.occursOn
            val action = if (existing) "REMOVE" else "ADD"
            p.addButton("$action ${t.name}" + (if (!existing && !valid) " (incompatible)" else "")) {
                p.close()
                if (!existing && !valid) notice(screen, "INCOMPATIBLE FEATURE", "Change the tile's base terrain before adding ${t.name}.")
                else if (!existing && t.impassable && tile.getUnits().any()) notice(screen, "BLOCKED", "Move units before adding impassable terrain.")
                else apply(screen, tile, "$action ${t.name}") {
                    if (existing) tile.removeTerrainFeature(t.name) else tile.addTerrainFeature(t.name)
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseResource(screen: WorldScreen, tile: Tile) {
        val p = popup(screen, "TILE RESOURCES: ${tile.position}")
        p.addGoodSizedLabel("Place ANY resource on ANY terrain, including Coal and Uranium. Custom placement survives saving and reloading. Magalanadu can see and extract its placed resources without the usual technology or improvement; the tile must belong to Magalanadu. Natural wonders cannot share a tile with resources.").row()
        p.addButton("REMOVE RESOURCE") {
            p.close()
            apply(screen, tile, "Resource cleared") {
                tile.tileResource = null
                tile.resourceAmount = 0
                tile.magalanaduTerraformResource = null
            }
        }.row()
        for (r in screen.gameInfo.ruleset.tileResources.values.sortedBy { it.name }) {
            val normalTerrain = r.terrainsCanBeFoundOn.any { it == tile.baseTerrain || it in tile.terrainFeatures }
            val naturalLabel = if (normalTerrain) "" else " [any terrain]"
            p.addButton("${r.name} (${r.resourceType})$naturalLabel") {
                p.close()
                if (tile.naturalWonder != null) notice(screen,"NOT AVAILABLE", "Remove the natural wonder before placing a resource.")
                else if (r.resourceType == ResourceType.Strategic) chooseResourceAmount(screen,tile,r.name)
                else apply(screen,tile,"${r.name} added") {
                    tile.setTileResource(r)
                    tile.resourceAmount = 0
                    tile.magalanaduTerraformResource = r.name
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseResourceAmount(screen: WorldScreen, tile: Tile, resourceName: String) {
        val resource = screen.gameInfo.ruleset.tileResources[resourceName] ?: return
        val p = popup(screen, "$resourceName: deposit quantity")
        p.addGoodSizedLabel("Normal reveal tech: ${resource.revealedBy ?: "None"}. Magalanadu can see edited deposits immediately. Other civilizations retain their usual technology requirements.").row()
        for (amount in listOf(1, 5, 10, 25, 50, 100, 250, 500, 1000, 9999)) {
            p.addButton("$amount units") {
                p.close()
                apply(screen,tile,"$resourceName deposit set to $amount") {
                    tile.setTileResource(resource)
                    tile.resourceAmount = amount
                    tile.magalanaduTerraformResource = resource.name
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseWonder(screen: WorldScreen, tile: Tile) {
        val p = popup(screen,"NATURAL WONDERS: ${tile.position}")
        p.addButton("REMOVE NATURAL WONDER") {
            p.close()
            apply(screen,tile,"Natural wonder removed") { tile.naturalWonder = null }
        }.row()
        val wonders = screen.gameInfo.ruleset.terrains.values
            .filter { it.type == TerrainType.NaturalWonder }.sortedBy { it.name }
        for (w in wonders) {
            p.addButton("PLACE ${w.name}") {
                p.close()
                if (tile.isCityCenter() || tile.getUnits().any()) notice(screen, "BLOCKED", "Move units and choose a tile without a city centre to place a natural wonder.")
                else apply(screen,tile,"Natural wonder ${w.name} placed") {
                    val targetBase = w.turnsInto
                        ?: if (w.occursOn.isEmpty() || tile.baseTerrain in w.occursOn) tile.baseTerrain
                           else w.occursOn.firstOrNull { it in screen.gameInfo.ruleset.terrains } ?: tile.baseTerrain
                    val target = screen.gameInfo.ruleset.terrains[targetBase]
                        ?: error("Natural wonder base terrain $targetBase is unavailable")
                    tile.naturalWonder = null
                    tile.setBaseTerrain(target)
                    tile.removeTerrainFeatures()
                    tile.tileResource = null
                    tile.resourceAmount = 0
                    tile.magalanaduTerraformResource = null
                    tile.removeImprovement()
                    tile.naturalWonder = w.name
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseImprovement(screen: WorldScreen, tile: Tile) {
        val p = popup(screen, "IMPROVEMENTS: ${tile.position}")
        p.addButton("REMOVE IMPROVEMENT") { p.close(); apply(screen,tile,"Improvement cleared") { tile.removeImprovement() } }.row()
        for (imp in screen.gameInfo.ruleset.tileImprovements.values.sortedBy { it.name }) {
            p.addButton(imp.name) {
                p.close()
                apply(screen,tile,"Improvement ${imp.name} placed") { tile.setImprovement(imp) }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseRiver(screen: WorldScreen, tile: Tile) {
        val p = popup(screen, "RIVER EDGES: ${tile.position}")
        if (tile.isWater) p.addGoodSizedLabel("Rivers require land tiles. Select land near a river or change terrain first.").row()
        for (other in tile.neighbors.filter { it.isLand }) {
            val enabled = tile.isConnectedByRiver(other)
            p.addButton("${if (enabled) "REMOVE" else "ADD"} river toward ${other.position}") {
                p.close()
                if (tile.isWater) notice(screen,"BLOCKED","Cannot add a river from a water tile.")
                else {
                    tile.setConnectedByRiver(other, !enabled)
                    refresh(screen,tile)
                    notice(screen,"RIVER UPDATED","River between ${tile.position} and ${other.position} ${if (enabled) "removed" else "added"}. Save your game to keep it.")
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun chooseRoad(screen: WorldScreen, tile: Tile) {
        val p = popup(screen,"ROADS: ${tile.position}")
        for (road in listOf(RoadStatus.None,RoadStatus.Road,RoadStatus.Railroad)) {
            p.addButton(road.name) {
                p.close()
                if (tile.isWater || tile.isImpassible()) notice(screen, "BLOCKED", "Roads and railroads require passable land.")
                else apply(screen,tile,"Road status: ${road.name}") {
                    tile.setRoadStatus(road,screen.viewingCiv)
                }
            }.row()
        }
        p.addCloseButton().row()
        p.open()
    }

    private fun apply(screen: WorldScreen, tile: Tile, label: String, change: () -> Unit) {
        val oldBase = tile.baseTerrain
        val oldFeatures = tile.terrainFeatures.toList()
        val oldWonder = tile.naturalWonder
        val oldResource = tile.tileResource
        val oldAmount = tile.resourceAmount
        val oldTerraformResource = tile.magalanaduTerraformResource
        val oldImprovement = tile.improvement
        val oldRoad = tile.roadStatus
        try {
            change()
            tile.setTerrainTransients()
            TileNormalizer.normalizeToRuleset(tile,screen.gameInfo.ruleset)
            tile.setTerrainTransients()
            // No false success: catch any resource that a later normalization still drops.
            if (tile.magalanaduTerraformResource != null &&
                tile.resource != tile.magalanaduTerraformResource)
                error("Edited resource was removed during terrain normalization")
            refresh(screen,tile)
            notice(screen, "TILE UPDATED", "$label. ${summary(tile)}. Save your game to retain the edit. Tap another tile to continue.")
        } catch (e: Exception) {
            // Restore serialized tile attributes before returning control to the game.
            tile.baseTerrain = oldBase
            tile.naturalWonder = oldWonder
            tile.setTerrainFeatures(oldFeatures)
            tile.tileResource = oldResource
            tile.resourceAmount = oldAmount
            tile.magalanaduTerraformResource = oldTerraformResource
            tile.improvement = oldImprovement
            tile.roadStatus = oldRoad
            tile.setTerrainTransients()
            refresh(screen,tile)
            notice(screen, "CHANGE FAILED", e.message ?: "The requested terrain combination is incompatible with this map.")
        }
    }

    private fun refresh(screen: WorldScreen, tile: Tile) {
        // Update city yields, resources, visibility, then let WorldScreen rebuild sprites.
        tile.getCity()?.reassignPopulationDeferred()
        tile.getCity()?.cityStats?.update()
        tile.getOwner()?.cache?.updateCivResources()
        for (civ in screen.gameInfo.civilizations) {
            if (!civ.isDefeated() && civ.hasExplored(tile)) civ.cache.discoverNaturalWonders(listOf(tile))
        }
        screen.shouldUpdate = true
    }
}
