# Magalanadu v3.1 — Diplomatic Unit Exports

Supports Unciv 4.22.16. This update modifies only `jsons/Units.json` and `jsons/Nations.json` plus documentation, manifests and tests; it preserves v3.0 custom units, buildings, Omni Resource Generator, 5× movement, 300-point Settler, and purchase rules.

## Why the Gift Unit action was missing

Unciv only displays native **Gift Unit** when you stand inside territory owned by the intended recipient, the unit has movement, and it is not transported.

- **Major civilizations:** recipient territory must count as friendly for Magalanadu, normally because the recipient allows your units through Open Borders. The unique *May enter foreign tiles without open borders* does not satisfy this friendship requirement.
- **City-states:** you cannot gift to one you are at war with. All military units can be donated. Civilian units require an explicit `Gain [amount] Influence with a [baseUnitFilter] gift to a City-State` ability. v3.1 adds that native allowance for the 20 named diplomatic aid units, including blueprints and civilian envoys.
- To use: move a unit **inside a recipient-owned tile**, select it, and choose **Gift Unit** in its actions. It is a unit action, not an option in the trade screen.

## Rewards and limitations

1. **Gold export grant:** each of 52 named Magalanadu units with a defined Production cost triggers `Gain [2 × cost] Gold` when you lose ownership of that unit on an owned, non-hostile foreign tile. This **fires on a standard Gift Unit transfer** because the game calls `UnitManager.removeUnit` before changing the unit owner.
2. **Important:** the `upon losing a unit` trigger is not an exclusive *gift* event. Other unit losses on qualifying foreign non-enemy territory can also pay the grant. This is a native-engine limitation, not a recipient payment. Units lost in hostile territory, in Magalanadu's territory, or in unowned tiles do not qualify.
3. **Influence:** each of 20 purpose-built aid/blueprint units gains 25–110 City-State Influence, determined by nominal Production cost, instead of the native 5 when gifted. The effect is tied to native gifting, not removing the unit.
4. **Actual City-State resources:** once allied, Magalanadu gets 100% additional City-State resource benefits over base supply via the native `[+100]% resources gifted by City-States` unique. This depends on *real resources the allied city-state can provide*.
5. **Gold per turn:** while allied, Magalanadu also receives a Gold amount equal to +50% of the allied City-State's own Gold production through Unciv's standard City-State Gold bonus. This is **not a trade that debits the city-state treasury** and is not guaranteed to be positive.
6. **Major civ GPT or specific resources:** no automatic resource/GPT transfer on unit gift exists in vanilla 4.22.16. Negotiate Gold-per-turn or resources in a separate diplomatic Trade deal. A real priced unit-for-resource transaction deducted from the recipient requires Kotlin engine changes, because `TradeOfferType` contains no unit transfer type.

### Sample immediate Gold export rewards

| Unit | Base Production cost | Gold grant on eligible transfer | City-State Influence |
|---|---:|---:|---:|
| Magalanadu Foreign Aid Battalion | 350 | 700 | 60 |
| Magalanadu Relief Engineer | 180 | 360 | 25 |
| Magalanadu Science Envoy | 260 | 520 | 40 |
| Magalanadu Technology Ambassador | 900 | 1,800 | 110 |
| Indian Tank | 375 | 750 | Native 5 |

## Test procedure

1. Start a **new game** as Magalanadu with a City-State and one friendly major civ.
2. Produce an Aid Battalion (or Science Envoy). Move onto a tile **owned by a neutral City-State**. Gift Unit should appear and the donor should get Gold + the scaled Influence reward.
3. Verify that the City-State becomes your Ally. Check the Resources Overview and Gold-per-turn line. The actual supply depends on the City-State's resource availability and Gold output.
4. For a major civilization, negotiate Open Borders so their land is friendly; move onto their territory and gift a unit. Verify Gold grant and +5 opinion modifier (without City-State Influence).
5. Try gifting in own/unowned/hostile territory; reward should not fire there. Verify existing unit effects and reload a saved game.

Only **offline** tests are provided here; the actual Unciv runtime and save/reload behavior have **not** been tested.
