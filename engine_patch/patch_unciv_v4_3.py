#!/usr/bin/env python3
"""Cumulative Magalanadu v4.3 terraforming + all v4.2 source patches for Unciv 4.22.16."""
from pathlib import Path
import sys
from patch_unciv_v4_2 import apply as apply_v4_2

HOOK = '    fun onTileClicked(tileView: TileView) {\n'
INJECT = '''    fun onTileClicked(tileView: TileView) {
        // MAGALANADU_V4_3_TERRAFORM_TILE_SELECT
        // While armed, the in-game terrain editor intercepts map tile selection.
        if (com.unciv.ui.popups.MagalanaduTerraformEditor.consumeTileClick(worldScreen, tileView)) return
'''
MENU_ANCHOR = '        popup.addButton("ARMS CONTRACTS: donate a military unit") {'
MENU_INJECT = '''        // MAGALANADU_V4_3_TERRAFORM_MENU
        popup.addButton("LIVE TERRAFORMING: edit a map tile") {
            popup.close()
            MagalanaduTerraformEditor.arm(GUI.getWorldScreen())
        }.row()
'''

def apply(root: Path):
    root=Path(root).resolve()
    dst=root/'core/src/com/unciv/ui/popups/MagalanaduTerraformEditor.kt'
    map_path=root/'core/src/com/unciv/ui/screens/worldscreen/worldmap/WorldMapHolder.kt'
    dir_path=root/'core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt'
    if all(p.is_file() for p in (dst,map_path,dir_path)) and all((
        'MAGALANADU_V4_3_TERRAFORM_TILE_SELECT' in map_path.read_text(encoding='utf-8'),
        'MAGALANADU_V4_3_TERRAFORM_MENU' in dir_path.read_text(encoding='utf-8'),
        'object MagalanaduTerraformEditor' in dst.read_text(encoding='utf-8'),
    )):
        print('PASS: v4.3 already installed; skipped')
        return
    apply_v4_2(root)
    for path in (map_path,dir_path):
        if not path.is_file(): raise FileNotFoundError(path)
    map_s=map_path.read_text(encoding='utf-8')
    dir_s=dir_path.read_text(encoding='utf-8')
    if 'MAGALANADU_V4_3_TERRAFORM_TILE_SELECT' in map_s or 'MAGALANADU_V4_3_TERRAFORM_MENU' in dir_s or dst.exists():
        raise RuntimeError('Partial v4.3 patch found. Restore clean checkout and rerun.')
    if map_s.count(HOOK)!=1 or dir_s.count(MENU_ANCHOR)!=1:
        raise RuntimeError('Unciv 4.22.16 or v4.2 source does not match expected anchors')
    src=Path(__file__).with_name('MagalanaduTerraformEditor.kt')
    if not src.exists():raise FileNotFoundError(src)
    # Validate all required files before writes; do not alter v4.2 files.
    dst.write_text(src.read_text(encoding='utf-8'),encoding='utf-8')
    map_path.write_text(map_s.replace(HOOK,INJECT,1),encoding='utf-8')
    dir_path.write_text(dir_s.replace(MENU_ANCHOR,MENU_INJECT+MENU_ANCHOR,1),encoding='utf-8')
    print('PASS: Magalanadu v4.3 live tile editor installed on Unciv 4.22.16')

if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('Usage: python engine_patch/patch_unciv_v4_3.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]))
