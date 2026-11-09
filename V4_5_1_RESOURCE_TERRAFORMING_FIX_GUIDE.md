# Magalanadu v4.5.1: Coal, Uranium, and all-resource Terraforming fix

Base: Unciv 4.22.16; cumulative source patch includes earlier Magalanadu v4.5 features.

## Diagnosis

The previous Terraforming Editor rejects resource placement on a tile unless the tile's terrain is in `TileResource.terrainsCanBeFoundOn`. Unciv's `TileNormalizer` will also remove a resource on an incompatible terrain when validating or reloading the map. Independently, Coal, Uranium and other strategic resources are hidden until their reveal technologies are researched. A tile with a resource might not contribute supply until a suitable improvement has been constructed and the civilization owns that tile.

Iron commonly works because it is compatible with many more terrain types and is revealed earlier in the technology tree.

## Fix and exact behavior

- You can select ANY available ruleset resource on ANY explored map tile, regardless of natural terrain compatibility. Natural wonders still cannot share a tile with a resource.
- All manually placed resources are recorded in the tile's serialized `magalanaduTerraformResource` property. That marker is copied in `Tile.clone` and checked by `TileNormalizer`. Only marked resources bypass natural terrain restrictions; ordinary map resources keep their original validation.
- Magalanadu sees all resource types regardless of reveal technology. Other civilizations still use their normal technology requirements.
- A **Magalanadu-owned** tile bearing a manually placed resource contributes its resource supply without needing a terrain-compatible extraction improvement. Strategic resources provide the exact deposit count chosen in the editor. Luxury resources provide one copy per tile; bonus resources affect normal tile yields. Neither foreign-owned nor neutral resources become Magalanadu-owned simply because they were edited.
- The editor offers 1, 5, 10, 25, 50, 100, 250, 500, 1000 and 9999 units for strategic deposits.
- Resource removals and wonder placements clear the override marker. The editor checks for silent resource deletion and rolls back failed changes.
- Save normally and reload to verify persistence. Use the *v4.5.1 custom app*, not official Unciv, for saves containing the custom marker.

## Strategic resource rule audit (Civ V Gods & Kings base ruleset)

| Resource | Original reveal technology | Natural terrains | Normal extractor |
|---|---|---|---|
| Horses | Animal Husbandry | Plains, Grassland, Hill | Pasture |
| Iron | Iron Working | Grassland, Plains, Desert, Tundra, Snow, Hill, Marsh | Mine |
| Coal | Industrialization | Grassland, Plains, Hill, Jungle, Forest, Marsh | Mine |
| Oil | Biology | Desert, Coast, Tundra, Snow, Marsh, Jungle | Oil Well or Offshore Platform |
| Aluminum | Electricity | Desert, Tundra, Hill, Snow, Jungle | Mine |
| Uranium | Atomic Theory | Marsh, Jungle, Forest, Tundra, Snow | Mine |

The v4.5.1 editor explicitly bypasses the natural terrain and reveal restrictions **only for the authorized Magalanadu player** in the patched game. It does not rewrite the base game resource definitions or require an illegal improvement on a water tile.

The normal ruleset contains **35 resources**: 6 strategic, 22 luxury, 7 bonus. The editor enumerates the *currently active ruleset* instead of depending on a hardcoded 35-item list, so additional compatible mod resources are also selectable. The special City-State luxuries Jewelry and Porcelain have no natural terrain list, but can be deliberately placed using the new editor.

## Build and install

1. Publish the four changed/new source files and this guide using the supplied targeted GitHub publisher. The existing mod's `jsons/` and image atlases are NOT replaced.
2. In GitHub Actions, choose **Build Magalanadu v4.5.1 Any-Terrain Resource Fix APK**, then **Run workflow** on `main`.
3. After a green build, download the `Magalanadu-v4-5-1-Resource-Fix-Android-APK` artifact and extract the APK.
4. This build uses `com.unciv.magalanadu.v451` to avoid overwriting a working custom app. Export/import existing saves and install the Magalanadu mod within the new app. Back up saves before migrating.
5. In a copied save, open Strategic Directorate > Live Terraforming, select Grassland, add Uranium 50, save/reload. Repeat on Snow with Coal 50 and on a normal Iron tile. Check Magalanadu's resources overview after owning those tiles.

## Validation limits

The Python tests verify expected engine anchors, source transformations, idempotence, resource enumeration and the prior mod regression suite. They cannot prove a completed Android APK compilation or gameplay behavior. Build it via GitHub Actions and check in-game on a copied save before trusting your primary save.
