#!/usr/bin/env python3
"""Static and isolated source-integration checks for Magalanadu resource editing.

This is NOT a replacement for a full Android Kotlin compile or in-game test.
"""
from pathlib import Path
import sys
import tempfile
import types
import importlib.util

root = Path(__file__).resolve().parents[1]
editor = (root/'engine_patch/MagalanaduTerraformEditor.kt').read_text(encoding='utf-8')
patcher = (root/'engine_patch/patch_unciv_v4_5_1.py').read_text(encoding='utf-8')
assert 'else if (!compatible)' not in editor, 'Old terrain rejection still present'
for name in ('Coal', 'Uranium', 'Iron'):
    # Every resource from the active ruleset uses the same menu path;
    # there is no hardcoded Iron-only whitelist.
    assert 'for (r in screen.gameInfo.ruleset.tileResources.values.sortedBy { it.name })' in editor
assert 'tile.magalanaduTerraformResource = r.name' in editor
assert 'tile.magalanaduTerraformResource = resource.name' in editor
assert 'val oldTerraformResource = tile.magalanaduTerraformResource' in editor
assert 'tile.magalanaduTerraformResource = oldTerraformResource' in editor
assert 'tile.resource != tile.magalanaduTerraformResource' in editor
assert 'resourceObject.name' in patcher
assert 'if (civName == "Magalanadu") return true' in patcher
assert 'getOwner() == civInfo' in patcher

# Run the actual patcher against faithful 4.22.16 source anchors, then again.
# The v4.4 prerequisite is replaced by a stub to isolate the new patch.
mock = types.ModuleType('patch_unciv_v4_4')
def old_patcher(p):
    src = root/'engine_patch/MagalanaduTerraformEditor.kt'
    to = p/'core/src/com/unciv/ui/popups/MagalanaduTerraformEditor.kt'
    to.parent.mkdir(parents=True, exist_ok=True)
    if not to.exists(): to.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
mock.apply = old_patcher
sys.modules['patch_unciv_v4_4'] = mock
spec = importlib.util.spec_from_file_location('resource_patch_under_test', root/'engine_patch/patch_unciv_v4_5_1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

samples = {
 'core/src/com/unciv/logic/map/tile/Tile.kt': '''class Tile {
    var resourceAmount: Int = 0
    fun clone() {
        toReturn.resource = resource
        toReturn.resourceAmount = resourceAmount
    }
    fun providesResources(civInfo: Civilization): Boolean {
        val resource = tileResource // To avoid additional checks later
        if (!civInfo.canSeeResource(resource)) return false
    }
}
''',
 'core/src/com/unciv/logic/map/tile/TileNormalizer.kt': '''object TileNormalizer {
    fun normalizeToRuleset(tile: Tile, ruleset: Ruleset) {
        if (resourceObject != null) {
            if (resourceObject.terrainsCanBeFoundOn.none { it == tile.baseTerrain || tile.terrainFeatures.contains(it) })
                tile.tileResource = null
        }
    }
}
''',
 'core/src/com/unciv/logic/civilization/Civilization.kt': '''class Civilization {
    fun canSeeResource(resource: TileResource?): Boolean {
        if (resource == null) return false
        return tech.isRevealed(resource)
    }
}
'''
}
with tempfile.TemporaryDirectory() as folder:
    fresh = Path(folder)
    for relative, text in samples.items():
        path = fresh/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
    module.apply(fresh)
    once = {relative:(fresh/relative).read_text(encoding='utf-8') for relative in samples}
    assert 'var magalanaduTerraformResource: String? = null' in once['core/src/com/unciv/logic/map/tile/Tile.kt']
    assert 'toReturn.magalanaduTerraformResource = magalanaduTerraformResource' in once['core/src/com/unciv/logic/map/tile/Tile.kt']
    module.apply(fresh)
    assert once == {relative:(fresh/relative).read_text(encoding='utf-8') for relative in samples}, 'Patch changed files on rerun'

# Expected resource examples: normal ruleset restrictions never override marked edits.
class Tile:
    def __init__(self, name, natural_terrains, terrain, marked):
        self.name,self.natural_terrains,self.terrain,self.marked=name,natural_terrains,terrain,marked
    def normalized_resource(self):
        return self.name if self.name == self.marked or self.terrain in self.natural_terrains else None
for resource,valid,terrain in (
        ('Iron', ('Grassland','Plains','Desert','Tundra','Snow','Hill','Marsh'),'Grassland'),
        ('Coal', ('Grassland','Plains','Hill','Jungle','Forest','Marsh'),'Snow'),
        ('Uranium',('Marsh','Jungle','Forest','Tundra','Snow'),'Grassland')):
    assert Tile(resource,valid,terrain,resource).normalized_resource()==resource
    if terrain not in valid:
        assert Tile(resource,valid,terrain,None).normalized_resource() is None

# Optionally verify the patched game source checked out by the workflow.
if '--root' in sys.argv:
    i=sys.argv.index('--root')
    game=Path(sys.argv[i+1])
    tile=(game/'core/src/com/unciv/logic/map/tile/Tile.kt').read_text(encoding='utf-8')
    normal=(game/'core/src/com/unciv/logic/map/tile/TileNormalizer.kt').read_text(encoding='utf-8')
    civ=(game/'core/src/com/unciv/logic/civilization/Civilization.kt').read_text(encoding='utf-8')
    assert 'var magalanaduTerraformResource: String? = null' in tile
    assert 'toReturn.magalanaduTerraformResource = magalanaduTerraformResource' in tile
    assert 'getOwner() == civInfo' in tile
    assert 'tile.magalanaduTerraformResource != resourceObject.name' in normal
    assert 'if (civName == "Magalanadu") return true' in civ
    assert (game/'core/src/com/unciv/ui/popups/MagalanaduTerraformEditor.kt').read_text(encoding='utf-8') == editor
    print('PASS: patched game sources validated')
print('PASS: v4.5.1 resource validation, persistence and repeatability')
