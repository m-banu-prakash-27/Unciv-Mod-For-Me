# Magalanadu v2.2 — Custom Unit Utility Audit

Target: Unciv 4.22.16, Gods & Kings extension. **Static source audit, not an in-game playtest.**

## Changes made

- **Removed Magalanadu World Shaper** (61 → 60 active custom units). It contained nine "Turn this tile into" triggerables and removal effects but no player-invokable unit action modifiers. A player could not select the advertised terraforming action.
- Deleted the live World Shaper unit definition, matching PNG icon, and stale atlas region. The packed `game.png` atlas sheet is unchanged; the sprite is no longer registered.
- Removed the inert **Can move after attacking** bonus from the civilian Super Cheat Worker and Super Cheat Settler.
- Made **Corporate Mercenary** unique to Magalanadu. It was accidentally recruitable by all civilizations.
- Added Civilopedia explanations for thematic units whose names imply game mechanics they do not possess. No functional combat unit was removed simply because its name is theatrical.
- Retained all v2.1 military aid and technology-package units. They are playable with human recipients, but AI cannot be guaranteed to activate a custom technology blueprint. Built-in Hurry Research is the fallback.

## Main functional findings

| Unit | Verdict | Why |
|---|---|---|
| Magalanadu World Shaper | **Removed** | Terrain-change triggers were not exposed as action buttons |
| Super Cheat Worker | Keep | Can build normal improvements and use instant-construction actions |
| Magalanadu Arms Dealer | Keep | Can consume itself to create an Arms Depot on a legal tile |
| Magalanadu Resource Smuggler | Keep | Can construct resource/depot improvements, but cannot trade resources diplomatically |
| Magalanadu Architect of Wonders | Keep | Native construction rushing and instant improvements |
| Veer | Keep with access warning | Unbuildable Great Person, can be obtained via Great Person rewards rather than normal production |
| False Flag Operative / Cyber Warfare Cell | Keep with corrected descriptions | Functional stealth military units; neither changes diplomatic attribution nor runs cyber missions |
| Orbital Strike Team | Keep with corrected description | Battlefield ranged unit, not an actual map-wide orbital attack |
| Blueprint units | Keep, with AI limitation | Human receivers can activate a specific technology; AI activation is not guaranteed |

## 61-unit audit register

| # | Unit | Decision | Mechanically useful role |
|---:|---|---|---|
| 1 | Super Cheat Worker | KEEP: tested syntax, runtime pending | Worker and instant improvement construction |
| 2 | Super Cheat Settler | KEEP: tested syntax, runtime pending | Found cities |
| 3 | Super Cheat Warrior | KEEP: combat / utility | Early ranged combat |
| 4 | Super Cheat Trooper | KEEP: combat / utility | Upgraded early ranged combat |
| 5 | Indian Bowman | KEEP: combat / utility | Civilization-specific replacement of Archer |
| 6 | Indian War Elephant | KEEP: combat / utility | Civilization-specific replacement of Chariot Archer |
| 7 | Indian Infantry | KEEP: combat / utility | Civilization-specific replacement of Rifleman |
| 8 | Indian Carrier | KEEP: combat / utility | Civilization-specific replacement of Carrier |
| 9 | Indian Anti-Aircraft Gun | KEEP: combat / utility | Civilization-specific replacement of Anti-Aircraft Gun |
| 10 | Indian Destroyer | KEEP: combat / utility | Civilization-specific replacement of Destroyer |
| 11 | MAG-41 | KEEP: combat / utility | Civilization-specific replacement of Bomber |
| 12 | Indian Paratrooper | KEEP: combat / utility | Civilization-specific replacement of Paratrooper |
| 13 | Indian Tank | KEEP: combat / utility | Civilization-specific replacement of Tank |
| 14 | Indian Anti-Tank Gun | KEEP: combat / utility | Civilization-specific replacement of Anti-Tank Gun |
| 15 | Indian Mobile SAM | KEEP: combat / utility | Civilization-specific replacement of Mobile SAM |
| 16 | Indian Guided Missile | KEEP: combat / utility | Civilization-specific replacement of Guided Missile |
| 17 | Indian Helicopter Gunship | KEEP: combat / utility | Civilization-specific replacement of Helicopter Gunship |
| 18 | Indian Nuclear Submarine | KEEP: combat / utility | Civilization-specific replacement of Nuclear Submarine |
| 19 | Indian Mechanized Infantry | KEEP: combat / utility | Civilization-specific replacement of Mechanized Infantry |
| 20 | Indian Missile Cruiser | KEEP: combat / utility | Civilization-specific replacement of Missile Cruiser |
| 21 | Indian Modern Armor | KEEP: combat / utility | Civilization-specific replacement of Modern Armor |
| 22 | Indian Jet Fighter | KEEP: combat / utility | Civilization-specific replacement of Jet Fighter |
| 23 | Indian Giant Death Robot | KEEP: combat / utility | Civilization-specific replacement of Giant Death Robot |
| 24 | Indian Stealth Bomber | KEEP: combat / utility | Civilization-specific replacement of Stealth Bomber |
| 25 | Magalanadu Shadow Agent | KEEP: combat / utility | Stealth scout / ranged raider |
| 26 | Magalanadu Divine Apostle | KEEP: combat / utility | Religion spreading / theological actions |
| 27 | Veer | KEEP: limited/clarified | Great Person with combat aura / citadel / golden age |
| 28 | Magalanadu Saboteur | KEEP: combat / utility | Stealth pillager and scout |
| 29 | Magalanadu False Flag Operative | KEEP: limited/clarified | Stealth raider, not diplomatic false flags |
| 30 | Magalanadu Proxy Commander | KEEP: combat / utility | Combat aura and nearby healing |
| 31 | Magalanadu Religious Agitator | KEEP: combat / utility | Advanced religious conversion |
| 32 | Magalanadu Black Ops Cell | KEEP: combat / utility | Late-game stealth ranged combat |
| 33 | Magalanadu Arms Dealer | KEEP: limited/clarified | Consumable instant Arms Depot constructor |
| 34 | Magalanadu Drone Swarm | KEEP: combat / utility | Fast ranged support |
| 35 | Magalanadu Cyber Warfare Cell | KEEP: limited/clarified | Stealth raider, not cyber espionage |
| 36 | Magalanadu Resource Smuggler | KEEP: limited/clarified | Consumable depot/resource construction |
| 37 | Corporate Mercenary | KEEP: combat / utility | Buildable bonus melee mercenary |
| 38 | Magalanadu War Profiteer | KEEP: limited/clarified | Combat support aura, not passive Gold generation |
| 39 | Magalanadu Peacekeeper Battalion | KEEP: combat / utility | Defensive support/healing |
| 40 | Magalanadu Orbital Strike Team | KEEP: limited/clarified | Long-range land attack, not map-wide orbital attack |
| 41 | Magalanadu World Shaper | REMOVE | NO ACTION: terrain changes were not exposed as unit controls |
| 42 | Magalanadu Architect of Wonders | KEEP: tested syntax, runtime pending | Hurry buildings/wonders or place improvement |
| 43 | Magalanadu Foreign Aid Battalion | KEEP: combat / utility | Giftable military combat unit |
| 44 | Magalanadu Relief Engineer | KEEP: combat / utility | Giftable infrastructure worker |
| 45 | Magalanadu Science Envoy | KEEP: limited/clarified | Science consumable or hurry research |
| 46 | Magalanadu Technology Ambassador | KEEP: limited/clarified | Free-tech consumable or hurry research |
| 47 | Magalanadu Blueprint - Writing | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 48 | Magalanadu Blueprint - Education | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 49 | Magalanadu Blueprint - Gunpowder | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 50 | Magalanadu Blueprint - Scientific Theory | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 51 | Magalanadu Blueprint - Industrialization | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 52 | Magalanadu Blueprint - Electricity | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 53 | Magalanadu Blueprint - Flight | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 54 | Magalanadu Blueprint - Radio | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 55 | Magalanadu Blueprint - Plastics | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 56 | Magalanadu Blueprint - Electronics | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 57 | Magalanadu Blueprint - Radar | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 58 | Magalanadu Blueprint - Rocketry | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 59 | Magalanadu Blueprint - Computers | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 60 | Magalanadu Blueprint - Satellites | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |
| 61 | Magalanadu Blueprint - Robotics | KEEP: limited/clarified | Giftable researched-tech package (human receiver action; AI may use Hurry Research) |

## Validation and limitations

The bundled `tests/validate_mod.py`, `tests/validate_diplomatic_aid.py`, and `tests/validate_unit_utility.py` are static checks. They confirm JSON/reference integrity and the presence/absence of declared actions, but do not simulate tile placement, research behavior or AI automation.
Run official `java -jar Unciv.jar mod-ci` on the mod folder and test 2–3 specific specialist unit actions in an actual new game. If you have an existing save with World Shaper units deployed, back it up before updating; removing a unit definition can affect save compatibility.

Official reference: https://yairm210.github.io/Unciv/Modders/uniques/
