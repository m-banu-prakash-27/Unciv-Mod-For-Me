# Magalanadu v4.6 Campaign Objectives

## Play a city-defense objective

1. In an offline game as Magalanadu, meet two major civilizations at war with each other. Magalanadu must be at peace with both. An existing war or one started using the Directorate's Proxy War action qualifies.
2. Select one of your units and open **Magalanadu Strategic Directorate → Campaign Objectives → Start a city-defense objective**.
3. Choose the civilization to defend, its rival, and a city that the defender owns. Confirm the objective.
4. Keep the city under the defender's control for **20 turns** and stay at peace with both participants. Use troop gifts, arms contracts, or normal trade if you want to help. If the participants make peace, the countdown continues.
5. Reopen Campaign Objectives to see the countdown or the last result. Success awards **500 Gold** once and sends a notification. You can cancel an active objective and start a different one. Only one can be active at a time.

The objective fails when the defender loses the selected city through transfer or destruction, even if it is retaken immediately. It also fails when Magalanadu enters a war against either participant. An objective's progress and result are part of the saved game. Use the v4.6 custom game when resuming it.

## Build on Android

1. Extract this ZIP and place the contents of the enclosed repository folder at the root of your Magalanadu repository, including the hidden `.github` directory.
2. Open GitHub Actions and run **Build Magalanadu v4.6 Campaign Objectives APK** from the branch that contains the workflow. A new workflow must be on the default branch before GitHub exposes manual dispatch.
3. After the run succeeds, download **Magalanadu-v4-6-Campaign-Android-APK**, extract the APK, and install it. It uses a separate Android package ID, so import a backed-up save and install the Magalanadu ruleset in the v4.6 app as needed.

This source package contains the full mod and cumulative engine patches. The campaign menu requires a rebuilt custom game.

## Build on Windows

With Java 21, Python 3, and a fresh checkout of Unciv tag `4.22.16`, run the cumulative patcher from the Magalanadu repository folder. Then build the desktop JAR from the patched game folder.

```powershell
python engine_patch/patch_unciv_v4_6.py C:\path\to\Unciv
cd C:\path\to\Unciv
.\gradlew.bat :desktop:dist
java -jar .\desktop\build\libs\Unciv.jar
```

## In-game verification

- Start an objective and save/reload with several turns left. Verify the city, participants and deadline persist.
- Keep the city for all 20 turns and check that 500 Gold is credited once. Reload the completed game and advance another turn.
- In separate attempts, lose the city, enter the war against a participant, and cancel from the objective menu. Verify the relevant result appears and the reward is withheld.
- Have the participants sign peace before the deadline. Check that the objective remains active.
