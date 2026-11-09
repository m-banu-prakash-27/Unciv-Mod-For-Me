> For the current cumulative Android release, see the [v4.9.1 build guide](V4_9_1_UNCIV_UPDATE.md). This document describes the original gifting build.

# Build a patched Unciv APK with GitHub Actions (Android)

**The mod ZIP alone cannot bypass Unciv's major-Civ gifting check.** That behavior is compiled into the game. To use the new gift menu without Open Borders, you need a patched Unciv application.

The mod repository includes an optional GitHub Actions workflow: `.github/workflows/build-magalanadu-patched-android.yml`.

## Build from GitHub (no local Android SDK needed)

1. Push **v3.2** of the mod to `https://github.com/m-banu-prakash-27/Unciv-Mod-For-Me`, including the `engine_patch/` and `.github/workflows/` folders. The publisher ZIP can do this.
2. Open the repository on GitHub -> **Actions** -> **Build Magalanadu custom Unciv Android APK** -> **Run workflow**.
3. If the workflow passes, open the workflow run and download the `Magalanadu-patched-Unciv-4.22.16-debug-APK` artifact. It contains a debug APK built on GitHub's Android runner.
4. Install the downloaded APK on your Android device (Android will ask you to allow this source to install an APK). The debug build uses an **independent package ID** `com.unciv.magalanadu`, so it should not overwrite official Unciv.
5. In the new app's Mods menu, install **Magalanadu v3.2**, select it in a new game's setup, and test Science Envoy / Technology Ambassador donation to a major Civ from an adjacent border tile.

**Note:** This GitHub workflow has not been executed here and may need fixes for upstream dependencies or newer Android SDK rules. An APK is only available if the workflow finishes successfully. This is an experimental development build, not a verified official app.

## Why not simply install the mod?

Unmodified Unciv 4.22.16 runs this hardcoded test before showing Gift Unit for a major civilization:

`else if (!tile.isFriendlyTerritory(unit.civ)) return@sequence`

This is separate from movement permissions and cannot be changed by the JSON ruleset. The v3.2 Kotlin patch replaces this condition *for Magalanadu* and lets it donate units from inside or immediately next to other non-hostile major-Civ borders. City-State donations remain supported.

## Promotions

New Magalanadu custom units have all three original special ability promotions even in the stock app. Trained units also receive compatible standard G&K promotions through the v3.2 ruleset. The patched app extends these grants to newly spawned units, choosing compatible promotions from the loaded ruleset.

## Important

- Back up your official Unciv saves before experimenting; the custom debug app keeps separate app data and needs fresh saves/mod installation.
- Debug APKs are signed differently than store releases and are not supported by the Unciv team.
- We have not compiled, signed, installed or run this APK in the current environment.
- Gifted units belong to the recipient, but AI research envoys may not know how to trigger custom research effects.
