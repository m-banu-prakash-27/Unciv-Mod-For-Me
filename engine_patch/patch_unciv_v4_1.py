#!/usr/bin/env python3
'''Magalanadu 4.1: apply v4 Directorate and private 108-radius city limits.

Only Magalanadu cities use the large range. Other nations retain normal mod
constants. Idempotent; uses exact source anchors for Unciv 4.22.16 only.
'''
from pathlib import Path
import sys
from patch_unciv_v4_0 import apply as apply_v4

RADIUS = 108
VIEW_RADIUS = 12


def _replace_once(file: Path, before: str, after: str, marker: str):
    text = file.read_text(encoding='utf-8')
    if marker in text:
        if after not in text:
            raise RuntimeError(f'{file}: marker exists but replacement is damaged')
        return False
    if text.count(before) != 1:
        raise RuntimeError(f'{file}: source does not match Unciv 4.22.16 (anchor count {text.count(before)})')
    file.write_text(text.replace(before,after,1), encoding='utf-8')
    print(f'Patched {file.relative_to(file.parents[4])}: {marker}')
    return True


def apply_radius(root: Path):
    root = Path(root).resolve()
    city = root/'core/src/com/unciv/logic/city/City.kt'
    expansion = root/'core/src/com/unciv/logic/city/managers/CityExpansionManager.kt'
    screen = root/'core/src/com/unciv/ui/screens/cityscreen/CityScreen.kt'
    for p in [city,expansion,screen]:
        if not p.is_file(): raise FileNotFoundError(f'Missing Unciv source: {p}')

    _replace_once(city,
'''    @Readonly fun getWorkRange(): Int = civ.gameInfo.ruleset.modOptions.constants.cityWorkRange
    @Readonly fun getExpandRange(): Int = civ.gameInfo.ruleset.modOptions.constants.cityExpandRange''',
'''    // MAGALANADU_V4_1_RADIUS_108: Magalanadu-only; other civs retain the ruleset ranges.
    @Readonly fun getWorkRange(): Int =
        if (civ.civName == "Magalanadu") 108 else civ.gameInfo.ruleset.modOptions.constants.cityWorkRange
    @Readonly fun getExpandRange(): Int =
        if (civ.civName == "Magalanadu") 108 else civ.gameInfo.ruleset.modOptions.constants.cityExpandRange''',
'MAGALANADU_V4_1_RADIUS_108')

    _replace_once(city,
'''    @Readonly fun getWorkableTiles() = tilesInRange.asSequence().filter { it.getOwner() == civ }''',
'''    // MAGALANADU_V4_1_WORKABLE_TILES: only inspect empire-owned plots for the
    // massive 108-range, rather than scanning up to 35,317 empty candidates.
    @Readonly fun getWorkableTiles() = if (civ.civName == "Magalanadu") {
        civ.cities.asSequence().flatMap { it.getTiles() }
            .filter { it.aerialDistanceTo(getCenterTile()) <= getWorkRange() }
            .distinct()
    } else tilesInRange.asSequence().filter { it.getOwner() == civ }''',
'MAGALANADU_V4_1_WORKABLE_TILES')

    _replace_once(expansion,
'''    @Readonly
    fun getChoosableTiles() = city.getCenterTile().getTilesInDistance(city.getExpandRange())
        .filter { it.getOwner() == null }''',
'''    // MAGALANADU_V4_1_BORDER_FRONTIER: cultural growth may reach radius 108,
    // but selects only tiles bordering our city instead of scoring the whole map.
    @Readonly
    fun getChoosableTiles() = if (city.civ.civName == "Magalanadu") {
        city.getTiles()
            .flatMap { it.neighbors.asSequence() }
            .filter { it.getOwner() == null &&
                it.aerialDistanceTo(city.getCenterTile()) <= city.getExpandRange() }
            .distinct()
    } else city.getCenterTile().getTilesInDistance(city.getExpandRange())
        .filter { it.getOwner() == null }''',
'MAGALANADU_V4_1_BORDER_FRONTIER')

    _replace_once(screen,
'''        val viewRange = max(cityView.getExpandRange(), cityView.getWorkRange())''',
'''        // MAGALANADU_V4_1_CITY_VIEW_CAP: don't instantiate an entire world of
        // CityTileGroup actors on Android. This is UI only, NOT city influence.
        val viewRange = if (cityView.getWorkRange() >= 108) 12
            else max(cityView.getExpandRange(), cityView.getWorkRange())''',
'MAGALANADU_V4_1_CITY_VIEW_CAP')
    # Explicit postconditions; do not silently succeed on partially-patched source.
    assert all(token in city.read_text(encoding='utf-8') for token in ['MAGALANADU_V4_1_RADIUS_108','MAGALANADU_V4_1_WORKABLE_TILES'])
    assert 'MAGALANADU_V4_1_BORDER_FRONTIER' in expansion.read_text(encoding='utf-8')
    assert 'MAGALANADU_V4_1_CITY_VIEW_CAP' in screen.read_text(encoding='utf-8')
    print('PASS: 108-radius Magalanadu expansion and work, optimized frontier, safe city screen.')


def apply(root: Path):
    root=Path(root).resolve()
    apply_v4(root)
    apply_radius(root)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_1.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]).expanduser())
