# Magalanadu v4.2: radius 14, 60% land / 40% water territory

## The requested behavior
- **Radius is 14 in all six hex directions**, potentially **631 hexes** including the center. This is approximately **379 land / 252 water** at a 60:40 mix on a sufficiently large and suitably shaped map.
- Both **city working range** and **cultural border expansion range** are 14 for Magalanadu. Other civilizations keep their original ruleset ranges of 5.
- Normal cultural expansion **actively favors tiles that bring the city's actual claimed territory closer to 60% land / 40% water**, using current tiles and the adjacent, unowned border frontier. The preference applies automatically as culture claims tiles.
- New Strategic Directorate option: **CLAIM TERRITORY: 14 radius, target 60% land / 40% water**. Select a Magalanadu city, view its actual land/water count, and claim **10, 25, or 40 tiles** in one action, respecting ownership and contiguous expansion. Repeat to expand farther. Small batches avoid hundreds of expensive city-stat updates on Android.
- **Water** means all water tiles, including Coast, Ocean and Lakes. The system does not turn land into ocean, fabricate sea tiles, annex another civilization's territory, or guarantee resource deposits. It only claims unowned tiles actually present on the map.
- **Settling** retains the normal city-centre + adjacent first-ring behavior. Since the centre is normally land, initial percentage may not be 60/40. After founding, auto cultural growth and Directorate claims move toward the target as geography allows. A landlocked city with no water in range cannot meet a strict 40% water quota without editing the map itself. No silent terraforming is performed.
- Existing resource deposit effects and access, improvements and special buildings from prior releases are unchanged. The Omni Generator supplies resources separately from the natural map deposits.

## Performance and compatibility
- 14-radius maximum = 631 tiles, compared with 35,317 tiles at radius 108. On a 14-radius claim this is a **98.2% reduction** in maximum range candidates relative to 108.
- City-screen local viewport remains 12, to avoid rendering too many full tile actors. Cultural expansion and city work range remain 14 in engine logic.
- Border expansion considers only adjacent unowned frontier tiles. Batch claiming is capped at **40** per click. This should reduce freezes but does not guarantee mobile performance on huge maps or dozens of cities.
- This is a **custom Unciv 4.22.16 engine patch**, not a change to standard jsons/ModOptions.json, because the limits only apply to Magalanadu.
- Previous v3.2 unit gifts/promotions and v4.0 Directorate (proxy wars, resource concessions, covert sabotage and arms contracts) are preserved.

## Install / build
1. Extract `Magalanadu_v4.2_GitHub_Publish_Kit.zip` and double-click `Run_Publisher.bat` on Windows. You must have Git for Windows and GitHub write access. The script backs up the GitHub branch, shows a preview, then asks you to type `PUBLISH`.
2. In the repository's GitHub Actions, run **Build Magalanadu v4.2 14-Radius Balanced Territory APK** on `main`.
3. Download `Magalanadu-v4-2-Balanced-14-Radius-Android-APK`, extract and install the APK. Install/enable the Magalanadu mod too.
4. Test in a **new game** first. Select a Magalanadu unit -> **MAGALANADU STRATEGIC DIRECTORATE** -> **CLAIM TERRITORY** -> select city -> claim 10 tiles. Observe the new count. Try a coastal city and an inland city to see geographical limits.
5. Back up saves before replacing the custom APK. Initial offline tests do not replace a full successful Gradle Android build and real in-game checks.

## Known limitations
- Exact 60:40 coverage is **not guaranteed** on arbitrary maps. This version implements **preferential claiming toward 60:40** rather than creating water or blocking inland settlements.
- Automatic settlement-site veto/placement assistant and permanent terrain transformation are not included.
- The batch claim is a cheat operation that may be unavailable for puppet, razing or resisting cities. Standard cultural border growth continues to work normally.
- Rebuild the custom APK: the v4.1 APK cannot gain engine-level features merely by replacing JSON.
