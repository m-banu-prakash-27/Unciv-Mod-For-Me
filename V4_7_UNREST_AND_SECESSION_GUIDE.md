# Magalanadu v4.7 Unrest and Secession

## Play

1. In an offline game as Magalanadu, select one of your units. Open **Magalanadu Strategic Directorate → Unrest and Secession**.
2. Choose a known foreign major civilization. Select **Foment unrest in all cities** or select one city and foment unrest there.
3. Confirm. The affected cities enter normal Unciv resistance for at least eight turns.
4. While the city is in resistance, select it again and choose **Create an independent major civilization** or **Create an independent City-State**.
5. Pick an unused identity from the active ruleset and confirm. The city keeps its name, becomes the capital of the new AI-controlled nation, and transfers with its territory. The new nation starts at peace with Magalanadu and its former owner. It inherits completed technologies from the former owner. The former owner's army and diplomacy stay with the former owner.
6. Use **Back to [civilization]** to handle another city. Each confirmed secession uses one available nation identity.

Original capitals and the former owner's last city are protected. The supply of breakaway identities depends on the active ruleset and the civilizations already in the save. The campaign objective feature from v4.6 remains available separately.

## Build

- **Android**. Run **Build Magalanadu v4.7 Unrest and Secession APK** on the repository's Actions tab. Download the **Magalanadu-v4-7-Unrest-Secession-Android-APK** artifact after the build succeeds. The app uses a separate package ID. Import a backed-up save and install the Magalanadu ruleset in the new app.
- **Windows**. From the Magalanadu repository, apply `python engine_patch/patch_unciv_v4_7.py C:\path\to\Unciv` to a fresh checkout of Unciv 4.22.16. From the patched game folder with Java 21, run `.\gradlew.bat :desktop:dist` and then `java -jar .\desktop\build\libs\Unciv.jar`.

## In-game checks

- Foment unrest in one city, then across the target. Check the timer and save/reload during resistance.
- Release an eligible city as a City-State, then release another as a major civilization. Advance a turn, save and reload. Check territory, the new capitals, diplomacy, and city-state actions.
- Confirm the old civilization still has its capital, foreign units are displaced where applicable, and original capitals stay protected. Check that the same nation identity cannot be chosen twice.
- Start a campaign objective and make its target city secede. Check that the ownership change records a city-loss result.
