#!/usr/bin/env python3
"""Patch clean Unciv tag 4.22.16 with stable v3.2 gifting, then v4.0 Directorate.

Idempotent for v4.0. Refuses unexpected source shapes, protects backups.
"""
from pathlib import Path
import sys
from patch_unciv_4_22_16 import patch_unciv

LAUNCHER_ANCHOR = '        yieldAll(UnitActionsUpgrade.getUpgradeActions(unit))'
LAUNCHER_PATCH = '''

        // MAGALANADU_V4_0_DIRECTORATE_LAUNCHER
        // Expose one visible action on every own Magalanadu unit.
        if (unit.civ.civName == "Magalanadu" && unit.civ.isCurrentPlayer()) {
            yield(UnitAction(
                UnitActionType.TriggerUnique,
                title = "MAGALANADU STRATEGIC DIRECTORATE",
                action = { com.unciv.ui.popups.MagalanaduDirectorate.open(unit) }
            ))
        }
'''
GIFT_ANCHOR = '''            yield(UnitAction(
                UnitActionType.GiftUnit,
                title = "Gift to [${recipient.civName}]",
                action = giftAction.takeIf { unit.hasMovement() }
            ))'''
GIFT_PATCH = '''

            // MAGALANADU_V4_0_ARMS_EXPORT_CONTRACT
            // Separate action from a free gift. The receiving major Civ pays GPT
            // using normal saved Trade records. Both actions transfer the same unit.
            if (fromMagalanadu && recipient.isMajorCiv && unit.isMilitary()) {
                val installment = (unit.baseUnit.cost / 20).coerceIn(5, 250)
                yield(UnitAction(
                    UnitActionType.GiftUnit,
                    title = "Arms contract to [${recipient.civName}] ($installment Gold/turn)",
                    action = ({
                        val value = unit.baseUnit.cost
                        giftAction.invoke()
                        com.unciv.ui.popups.MagalanaduDirectorate.registerArmsContract(donor, recipient, value)
                        Unit  // Preserve the UnitAction.action lambda return type.
                    }).takeIf { unit.hasMovement() }
                ))
            }
'''


def apply(root: Path) -> None:
    root = root.resolve()
    patch_unciv(root)
    actions = root/'core/src/com/unciv/logic/map/mapunit/actions/UnitActions.kt'
    destination = root/'core/src/com/unciv/ui/popups/MagalanaduDirectorate.kt'
    source = Path(__file__).with_name('MagalanaduDirectorate.kt')
    if not source.is_file() or not actions.is_file() or not destination.parent.is_dir():
        raise FileNotFoundError('Missing Unciv source directory or MagalanaduDirectorate.kt payload')
    text = actions.read_text(encoding='utf8')
    if 'MAGALANADU_V4_0_DIRECTORATE_LAUNCHER' not in text:
        assert text.count(LAUNCHER_ANCHOR) == 1, 'Unexpected UnitActions.kt launcher anchor'
        text = text.replace(LAUNCHER_ANCHOR, LAUNCHER_ANCHOR+LAUNCHER_PATCH, 1)
    if 'MAGALANADU_V4_0_ARMS_EXPORT_CONTRACT' not in text:
        assert text.count(GIFT_ANCHOR) == 1, 'Unexpected UnitActions.kt gifts anchor'
        text = text.replace(GIFT_ANCHOR, GIFT_ANCHOR+GIFT_PATCH, 1)
    if text != actions.read_text(encoding='utf8'):
        backup = actions.with_name(actions.name+'.before-magalanadu-v4.0')
        if backup.exists():
            raise FileExistsError(f'Refusing to overwrite prior backup: {backup}')
        backup.write_text(actions.read_text(encoding='utf8'), encoding='utf8')
        actions.write_text(text, encoding='utf8')
        print('Injected Directorate and Arms Contract actions into UnitActions.kt')
    if destination.exists():
        if destination.read_bytes() != source.read_bytes():
            raise FileExistsError('Existing Directorate file differs. Restore source and patch again.')
    else:
        destination.write_bytes(source.read_bytes())
        print('Added real diplomacy/economic control UI: MagalanaduDirectorate.kt')
    assert 'MAGALANADU_V4_0_ARMS_EXPORT_CONTRACT' in text
    assert 'MAGALANADU_V4_0_DIRECTORATE_LAUNCHER' in text

if __name__ == '__main__':
    if len(sys.argv)!=2:
        sys.exit('Usage: python engine_patch/patch_unciv_v4_0.py path/to/Unciv-4.22.16')
    apply(Path(sys.argv[1]).expanduser())
