#!/usr/bin/env python3
"""Offline regression and balance validation for Magalanadu (Unciv 4.22.16).

Unciv's official mod-ci must still be run in GitHub Actions or in the game.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
J = ROOT / 'jsons'
F = json.loads((ROOT / 'compatibility' / 'balance_manifest.json').read_text('utf-8'))
errors=[]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
current={file:load(J/file) for file in F['originalObjectNames']}
original={file:load(ROOT/'backup'/'prebalance_ruleset'/file) for file in F['originalObjectNames']}

for file,objs in current.items():
    names=[x.get('name') for x in objs]
    old_names=F['originalObjectNames'][file]
    if len(names)!=len(set(names)):errors.append(f'{file}: duplicate object name')
    retired=set(F.get('removedUnits',[])) if file=='Units.json' else set()
    for name in old_names:
        if name not in names and name not in retired:errors.append(f'{file}: deleted original {name}')
    if file=='Units.json':
        for name in retired:
            if name in names:errors.append(f'{file}: retired unit still active: {name}')
    if file=='Buildings.json':
        if names[:len(old_names)]!=old_names:errors.append('Original building order changed')
        if names[len(old_names)+len(F['newRepeatableProjects']):]!=F.get('newResourceBuildings',[]):errors.append('New resource supply buildings missing or out of order')
        if len(names)!=len(old_names)+len(F['newRepeatableProjects'])+len(F.get('newResourceBuildings',[])):errors.append('Wrong number of new buildings')
    elif file=='Units.json':
        retained_old=[name for name in old_names if name not in F.get('removedUnits',[])]
        if names[:len(retained_old)]!=retained_old: errors.append('Existing retained unit names/order changed')
        if names[len(retained_old):]!=F['newDiplomaticAidUnits']+F.get('newResourceUnits',[]): errors.append('Diplomatic aid unit list incomplete or changed')
    elif file=='TileImprovements.json':
        if names[:len(old_names)]!=old_names or names[len(old_names):]!=F.get('newResourceImprovements',[]): errors.append('Resource fabricator improvements missing or out of order')
    elif names!=old_names: errors.append(f'{file}: original object names/order changed')
    if hashlib.sha256((ROOT/'backup'/'prebalance_ruleset'/file).read_bytes()).hexdigest()!=F['originalRuleHashes'][file]:
        errors.append(f'Original backup altered: {file}')
    print(f'{file}: {len(names)} definitions')

# There must be no overpowered numeric boosts outside clearly optional, manually constructed projects.
nation=current['Nations.json'][0]
if nation['name']!='Magalanadu':errors.append('Magalanadu nation missing')
for u in nation['uniques']:
    if re.search(r'\[([+-]?\d{3,})\]%',u):errors.append('Massive passive nation bonus: '+u)
for o in current['Buildings.json']:
    if o['name'] not in F['newRepeatableProjects']:
        if o.get('cost')!=5:errors.append('Custom building base Production cost is not 5: '+o['name'])
        for u in o.get('uniques',[]):
            if re.search(r'\[([+-]?\d{3,})\]%',u):errors.append('Massive passive legacy building bonus: '+o['name']+' '+u)
for o in current['Units.json']:
    if o.get('cost') is not None and o['cost']<40:errors.append('Cheap custom unit: '+o['name'])
    if o.get('strength',0)>260:errors.append('Overpowered unit strength: '+o['name'])
for o in current['TileImprovements.json']:
    for stat in ('gold','food','production','faith','science','culture'):
        if o.get(stat,0)>12: errors.append('Excessive tile yield '+o['name']+' / '+stat)

projects={b['name']:b for b in current['Buildings.json'] if b['name'] in F['newRepeatableProjects']}
if len(projects)!=10:errors.append('Missing repeatable projects')
for name,b in projects.items():
    if b.get('uniqueTo')!='Magalanadu':errors.append(f'{name}: not limited to Magalanadu')
    if b.get('isWonder') or b.get('isNationalWonder'):errors.append(f'{name}: must be ordinary repeatable build')
    u=b.get('uniques',[])
    if 'Cannot be purchased' in u:errors.append(f'{name}: cash purchase still blocked')
    if u[-1]!=f'Remove [{name}] [in this city]':errors.append(f'{name}: self-removal must be LAST')
    if not any('<for [9999] turns>' in a for a in u):errors.append(f'{name}: no persistent stackable reward')
    if any('Can be built [' in a for a in u):errors.append(f'{name}: 4.22.16 does not implement repeat-build unique')
    if b.get('cost') != 5:errors.append(f'{name}: incorrect base production cost')

treasury=projects.get('Magalanadu Treasury Contract',{})
if 'Gain [999999999] [Gold]' not in treasury.get('uniques',[]):errors.append('Gold lump-sum reward missing')
if '[+9999 Gold] [in capital] <for [9999] turns>' not in treasury.get('uniques',[]):errors.append('Treasury recurring +9999 Gold missing')

names_by_file={file:set(o['name'] for o in values) for file,values in current.items()}
nations=names_by_file['Nations.json'];promos=names_by_file['UnitPromotions.json'];units=names_by_file['Units.json']
for section in ('Buildings.json','TileImprovements.json','Units.json'):
    for o in current[section]:
        if o.get('uniqueTo') not in (None,*nations):errors.append('Bad uniqueTo: '+o['name'])
for u in current['Units.json']:
    if u.get('upgradesTo','').startswith(('Magalanadu ','Indian ')) and u['upgradesTo'] not in units:
        errors.append('Missing custom upgrade: '+u['name'])
    for name in u.get('promotions',[]):
        if name.endswith(' Magalanadu Ability') and name not in promos:
            errors.append('Missing promotion: '+name)
for b in current['Buildings.json']:
    for text in b.get('uniques',[]):
        m=re.search(r'receive the \[([^\]]+)\] promotion$',text)
        if m and m.group(1) not in promos:errors.append('Missing training promotion: '+m.group(1))

options=load(J/'ModOptions.json')
if options.get('isBaseRuleset',False):errors.append('Must remain extension mod')
if options.get('constants',{}).get('cityWorkRange')!=5 or options.get('constants',{}).get('cityExpandRange')!=5:
    errors.append('5-tile working/expansion range not preserved')

atlas_names=load(ROOT/'Atlases.json')
if atlas_names!=F['atlasPages']:errors.append('Atlas registrations incorrect')
for name in atlas_names:
    if not (ROOT/(name+'.png')).is_file(): errors.append('Missing '+name+'.png')
    if not (ROOT/(name+'.atlas')).is_file(): errors.append('Missing '+name+'.atlas')
all_atlas=set()
for name in atlas_names:
    if not (ROOT/(name+'.atlas')).exists():continue
    text=(ROOT/(name+'.atlas')).read_text('utf8')
    for key in re.findall(r'^(\w+Icons/[^\n\r]+)$',text,re.M):
        if key in all_atlas:errors.append('Sprite registered twice: '+key)
        all_atlas.add(key)
all_icons={p.relative_to(ROOT/'Images').with_suffix('').as_posix() for p in (ROOT/'Images').rglob('*.png')}
for sprite in sorted(all_icons-all_atlas):errors.append('Missing sprite: '+sprite)
for sprite in sorted(all_atlas-all_icons):errors.append('Orphaned atlas sprite: '+sprite)
print(f'Icons: {len(all_icons)} PNGs / {len(all_atlas)} atlas regions')

for file,folder in [('Nations.json','NationIcons'),('Buildings.json','BuildingIcons'),('Units.json','UnitIcons'),('UnitPromotions.json','UnitPromotionIcons'),('TileImprovements.json','ImprovementIcons')]:
    for o in current[file]:
        if not (ROOT/'Images'/folder/(o['name']+'.png')).exists():errors.append('Icon missing: '+o['name'])

abilities=sum(len(o.get('uniques',[])) for objs in current.values() for o in objs)
if abilities!=F['newUniqueEntries']:errors.append(f'Unexpected ability count: {abilities}')
print('Unique-ability entries:',abilities)
if errors:
    print('\nFAILED with',len(errors),'error(s):')
    for e in errors:print(' -',e)
    sys.exit(1)
print('PASS: all non-retired original objects preserved; one non-working terraformer retired; repeatable projects, aid units, backups, balance and atlases checked.')
print('NOTE: Official Unciv mod-ci and actual gameplay testing are required to certify runtime behavior.')
