# Magalanadu v2.1: Foreign Military Aid and Technology Packages

**Game target:** Unciv 4.22.16, Gods & Kings extension. **This is NOT a modified Unciv game executable.**

## Troop transfer to other major civilizations

Unciv **already has a native Gift Unit action for major civilizations**, not only City-States.
To use it: open borders / friendly territorial access -> move an owned unit into that civ's land -> keep movement points -> choose **Gift Unit** in the unit actions. Transported units cannot be gifted. Gifts to major civs improve relations.

New aid units:
- **Magalanadu Foreign Aid Battalion**, Rifling; 46 Strength, 3 Movement, 350 Production. Designed to give a friendly major civilization combat support.
- **Magalanadu Relief Engineer**, Engineering; 3 Movement, 180 Production. Buildable infrastructure worker that can also be gifted.

All original 42 units and original combat/tech features are preserved.

## Technology transfer (workaround, no fake diplomacy buttons)

Unciv has an internal `TradeOfferType.Technology` handler, but its standard trading screen does not OFFER technology transfers on 4.22.16. JSON mods cannot add arbitrary items to that offer list.

This version adds two **recipient-activated** technology-aid units:
- **Magalanadu Science Envoy**, after Education, costs 260 Production; if a human recipient activates its special action, gains 650 Science. Also supports the game's built-in Hurry Research action.
- **Magalanadu Technology Ambassador**, after Scientific Theory, costs 900 Production; if a human recipient activates its special action, receives one free technology choice. Also supports Hurry Research.

It also adds **15 exact-technology blueprint units**. You can build each one only **after Magalanadu has researched that technology**. Move the blueprint unit into friendly recipient territory and use **Gift Unit**. A human recipient selects the gifted unit and presses `Discover [Technology]` to consume the unit and unlock exactly that technology. An AI recipient cannot be relied upon to activate this custom action. Blueprints also support Hurry Research as an AI fallback in late game, which yields science rather than the named technology.

Technology blueprints: Writing, Education, Gunpowder, Scientific Theory, Industrialization, Electricity, Flight, Radio, Plastics, Electronics, Radar, Rocketry, Computers, Satellites, Robotics.

### Technical limitations

1. You **cannot choose any arbitrary major civ from a new popup**. The target is the civilization whose friendly territory the gifted unit enters.
2. For **human players / multiplayer**, a recipient can consciously activate the transferred Science, Free Technology, or specific-tech blueprint action. For **AI recipients**, `CivilianUnitAutomation` is not programmed to use arbitrary `TriggerUnique` actions; it recognizes standard `Hurry Research` late in the game. Tech transfers are therefore **not guaranteed to be applied by AI**.
3. Tech blueprints grant the named tech even if the recipient did not research normal prerequisites; test carefully if this matters for your progression settings.
4. Gifts need eligible territory, movement, and no transport. A mod cannot grant the normal Gift Unit action anywhere on the map without changes to Unciv's Kotlin source.
5. There is no automatic tech matching, no global tech synchronizing, and no diplomacy-screen technology trading. Those require an Unciv engine/UI patch.
6. All technology aid units remain buildable and usable by Magalanadu itself, so they can also be used for self-research. Production costs are set to make that a deliberate choice.
7. New icons use `MagalanaduAid.atlas` in an independently registered atlas page; original atlases are not repacked.

## Preservation

Existing original 42 units, 24 buildings, 9 improvements, 3 promotion groups, Magalanadu nation, repeatable power projects, 5-tile capital improvement range, and all original graphics have been retained.

## Testing

Run `python tests/validate_mod.py` and `python tests/validate_diplomatic_aid.py`. Official `Unciv.jar mod-ci` plus in-game two-player/AI tests are still needed before release-grade certification.

**Specific tests:** friendly civ gift, hostile territory prohibition, transported unit prohibition, specific blueprint activation for a human recipient, generic free technology selection, and AI fallback in late game.
