#!/usr/bin/env python3
"""Offline v3.0 ruleset and resource/war-unit cleanup checks.

Does not substitute for Unciv 4.22.16 mod-ci and in-game tests.
"""
from pathlib import Path
import json, re, hashlib, sys, collections
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
J=ROOT/'jsons'
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def read(name):return load(J/(name+'.json'))
errors=[]
def check(ok,message):
    if not ok: errors.append(message)

B=read('Buildings');U=read('Units');I=read('TileImprovements');N=read('Nations');P=read('UnitPromotions');O=read('ModOptions')
manifest=load(ROOT/'compatibility'/'balance_manifest.json')
old=load(ROOT/'compatibility'/'balance_manifest_v2_9.json')
removed=set(manifest['v3Changes']['removedUnits'])
removed_buildings=set(manifest['v3Changes']['removedResourceBuildings'])
assert len(removed)==12 and len(removed_buildings)==35

def names(entities):return [o['name'] for o in entities]
for title,entities,expected in [('Nations',N,1),('Units',U,53),('Buildings',B,24),('TileImprovements',I,44),('UnitPromotions',P,3)]:
    check(len(entities)==expected,f'{title}: expected {expected}, got {len(entities)}')
    check(len(set(names(entities)))==len(entities), f'{title}: duplicate object names')
    print(f'{title}: {len(entities)}')

check(set(names(U)).isdisjoint(removed),'Retired units still present')
check(set(names(B)).isdisjoint(removed_buildings),'Removed resource supply buildings still present')
check(set(names(B))==set(manifest['originalObjectNames']['Buildings.json'])|set(manifest['newRepeatableProjects']),'Original buildings or Supreme Projects missing')
check(set(names(I))==set(manifest['originalObjectNames']['TileImprovements.json'])|set(manifest['newResourceImprovements']),'Existing tile improvements missing')
expected_units=(set(old['originalObjectNames']['Units.json']) | set(old['newDiplomaticAidUnits']) | set(old['newResourceUnits'])) - set(old['removedUnits']) - removed
check(set(names(U))==expected_units,'Retained unit roster does not match v2.9 minus explicit removals')
# Git normally converts CRLF to LF when committing text files. The original source
# archive contains mixed CRLF/LF endings, so its raw SHA-256 hashes do not always
# survive Git's standard line-ending normalization. Check a canonical, LF-only
# hash instead. This remains a cryptographic content-integrity check: changing any
# JSON text other than the CRLF vs LF representation still fails.
# These canonical digests were calculated from the ORIGINAL repository archive,
# after verifying every archival file against its `originalRuleHashes` raw SHA-256.
# They are fixed reference values, NOT recalculated from current backup files.
# This protects real backup changes without relying on a second manifest update.
_CANONICAL_HISTORICAL_SOURCE_HASHES = {
    "Units.json": "29a8523d50c830791a093497e6658d3259aad7e8fac5c0e8c5c8b515b268a553",
    "Nations.json": "ac192c707dc8d0c60a7d57e1eb3dc4538087be3d6cc24e364bfa359ea86ebb56",
    "ModOptions.json": "108a9bf17ff58b8abc06ed2aa0d81a7073395c04c9d720c55fa644e87c69b557",
    "TileImprovements.json": "b4e773c713736f5ffe260258e97e03a452e2ef537f3f7bcc4799bac24a02b0dd",
    "Buildings.json": "e462636d3f90458a9b876476cfca07a4ca63c9c03d0917572a3ae885f4d82fef",
    "UnitPromotions.json": "32f1cae247893eb8e856252f73c550ca6c158ef974a59c4f552fea0e38db3aa0"
}
normalized_expected = _CANONICAL_HISTORICAL_SOURCE_HASHES
check(set(normalized_expected)==set(manifest['originalRuleHashes']),
      'Historical reference files do not match the original manifest')
if 'originalRuleHashesLFNormalized' in manifest:
    check(manifest['originalRuleHashesLFNormalized']==normalized_expected,
          'Historical normalized manifest disagrees with verified original archive')
for fname,sha in manifest['originalRuleHashes'].items():
    backup=ROOT/'backup'/'prebalance_ruleset'/fname
    if not backup.exists():
        check(False, 'Historical source backup missing: '+fname)
        continue
    data=backup.read_bytes()
    raw_hash=hashlib.sha256(data).hexdigest()
    normalized_hash=hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()
    check(raw_hash==sha or normalized_hash==normalized_expected[fname],
          'Historical source backup content changed: '+fname)

check(N[0]['name']=='Magalanadu','Magalanadu civilization not present')
check(not O.get('isBaseRuleset',False),'Mod incorrectly changed to base ruleset')
check(O['constants'].get('cityWorkRange')==5 and O['constants'].get('cityExpandRange')==5,'Original expansion range changed')

# No false-flag / third-party declaration mechanics claimed in active unit descriptions.
for unit in U:
    for unique in unit.get('uniques',[]):
        check(not any(f'[{item}]' in unique for item in removed),'Remaining unit references removed unit in '+unit['name']+' : '+unique)
    check(unit.get('uniqueTo')=='Magalanadu','Unit not Magalanadu-exclusive '+unit['name'])

# Only native, documented functionally concrete units are retained.
for keep in ['Super Cheat Worker','Super Cheat Settler','Magalanadu Drone Swarm','Magalanadu Divine Apostle','Magalanadu Peacekeeper Battalion',
             'Magalanadu Architect of Wonders','Magalanadu Foreign Aid Battalion','Magalanadu Relief Engineer',
             'Magalanadu Science Envoy','Magalanadu Technology Ambassador','Magalanadu Strategic Fabricator','Magalanadu Luxury Fabricator I','Magalanadu Luxury Fabricator II','Magalanadu Bonus Fabricator']:
    check(keep in names(U),'Required working unit lost: '+keep)

worker=next(u for u in U if u['name']=='Super Cheat Worker')
check(any('Can instantly construct a [Omni Resource Generator] improvement' in x for x in worker['uniques']),'Worker cannot instantly build Omni')
for expected in ['Can enter ice tiles','Can pass through impassable tiles','May travel on Water tiles without embarking','All tiles cost 1 movement']:
    check(expected in worker['uniques'],'Worker missing broad-terrain mobility: '+expected)
settler=next(u for u in U if u['name']=='Super Cheat Settler')
check(settler.get('movement')==300 and settler.get('replaces')=='Settler','300 movement Settler lost')
# Retained units must keep the 5x movement values from the 2.7 baseline (air relocation uses range).
baseline=load(ROOT/'compatibility'/'units_before_movement_v2_7.json')
check(len(baseline)==65,'Original 2.7 movement baseline unexpectedly changed')
base={u['name']:u for u in baseline}
for u in U:
    b=base.get(u['name'])
    check(b is not None,'No original movement value for '+u['name'])
    if b is None or u['name']=='Super Cheat Settler':continue
    check(u['movement']==b['movement']*5,f'5x movement lost for {u["name"]}: {u["movement"]}')
    if u['unitType'] in {'Bomber','Fighter','Missile'}:
        check(u.get('range',0)==b.get('range',0)*5,f'5x aircraft range lost for {u["name"]}')

omni=next(x for x in I if x['name']=='Omni Resource Generator')
for typ,expected_n in [('Strategic',6),('Luxury',22),('Bonus',7)]:
    group=manifest['v3Changes']['omniResourceCategories'][typ]
    check(len(group)==expected_n, f'{typ} group has {len(group)} names')
    for res in group:
        check(f'Provides [50] [{res}]' in omni['uniques'],f'Omni fails to supply 50 {res}')
res_uniques=[x for x in omni['uniques'] if x.startswith('Provides [')]
check(len(res_uniques)==35, f'Omni must supply exactly 35 resources, got {len(res_uniques)}')
check(len(set(res_uniques))==35,'Omni contains duplicate resource-grants')
check('Great Improvement' in omni['uniques'],'Omni Great Improvement tag lost')
check('Water' in omni['terrainsCanBeBuiltOn'] and 'Forest' in omni['terrainsCanBeBuiltOn'] and 'Jungle' in omni['terrainsCanBeBuiltOn'],'Omni terrain support degraded')
# Specialized resource fabrication still works for individual resource selection.
for group in ('Strategic','Luxury','Bonus'):
    for res in manifest['v3Changes']['omniResourceCategories'][group]:
        impname=f'Magalanadu {group} Fabricator - {res}'
        check(impname in names(I),'Individual fabricator deleted '+impname)

for b in B:
    uniques=b.get('uniques',[])
    check(b.get('cost')==5,'Building cheap production changed '+b['name'])
    for stat in ('Gold','Culture','Faith'):
        check(f'Can be purchased with [{stat}] [in all cities]' in uniques,'Cannot buy '+b['name']+' with '+stat)
    check('Cannot be purchased' not in uniques,'Cannot be purchased restriction reintroduced '+b['name'])
    check(b['uniqueTo']=='Magalanadu','Unrestricted building '+b['name'])
for nm in manifest['newRepeatableProjects']:
    b=next(x for x in B if x['name']==nm)
    check(b.get('uniques',[])[-1]==f'Remove [{nm}] [in this city]','Repeatability of project broken '+nm)

# Assets and atlases: no sprites for removed definitions and no orphaned atlas regions.
pages=load(ROOT/'Atlases.json')
check(pages==['game','MagalanaduProjects','MagalanaduAid','MagalanaduResources'],'Unexpected atlas registration')
check(not (ROOT/'MagalanaduResourceBuildings.png').exists(),'Obsolete resource-building atlas still present')
allicons={p.relative_to(ROOT/'Images').with_suffix('').as_posix() for p in (ROOT/'Images').rglob('*.png')}
regions=[]
for page in pages:
    atlas=ROOT/(page+'.atlas');texture=ROOT/(page+'.png')
    check(atlas.exists() and texture.exists(),'Atlas page missing '+page)
    if atlas.exists():
        regions += re.findall(r'^(\w+Icons/[^\n\r]+)$',atlas.read_text(),re.M)
    if texture.exists():
        with Image.open(texture) as im:
            im.verify()
check(len(regions)==len(set(regions)),'Duplicate atlas regions')
check(allicons==set(regions),f'Icon assets and atlas regions mismatch: extra icons {sorted(allicons-set(regions))[:4]}, missing icons {sorted(set(regions)-allicons)[:4]}')
for category,objs in [('BuildingIcons',B),('UnitIcons',U),('ImprovementIcons',I),('NationIcons',N),('UnitPromotionIcons',P)]:
    for o in objs:
        check(f'{category}/{o["name"]}' in allicons, 'Missing sprite '+category+'/'+o['name'])
for nm in removed|removed_buildings:
    check(f'UnitIcons/{nm}' not in allicons and f'BuildingIcons/{nm}' not in allicons,'Dead sprite retained: '+nm)
print(f'Assets: {len(allicons)} icons; {len(regions)} atlas regions; {len(pages)} pages')
if errors:
    print('FAILED: '+str(len(errors))+' issues')
    for e in errors: print(' - '+e)
    sys.exit(1)
print('PASS: functional-unit cleanup, 50-supply Omni, 35 resource buildings removed, 5x movement retained, images and original files verified')
print('NOTE: Game runtime and official mod-ci not executed here')
