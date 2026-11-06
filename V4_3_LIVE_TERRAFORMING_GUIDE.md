# Magalanadu v4.3: In-game Terraforming Editor (Unciv 4.22.16)

## What is included

All v4.2 features remain: 14-radius 60/40 territory preference, claims, Strategic Directorate, unit gifting, all starting promotions, resource deals, proxy wars, and arms contracts.

New: **LIVE TERRAFORMING** from the Directorate unit action. You can tap an explored map tile to edit its actual terrain, features, resource (with strategic quantity), natural wonder, improvement, road and river edges. The chosen edits are stored in Unciv's normal tile save fields. **Normal Save Game is still required** to persist edits to disk. `WorldScreen.shouldUpdate` requests a full sprite/map refresh after each operation. Save and reload if sprites or yields appear stale.

### Use in the game

1. Select a Magalanadu unit to open **MAGALANADU STRATEGIC DIRECTORATE**.
2. Select **LIVE TERRAFORMING: edit a map tile**.
3. Close the instruction message and tap any *explored* map tile. This opens the **MAGALANADU LIVE TERRAFORMING** menu.
4. Choose Base Terrain, Features, Resources, Natural Wonders, Improvements, Rivers or Roads. Follow menu instructions.
5. Repeat for other tiles. Click **STOP TERRAFORMING** when finished to restore ordinary map-click controls.
6. **Save Game**, then reload the save if any drawing or yields are not immediately updated.

### Data consistency safeguards

- No land/water conversions or impassable terrain are permitted under cities or units.
- Resource placement requires the resource to be valid on that terrain; change the base terrain first if necessary. Natural wonder placement removes incompatible features, improvements and resources.
- Natural wonder placement is prohibited directly under cities and units. Some natural wonders are designed to span several tiles; this editor places single tile entries only, so complex multi-tile arrangements are not guaranteed to match procedural map generation.
- It will not generate new map tiles or extend the actual map dimensions.
- Editing is disabled during other players' turns and for online multiplayer games.
- No automatic undo history. Back up saved games before editing.
- Editing rivers affects both tiles on the river edge.
- Changing tiles of other civilizations may affect their gameplay. AI and map-dependent caches can take a turn or a reload to fully update.
- Some rare combinations or map generator assumptions may be unstable despite the included checks. Prefer incremental edits and save a backup.

### Build

The v4.3 GitHub Actions workflow checks out vanilla Unciv **4.22.16**, applies the complete cumulative patch with `python engine_patch/patch_unciv_v4_3.py game`, and assembles a separately installable debug APK via `./gradlew --no-daemon :android:assembleDebug`. A successful workflow yields the `Magalanadu-v4-3-Terraforming-Android-APK` artifact.

**Validation levels:** Structural/integration patch tests run locally. Full Android compilation and real in-game rendering / saves are **not** verified until the GitHub Actions build succeeds and the user tests an installed APK.
