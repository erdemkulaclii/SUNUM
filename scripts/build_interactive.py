"""Build an offline, self-contained interactive presentation from archived evidence."""
import csv, json, pathlib, runpy
R=pathlib.Path(__file__).resolve().parents[1]
slides=runpy.run_path(str(R/'scripts/build_presentation.py'))['S']
raw=next((R/'research/meta/indicators/csv').glob('2022_09*'))
rows=[r for r in csv.DictReader(raw.open(encoding='utf-8-sig')) if r['indicator_type']=='domain_name']
unique=list({r['indicator_value'].lower():r for r in rows}.values())
data=[{'domain':r['indicator_value'].replace('.','[.]'),'country':r['comment'].split('-targeting')[0],'date':r['ds']} for r in unique]
geo=json.loads((R/'research/countries.geojson').read_text())
# Only retain European and neighbouring geometries, without external map tiles.
features=[]
for f in geo['features']:
 g=f['geometry']; ps=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 selected=[]
 for p in ps:
  if any(-25<x<48 and 28<y<73 for x,y in p[0]):selected.append(p)
 if selected:features.append({'name':f['properties']['ADMIN'],'polygons':selected})
payload={'records':data,'features':features,'slides':slides,
 'source':'https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv',
 'hash':json.loads((R/'output/veri_manifest.json').read_text())['files'][str(raw.relative_to(R))]['sha256']}
template=(R/'scripts/interactive.html').read_text()
result=template.replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
result=result.replace('</head>','<style>'+(R/'scripts/editorial.css').read_text()+'</style></head>')
result=result.replace('</body>','<script>'+(R/'scripts/editorial.js').read_text()+'</script></body>')
result=result.replace('</body>','<script>'+(R/'scripts/editorial_story.js').read_text()+'</script></body>')
(R/'output/CANLI_HARITA.html').write_text(result,encoding='utf8')
(R/'output/GORUNMEZ_CEPHE_ATLAS.html').write_text(result,encoding='utf8')
print('Offline interactive map built:',len(data),'unique indicators; 14 timed scenes.')
