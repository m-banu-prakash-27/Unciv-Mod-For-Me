#!/usr/bin/env python3
"""v4.4 offline regression: depot source wiring, saved assignments and world paradrops.
Does not replace building and gameplay tests against the official Unciv APK.
"""
from pathlib import Path
import json, tempfile, subprocess, sys, shutil
R=Path(__file__).resolve().parents[1]
L=(R/'engine_patch/MagalanaduLogistics.kt').read_text(encoding='utf-8')
P=(R/'engine_patch/patch_unciv_v4_4.py').read_text(encoding='utf-8')
W=(R/'.github/workflows/build-magalanadu-v4-4-android.yml').read_text(encoding='utf-8')
B=json.loads((R/'jsons/Buildings.json').read_text(encoding='utf-8'))
U=json.loads((R/'jsons/Units.json').read_text(encoding='utf-8'))
assert sum(x['name']=='Magalanadu Armament Depot' for x in B)==1
assert sum(x['name']=='Super Cheat Worker' for x in U)==1
assert any('Can instantly construct a [Arms Depot]' in a for u in U if u['name']=='Super Cheat Worker' for a in u['uniques'])
assert (R/'Images/BuildingIcons/Magalanadu Armament Depot.png').exists()
assert 'BuildingIcons/Magalanadu Armament Depot' in (R/'MagalanaduProjects.atlas').read_text()
for term in ('productionSpawnPosition','magalanaduDepotPosition','"Arms Depot"','"Magalanadu Armament Depot"','chooseUnit','chooseQuantity','placeUnitNearTile','coerceIn(1, 10)'):
    assert term in L,term
for term in ('MAGALANADU_V4_4_DEPOT_CLONE','MAGALANADU_V4_4_DEPOT_SAVE','MAGALANADU_V4_4_PARADROP_TILES','MAGALANADU_V4_4_PARADROP_LANDING','MAGALANADU_V4_4_PARADROP_UNIT','apply_v4_3(root)','MAGALANADU_V4_4_UNIT_PRODUCTION'):
    assert term in P,term
assert 'tileMap.tileList.asSequence()' in P
assert 'getTilesInDistance(Int.MAX_VALUE' not in P
assert 'hasExplored(destination) && canMoveTo(destination)' in P
assert 'patch_unciv_v4_4.py game' in W

# End-to-end patch generator integration on a synthetic v4.3 engine source tree.
# Previous-version markers deliberately preseeded to exercise only the v4.4 delta.
with tempfile.TemporaryDirectory() as d:
    root=Path(d)
    def put(path,content):
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
    put('core/src/com/unciv/logic/city/City.kt','''class City {
    var location = HexCoord()
    var id: String = NO_ID
    fun clone(): City {
        val toReturn = City()
        toReturn.location = location
        toReturn.id = if (id != NO_ID) id else pseudoRandomId(civ)
        return toReturn
    }
}
''')
    put('core/src/com/unciv/logic/civilization/managers/UnitManager.kt','''        val placedUnit = placeUnitNearTile(cityToAddTo.location.toHexCoord(), unit.name)
''')
    put('core/src/com/unciv/logic/map/mapunit/actions/UnitActionsFromUniques.kt','''        if (unit.cache.paradropDestinationTileFilters.isEmpty()) return emptySequence()
''')
    put('core/src/com/unciv/logic/map/mapunit/movement/UnitMovement.kt','''            unit.isPreparingParadrop() -> {
                unit.getTile().getTilesInDistance(unit.cache.paradropDestinationTileFilters.maxOf { it.value } )
                    .filter { unit.movement.canParadropOn(it, it.aerialDistanceTo(unit.getTile())) }
            }
'''+'''        if (destination.isImpassible() || !unit.civ.viewableTiles.contains(destination)) return false

        // The destination is valid if any of the `tileFilters` match, and is within range
''')
    put('core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt','''        // MAGALANADU_V4_3_TERRAFORM_MENU
        popup.addButton("ARMS CONTRACTS: donate a military unit") {
''')
    put('core/src/com/unciv/ui/popups/MagalanaduTerraformEditor.kt','''object MagalanaduTerraformEditor {}''')
    put('core/src/com/unciv/ui/screens/worldscreen/worldmap/WorldMapHolder.kt','''        // MAGALANADU_V4_3_TERRAFORM_TILE_SELECT
''')
    proc=subprocess.run([sys.executable,str(R/'engine_patch/patch_unciv_v4_4.py'),str(root)],capture_output=True,text=True)
    assert proc.returncode==0,(proc.stdout,proc.stderr)
    proc2=subprocess.run([sys.executable,str(R/'engine_patch/patch_unciv_v4_4.py'),str(root)],capture_output=True,text=True)
    assert proc2.returncode==0,(proc2.stdout,proc2.stderr)
    assert 'already installed' in proc2.stdout
    assert (root/'core/src/com/unciv/logic/city/City.kt').read_text().count('MAGALANADU_V4_4_DEPOT_SAVE')==1
    assert (root/'core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt').read_text().count('MAGALANADU_V4_4_LOGISTICS_MENU')==1
    assert (root/'core/src/com/unciv/ui/popups/MagalanaduLogistics.kt').read_text()==L
print('PASS v4.4: depot roster, save/clone, real unit placement, global paradrop, safe patch and rerun')
