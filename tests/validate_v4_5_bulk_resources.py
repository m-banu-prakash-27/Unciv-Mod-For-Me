#!/usr/bin/env python3
"""Static integration checks for Magalanadu v4.5 resource acquisition UI and engine wiring.
Not a replacement for full Android compile or actual gameplay testing.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
kt=(root/'engine_patch/MagalanaduDirectorate.kt').read_text(encoding='utf-8')
patch=(root/'engine_patch/patch_unciv_v4_4.py').read_text(encoding='utf-8')
workflow=(root/'.github/workflows/build-magalanadu-v4-5-android.yml').read_text(encoding='utf-8')
assert 'ACQUIRE ALL RESOURCES: every known civilization / City-State' in kt
assert 'ACQUIRE ALL ${available.size} RESOURCE TYPES (30 turns)' in kt
assert 'ACQUIRE ALL ${available.size} RESOURCE TYPES (9,999 turns)' in kt
assert 'ACQUIRE ALL $current $resourceName' in kt
assert 'CONFIRM: ACQUIRE EVERYTHING' in kt and 'CONFIRM: ACQUIRE FROM ALL' in kt
assert 'private fun availableResourceBundle' in kt
assert 'private fun acquireResourceBundle' in kt
assert 'val stillAvailable = availableResourceBundle(supplier)' in kt
assert 'if (available < quantity) return 0' in kt
assert 'if (total == 0) return 0' in kt
assert 'val mirror = trade.reverse()' in kt
assert 'playerDiplo.trades.add(trade)' in kt and 'supplierDiplo.trades.add(mirror)' in kt
assert 'ResourceType.Strategic -> TradeOfferType.Strategic_Resource' in kt
assert 'ResourceType.Luxury -> TradeOfferType.Luxury_Resource' in kt
assert 'ResourceType.Bonus' not in kt # No pretend bonus transfers
assert 'UniqueType.CannotBeTraded' in kt
assert 'MagalanaduDirectorate.kt' in (root/'engine_patch/patch_unciv_v4_0.py').read_text()
assert 'apply_v4_3(root)' in patch and 'MAGALANADU_V4_4_LOGISTICS_MENU' in patch
assert 'patch_unciv_v4_4.py game' in workflow
assert 'validate_v4_5_bulk_resources.py' in workflow
assert 'com.unciv.magalanadu.v45' in workflow
assert 'minWithOrNull' not in (root/'engine_patch/patch_unciv_v4_2.py').read_text()
assert (root/'engine_patch/MagalanaduLogistics.kt').exists()
assert (root/'engine_patch/MagalanaduTerraformEditor.kt').exists()
assert (root/'jsons/Buildings.json').exists()
print('PASS: v4.5 acquire-one/all selected/all-known source wiring; mirrored persistent trade; no duplicate overdraw; cumulative v4.4 patch; v4.3.1 repair')
