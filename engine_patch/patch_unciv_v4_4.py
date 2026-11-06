#!/usr/bin/env python3
"""Cumulative Magalanadu v4.4 logistics, depot unit spawning and world paradrops.

Applies on a fresh Unciv 4.22.16 checkout after all earlier v4.3 patches.
Patches exact version-checked anchors; reruns are harmless.
"""
from pathlib import Path
import sys
from patch_unciv_v4_3 import apply as apply_v4_3

MARK = 'MAGALANADU_V4_4_LOGISTICS'


def replace_once(path: Path, before: str, after: str, marker: str):
    data = path.read_text(encoding='utf-8-sig')
    if marker in data:
        if after not in data:
            raise RuntimeError(f'Malformed existing v4.4 patch: {path}, {marker}')
        print('Already patched:',path,marker)
        return
    if data.count(before) != 1:
        raise RuntimeError(f'Unexpected Unciv source for {marker}: {path} (matches={data.count(before)})')
    path.write_text(data.replace(before, after, 1), encoding='utf-8')
    print('Patched:',path.name,marker)


def apply(root: Path):
    root=Path(root).resolve()
    city=root/'core/src/com/unciv/logic/city/City.kt'
    unit_manager=root/'core/src/com/unciv/logic/civilization/managers/UnitManager.kt'
    from_uniques=root/'core/src/com/unciv/logic/map/mapunit/actions/UnitActionsFromUniques.kt'
    movement=root/'core/src/com/unciv/logic/map/mapunit/movement/UnitMovement.kt'
    directory=root/'core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt'
    deployed=root/'core/src/com/unciv/ui/popups/MagalanaduLogistics.kt'
    targets=(city,unit_manager,from_uniques,movement,directory)
    if all(f.exists() for f in targets) and deployed.exists() and all([
        'MAGALANADU_V4_4_DEPOT_SAVE' in city.read_text(encoding='utf-8-sig'),
        'MAGALANADU_V4_4_UNIT_PRODUCTION' in unit_manager.read_text(encoding='utf-8-sig'),
        'MAGALANADU_V4_4_PARADROP_UNIT' in from_uniques.read_text(encoding='utf-8-sig'),
        'MAGALANADU_V4_4_PARADROP_TILES' in movement.read_text(encoding='utf-8-sig'),
        'MAGALANADU_V4_4_LOGISTICS_MENU' in directory.read_text(encoding='utf-8-sig'),
    ]):
        print('PASS: v4.4 already installed')
        return
    # Always apply predecessor only to a clean Unciv checkout. It validates
    # the existing v4.3 features, including the v4.2 Kotlin purity repair.
    apply_v4_3(root)
    if any(f.read_text(encoding='utf-8-sig').count('MAGALANADU_V4_4') for f in targets):
        raise RuntimeError('Partial v4.4 found; restore a clean Unciv checkout')
    src=Path(__file__).with_name('MagalanaduLogistics.kt')
    if not src.exists() or deployed.exists():
        raise RuntimeError('Missing source or unexpected existing logistics Kotlin')

    replace_once(city,
'''    var location = HexCoord()
    var id: String = NO_ID''',
'''    // MAGALANADU_V4_4_DEPOT_SAVE: selected military production depot survives saves.
    var magalanaduDepotPosition: HexCoord? = null
    var location = HexCoord()
    var id: String = NO_ID''',
'MAGALANADU_V4_4_DEPOT_SAVE')
    replace_once(city,
'''        toReturn.location = location
        toReturn.id = if (id != NO_ID) id else pseudoRandomId(civ)''',
'''        // MAGALANADU_V4_4_DEPOT_CLONE: next-turn game clone retains selected depot.
        toReturn.magalanaduDepotPosition = magalanaduDepotPosition
        toReturn.location = location
        toReturn.id = if (id != NO_ID) id else pseudoRandomId(civ)''',
'MAGALANADU_V4_4_DEPOT_CLONE')
    replace_once(unit_manager,
'''        val placedUnit = placeUnitNearTile(cityToAddTo.location.toHexCoord(), unit.name)''',
'''        // MAGALANADU_V4_4_UNIT_PRODUCTION: route newly built units to a valid depot.
        // The standard unit placement method preserves all usual construction triggers.
        val logisticsLocation = com.unciv.ui.popups.MagalanaduLogistics.productionSpawnPosition(cityToAddTo, unit)
        val placedUnit = placeUnitNearTile(logisticsLocation ?: cityToAddTo.location.toHexCoord(), unit.name)''',
'MAGALANADU_V4_4_UNIT_PRODUCTION')
    replace_once(from_uniques,
'''        if (unit.cache.paradropDestinationTileFilters.isEmpty()) return emptySequence()''',
'''        // MAGALANADU_V4_4_PARADROP_UNIT: all land units can drop worldwide.
        // Filters are kept for other civilizations; the 4.22.16 movement engine
        // is patched to enumerate ONLY the actual explored map tiles.
        if (unit.civ.civName == "Magalanadu" && unit.baseUnit.isLandUnit) {
            unit.cache.paradropDestinationTileFilters["Land"] = Int.MAX_VALUE / 4
        }
        if (unit.cache.paradropDestinationTileFilters.isEmpty()) return emptySequence()''',
'MAGALANADU_V4_4_PARADROP_UNIT')
    replace_once(movement,
'''            unit.isPreparingParadrop() -> {
                unit.getTile().getTilesInDistance(unit.cache.paradropDestinationTileFilters.maxOf { it.value } )
                    .filter { unit.movement.canParadropOn(it, it.aerialDistanceTo(unit.getTile())) }
            }''',
'''            unit.isPreparingParadrop() -> {
                // MAGALANADU_V4_4_PARADROP_TILES: avoid an enormous O(radius^2)
                // allocation for worldwide paradrops. Visit only real map tiles.
                if (unit.civ.civName == "Magalanadu")
                    unit.civ.gameInfo.tileMap.tileList.asSequence()
                        .filter { canParadropOn(it, it.aerialDistanceTo(unit.getTile())) }
                else unit.getTile().getTilesInDistance(unit.cache.paradropDestinationTileFilters.maxOf { it.value })
                    .filter { canParadropOn(it, it.aerialDistanceTo(unit.getTile())) }
            }''',
'MAGALANADU_V4_4_PARADROP_TILES')
    replace_once(movement,
'''        if (destination.isImpassible() || !unit.civ.viewableTiles.contains(destination)) return false

        // The destination is valid if any of the `tileFilters` match, and is within range''',
'''        if (unit.civ.civName == "Magalanadu" && unit.baseUnit.isLandUnit) {
            // MAGALANADU_V4_4_PARADROP_LANDING: distance unlimited for explored land,
            // but no drop onto occupied, impassable, or otherwise illegal tiles.
            return destination.isLand && !destination.isImpassible() &&
                unit.civ.hasExplored(destination) && canMoveTo(destination)
        }
        if (destination.isImpassible() || !unit.civ.viewableTiles.contains(destination)) return false

        // The destination is valid if any of the `tileFilters` match, and is within range''',
'MAGALANADU_V4_4_PARADROP_LANDING')
    replace_once(directory,
'''        popup.addButton("ARMS CONTRACTS: donate a military unit") {''',
'''        // MAGALANADU_V4_4_LOGISTICS_MENU
        popup.addButton("MILITARY LOGISTICS: Armament Depots & unit spawning") {
            popup.close()
            MagalanaduLogistics.open(user)
        }.row()
        popup.addButton("ARMS CONTRACTS: donate a military unit") {''',
'MAGALANADU_V4_4_LOGISTICS_MENU')
    deployed.write_text(src.read_text(encoding='utf-8'),encoding='utf-8')
    print('PASS: v4.4 depot logistics and global paradrop patches installed')


if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('Usage: python engine_patch/patch_unciv_v4_4.py <Unciv-4.22.16-checkout>')
    apply(Path(sys.argv[1]))
