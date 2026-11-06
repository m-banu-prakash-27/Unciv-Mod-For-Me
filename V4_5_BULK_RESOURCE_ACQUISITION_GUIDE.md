# Magalanadu v4.5: Acquire ALL resources at once

This is a cumulative update to v4.4 for the custom Unciv 4.22.16 Android APK.

## New options

1. Select a Magalanadu unit and open `MAGALANADU STRATEGIC DIRECTORATE`.
2. `FOREIGN RESOURCE RIGHTS`: select a **civilization or City-State**. In its menu:
   - `ACQUIRE ALL N RESOURCE TYPES (30 turns)`
   - `ACQUIRE ALL N RESOURCE TYPES (9,999 turns)`
   - Select an individual resource to buy a fixed quantity **or its entire currently available quantity**.
3. Alternatively, use `ACQUIRE ALL RESOURCES: every known civilization / City-State` from the Directorate's main menu, choose 30 or 9,999 turns, and confirm.

## Actual effects, not just interface labels

- One bilateral Unciv `Trade` object is created **per supplying civilization**. It contains one `TradeOffer` for every valid resource type, with the actual quantity.
- The resource supply is debited from the supplier and credited to Magalanadu. Each side holds a reversed copy of the same trade in diplomacy data, which is saved with the game.
- The menu re-reads the supplier's *current net supply* at confirmation time, so an existing transfer isn't duplicated by pressing Acquire All again.
- Hostile and defeated suppliers are skipped in the global operation. You can only operate on civilizations Magalanadu has discovered.
- The game remains responsible for trade expiry and early cancellation when the supplier no longer has the resource or diplomatic conditions change.
- **Only normal tradable Strategic and Luxury resources** are supported by these trade agreements. Bonus resources (Wheat, Fish etc.) and stockpiled resources are NOT transferred. Handling those would require a different custom game-economy system; this update does not pretend otherwise.

## Previous features kept

v4.4 armament depot unit spawning, world-wide paradrops, v4.3 terraforming, v4.2 radius 14 and 60/40 claimed land/water, v4.0 proxy wars, gifting and promotions.

## Publishing and building

1. Extract `Magalanadu_v4.5_GitHub_Publish_Kit.zip`.
2. Run `Run_Publisher.bat` on Windows. Requires Git for Windows and GitHub write access. It clones `main`, verifies the v4.3.1 purity compiler fix and existing v4.3 source, and pushes a timestamped backup branch before publishing.
3. Review the changed files, then type `PUBLISH`.
4. Open GitHub Actions, select **Build Magalanadu v4.5 Global Resource Acquisition APK**, and run it on `main`.
5. Download `Magalanadu-v4-5-Bulk-Resources-Android-APK` from the successful run's Artifacts.

**Validation**: Offline mod regression tests and Kotlin mock-API integration tests were run, but the full Android Gradle build and actual in-game behavior have not yet been verified. Back up saves first.
