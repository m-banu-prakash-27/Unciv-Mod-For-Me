# Magalanadu v2.6 - Building Purchase System (Unciv 4.22.16)

## What changed

- All **59 Magalanadu buildings** have base **5 Production** costs.
- Every Magalanadu building has `Cost increases by [5] when built`, allowing the construction cost to increase with completed production (Unciv tracks the build count at civilization level).
- Magalanadu can buy **all eligible buildings** with **Gold**, **Culture**, or **Faith** using the built-in increasing-price mechanic.
- All **14 Magalanadu wonders/national wonders** have explicit permission to buy with Gold, overcoming the engine's usual Gold/wonder restriction.
- Removed the `Cannot be purchased` flag from 10 repeatable Supreme Projects. Their original rewards and self-removal remain.
- All 35 resource buildings still add +100 of the selected resource with every completion and then become available again.

## Starting purchase cost and increase

The game **rounds down** building purchase prices to multiples of **10**. A configured starting price of 5 would actually appear as 0 on normal game speed. Thus, the configuration starts at **10** for each currency.

The `at an increasing price ([10])` unique is **quadratic**, not linear:
`base + 10/2 * (previousPurchases^2 + previousPurchases)`.

On Standard game speed, before purchase discounts, the sequence for a specific building is:

| Number of times bought | Gold / Culture / Faith cost |
| --- | ---: |
| First | 10 |
| Second | 20 |
| Third | 40 |
| Fourth | 70 |
| Fifth | 110 |

Each building has its **own purchase counter** (e.g., buying Iron Mill raises the future price of Iron Mill, not Uranium Enrichment Facility). It is shared between cities and payment currencies. Other game speeds or discounts may affect the displayed prices.

Production starts at 5; the `Cost increases by [5] when built` ability changes production construction costs according to the game's recorded completed build count. Purchase-count and build-count formulas are not identical.

## Where to buy

Open an owned city's construction screen, select a building, then use the buy option for Gold, Culture or Faith. Currency choices depend on your reserves and the game's purchase interface.

The global purchase rules also cover regular non-Magalanadu buildings, subject to technology, location, and other engine constraints. **Vanilla world wonders cannot necessarily be bought with Gold**, since the game requires an object-level exception; this mod supplies that exception for all *14 Magalanadu* special wonders only, without overriding vanilla wonder data. Ordinary technology prerequisites and exclusion rules still apply.

## Known limitations and tests

1. Verified against the **4.22.16 source**: `BuyBuildingsIncreasingCost`, `CanBePurchasedWithStat`, build-cost increase and the purchase counter exist. The final buy price rounds to a multiple of 10.
2. Actual gameplay and save/reload persistence **have not been tested** here. Validate the first five purchases of *Iron Mill*, then load the saved game and verify the new price and resource supply.
3. The resource facilities' existing +100 supply is a duration-limited triggered effect for 999,999 turns, not literally infinite. It depends on the v2.5 trigger implementation.
4. As before, Unciv JSON mods cannot add a new purchase tab or override the game's base purchasing UI.
5. The purchase rules apply only when playing as Magalanadu; they do not give other civilizations cheap purchases.

## Installation

Install the complete v2.6 ZIP as an Unciv extension mod. Back up existing saves and test a new game. The mod's GitHub repository is **not automatically updated** by downloading the ZIP; use the publisher kit or push the files in your local repository.

## v2.7: Remove all custom-building purchase restrictions

Every one of Magalanadu's **59 building definitions** now explicitly contains these permissions:

```json
"Can be purchased with [Gold] [in all cities]",
"Can be purchased with [Culture] [in all cities]",
"Can be purchased with [Faith] [in all cities]"
```

There are **zero active `Cannot be purchased` entries** in any mod JSON file. The v2.6 price-escalation rule is unchanged: first purchase 10 on Standard speed before discounts, later purchases increasingly expensive. All production costs and repeatable +100 resource rewards remain unchanged.

**Scope:** Mod-defined buildings are explicitly enabled. Default-game wonders and other built-in exceptions are not overwritten, because doing so would replace native game definitions and risk incompatibility. Buying a building still requires the corresponding city to meet ordinary prerequisites such as researched technologies, national-wonder restrictions, and available funds. Archived historical change records and original-rule backups remain intact and are not loaded as rules.

This is **offline validated only**. Test purchases with Gold, Culture, and Faith on a resource facility and a Supreme Project, then save and reload before treating it as gameplay-certified.
