# Magalanadu v4.0 | Strategic Directorate (Unciv 4.22.16)

## What changed

This release retains **all 53 custom units, 24 buildings, 44 tile improvements**, the three Magalanadu ability promotions, 5x normal movement for custom units, 300-movement settlers, 50 supplies per resource from Omni Resource Generator, affordable buildings, and the fully functional v3.2 major-civilization gift behavior.

In **the custom v4.0 Android APK** (not standard Unciv), select **any unit owned by Magalanadu**, then choose **MAGALANADU STRATEGIC DIRECTORATE** in that unit's actions. The menu contains these working features:

1. **Force Proxy War**: pick two previously met major civilizations that know each other. Use **FORCE WAR NOW**. The attacker genuinely declares war on the defender via `DiplomacyManager.declareWar()`. The game's peace treaties and existing-war restrictions remain enforced, and defensive alliances can involve Magalanadu indirectly. The attacker transfers up to 250 Gold to Magalanadu as a consulting fee if it has Gold.
2. **Foreign Resource Rights**: choose a previously met major civilization or City-State with available non-stockpiled strategic or luxury resources, select a resource and quantity (1/5/10/25). Creates a real **30-turn or 9,999-turn bilateral resource trade**: target supply decreases and Magalanadu supply increases. Supply shortages can terminate the contract under Unciv's normal trade rules. These are commercial rights to resource supply, **not tile ownership** or city annexation.
3. **Covert Treasury**: steal treasury from a previously met major civ: Stealth costs 50 Gold, 75% success, transfers up to 300 Gold; Supreme guarantees a transfer of up to 1,000 Gold with no operating cost. Money is deducted from the target's actual treasury, not created out of thin air.
4. **City Construction Sabotage**: choose a rival and city, then Stealth (costs 100 Gold, 75% chance) or Supreme (guaranteed). Removes half the currently accumulated Production on the city's active project. Does not delete completed buildings.
5. **Strategic Disinformation**: choose two previously met major civs that know each other. Adds a -40 Denunciation diplomatic modifier in each direction. This worsens relations but **does not itself declare war**.
6. **Military Arms Contract**: use the same v3.2 adjacent-border or friendly-territory donation workflow. On a Magalanadu **military unit**, choose **Arms contract to [Civ]** instead of **Gift to [Civ]**. The recipient receives the unit and pays **Gold per turn for 20 turns**, calculated as `max(5, min(250, floor(Production cost / 20)))`. This is a real recipient-funded trade obligation; the v3.1 bounty system remains separately enabled. The normal free gift option is still available.

## Build and install

1. Publish the **complete v4.0 ZIP** to the dedicated repo with the Windows publish kit. It makes a remote backup branch before changing `main` and retains the last v3.2 APK workflow as a fallback.
2. Open **GitHub → Actions → Build Magalanadu v4.0 Strategic Directorate APK → Run workflow** on `main`.
3. If the Android compilation succeeds, download the **Magalanadu-v4-Strategic-Directorate-Android-APK** artifact and extract the APK.
4. **Back up your saved games**, install the APK, and update/install the Magalanadu v4.0 mod. The custom APK uses `com.unciv.magalanadu` and does not replace the official `com.unciv.app` installation.
5. Test a **new single-player game** first. Select any Magalanadu unit; open the new Directorate action. Then confirm resources and Gold actually change and that a saved/reloaded game preserves the contracts.

**Important limitations:** This update is source-level Kotlin code, not an ordinary JSON cheat. Mod ZIP alone cannot add the new menu or forced diplomacy; it must be used with a successfully compiled v4.0 custom APK. At package time, offline ruleset tests, patcher idempotence tests and Kotlin stub compilation passed, but the **complete v4.0 APK has not yet been compiled or tested in-game**. The previous v3.2 APK did compile and unit gifting was verified in-game by the user. The new resource, proxy-war, and contract code requires the new build and gameplay validation.

### Source files

- `engine_patch/patch_unciv_4_22_16.py`: previously validated v3.2 engine gift and full-promotion patch.
- `engine_patch/patch_unciv_v4_0.py`: adds the Directorate launcher and paid arms-contract alternative.
- `engine_patch/MagalanaduDirectorate.kt`: six concrete operation handlers, popups, saved resource and GPT trades.
- `.github/workflows/build-magalanadu-v4-android.yml`: new APK build workflow (previous v3.2 workflow retained).
- `tests/validate_v4_directorate.py`: checks correct wiring, preserves earlier patch and tests idempotence.

## Known behavior

- War orders honor the engine's `canDeclareWar` checks; they will not bypass active peace treaties.
- Resource contracts can end when goods are no longer available, as Unciv normally cancels unfulfillable trades.
- Arms-contract recipient payments may lower its treasury below zero over time if it cannot afford the contract. This is an intentionally powerful cheat.
- Major-civilization gifting works on already eligible tiles or across adjacent borders as in v3.2, but not from arbitrary locations on the map.
- Stealth operations use pseudorandom chances; repeated use may yield repeated transfers unless you voluntarily limit use. There is no covert detection/cooldown subsystem yet.
- Future game-version updates may require new source patch anchors. Designed for Unciv **4.22.16** only.
