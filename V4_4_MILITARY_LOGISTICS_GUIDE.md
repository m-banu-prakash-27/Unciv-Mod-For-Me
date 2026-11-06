# Magalanadu v4.4: Armament Depots and Global Paradrop

Target: Unciv **4.22.16** with the cumulative Magalanadu v4.3.1 engine patches.

## What is added

**Armament Depot building:** Build or buy **Magalanadu Armament Depot** in a Magalanadu city. It creates a selectable city-centre spawning location.

**Arms Depot improvement:** The existing **Arms Depot** terrain improvement now serves as a practical unit-deployment point when built on a tile owned by a Magalanadu city. The Super Cheat Worker can now construct it immediately.

**Choose a spawn site:** Select any Magalanadu unit, open **MAGALANADU STRATEGIC DIRECTORATE**, then **MILITARY LOGISTICS: Armament Depots & unit spawning**. Choose a city and one of its eligible depot sites. The chosen site is stored on the city's save-game data and survives end turns and reloads. One production site per city can be selected at a time.

**Normal production routes to the depot:** Units constructed or purchased by the city should spawn on the selected depot tile, or at the closest legal available tile found by the existing Unciv unit-placement routine. If no depot is active, the normal city spawning position is used. Naval units continue using coastal city placement to avoid invalid inland deployments. This does **not** teleport units produced before the depot assignment.

**Instant spawning:** With an active depot selected, use the menu to choose a land, naval, air, civilian or any ruleset unit, and spawn batches of **1, 5, or 10** immediately. These are explicit cheat operations and charge no Gold or Production. The game can place units next to, rather than exactly on, the depot if stacking or terrain rules prevent placement. Units are not created when the game cannot find a valid tile.

**Unlimited paradrops:** A Magalanadu **land unit** (military or civilian) has the standard **Paradrop** action regardless of a native paratrooper unique. It can drop to any **previously explored**, otherwise legal land tile, with no distance limit. Unit stacking, impassable terrain and normal foreign-territory permission rules remain in force. Units that have moved this turn cannot initiate a new paradrop. Water/naval and aircraft are excluded. Other civilizations' paradrop ranges stay unchanged.

**Performance:** For unlimited paradrops, the patched game checks the actual map tile list instead of generating a giant theoretical radius; this avoids the catastrophic O(radius²) enumeration. Keep individual instant spawn batches to 10 units. Much larger maps may still produce a brief UI delay when showing global paradrop destinations.

## APK build

1. Publish the v4.4 targeted ZIP to `m-banu-prakash-27/Unciv-Mod-For-Me` using the included `Run_Publisher.bat` and `PUBLISH` confirmation. The publisher creates and pushes a backup branch before changing main.
2. GitHub Actions: select **Build Magalanadu v4.4 Military Logistics APK** and manually run it on `main`.
3. After a **green successful** run, download artifact `Magalanadu-v4-4-Military-Logistics-Android-APK` and extract the APK.
4. Back up your save before replacing the prior custom APK. This build uses a **separate** app ID `com.unciv.magalanadu.v44` so it can be installed alongside the earlier working custom Magalanadu APK. Install the mod in the new app and import any saves only after backing them up.
5. Test an actual City Armament Depot and an Arms Depot improvement, 1/5/10 spawn batches, routing of a naturally built unit, save/reload persistence, and global paradrop on explored legal land.

## Limitations and safeguards

- **This kit contains engine source and workflows, not a compiled APK.** Kotlin mock-interface compilation and offline tests are not a substitute for a successful Android Gradle build and in-game verification.
- Does not allow multiple military units on one hex. Units appear on adjacent valid terrain when needed.
- Depot improvements must be owned by the relevant Magalanadu city; improvements outside borders are not recognized until that tile belongs to the city.
- The original map/editor and diplomatic systems are not changed by this feature.
- The building uses a deliberately reused atlas icon from Magalanadu Military Mobilization, so a valid PNG + atlas region exists without repacking textures.
- Legacy validation scripts were updated to acknowledge one *new* legitimate building and icon. Historical backup JSON files are unchanged.
- On-demand spawned units use the regular unit-placement path; they do not pay city production and are not necessarily treated as "trained units" for every construction-only bonus. Normally constructed units still receive their ordinary training bonuses.
