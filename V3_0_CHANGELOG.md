# Magalanadu v3.0: Functional Cleanup and Omni Resources

Target: **Unciv 4.22.16** (Gods & Kings extension).

## What was removed

- **12 specialist units** that cannot provide their advertised two-civilization false-flag/war-brokering actions or have misleading game roles, including Saboteur, False Flag Operative, War Profiteer, Cyber Warfare Cell, Shadow Agent, and the terrain-restricted Natural Deposit Surveyor.
- **35 resource-supply buildings** (the named Iron Mill, Uranium Enrichment Facility, etc.) whose accumulated/resource behavior has been unreliable in play. They are absent from construction menus. Their standalone sprite page has also been removed.
- Any unit imagery for the deleted units. Unit and resource texture atlases have been repacked so there are no orphan sprite references.

**Not possible through ordinary Unciv JSON mods:** force Civilization B to declare war on Civilization C from a Magalanadu false-flag unit, pick arbitrary enemy governments, or automatically collect Gold because two *other* civilizations are at war. The standard diplomatic trade system may allow negotiating declarations of war, but not a modded button for coercing both sides.

## Worker-based supply

A **Super Cheat Worker** can construct **Omni Resource Generator**. On a tile owned by your civilization, the improvement supplies **+50 of every resource**: 6 strategic, 22 luxury, 7 bonus, **35 types** in all. Additional generator tiles each add another 50, assuming they remain operational and owned. The worker has water/ice/impassable terrain traversal uniques to reach more kinds of tiles. Unciv still disallows improvement placement on city-center tiles and may bar special/protected terrain.

This is *ongoing resource supply* (`Provides [50] [resource]` from a tile improvement), not an accumulating +50 per turn and not 50 resource icons appearing on the map. **Luxury duplicates do not stack happiness**; bonus types do not give 50 Food. The supply is usable for trading/strategic requirements according to game rules. Jewelry/Porcelain are city-state-themed luxuries; their trade availability should be tested specifically.

Four individual resource fabricator units and 35 tile improvements remain for choosing an individual resource. The 300-movement Settler, 5× other custom unit movement, 10 Supreme Projects, affordable Gold/Culture/Faith purchasing, military aid and blueprint units remain.

## Installation and compatibility

Install as a full replacement of the prior mod folder (do not merge over it, because deleted JSON/assets might remain). **Back up old saves** and test with a new game. A saved game containing a now-removed unit or in-progress named resource building may not load correctly. The `backup/prebalance_ruleset` folder is historical source backup, not an active ruleset.

**Validation:** static JSON/schema-like checks, asset/atlas checks and archive verification have been run. The full Unciv 4.22.16 executable and its mod-ci checker were not available in this environment. In-game validation is required before considering this production-stable.
