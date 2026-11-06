# Magalanadu v2.5 - Repeatable Named Resource Facilities

**Game version:** Unciv 4.22.16, Civ V - Gods & Kings ruleset add-on

## How it works

Every facility is unique to Magalanadu. Upon construction, its Nation-level
`Provides [100] [Resource]` trigger is activated for 999,999 turns, then
the completed building removes itself. The Nation-level source is essential:
Unciv deliberately excludes removed *Building*-owned effects from its global resource cache.
A second construction triggers another independent +100 supply, including in the same city.
The supply does not accumulate 100 every turn: each completed facility provides another
100 copies of ongoing supply. These long-duration bonuses survive in the save-data in the
engine's `temporaryUniques` list, according to Unciv 4.22.16 source; not yet runtime-verified.
Each construction also adds +2 Food, Gold, or Production to the capital (depending on category).

## Facilities by resource category

### Strategic (6)

| Resource | Building | Every construction |
|---|---|---:|
| Aluminum | Aluminum Smelter | +100 Aluminum |
| Coal | Coal Processing Plant | +100 Coal |
| Horses | Horses Stable | +100 Horses |
| Iron | Iron Mill | +100 Iron |
| Oil | Oil Refinery | +100 Oil |
| Uranium | Uranium Enrichment Facility | +100 Uranium |

### Luxury (22)

| Resource | Building | Every construction |
|---|---|---:|
| Citrus | Citrus Grove Estate | +100 Citrus |
| Copper | Copper Smelting Works | +100 Copper |
| Cotton | Cotton Weaving House | +100 Cotton |
| Crab | Crab Aquaculture Farm | +100 Crab |
| Dyes | Dyes Pigment Workshop | +100 Dyes |
| Furs | Furs Trading Lodge | +100 Furs |
| Gems | Gems Cutting Atelier | +100 Gems |
| Gold Ore | Gold Ore Mintworks | +100 Gold Ore |
| Incense | Incense Distillery | +100 Incense |
| Ivory | Ivory Artisan Hall | +100 Ivory |
| Jewelry | Jewelry Guildhall | +100 Jewelry |
| Marble | Marble Stoneworks | +100 Marble |
| Pearls | Pearls Cultivation Laboratory | +100 Pearls |
| Porcelain | Porcelain Kilns | +100 Porcelain |
| Salt | Salt Evaporation Works | +100 Salt |
| Silk | Silk Loomworks | +100 Silk |
| Silver | Silver Foundry | +100 Silver |
| Spices | Spices Trading Bazaar | +100 Spices |
| Sugar | Sugar Refinery | +100 Sugar |
| Truffles | Truffles Mycology Conservatory | +100 Truffles |
| Whales | Whales Maritime Station | +100 Whales |
| Wine | Wine Vintner Cellar | +100 Wine |

### Bonus (7)

| Resource | Building | Every construction |
|---|---|---:|
| Bananas | Bananas Plantation | +100 Bananas |
| Cattle | Cattle Ranch | +100 Cattle |
| Deer | Deer Game Reserve | +100 Deer |
| Fish | Fish Hatchery | +100 Fish |
| Sheep | Sheep Pastures | +100 Sheep |
| Stone | Stone Quarry | +100 Stone |
| Wheat | Wheat Granary | +100 Wheat |

## Finding them in game

1. Choose Magalanadu and enable the mod.
2. In any city, select Choose Construction > Buildings.
3. Look for the resource-first names with matching color-coded **Resource Supply** icons. Blue = strategic, purple = luxury, green = bonus.
4. Construct, for example, **Uranium Enrichment Facility**. It disappears after completion and can be constructed again.
5. Check Resources Overview for +100 Uranium for each completion. Save, reload, and verify totals remain.

### Game limitations

- The construction UI in Unciv 4.22.16 has fixed tabs. A JSON-only mod cannot add a dedicated collapsible `Resource Supply` tab. These facilities remain grouped together in **Buildings** by consecutive JSON order, icon colors and Civilopedia labels.
- 999,999 turns is effectively permanent for a normal game, but not mathematically infinite.
- Luxury duplicates do not give 100 times the Happiness. Bonus resources are tracked supplies, not +100 tile Food.
- This does not add a map deposit. The builder works regardless of local terrain.
- `mod-ci` and in-game save/reload stacking remain unverified. Do not overwrite a valued save before testing.

## Why the source of the unique matters

In Unciv 4.22.16, `CivInfoTransientCache.updateCivResources` excludes resource uniques whose source is `Building` or `Wonder` because they are normally counted from existing buildings. Therefore a self-removing building that simply uses `Provides [100] [Uranium] <for [999999] turns>` would not reliably count resources. This release instead places the timed trigger in **Magalanadu's nation uniques**, so it is stored as a Nation-sourced temporary unique and included by the civilization-wide resource calculation.

## Preservation

The preceding v2.4 release had 65 units, 59 buildings and 44 improvements. v2.5 retains the same totals, only renaming and changing the 35 resource-supply buildings and adding their companion nation triggers.
