#!/usr/bin/env python3
"""Unciv 4.22.16 + Magalanadu v4.5.1: save-safe any-terrain resource editing.

Cumulative with v4.4/v4.5 military and resource features. Adds a serialized,
per-tile resource override only for resources deliberately placed via the
Magalanadu Terraforming Editor. All vanilla map tiles retain vanilla rules.
"""
from pathlib import Path
import sys
from patch_unciv_v4_4 import apply as apply_v4_4

MARK = 'MAGALANADU_V4_5_1_RESOURCE_PLACEMENT'


def once(path: Path, before: str, after: str):
    content = path.read_text(encoding='utf-8-sig')
    if after in content:
        print('ALREADY PATCHED:', path)
        return
    count = content.count(before)
    if count != 1:
        raise RuntimeError(f'{path}: expected exactly one v4.22.16 anchor, found {count}')
    path.write_text(content.replace(before, after, 1), encoding='utf-8')
    print('PATCHED:', path)


def apply(root: Path):
    root = Path(root).resolve()
    apply_v4_4(root)
    tile = root/'core/src/com/unciv/logic/map/tile/Tile.kt'
    normalizer = root/'core/src/com/unciv/logic/map/tile/TileNormalizer.kt'
    civ = root/'core/src/com/unciv/logic/civilization/Civilization.kt'
    editor = root/'core/src/com/unciv/ui/popups/MagalanaduTerraformEditor.kt'
    source = Path(__file__).with_name('MagalanaduTerraformEditor.kt')
    if not source.exists() or not all(p.exists() for p in (tile, normalizer, civ, editor)):
        raise FileNotFoundError('Missing Unciv 4.22.16 source or v4.5.1 Terraforming Editor')
    if 'magalanaduTerraformResource' not in source.read_text(encoding='utf-8'):
        raise RuntimeError('Expected v4.5.1 Terraforming Editor source')

    once(tile,
        '    var resourceAmount: Int = 0\n',
        '''    var resourceAmount: Int = 0
    // %s: persisted along with tile data; only deliberately edited resources.
    var magalanaduTerraformResource: String? = null
''' % MARK)
    once(tile,
        '''        toReturn.resource = resource
        toReturn.resourceAmount = resourceAmount
''',
        '''        toReturn.resource = resource
        toReturn.resourceAmount = resourceAmount
        toReturn.magalanaduTerraformResource = magalanaduTerraformResource
''')
    once(tile,
        '''        val resource = tileResource // To avoid additional checks later
        if (!civInfo.canSeeResource(resource)) return false
''',
        '''        val resource = tileResource // To avoid additional checks later
        // Magalanadu terraformed and owned deposits generate their stated
        // resources even if an extractor cannot be placed on unusual terrain.
        // Normal non-terraform resources still obey tech and improvement rules.
        if (resource != null && civInfo.civName == "Magalanadu"
            && magalanaduTerraformResource == resource.name && getOwner() == civInfo) return true
        if (!civInfo.canSeeResource(resource)) return false
''')
    once(normalizer,
        '''            if (resourceObject.terrainsCanBeFoundOn.none { it == tile.baseTerrain || tile.terrainFeatures.contains(it) })
                tile.tileResource = null
''',
        '''            // %s: manual edits persist through save reload and cloning.
            // All unmarked/naturally generated resources remain terrain-validated.
            if (tile.magalanaduTerraformResource != resourceObject.name &&
                resourceObject.terrainsCanBeFoundOn.none { it == tile.baseTerrain || tile.terrainFeatures.contains(it) })
                tile.tileResource = null
''' % MARK)
    once(civ,
        '''        if (resource == null) return false
        return tech.isRevealed(resource)
''',
        '''        if (resource == null) return false
        // %s: the player sees Coal, Uranium etc without
        // researching their reveal technologies. Other civs remain unchanged.
        if (civName == "Magalanadu") return true
        return tech.isRevealed(resource)
''' % MARK)

    # The editor is copied by the cumulative v4.3 patch. Confirm that the
    # source is the exact version being shipped in this kit.
    required = source.read_text(encoding='utf-8')
    active = editor.read_text(encoding='utf-8')
    if active != required:
        # Do not silently replace an unfamiliar editor in an existing checkout.
        if MARK in active:
            raise RuntimeError('Partial or unexpected resource patch: Terraform editor mismatch')
        editor.write_text(required, encoding='utf-8')
        print('UPDATED:', editor)
    print('PASS: Magalanadu v4.5.1 any-terrain resource editing (save-safe)')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_5_1.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
