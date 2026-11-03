# Magalanadu v2.9: 5× Movement Upgrade

Target: **Unciv 4.22.16**. Previous v2.8 release multiplied most units by 3×. This release changes that to **5× of the original v2.7 values**, not 5× of the already-boosted v2.8 values.

## Summary

- **64 non-settler custom units** now have exactly **5× their v2.7 base movement**. Combat, specialist civilian, diplomatic-aid, fabricator, and technology-blueprint units are included.
- **Super Cheat Settler retains its special 300 movement** and continues replacing Magalanadu starting and trained Settlers. This meets the previous minimum-300 requirement without introducing a 1500-point pathfinding load.
- **Four air/missile units** have **5× their v2.7 flight/strike range** because aircraft use their range (not ordinary movement) to determine relocation. Existing intercept range is also scaled to 5× where specified.
- No combat stats, bonuses, construction prices, resource facilities, diplomacy systems, graphics or other assets were changed.

## Complete movement conversion

| Unit | v2.7 baseline movement | v2.8 movement (3×) | v2.9 movement (5×) | v2.9 air/strike range |
|---|---:|---:|---:|---:|
| Super Cheat Worker | 3 | 9 | **15** | — |
| Super Cheat Settler | 3 | 300 | **300** | — |
| Super Cheat Warrior | 3 | 9 | **15** | — |
| Super Cheat Trooper | 3 | 9 | **15** | — |
| Indian Bowman | 3 | 9 | **15** | — |
| Indian War Elephant | 5 | 15 | **25** | — |
| Indian Infantry | 3 | 9 | **15** | — |
| Indian Carrier | 6 | 18 | **30** | — |
| Indian Anti-Aircraft Gun | 3 | 9 | **15** | — |
| Indian Destroyer | 7 | 21 | **35** | — |
| MAG-41 | 2 | 6 | **10** | 55 |
| Indian Paratrooper | 3 | 9 | **15** | — |
| Indian Tank | 6 | 18 | **30** | — |
| Indian Anti-Tank Gun | 3 | 9 | **15** | — |
| Indian Mobile SAM | 4 | 12 | **20** | — |
| Indian Guided Missile | 2 | 6 | **10** | 45 |
| Indian Helicopter Gunship | 7 | 21 | **35** | — |
| Indian Nuclear Submarine | 7 | 21 | **35** | — |
| Indian Mechanized Infantry | 4 | 12 | **20** | — |
| Indian Missile Cruiser | 8 | 24 | **40** | — |
| Indian Modern Armor | 6 | 18 | **30** | — |
| Indian Jet Fighter | 2 | 6 | **10** | 55 |
| Indian Giant Death Robot | 6 | 18 | **30** | — |
| Indian Stealth Bomber | 3 | 9 | **15** | 105 |
| Magalanadu Shadow Agent | 4 | 12 | **20** | — |
| Magalanadu Divine Apostle | 5 | 15 | **25** | — |
| Veer | 4 | 12 | **20** | — |
| Magalanadu Saboteur | 4 | 12 | **20** | — |
| Magalanadu False Flag Operative | 4 | 12 | **20** | — |
| Magalanadu Proxy Commander | 3 | 9 | **15** | — |
| Magalanadu Religious Agitator | 5 | 15 | **25** | — |
| Magalanadu Black Ops Cell | 4 | 12 | **20** | — |
| Magalanadu Arms Dealer | 4 | 12 | **20** | — |
| Magalanadu Drone Swarm | 6 | 18 | **30** | — |
| Magalanadu Cyber Warfare Cell | 5 | 15 | **25** | — |
| Magalanadu Resource Smuggler | 4 | 12 | **20** | — |
| Corporate Mercenary | 3 | 9 | **15** | — |
| Magalanadu War Profiteer | 4 | 12 | **20** | — |
| Magalanadu Peacekeeper Battalion | 4 | 12 | **20** | — |
| Magalanadu Orbital Strike Team | 4 | 12 | **20** | — |
| Magalanadu Architect of Wonders | 4 | 12 | **20** | — |
| Magalanadu Foreign Aid Battalion | 3 | 9 | **15** | — |
| Magalanadu Relief Engineer | 3 | 9 | **15** | — |
| Magalanadu Science Envoy | 3 | 9 | **15** | — |
| Magalanadu Technology Ambassador | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Writing | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Education | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Gunpowder | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Scientific Theory | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Industrialization | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Electricity | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Flight | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Radio | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Plastics | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Electronics | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Radar | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Rocketry | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Computers | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Satellites | 3 | 9 | **15** | — |
| Magalanadu Blueprint - Robotics | 3 | 9 | **15** | — |
| Magalanadu Strategic Fabricator | 5 | 15 | **25** | — |
| Magalanadu Luxury Fabricator I | 5 | 15 | **25** | — |
| Magalanadu Luxury Fabricator II | 5 | 15 | **25** | — |
| Magalanadu Bonus Fabricator | 5 | 15 | **25** | — |
| Magalanadu Natural Deposit Surveyor | 5 | 15 | **25** | — |

## Notes & limitations

1. **One movement point is not always one tile.** Terrain costs, enemies, blocked passage, action costs, and fog of war still matter. Only the Super Cheat Settler has the special `All tiles cost 1 movement` rule.
2. **Aircraft:** usable relocation/attack reach depends on range. We increased both movement and range for aircraft, but relocation is calculated from range (normally 2× it).
3. **300-movement settlers may still strain pathfinding on huge maps.** They have not been raised further.
4. **Existing saves:** a base-game Settler already in a save may remain a normal Settler; newly created Magalanadu settlers should use the special replacement. Test by saving and reloading.
5. **In-game verification pending.** All eight offline checks pass, but the Unciv 4.22.16 application and official mod-ci were not executed.

## Quick verification

- Start a new game as Magalanadu and check that the starting Super Cheat Settler has **300 movement**.
- Check Indian Infantry: **15** (was 3 in v2.7; 9 in v2.8).
- Check Indian Tank: **30** (was 6 in v2.7; 18 in v2.8).
- Check Indian Destroyer: **35** (was 7 in v2.7; 21 in v2.8).
- Check the MAG-41 Bomber: its range should now be **55** (was 11 in v2.7; 33 in v2.8).
- Verify Gold/Culture/Faith building purchases and repeatable +100 resource facilities work after saving and reloading.
