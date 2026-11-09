# Magalanadu for Unciv 4.22.18-patch1

**Current release: v4.9.1.** See the [Android and Windows build guide](V4_9_1_UNCIV_UPDATE.md) and the [native spy operations guide](V4_9_NATIVE_SPY_OPERATIONS_GUIDE.md).

## v3.2 ruleset and gifting reference

**Target game:** Unciv 4.22.16, Civ V: Gods & Kings extension mod.

## Install this mod

Replace your old Magalanadu mod folder with the contents of this ZIP, and start a new game if possible. The regular ZIP can be installed on stock Unciv.

## Changes

- All 53 Magalanadu custom units (including Science Envoy and Technology Ambassador) spawn with the three original Magalanadu custom promotions. This includes new units, bought units, and starting units.
- Units trained in a Magalanadu city additionally receive all 91 listed G&K *compatible standard promotions*, using Unciv's built-in `relevant` promotion filter. One-shot Heal Instantly and the harmful Unable to pillage promotion are intentionally excluded. Compatibility is determined from the unit type in the loaded ruleset.
- All Magalanadu custom units can physically pass foreign territory where other movement rules permit, but **this does not bypass stock Unciv's Gift Unit rule**.
- Existing strategic/luxury worker Omni Resource Generator (+50 each), 5× custom movement, 300-point Settler, 24 buildings and 44 improvements are preserved.
- Gift revenue and City-State alliance bonuses from v3.1 remain. Native Gold rewards that trigger on unit loss can also arise from non-gift unit loss under similar conditions; this is a known limitation.

## Gifting to Major Civilizations

**Stock Unciv:** To gift to a major civ, move the unit into that civ's owned territory **when that territory counts as friendly for Magalanadu**, usually with Open Borders; select the unit and tap **Gift Unit**. You must have movement left and the unit cannot be transported.

**For full gifting without Open Borders:** The separate `Magalanadu_v3.2_Unciv_Engine_Patch_Kit.zip` contains a patch for the Unciv 4.22.16 *game source*. After building and installing your own patched Unciv app, a Magalanadu unit may gift to non-hostile major civilizations from inside their territory or from an adjacent border tile, even without Open Borders. City-State gifting rules remain unchanged. The patch also grants all compatible promotions to newly spawned Magalanadu units. **Installing this JSON mod alone does not modify the Android/desktop executable**.

**Important:** We could not compile or execute a patched Android APK in this environment. This is a source-code patch, not a working APK or proof of in-game compatibility. See the engine patch kit for exact build instructions and limitations.

## Test checklist

1. Start a fresh Magalanadu game. Produce Science Envoy and Technology Ambassador; open their promotions panel and verify the 3 Magalanadu abilities.
2. Train a combat unit (Indian Infantry): check the 3 custom abilities and compatible standard promotions like Shock I / Drill I.
3. On unmodified Unciv: open Open Borders, enter a major Civ's owned tile with movement left, and use Gift Unit.
4. On a patched executable: stand directly next to a major Civ's owned tile, select Science Envoy, and use Gift to [Civilization] without Open Borders.
5. Gift an aid unit to a City-State using the usual action and check Influence.
6. Save/reload and check unit ownership, Gold reward, and promotion persistence.

## Cloud build option for Android

See [ANDROID_CUSTOM_BUILD.md](ANDROID_CUSTOM_BUILD.md) for the optional GitHub Actions workflow to compile a separate debug APK containing the necessary source-level gifting change.
