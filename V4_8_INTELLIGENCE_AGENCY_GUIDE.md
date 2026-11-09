# Magalanadu v4.8 Intelligence Agency

In an offline game as Magalanadu, select one of your units and open **Strategic Directorate → Intelligence Agency**. Meet a foreign civilization, pick a mission, select its target, and choose Standard or Careful. Advance the turn to execute queued missions.

You can run three missions at once, one per target civilization. Gold is paid upfront. Careful planning costs 25 more Gold and one more turn. It improves the success estimate and lowers the exposure estimate. Heat reduces success and raises exposure. It cools by four points per turn. A successful operation can still be exposed, which raises heat, costs one access, and worsens relations.

Start with **Recruit a local source**, then **Plant an agency mole** to build access and leverage. Use a station, route or safehouse to improve your network. **Active operations** lets you lay low once per mission or abort. Laying low delays it by two turns and reduces heat by up to 15. **Network dossiers** and **Operation reports** show progress and outcomes. Networks, active missions and reports are stored in the save. Operations recheck targets when they resolve, and an obsolete target may leave a mission without an effect.

## The 34 Unciv missions

| Group | Mission | Effect |
|---|---|---|
| Intelligence | Field surveillance | Explores the city and nearby terrain. |
| Intelligence | Signals interception | Reports wars, trade partners and strategic supply. |
| Intelligence | Military reconnaissance | Reports army composition and the strongest unit's location. |
| Intelligence | Scientific dossier | Reports current research and eligible technology thefts. |
| Intelligence | Break into archives | Adds two leverage. |
| Intelligence | Interrogate captured agent | Uses a captive to obtain a research report and two leverage. |
| Networks | Recruit a local source | Adds one access. |
| Networks | Plant an agency mole | Adds two access and one leverage. |
| Networks | Open an intelligence station | Adds seven success points on later operations against the target. |
| Networks | Open a smuggling route | Reduces exposure by ten points on later operations against the target. |
| Networks | Prepare a safehouse | Adds cover and reduces heat. |
| Networks | Exfiltrate compromised assets | Spends access to reduce heat. |
| Networks | Turn a captured agent | Uses a captive to gain access and cover. |
| Networks | Counterintelligence sweep | Captures a rival spy operating in a Magalanadu city. |
| Influence | Broadcast propaganda | Improves diplomatic opinion or gains City-State influence. |
| Influence | Expose a scandal | Spends leverage to damage the target's standing with known major civilizations. |
| Influence | Blackmail officials | Spends leverage to extract up to 400 Gold. |
| Influence | Plant disinformation | Worsens relations between two foreign civilizations. |
| Influence | Stage a false flag | Sabotages the capital's active production and attributes the action to a third party. |
| Influence | Bribe intermediaries | Transfers 100 Gold to the target from the operation budget and gains goodwill. |
| Influence | Backchannel ceasefire | Creates a native peace treaty between two foreign major civilizations. |
| Influence | Disrupt a trade corridor | Cancels matched commercial trade records, preserving treaties and agreements. |
| Covert action | Steal technology | Acquires an eligible researched technology from the target. |
| Covert action | Sabotage construction | Removes half the accumulated Production on the active project. |
| Covert action | Sabotage infrastructure | Uses native pillage mechanics on an improvement or road. |
| Covert action | Sabotage research | Removes half the stored Science on the target's active research. |
| Covert action | Raid the treasury | Transfers up to 300 Gold from the target. |
| Covert action | Eliminate a Great Person | Removes a foreign Great Person from the chosen city's territory. |
| Covert action | Expel a hostile spy | Returns a rival spy operating in a Magalanadu city to its hideout. |
| Conflict | Organize resistance | Incites native resistance in a city of a foreign major civilization. |
| Conflict | Back a capital coup | Spends leverage to relocate the government to a resisting city. The former capital goes into resistance. |
| Conflict | Sponsor independence | Turns an eligible resisting city into the selected unused nation or City-State. Original capitals and the last city remain protected. |
| Conflict | Arm a proxy | Deploys a buildable land military unit at the chosen recipient city. |
| Conflict | Instigate a proxy war | Spends leverage to trigger a legal declaration of war between two major civilizations. |

**Mission chains**

- Recruit a local source → Plant an agency mole → Break into archives → Back a capital coup or Instigate a proxy war. A coup also requires a resisting city other than the target's current capital.
- Organize resistance → Sponsor independence → Arm a proxy in the new capital. The breakaway identity must still be unused when the operation resolves.
- Counterintelligence sweep → Interrogate captured agent or Turn a captured agent. These chains depend on native espionage being enabled and a rival spy actually being present.

## Research and adaptation

Espiocracy is listed as unreleased, with 34 operation types advertised. Its public diaries illustrate mission families and selected operations. This is a catalogue of 34 original Unciv adaptations grounded in those examples. The implementation models the game through Unciv's cities, technology, units, native spies, trade and diplomacy. For example, an assassination targets a Great Person and a coup relocates the seat of government.

- [Steam listing and feature overview](https://store.steampowered.com/app/1670650/Espiocracy/)
- [Operations 2.0 and preparation, exposure, pause and abort](https://store.steampowered.com/news/posts/?enddate=1670617019&feed=steam_community_announcements)
- [Espionage gameplay, assets and networks](https://store.steampowered.com/news/posts/?enddate=1697234624&feed=steam_community_announcements)
- [Developer diary index for propaganda, coups, counterintelligence, false intelligence and signals intelligence](https://steamcommunity.com/app/1670650/discussions/0/3183486955467718303/)

## Build

- On Android, run **Build Magalanadu v4.8 Intelligence Agency APK** in GitHub Actions. Download **Magalanadu-v4-8-Intelligence-Agency-Android-APK** when the build succeeds. Install the APK and Magalanadu ruleset. The app has a separate package ID, so import a backed-up save as needed.
- On Windows, apply `python engine_patch/patch_unciv_v4_8.py C:\path\to\Unciv` to a fresh Unciv 4.22.16 checkout. In the patched checkout with Java 21, run `.\gradlew.bat :desktop:dist`, then `java -jar .\desktop\build\libs\Unciv.jar`.
- Try a new game first. Queue a recruitment mission, save and reload, lay low, advance the turn and check the report. Then test a hostile operation, a paired diplomacy operation and a native espionage operation. Reopen the menu to check the network and reports.
