"""Build the academic presentation (HTML) with the embedded GDELT news map.

The GDELT layer is filled at presentation time (live request, local proxy or
a saved JSON snapshot). If research/gdelt/GDELT_HARITA_VERISI.json exists,
it is embedded so the map also works offline. No observations are invented.
"""
from pathlib import Path
import json,re,runpy,sys,unicodedata
sys.path.insert(0,str(Path(__file__).resolve().parent))
from gdelt_common import QUERY,WINDOWS,MAX_RECORDS,DOC_ENDPOINT,SCHEMA
R=Path(__file__).resolve().parents[1];O=R/'output';O.mkdir(exist_ok=True)
SNAPSHOT=R/'research/gdelt/GDELT_HARITA_VERISI.json'
MAX_WORDS=34;TALK_SECONDS=810;SESSION_SECONDS=900

def norm_name(s):
 s=unicodedata.normalize('NFKD',str(s)).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]','',s)

def simplify(ring,digits=2):
 out=[]
 for x,y in ring:
  p=[round(x,digits),round(y,digits)]
  if not out or out[-1]!=p:out.append(p)
 if out and out[0]!=out[-1]:out.append(out[0])
 return out if len(out)>=4 else None

def world_features():
 geo=json.loads((R/'research/countries.geojson').read_text());features=[]
 for f in geo['features']:
  pr=f['properties'];g=f['geometry'];polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
  polys=[]
  for poly in polygons:
   rings=[r for r in (simplify(r) for r in poly) if r]
   if rings:polys.append(rings)
  if not polys:continue
  names=sorted({norm_name(pr.get(k)) for k in ['ADMIN','NAME','NAME_LONG','NAME_EN','FORMAL_EN','NAME_ALT','BRK_NAME','GEOUNIT','SUBUNIT','NAME_SORT','NAME_CIAWF'] if pr.get(k)}-{''})
  features.append({'name':pr['ADMIN'],'name_tr':pr.get('NAME_TR') or pr['ADMIN'],'iso2':pr.get('ISO_A2_EH') or pr.get('ISO_A2'),'fips':pr.get('FIPS_10'),'names':names,'polygons':polys})
 return features

def load_snapshot():
 if not SNAPSHOT.is_file():return None
 snap=json.loads(SNAPSHOT.read_text())
 assert snap.get('schema')=='sunum.gdelt-map/1','Unexpected GDELT snapshot schema'
 assert isinstance(snap.get('articles'),list)
 snap['origin']='embedded_snapshot:'+snap.get('origin','unknown')
 return snap

def main():
 runpy.run_path(str(R/'scripts/analyze_ioc_structure.py'),run_name='__main__')
 s=json.loads((R/'scripts/concise_narrative.json').read_text());a=json.loads((R/'scripts/concise_appendices.json').read_text());refs=json.loads((R/'scripts/concise_references.json').read_text());analysis=json.loads((O/'IOC_YAPISAL_ANALIZ.json').read_text())
 meta=json.loads((R/'scripts/presentation_meta.json').read_text())
 assert sum(x['seconds'] for x in s)==TALK_SECONDS
 for x in s:
  count=sum(len(v.split()) for v in [x['title'],x.get('subtitle',''),*x['display_points'],x['takeaway']]);assert count<=MAX_WORDS,(x['id'],count)
 ids={r['id'] for r in refs};assert all(set(x['citations'])<=ids for x in s)
 snap=load_snapshot()
 payload={'slides':s,'appendices':a,'references':refs,'analysis':analysis,'features':world_features(),'gdelt':snap,'gdelt_config':{'query':QUERY,'windows':WINDOWS,'max_records':MAX_RECORDS,'endpoint':DOC_ENDPOINT,'schema':SCHEMA,'warnings':['sourcecountry haberin yayımlandığı ülkedir; hedef ülke veya okur ülkesi değildir.','Her dilim en fazla 250 makale döndürür; capped=true olan dilimlerde seçki eksiktir.','Eşleşme anahtar sözcüğe dayanır; makalelerin konuyla ilgisi elle kodlanmamıştır.']},'meta':meta,'timing':{'talk':TALK_SECONDS,'session':SESSION_SECONDS}}
 result=(R/'scripts/concise.html').read_text().replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
 for token,path in [('__LEAFLET_CSS__','assets/vendor/leaflet.css'),('__LEAFLET_JS__','assets/vendor/leaflet.js'),('__BASEMAP_JS__','scripts/basemap.js'),('__CSS__','scripts/concise.css'),('__JS__','scripts/concise.js'),('__GDELT_JS__','scripts/gdelt_map.js')]:result=result.replace(token,(R/path).read_text())
 for name in ['AKADEMIK_ODAKLI_SUNUM.html','PROFESYONEL_SUNUM.html','SINEMATIK_SUNUM.html','CANLI_HARITA.html','GORUNMEZ_CEPHE_ATLAS.html']:(O/name).write_text(result)
 (O/'APA7_KAYNAKCA.md').write_text('# Kaynakça / APA 7\n\n'+'\n\n'.join(r['apa'].replace('<i>','*').replace('</i>','*')+' '+r['url'] for r in refs)+'\n')
 print(f'Built {len(s)} main slides; {len(a)} appendices; {TALK_SECONDS}s talk + {SESSION_SECONDS-TALK_SECONDS}s buffer; GDELT snapshot embedded: {bool(snap)}; HTML {len(result)//1024} KB.')

if __name__=='__main__':main()
