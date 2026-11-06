#!/usr/bin/env python3
"""Patch a LOCAL checkout of upstream Unciv tag 4.22.16. Run on source, not the JSON mod.

This script modifies two Kotlin files. It cannot create/install an APK by itself.
"""
from pathlib import Path
import sys

UNIT_ACTION_START = '    private fun getGiftActions(unit: MapUnit, tile: Tile) = sequence {'
UNIT_ACTION_END = '    private suspend fun SequenceScope<UnitAction>.addAutomateActions'

NEW_GIFT = r"""
    // MAGALANADU_V3_2_MAJOR_CIV_GIFT_FIX
    private fun getGiftActions(unit: MapUnit, tile: Tile) = sequence {
        val donor = unit.civ
        val fromMagalanadu = donor.civName == "Magalanadu"
        val tileOwner = tile.getOwner()
        val recipients = linkedSetOf<com.unciv.logic.civilization.Civilization>()
        if (tileOwner != null && tileOwner != donor)
            recipients.add(tileOwner)

        // Unlike stock Unciv, a Magalanadu donor can give across an adjacent border.
        // This works for envoys and other civilians even if Open Borders isn't signed.
        if (fromMagalanadu) {
            for (neighbor in tile.neighbors) {
                val candidate = neighbor.getOwner() ?: continue
                if (candidate != donor && candidate.isMajorCiv)
                    recipients.add(candidate)
            }
        }

        if (unit.isTransported) return@sequence
        for (recipient in recipients) {
            // Never allow gifts during war; the Gift action is intended for peaceful aid.
            if (recipient.isAtWarWith(donor)) continue

            if (recipient.isCityState) {
                // Preserve Unciv's original City-State behavior and civilian eligibility.
                if (tileOwner != recipient) continue
                if (!unit.isMilitary() && unit.getMatchingUniques(
                    UniqueType.GainInfluenceWithUnitGiftToCityState,
                    checkCivInfoUniques = true
                ).none { unit.matchesFilter(it.params[1]) }) continue
            } else if (!fromMagalanadu && !tile.isFriendlyTerritory(donor)) {
                // No changes to non-Magalanadu major-civ gifting behavior.
                continue
            }

            val isBorderExport = tileOwner != recipient
            val giftAction = {
                if (recipient.isCityState) {
                    for (unique in unit.getMatchingUniques(
                        UniqueType.GainInfluenceWithUnitGiftToCityState,
                        checkCivInfoUniques = true
                    )) {
                        if (unit.matchesFilter(unique.params[1])) {
                            recipient.getDiplomacyManager(donor)!!
                                .addInfluence(unique.params[0].toFloat() - 5f)
                            break
                        }
                    }
                    recipient.getDiplomacyManager(donor)!!.addInfluence(5f)
                } else {
                    recipient.getDiplomacyManager(donor)!!
                        .addModifier(DiplomaticModifiers.GaveUsUnits, 5f)
                }

                if (recipient.isCityState && unit.isGreatPerson()) {
                    unit.destroy()
                } else {
                    unit.gift(recipient)
                    // A gifted unit originating just outside the border must be relocated
                    // if the new owner cannot legally stay in its old tile.
                    if (isBorderExport) {
                        // Prefer actually placing the unit on the recipient's side,
                        // since Magalanadu's border-passage ability would otherwise
                        // let it remain visibly inside the donor's territory.
                        val destination = tile.neighbors.firstOrNull { neighbor ->
                            neighbor.getOwner() == recipient &&
                                unit.movement.canMoveTo(neighbor) &&
                                neighbor.getUnits().all { it.civ == recipient }
                        }
                        if (destination != null) {
                            unit.removeFromTile()
                            unit.putInTile(destination)
                            unit.updateVisibleTiles()
                        } else {
                            unit.movement.teleportToClosestMoveableTile()
                        }
                        unit.currentMovement = 0f
                    }
                }

                // The existing v3.1 mod's loss-in-foreign-territory reward triggers
                // only for units actually standing on the recipient's tile. For an
                // adjacent Magalanadu export, pay the same 2x-production-cost reward.
                // This is generated Gold, NOT deducted from the receiving Civ.
                if (fromMagalanadu && isBorderExport)
                    donor.addGold(unit.baseUnit.cost.coerceAtLeast(0) * 2)
            }

            yield(UnitAction(
                UnitActionType.GiftUnit,
                title = "Gift to [${recipient.civName}]",
                action = giftAction.takeIf { unit.hasMovement() }
            ))
        }
    }

"""

# Also award all compatible promotions to units spawned or granted rather than trained.
# This avoids reliance on unit-specific or city training paths.
UNIT_MANAGER_ANCHOR = '        copiedFrom?.copyStatisticsTo(unit)'
UNIT_MANAGER_INJECT = r"""

        // MAGALANADU_V3_2_SPAWN_PROMOTIONS
        // Applies to bought, trained, starting, gifted-in or spawned Magalanadu units.
        // Only grant promotions relevant to the unit type; exclude one-time healing
        // and harmful/hidden pseudo-promotions that would break normal unit actions.
        if (civInfo.civName == "Magalanadu") {
            for (promotion in civInfo.gameInfo.ruleset.unitPromotions.values) {
                if (unit.baseUnit.unitType !in promotion.unitTypes) continue
                if (promotion.name == "Heal Instantly" ||
                    promotion.name == "Unable to pillage tiles") continue
                if (promotion.hasUnique(UniqueType.SkipPromotion, unit.cache.state) ||
                    promotion.hasUnique(UniqueType.Unavailable, unit.cache.state)) continue
                unit.promotions.addPromotion(promotion.name, isFree = true)
            }
        }
"""

def patch_unciv(root: Path) -> None:
    files = [
        root / 'core/src/com/unciv/logic/map/mapunit/actions/UnitActions.kt',
        root / 'core/src/com/unciv/logic/civilization/managers/UnitManager.kt',
    ]
    for f in files:
        if not f.is_file():
            raise FileNotFoundError(f'Missing game source file: {f}')
    actions = files[0].read_text(encoding='utf-8')
    manager = files[1].read_text(encoding='utf-8')
    if 'MAGALANADU_V3_2_MAJOR_CIV_GIFT_FIX' in actions and 'MAGALANADU_V3_2_SPAWN_PROMOTIONS' in manager:
        print('Already patched. No changes.')
        return
    if 'MAGALANADU_V3_2_MAJOR_CIV_GIFT_FIX' in actions or 'MAGALANADU_V3_2_SPAWN_PROMOTIONS' in manager:
        raise ValueError('Only part of the patch appears present. Restore original files first.')
    if actions.count(UNIT_ACTION_START)!=1 or actions.count(UNIT_ACTION_END)!=1:
        raise ValueError('Unexpected UnitActions.kt version, expected original Unciv 4.22.16')
    if manager.count(UNIT_MANAGER_ANCHOR)!=1:
        raise ValueError('Unexpected UnitManager.kt version, expected original Unciv 4.22.16')
    a=actions.index(UNIT_ACTION_START)
    b=actions.index(UNIT_ACTION_END,a)
    patched_actions=actions[:a]+NEW_GIFT+actions[b:]
    patched_manager=manager.replace(UNIT_MANAGER_ANCHOR,UNIT_MANAGER_ANCHOR+UNIT_MANAGER_INJECT,1)
    for f, old, new in [(files[0],actions,patched_actions),(files[1],manager,patched_manager)]:
        backup=f.with_name(f.name+'.before-magalanadu-v3.2')
        if backup.exists():
            raise FileExistsError(f'Refusing to overwrite existing backup: {backup}')
        backup.write_text(old,encoding='utf-8')
        f.write_text(new,encoding='utf-8')
        print(f'Patched {f.relative_to(root)}; backup {backup.name}')

if __name__=='__main__':
    if len(sys.argv)!=2:
        sys.exit('Usage: python patch_unciv_4_22_16.py /path/to/Unciv/source/checkout')
    patch_unciv(Path(sys.argv[1]).expanduser().resolve())
