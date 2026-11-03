# Magalanadu v2.0 Balance and Power Projects

Target: **Unciv 4.22.16**, Civ V: Gods & Kings ruleset extension.

## Permanent civilization advantage

| Bonus | Before | After |
|---|---:|---:|
| Gold | +1,000% | +20% |
| Food | +1,000% | +15% |
| Science | +1,000% | +20% |
| Faith | +1,000% | +15% |
| Culture | +1,000% | +20% |
| Production | +1,000% | +25% |
| Defensive strength | +100% | +15% |
| Tile purchase cost | -100% | -15% |

All original 14 special buildings remain, no longer costing 1 Production or granting million-percent passive bonuses. The original 42 units still exist, with smaller strength, mobility, range, experience and/or lower-sized bonuses. All 9 improvements, all 3 promotion groups and original city work/expand range 5 are retained. Faith generation drawback removed from the old Faith building.

## Repeatable bonus projects (10)

All of these cost 300 to 420 Production and can be selected again once completed. They are optional, civ-exclusive, cannot be purchased outright, and use the supported **self-removal on completion** approach. Bonuses last **9,999 turns** and stack on each completion.

| Name | One-time payout | Stacking long-term effect |
|---|---|---|
| Treasury Contract | 999,999,999 Gold | +9,999 Gold per turn in capital |
| Science Grant | 999,999 Science | +9,999 Science per turn in capital |
| Cultural Endowment | 999,999 Culture | +9,999 Culture per turn in capital |
| Faith Foundation | 999,999 Faith | +9,999 Faith per turn in capital |
| Industrial Surge | None | +999 Production/turn in capital; +15% Production in all cities |
| Agricultural Programme | None | +999 Food/turn in capital; +15% growth in all cities |
| Happiness Initiative | None | +999 Happiness in capital; -10% population unhappiness everywhere |
| Military Mobilization | None | +10% military strength; +15% unit Production |
| Frontier Initiative | 12 territory tiles for that city | -10% border growth Culture cost empire-wide |
| Diplomatic Initiative | None | +15% gift-generated Influence; +5 resting point |

Important: The base game generally allows each **ordinary building** only once per city, but the new projects remove themselves upon completion. This bypasses the restriction through supported actions without relying on the not-yet-supported `Can be built [amount] times in each city` unique on 4.22.16. The removed project will not remain in the building list, but its timed temporary unique remains and stacks.

## Compatibility, reversibility, tests

- Original gameplay files backed up under `backup/prebalance_ruleset/`.
- Detailed object-by-object diff data in `compatibility/balance_changes.json`.
- 69 original sprites and atlas entries preserved, plus 10 icons added in a separate, registered atlas.
- `python tests/validate_mod.py`: **PASS**.
- GitHub workflow includes Unciv's official `mod-ci` checker but **has not yet run**.
- Gameplay reward and stack persistence need actual Unciv 4.22.16 test. Do not treat this package as runtime-certified.
- A new game is recommended when comparing balance changes. Existing saves retain their previously accumulated high resources.
- Unciv caps stored Gold at 2,147,483,647. Once reached, additional Gold gains will not increase the stored amount until some is spent.
