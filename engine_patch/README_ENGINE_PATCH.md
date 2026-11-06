# Magalanadu v3.2 — Unciv engine patch kit

**Target is Unciv tag 4.22.16 source**, not another mod folder. This package is NOT an Android APK and cannot be installed into the game's Mods menu. It must be applied to a checked-out Unciv source tree and built into a customized game application.

## What this patch changes

1. Lets Magalanadu gift its units to **non-hostile major civilizations without Open Borders**. Select a Magalanadu unit while it is on a target civilization's tile OR an adjacent tile and use `Gift to [Civilization]`. Adjacent gifting works even when closed borders prevent entering the target tile. Existing City-State rules remain unchanged.
2. After an adjacent major-civ gift, lets Unciv relocate the unit if the recipient cannot stand on its previous tile.
3. Pays the v3.1 2× Production Cost export Gold bonus for Magalanadu gifts across a border. Gifts made inside foreign tiles continue to use the existing v3.1 Gold trigger. This is **not** a transfer from the recipient's treasury.
4. On creation of any Magalanadu unit, grants every applicable promotion in the installed ruleset, except one-time healing and harmful/hidden unavailable promotions. The standard mod additionally grants the three Magalanadu ability promotions.

## Apply to game source

1. Clone `https://github.com/yairm210/Unciv` with Git on a development machine.
2. Check out the exact `4.22.16` tag (use a separate feature branch before modifying).
3. Run `python patch_unciv_4_22_16.py PATH_TO_UNCIV_SOURCE`.
4. The script backs up two original Kotlin files. Review `git diff`.
5. Build the desktop or Android version using the upstream Unciv build instructions and its exact toolchain. You must install/use **that patched game build** to activate major-Civ gifts without Open Borders. Install the Magalanadu v3.2 mod into it as well.

The patch script is designed to fail if method signatures differ and not silently corrupt a different Unciv version. It is idempotent on a fully patched tree.

## Important limitations

- No compiled APK/JAR is included. The game **cannot** be changed by installing a JSON mod alone.
- The patch has not been compiled against all Unciv dependencies or gameplay tested here. Back up saves; test first in a new game on a test build.
- A recipient can receive a gifted Science Envoy or Technology Ambassador, but an AI civilization is **not guaranteed to activate** its special research action.
- The patch makes it possible to gift units. It does not support forcing recurring Gold-per-turn payments or withdrawing resources from the recipient. That would require separately modifying diplomacy trade logic.
- For Magalanadu, gifting a unit that stands on a recipient-owned tile still uses v3.1's conditional on-losing-unit Gold trigger; losses from other causes in similar territory may also trigger it. No fully native gift-only trigger exists in stock v4.22.16.
- The patch may need adjustments for additional Unciv versions and loaded base rulesets.

## Optional: restore source

Restore `UnitActions.kt` and `UnitManager.kt` from their `.before-magalanadu-v3.2` backups, then rebuild.

## Optional GitHub Actions Android build

The accompanying Magalanadu v3.2 mod ZIP contains a ready-to-run `.github/workflows/build-magalanadu-patched-android.yml` and the same patcher under `engine_patch/`. If you push the full mod repo to GitHub, run that workflow under GitHub Actions to attempt to build a separate Android debug APK. See `ANDROID_CUSTOM_BUILD.md` in the mod. No APK build has been executed or validated here.
