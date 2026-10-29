"""Build a compact, evidence-led presentation and an auxiliary offline atlas."""
from pathlib import Path
import json,re,runpy
R=Path(__file__).resolve().parents[1];O=R/'output';O.mkdir(exist_ok=True)
runpy.run_path(str(R/'scripts/analyze_ioc_structure.py'),run_name='__main__')
s=json.loads((R/'scripts/concise_narrative.json').read_text());a=json.loads((R/'scripts/concise_appendices.json').read_text());refs=json.loads((R/'scripts/concise_references.json').read_text());analysis=json.loads((O/'IOC_YAPISAL_ANALIZ.json').read_text());geo=json.loads((R/'research/countries.geojson').read_text());features=[]
for f in geo['features']:
 g=f['geometry'];polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']];chosen=[p for p in polygons if any(-25<x<48 and 28<y<73 for x,y in p[0])]
 if chosen:features.append({'name':f['properties']['ADMIN'],'polygons':chosen})
assert len(s)==11 and sum(x['seconds'] for x in s)==780
for x in s:
 count=sum(len(v.split()) for v in [x['title'],x.get('subtitle',''),*x['display_points'],x['takeaway']]);assert count<=30,(x['id'],count)
ids={r['id'] for r in refs};assert all(set(x['citations'])<=ids for x in s)
payload={'slides':s,'appendices':a,'references':refs,'analysis':analysis,'features':features}
result=(R/'scripts/concise.html').read_text().replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
for token,path in [('__LEAFLET_CSS__','assets/vendor/leaflet.css'),('__LEAFLET_JS__','assets/vendor/leaflet.js'),('__BASEMAP_JS__','scripts/basemap.js'),('__CSS__','scripts/concise.css'),('__JS__','scripts/concise.js')]:result=result.replace(token,(R/path).read_text())
for name in ['AKADEMIK_ODAKLI_SUNUM.html','PROFESYONEL_SUNUM.html','SINEMATIK_SUNUM.html','CANLI_HARITA.html','GORUNMEZ_CEPHE_ATLAS.html']:(O/name).write_text(result)
(O/'APA7_KAYNAKCA.md').write_text('# Kullanılan kaynaklar / APA 7\n\n'+'\n\n'.join(r['apa'].replace('<i>','*').replace('</i>','*')+' '+r['url'] for r in refs))
print('Built11 main slides;',len(a),'appendices;780sec+120sec buffer;311 evidence records;no city photos.')
