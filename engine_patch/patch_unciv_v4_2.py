#!/usr/bin/env python3
# Magalanadu v4.2: city radius 14 and geographically-balanced land/water expansion.
# Cumulative v3.2 gifting/promotions + v4.0 directorate + v4.1 frontier optimization.
# Target 60% LAND and 40% WATER (coast, lake, ocean).
# Does not alter terrain or annex others; only target 4.22.16.
from pathlib import Path
import sys
from patch_unciv_v4_1 import apply as apply_v4_1

RADIUS = 14
CITY_VIEW_RADIUS = 12
LAND_TARGET_PERCENT = 60
WATER_TARGET_PERCENT = 40


def replace_once(file: Path, before: str, after: str, marker: str):
    text = file.read_text(encoding='utf-8')
    if marker in text:
        if after not in text: raise RuntimeError(f'{file}: marker found but its content is damaged')
        return False
    if text.count(before) != 1:
        raise RuntimeError(f'{file}: mismatched Unciv source anchor for {marker}: {text.count(before)}')
    file.write_text(text.replace(before, after, 1),encoding='utf-8')
    print('Patched:',file,marker)
    return True


def apply_v4_2(root: Path):
    root=Path(root).resolve()
    city=root/'core/src/com/unciv/logic/city/City.kt'
    expansion=root/'core/src/com/unciv/logic/city/managers/CityExpansionManager.kt'
    screen=root/'core/src/com/unciv/ui/screens/cityscreen/CityScreen.kt'
    directorate=root/'core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt'
    # A rerun must be idempotent. v4.0's original installer correctly rejects
    # modified Directorate files, so first check if v4.2 was already applied.
    if all(p.is_file() for p in (city, expansion, screen, directorate)) and all([
        'MAGALANADU_V4_2_RADIUS_14' in city.read_text(encoding='utf-8'),
        'MAGALANADU_V4_2_60_40_CULTURE' in expansion.read_text(encoding='utf-8'),
        'MAGALANADU_V4_2_CLAIM_60_40' in directorate.read_text(encoding='utf-8'),
        'MAGALANADU_V4_2_CITY_VIEW' in screen.read_text(encoding='utf-8'),
    ]):
        print('PASS: Magalanadu v4.2 already applied, no changes made.')
        return

    apply_v4_1(root)
    replace_once(city,
'''    // MAGALANADU_V4_1_RADIUS_108: Magalanadu-only; other civs retain the ruleset ranges.
    @Readonly fun getWorkRange(): Int =
        if (civ.civName == "Magalanadu") 108 else civ.gameInfo.ruleset.modOptions.constants.cityWorkRange
    @Readonly fun getExpandRange(): Int =
        if (civ.civName == "Magalanadu") 108 else civ.gameInfo.ruleset.modOptions.constants.cityExpandRange''',
'''    // MAGALANADU_V4_2_RADIUS_14: genuine 14-hex city work + territorial influence radius.
    // This is private to Magalanadu. Other civilizations keep the original mod settings.
    @Readonly fun getWorkRange(): Int =
        if (civ.civName == "Magalanadu") 14 else civ.gameInfo.ruleset.modOptions.constants.cityWorkRange
    @Readonly fun getExpandRange(): Int =
        if (civ.civName == "Magalanadu") 14 else civ.gameInfo.ruleset.modOptions.constants.cityExpandRange''',
'MAGALANADU_V4_2_RADIUS_14')

    replace_once(screen,
'''        // MAGALANADU_V4_1_CITY_VIEW_CAP: don't instantiate an entire world of
        // CityTileGroup actors on Android. This is UI only, NOT city influence.
        val viewRange = if (cityView.getWorkRange() >= 108) 12
            else max(cityView.getExpandRange(), cityView.getWorkRange())''',
'''        // MAGALANADU_V4_2_CITY_VIEW: show 12 hexes to protect Android memory;
        // the actual Magalanadu city working and culture radius remains 14.
        val viewRange = if (cityView.getWorkRange() == 14 && cityView.getExpandRange() == 14) 12
            else max(cityView.getExpandRange(), cityView.getWorkRange())''',
'MAGALANADU_V4_2_CITY_VIEW')

    replace_once(expansion,
'''    @Readonly
    fun chooseNewTileToOwn(): Tile? {
        // Technically, in the original a random tile with the lowest score was selected
        // However, doing this requires either caching it, which is way more work,
        // or selecting all possible tiles and only choosing one when the border expands.
        // But since the order in which tiles are selected in distance is kinda random anyways,
        // this is fine.
        return getChoosableTiles().minByOrNull {
            rankTileForExpansion(it)
        }
    }''',
'''    @Readonly
    fun chooseNewTileToOwn(): Tile? {
        // MAGALANADU_V4_2_60_40_CULTURE: select from contiguous, unowned frontier.
        // Choose the next tile that best closes the gap to 60% land / 40% water.
        // Water includes Coast, Ocean and Lakes. Do NOT alter terrain or claim owned tiles.
        if (city.civ.civName == "Magalanadu") {
            val owned = city.getTiles().toList()
            val ownedLand = owned.count { !it.isWater }
            val total = owned.size
            return getChoosableTiles().minWithOrNull(
                compareBy<Tile>(
                    // Integer math: 5 * land - 3 * total is exactly 60% imbalance.
                    { kotlin.math.abs(5 * (ownedLand + if (it.isWater) 0 else 1) - 3 * (total + 1)) },
                    { rankTileForExpansion(it) }
                )
            )
        }
        // Keep the standard game behavior for every other civilization.
        return getChoosableTiles().minByOrNull { rankTileForExpansion(it) }
    }

    /** MAGALANADU_V4_2_BATCH_CLAIM: safe, bounded instant-claim operation.
     * Claims at most 40 CONNECTED, previously UNOWNED tiles per command.
     * If there is no water in reach, the 60/40 ratio is a target, not magic
     * terraforming. Population and map constraints remain in force.
     */
    fun claimMagalanaduBalancedTiles(maxTiles: Int): Int {
        if (city.civ.civName != "Magalanadu" || !city.civ.isCurrentPlayer()
            || city.isPuppet || city.isBeingRazed || city.isInResistance()) return 0
        var claimed = 0
        repeat(maxTiles.coerceIn(0, 40)) {
            val next = chooseNewTileToOwn() ?: return claimed
            if (next.getOwner() != null ||
                next.aerialDistanceTo(city.getCenterTile()) > city.getExpandRange()) return claimed
            takeOwnership(next)
            claimed++
        }
        city.reassignPopulationDeferred()
        return claimed
    }''',
'MAGALANADU_V4_2_60_40_CULTURE')

    replace_once(directorate,
'''        popup.addButton("ARMS CONTRACTS: donate a military unit") {''',
'''        // MAGALANADU_V4_2_CLAIM_60_40: selectable city territory controls.
        popup.addButton("CLAIM TERRITORY: 14 radius, target 60% land / 40% water") {
            popup.close()
            chooseBalancedTerritoryCity(user)
        }.row()
        popup.addButton("ARMS CONTRACTS: donate a military unit") {''',
'MAGALANADU_V4_2_CLAIM_60_40')

    replace_once(directorate,
'''    private fun selectCiv(
        player: Civilization,''',
'''    // MAGALANADU_V4_2_LAND_WATER_COUNTS: counts actual, currently owned terrain.
    private fun chooseBalancedTerritoryCity(player: Civilization) {
        val popup = newPopup("TERRITORY CLAIM: 60% LAND / 40% WATER")
        popup.addGoodSizedLabel("Every Magalanadu city now reaches 14 hexes in all directions. Select a city. You can claim up to 40 new, adjacent, unowned tiles per action. The engine favors 60% land / 40% water but will not convert land to ocean or steal owned tiles.").row()
        for (city in player.cities.sortedBy { it.name }) {
            val owned = city.getTiles().toList()
            val land = owned.count { !it.isWater }
            val water = owned.size - land
            popup.addButton("${city.name}: $land land / $water water") {
                popup.close()
                chooseBalancedTerritoryQuantity(city)
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun chooseBalancedTerritoryQuantity(city: City) {
        val popup = newPopup("TERRITORY: ${city.name}")
        val owned = city.getTiles().toList()
        val land = owned.count { !it.isWater }
        val water = owned.size - land
        val total = owned.size
        popup.addGoodSizedLabel("Now: $land land, $water water ($total tiles). Target is 60/40. This city can reach any suitable unowned tile within 14 hexes by contiguous expansion. 631 tiles is the theoretical maximum on an unrestricted map, not a guaranteed land/water split.").row()
        for (amount in listOf(10, 25, 40)) {
            popup.addButton("CLAIM UP TO $amount TILES (BALANCED)") {
                popup.close()
                val obtained = city.expansion.claimMagalanaduBalancedTiles(amount)
                val updated = city.getTiles().toList()
                val newLand = updated.count { !it.isWater }
                val newWater = updated.size - newLand
                message("${city.name}: claimed $obtained unowned tiles. Current territory: $newLand land / $newWater water. Target 60/40; the map's actual land-water geography limits the achievable mix.")
            }.row()
        }
        popup.addCloseButton().row()
        popup.open()
    }

    private fun selectCiv(
        player: Civilization,''',
'MAGALANADU_V4_2_LAND_WATER_COUNTS')

    for p,token in ((city,'MAGALANADU_V4_2_RADIUS_14'),(screen,'MAGALANADU_V4_2_CITY_VIEW'),
                    (expansion,'MAGALANADU_V4_2_BATCH_CLAIM'),(directorate,'MAGALANADU_V4_2_LAND_WATER_COUNTS')):
        assert token in p.read_text(encoding='utf-8'), f'Missing v4.2 postcondition {token}'
    print('PASS: Magalanadu v4.2 radius 14; culture and manual claims favor 60/40; non-Magalanadu ranges preserved.')


def apply(root: Path): apply_v4_2(Path(root))

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit('Usage: python engine_patch/patch_unciv_v4_2.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]).expanduser())
