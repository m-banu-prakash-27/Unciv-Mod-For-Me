# Magalanadu v2.3: Resource Fabrication Anywhere

**Target**: Unciv 4.22.16. Built from v2.2 with all previous units, buildings, improvements, and sprites retained.

## Supported abilities

- 4 new specialized civilian fabricators: 1 Strategic, 2 Luxury and 1 Bonus.
- **35 specialized resource-producing tile improvements**: 6 strategic, 22 luxury, 7 bonus.
- Units have one explicit Create improvement action per resource. They can be reused. Build costs 1 movement for each created resource fabricator.
- The engineered tile improvements have a real **Provides [N] [Resource]** unique recognized in 4.22.16. Strategic units give 8 copies; luxury give 1; bonus give 2 with a modest local tile yield.
- Improvements explicitly accept Land, Water, Mountain, Forest, Jungle, Marsh, Fallout, Oasis, Ice and more. The engineers are able to move through water, ice and otherwise impassable tiles.
- Added the fifth unit **Magalanadu Natural Deposit Surveyor** for **actual natural deposits** on terrain where Unciv accepts that resource. Has 35 separate resource-creation actions.

## Important limitation: what is a real resource deposit?

**This release deliberately does NOT replace the built-in TileResources.json definitions**.

Unciv 4.22.16 only supports `Add [Iron] to this tile` if the terrain is in that resource's `terrainsCanBeFoundOn`. The action also runs the game's ruleset tile normalizer. Consequently, literal natural resource deposits on *every* terrain are impossible through a simple Unciv extension without rewriting base resource definitions. Doing so would change resource placement and perhaps map generation for all players.

Instead, the 4 Fabricator units **create a tile improvement which provides the chosen resource to your civilization regardless of tile terrain** (where improvements are permitted). This supplies the resources used for builds and trading, and adds a visible custom improvement icon on that tile, but **does not alter the tile's natural resource field**. Only one improvement can exist per tile. This design preserves normal resource distributions and all existing vanilla resource metadata.

The Natural Deposit Surveyor is provided separately for authentic deposits on allowed terrain. Its actions can appear disabled on unsupported terrain; use the universal Fabricators instead.

## How to use

1. Start a new game or load a backed-up game with Magalanadu enabled.
2. Construct one of the 4 Fabricator units from a Magalanadu city: Strategic (after Industrialization), Luxury I/II (after Currency), or Bonus (after Agriculture).
3. Move the unit to a tile you own. It can move over land, sea, mountains and ice, but **cannot build an improvement on a city center or natural wonder**.
4. Select the unit. In its action list, choose **Create [Magalanadu Strategic Fabricator - Iron]** (or any other named resource).
5. The tile now contains an Iron-producing improvement granting 8 Iron to its owner while the improvement is active. Build on another tile for more Iron.
6. If you need a literal native Iron deposit, use the Natural Deposit Surveyor on a terrain that Iron naturally supports. Native placement will replace an existing resource on that tile.

## Limits and checks

- Fabrication does not populate the map's actual `tile.resource` field and will not visually appear as a vanilla resource deposit.
- Vanilla resource generation is unchanged, and all resource definitions remain untouched.
- Tile improvements are constrained by the game's normal territory, city-center, natural-wonder and buildability restrictions.
- Each tile can hold only one improvement; overwriting an existing improvement replaces it.
- AI use of these specialized civilian units is not guaranteed.
- Generated action names and sprite icons are validated offline. **No in-game runtime playtest was performed.**
- Run `python tests/validate_mod.py`, `python tests/validate_diplomatic_aid.py`, `python tests/validate_unit_utility.py`, and `python tests/validate_resource_fabrication.py`.
- Run official `java -jar Unciv.jar mod-ci` inside a clone of this mod folder, and playtest 1 land, 1 snow, 1 water, 1 mountain and 1 city-center case.

Reference: https://yairm210.github.io/Unciv/Modders/uniques/
