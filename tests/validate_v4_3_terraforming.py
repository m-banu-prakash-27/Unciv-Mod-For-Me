#!/usr/bin/env python3
from pathlib import Path
r=Path(__file__).resolve().parents[1]
k=(r/'engine_patch/MagalanaduTerraformEditor.kt').read_text()
p=(r/'engine_patch/patch_unciv_v4_3.py').read_text()
w=(r/'.github/workflows/build-magalanadu-v4-3-android.yml').read_text()
for phrase in ['object MagalanaduTerraformEditor','consumeTileClick','chooseBaseTerrain','chooseFeature','chooseResource','chooseResourceAmount','chooseWonder','chooseImprovement','chooseRiver','chooseRoad','TileNormalizer.normalizeToRuleset','screen.shouldUpdate = true','tile.setTerrainTransients()','setConnectedByRiver','tile.resourceAmount']:
    assert phrase in k, phrase
for phrase in ['MAGALANADU_V4_3_TERRAFORM_TILE_SELECT','MAGALANADU_V4_3_TERRAFORM_MENU','apply_v4_2(root)','MagalanaduTerraformEditor.kt']:
    assert phrase in p,phrase
assert 'patch_unciv_v4_3.py game' in w
print('PASS: v4.3 tile editor source, save-field writes, world refresh and build wiring')
