# Magalanadu v4.1: 108-hex city working and cultural expansion radius

## Exact implementation
- When a city's owner is **Magalanadu**, `City.getWorkRange()` and `City.getExpandRange()` return **108 hexes**. A full unobstructed hexagonal disc has **35,317 tiles**, including the center; actual tiles depend on map size, edges and occupied territory.
- Cultural tile expansion can claim **unowned** tiles at any radius up to 108 using the normal cultural-growth process. **It does not instantly seize the full disc or overwrite tiles already owned by other cities/civilizations**. The cultural frontier search only scores neighboring unowned tiles, minimizing CPU use on large maps.
- Population can work **empire-owned** plots up to 108 hexes away, subject to normal population and tile assignment mechanics. A radius of 108 does **not** mean 35,317 simultaneous workers or automatic global resource generation.
- The city screen deliberately shows a **12-hex viewport** for Magalanadu: rendering 35,317 full `CityTileGroup` actors at once can freeze Android. The city's ownership and working range remain 108 in the **engine**. Distant plots can be acquired through natural culture growth, and the working-tile automation considers acquired plots. Manual clicking on very distant tiles is not available in this local city-screen view.
- Normal civilizations and city-states keep the `jsons/ModOptions.json` range of **5**, untouched. The 108 override is a custom-APK feature, not a standard JSON-mod feature.

## Installation
1. Extract `Magalanadu_v4.1_GitHub_Publish_Kit.zip` and double-click `Run_Publisher.bat` on Windows. It adds only the v4 and v4.1 engine/workflow/test files, after creating a remote Git backup and asking for `PUBLISH`.
2. At GitHub Actions, run **Build Magalanadu v4.1 108-Radius Strategic Directorate APK** from `main`. Download the `Magalanadu-v4-1-108-Radius-Android-APK` artifact after a successful build.
3. Back up savegames, install the custom APK, and load a **new game** with Magalanadu v4.1. Existing saves may have cached city range data; reload the save after updating if testing compatibility.
4. Test cultural border expansion farther than 12, faraway tile assignment with a Magalanadu city, and city-screen performance. Compare a normal civilization to confirm its range remains 5.

## Limits and risks
- This source patch targets exactly **Unciv 4.22.16**. It should refuse to patch different layouts instead of silently mutating them.
- Large maps with dozens of Magalanadu cities may still experience slower turn processing and higher memory consumption because city-range sets can include many tiles. The 12-hex city-screen viewport and frontier-only expansion reduce two major risks but cannot guarantee performance.
- The engine patch changes only Magalanadu's **city work and city cultural-border expansion range**. It does not enlarge city bombardment, religious conversion range, diplomatic influence with city-states, or annex other civilizations' existing tiles.
- The existing 5x unit movement, 300-movement Settler, 50-resource Omni Generator, v3.2 gifting and promotions and v4.0 Directorate source remain intact.
- Full Android compilation and real gameplay still require a GitHub Actions build and an in-game test; offline regression tests are not a substitute.
