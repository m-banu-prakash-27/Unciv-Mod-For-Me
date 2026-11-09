# Magalanadu v4.9.1 for Unciv 4.22.18-patch1

The base game is [Unciv 4.22.18-patch1](https://github.com/yairm210/Unciv/releases/tag/4.22.18-patch1), GitHub commit [2043d26](https://github.com/yairm210/Unciv/commit/2043d26deec1278e11d864a2323230e2ea0a7ab6). The cumulative build includes native spy recruitment and all 34 operations, campaign objectives, unrest and secession, military logistics, bulk resource acquisition, and the resource and terrain editors.

## Build on GitHub

1. Extract the publisher kit and double-click **Run_Publisher.bat** on Windows. Review the staged changes and enter **PUBLISH**.
2. Run **Build Magalanadu v4.9.1 Android and Windows** under GitHub Actions.
3. Download **Magalanadu-v4-9-1-Android-APK** for Android or **Magalanadu-v4-9-1-Windows-x64** for Windows. On Windows, extract the inner **Unciv-Windows64.zip** and run **Unciv.exe**.
4. Install Magalanadu as a mod in the custom game and enable Espionage when setting up an offline game. The Android build uses a separate package ID. To resume an existing game, import a backed-up save into the new app.

## Build locally

Use Java 21 and a fresh checkout of Unciv tag `4.22.18-patch1`. From the Magalanadu source folder, run:

```powershell
python engine_patch/patch_unciv_v4_9_1.py C:\path\to\Unciv
```

From the patched Unciv checkout, run `.\gradlew.bat :desktop:dist :desktop:zipWindows64` to package the Windows executable. The archive is written to `deploy\Unciv-Windows64.zip`. Use `.\gradlew.bat :android:assembleDebug` with the Android SDK to build locally for Android. The GitHub Android workflow sets a separate app ID before it compiles.

## Validation

The cumulative patch and earlier build entry points were checked against source files from the release tag. Ruleset and patch integration checks run before packaging. APK compilation, Windows executable packaging and in-game verification require a completed build.

## Build hotfix

The original v4.9.1 patch attached Kotlin's private setter to the spy agency field instead of the gold field. The corrected patch keeps the setter on gold and checks that layout during validation. After publishing the hotfix, start a new workflow run from the updated main branch. Rerunning a failed job uses its original commit.
