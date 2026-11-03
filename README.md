# Magalanadu v2.9: Balanced Advantage, Power Projects, and Enhanced Movement

**For Unciv 4.22.16 (Civ V: Gods & Kings extension).** This is a rebalance of the original personal mod, `Unciv-Mod-For-Me`, preserving the civilization, all 42 custom units, the 14 original buildings, all 9 original tile improvements and the 3 promotion groups.


## v2.9 movement upgrade (Unciv 4.22.16)

Every non-settler Magalanadu custom unit has **5×** its original v2.7 base movement (64 units). The **Super Cheat Settler** now replaces the normal Settler for Magalanadu and has **300 movement**, all tiles cost 1 movement, water traversal without embarking, and broader passage permissions. Aircraft and missiles have **5×** their original `range` as well because Unciv handles their relocation with range, not movement. See [MOVEMENT_UPGRADE_GUIDE.md](MOVEMENT_UPGRADE_GUIDE.md) for a complete table and testing caveats. Existing pre-upgrade Settlers in saved games may not be replaced automatically.

## What changed?

The civilization is still privileged, but no longer receives automatic 1,000% or 1,000,000% stat buffs. Its starting passive bonuses are now Gold +20%, Food +15%, Science +20%, Faith +15%, Culture +20%, Production +25%; territorial acquisition is cheaper, and defensive strength remains superior. All original special buildings and units still exist, with lower numerical effects and meaningful construction costs. Improvements no longer create thousands of copies of every resource. Existing graphic sprites, atlas data and expansion range 5 are kept.

**The cheats were moved into ten optional, player-triggered, repeatable construction projects.** You can simply ignore these to play a modestly stronger civilization, or construct them in any Magalanadu city to scale power as far as you like.

## How repeatable construction works on 4.22.16

Unciv 4.22.16 does not include the newer `Can be built [amount] times in each city` feature. The version-compatible approach is:

1. Construct a project using Production, or purchase it directly using Gold, Culture, or Faith after enabling the v2.7 purchase rules.
2. It pays the immediate reward, if any, and applies long-lasting bonus abilities stored by the civilization.
3. The last unique removes **only that project** from the city. Therefore it is available for selection again immediately.
4. Repeating the build adds additional temporary unique bonuses. Each lasts **9,999 turns**, effectively the rest of a normal game, but is not literally permanent.

This strategy uses Unciv's built-in `Gain`, timed-unique, and `Remove building` mechanics. Nothing is added to a technology tree and no custom scripts are required. The project does **not** stay permanently visible in the city's completed-building list. The *income* persists through saved temporary abilities.

## The ten optional projects

| Project | Completion reward | Additional persistent bonus *per construction* |
|---|---|---|
| Magalanadu Treasury Contract | +999,999,999 Gold | +9,999 Gold per turn in the capital |
| Magalanadu Science Grant | +999,999 Science | +9,999 Science per turn in the capital |
| Magalanadu Cultural Endowment | +999,999 Culture | +9,999 Culture per turn in the capital |
| Magalanadu Faith Foundation | +999,999 Faith | +9,999 Faith per turn in the capital |
| Magalanadu Industrial Surge | None | +999 Production/turn in the capital and +15% Production in all cities |
| Magalanadu Agricultural Programme | None | +999 Food/turn in the capital and +15% growth in all cities |
| Magalanadu Happiness Initiative | None | +999 Happiness in the capital and -10% population unhappiness in all cities |
| Magalanadu Military Mobilization | None | +10% military Strength and +15% unit-production speed |
| Magalanadu Frontier Initiative | Gain up to 12 tiles for the constructing city | -10% border growth Culture cost in all cities |
| Magalanadu Diplomatic Initiative | None | +15% City-State influence from gifts and +5 influence resting point |

These are intentionally **very strong** and will make the game one-sided if used excessively. They are optional, not passive.

### Numerical limits

Unciv's Gold store is a signed 32-bit integer capped at **2,147,483,647**. One 999,999,999 Gold grant fits, but after a few contracts additional Gold will stop increasing the reserve until it is spent. Other stockpiled resources may also reach numeric limits after many projects. Multi-city income is targeted to the capital for predictable +9,999 per build. If a capital changes, the ongoing `in capital` bonus transfers to the current capital.

### Install and test

Extract the ZIP and copy the **contents** of `Unciv-Mod-For-Me-main` into your Unciv `mods/Unciv-Mod-For-Me` folder, preserving the `jsons`, `Images`, `.atlas` and `.png` files. Enable the mod in a **new** Civ V: Gods & Kings game, select Magalanadu and check the construction menu. On GitHub, use the included Actions workflow to run Unciv's official `mod-ci` checker. The offline test can be run using `python tests/validate_mod.py`.

Existing saved games created with the old numerical values might have very large resource reserves or construction states; use a new test game for accurate comparison.

**Testing status:** The ruleset has offline integrity and source-code checks, but the Unciv executable has **not** been run in this environment. Test the project rewards and income on your installed Unciv version before replacing the version you rely on.

## Backups and audit

`backup/prebalance_ruleset/` keeps the original six ruleset files untouched. `compatibility/balance_changes.json` contains per-object before/after changes; `compatibility/balance_manifest.json` records preservation and project checks. Original graphical assets are retained. You can revert any change from the backup without downloading another mod.

## v2.1: Military and technology aid to major civilizations

Added a Foreign Aid Battalion, Relief Engineer, Science Envoy, Technology Ambassador, and 15 specific Technology Blueprint units. See [DIPLOMATIC_AID_CHANGELOG.md](DIPLOMATIC_AID_CHANGELOG.md) for important limits and how to gift these to another civilization. Native Unit Gifting already supports friendly major civilizations. Custom Technology Packages must be activated by the receiving player; AI recipients may not use the exact-technology action.


## v2.2 Unit Utility Cleanup (Unciv 4.22.16)
- Removed the nonfunctional Magalanadu World Shaper unit and its icon.
- Preserved all operational combat, improvement, diplomatic-aid and technology-transfer units.
- Corporate Mercenary is now Magalanadu-only; civilian worker/settler no-op bonuses removed.
- See `UNIT_UTILITY_AUDIT.md` and `UNIT_UTILITY_AUDIT.csv` for the complete 61-unit review and limitations.
- Existing saves with World Shaper units need a backup; prefer starting a new game for this update.

## v2.3: Resources on any terrain (via tile fabricators)

Four new civilian units create 35 resource-producing tile improvements anywhere a non-city-center tile improvement can legally be built, including land, water, mountains, jungle and ice. A separate Natural Deposit Surveyor creates real natural resource deposits only on their valid terrain. See [RESOURCE_FABRICATION_GUIDE.md](RESOURCE_FABRICATION_GUIDE.md) for the difference and usage instructions. Vanilla map resource definitions are not overridden.

## v2.4: Resource Supply Buildings (35 selectable buildings)

Added a set of 35 named Resource Supply buildings, one per base Unciv resource, each providing **100 copies** while built. They are visually grouped into **Bonus**, **Luxury**, and **Strategic** by name and icon inside the game's standard Buildings category. For a complete list and installation/usage instructions see [RESOURCE_SUPPLY_BUILDINGS_GUIDE.md](RESOURCE_SUPPLY_BUILDINGS_GUIDE.md). A new dedicated construction tab cannot be added through JSON alone.

## v2.5: Repeatable resource-first named facilities

Each of the 35 v2.4 resource supply buildings is now repeatable in the same city, and named with the resource first (e.g. **Iron Mill**, **Oil Refinery**, **Uranium Enrichment Facility**). Each construction gives another **+100** supply for 999,999 turns via a Nation-owned construction trigger and then removes the building. See [RESOURCE_SUPPLY_REPEATABLE_GUIDE.md](RESOURCE_SUPPLY_REPEATABLE_GUIDE.md). A separate custom construction category is not supported by Unciv JSON mods.


## v2.6 - Low-cost building purchases

All 59 Magalanadu buildings start at 5 Production and can be purchased with Gold, Culture, or Faith at an increasing price from 10 on Standard speed. See [PURCHASE_SYSTEM_GUIDE.md](PURCHASE_SYSTEM_GUIDE.md). The 35 resource facilities, 10 Supreme Projects, custom units, and preexisting assets are preserved. This build is offline-validated, not gameplay-certified.

## v2.7 - Explicit purchase access for every Magalanadu building

All **59 mod-defined buildings** now explicitly allow purchase using **Gold, Culture, and Faith**, including Supreme Projects, all 35 repeatable resource facilities, and the 14 original special wonders. This also removes any active per-building `Cannot be purchased` flag. Base costs and their escalating-price mechanics remain from v2.6. See `PURCHASE_SYSTEM_GUIDE.md`. The change does not overwrite vanilla world wonders, remove technology prerequisites, or bypass city/turn restrictions.
