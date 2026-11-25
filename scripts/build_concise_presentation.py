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
MAX_WORDS=34;TALK_SECONDS=1200;SESSION_SECONDS=1200

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
  features.append({'name':pr['ADMIN'],'name_tr':pr.get('NAME_TR') or pr['ADMIN'],'c':[round(pr.get('LABEL_X') or 0,2),round(pr.get('LABEL_Y') or 0,2)],'iso2':pr.get('ISO_A2_EH') or pr.get('ISO_A2'),'fips':pr.get('FIPS_10'),'names':names,'polygons':polys})
 return features

# GDELT source-country names that differ from Natural Earth ADMIN names
ALIAS={'unitedstates':'United States of America','czechrepublic':'Czechia','bosniaherzegovina':'Bosnia and Herzegovina','macedonia':'North Macedonia','serbia':'Republic of Serbia','tanzania':'United Republic of Tanzania','burma':'Myanmar','swaziland':'eSwatini','congo':'Republic of the Congo','bahamas':'The Bahamas','slovakrepublic':'Slovakia','eastimor':'East Timor','russianfederation':'Russia','southkorea':'South Korea','korea':'South Korea'}
MIN_ACTIVE,MIN_ARTICLES=100,5  # rate columns only for countries with stable denominators

def globe_data(features,snap,analysis):
 """Data for the 3D globe: every value comes from the archive scan outputs."""
 paper=O/'ANALIZ_SAYILARI.json';totals=R/'research/gdelt/gkg_archive/totals.json'
 if not (snap and paper.is_file() and totals.is_file()):return None
 S=json.loads(paper.read_text())['gdelt'];act=json.loads(totals.read_text()).get('active_domains_per_source_country',{})
 by={norm_name(f['name']):f for f in features};idx={}
 for f in features:
  for n in f['names']:idx.setdefault(n,f)
 def find(name):
  k=norm_name(name)
  return by.get(norm_name(ALIAS[k])) if k in ALIAS else (by.get(k) or idx.get(k))
 from collections import Counter,defaultdict
 daily=defaultdict(Counter);seen=set()
 for a in snap['articles']:
  if a['url'] in seen:continue
  seen.add(a['url']);daily[a.get('sourcecountry') or ''][re.sub(r'\D','',a.get('seendate',''))[:8]]+=1
 countries=[]
 for x in S['all_countries']:
  f=find(x['country'])
  if not f:continue
  a=act.get(x['country'])
  countries.append({'name':f['name_tr'],'admin':f['name'],'lon':f['c'][0],'lat':f['c'][1],'articles':x['articles'],'outlets':x['outlets'],'active':a,
   'per1000':round(x['outlets']/a*1000,1) if a else None,'rate_shown':bool(a and a>=MIN_ACTIVE and x['articles']>=MIN_ARTICLES),'daily':dict(sorted(daily[x['country']].items()))})
 tc=analysis['findings']['target_country_counts'];tmap={'Germany':'Germany','UK':'United Kingdom','France':'France','Italy':'Italy','Latvia':'Latvia','Ukraine':'Ukraine'}
 targets=[{'admin':adm,'name':by[norm_name(adm)]['name_tr'],'lon':by[norm_name(adm)]['c'][0],'lat':by[norm_name(adm)]['c'][1],'domains':tc[k]} for k,adm in tmap.items()]
 places=[{'name':r['name'],'lat':r['lat'],'lon':r['lon'],'articles':r['articles']} for r in (snap.get('locations') or {}).get('rows',[])[:70]]
 return {'countries':countries,'targets':targets,'places':places,'days':[d['day'] for d in snap['daily']],'total':S['matched_articles'],'rows_scanned':S['rows_scanned'],
  'mention_de_pct':S['mention_share_pct']['GM'],'outlet_ratio':S['outlet_ratio_us_de'],'two_day_pct':S['two_day_share_pct'],'distinct_titles':S['distinct_titles'],
  'titles_us':S['levels']['United States']['titles'],'min_active':MIN_ACTIVE,'min_articles':MIN_ARTICLES,'unique_domains':analysis['audit']['unique_domains']}

def typology_data(analysis):
 import domain_typology as dt
 t=dt.analyse(analysis['records'])
 return {'rows':[[r['first_dns_label'],r['last_dns_label'],r['class'],r['brand'] or '',int(r['anagram_family'])] for r in t['rows']],'families':t['families'],'counts':t['class_counts'],
  'top6':['online','website','site','space','pw','fun'],'top6_by_class':t['top6_tld_by_class'],'family_domains':t['anagram_family_domains'],'family_count':t['anagram_families'],'brand_tlds':len(t['tld_by_class']['marka_birebir'])}

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
 snap=load_snapshot();(snap or {}).get('validation',{}).pop('coder_note',None);features=world_features()
 payload={'slides':s,'appendices':a,'references':refs,'analysis':analysis,'features':features,'gdelt':snap,'globe':globe_data(features,snap,analysis),'typology':typology_data(analysis),'gdelt_config':{'query':QUERY,'windows':WINDOWS,'max_records':MAX_RECORDS,'endpoint':DOC_ENDPOINT,'schema':SCHEMA,'warnings':['sourcecountry haberin yayımlandığı ülkedir; hedef ülke veya okur ülkesi değildir.','Her dilim en fazla 250 makale döndürür; capped=true olan dilimlerde seçki eksiktir.','Eşleşme anahtar sözcüğe dayanır; makalelerin konuyla ilgisi elle kodlanmamıştır.']},'meta':meta,'timing':{'talk':TALK_SECONDS,'session':SESSION_SECONDS}}
 result=(R/'scripts/concise.html').read_text().replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('</','<\\/'))
 for token,path in [('__LEAFLET_CSS__','assets/vendor/leaflet.css'),('__LEAFLET_JS__','assets/vendor/leaflet.js'),('__BASEMAP_JS__','scripts/basemap.js'),('__CSS__','scripts/concise.css'),('__JS__','scripts/concise.js'),('__GDELT_JS__','scripts/gdelt_map.js'),('__THREE_JS__','assets/vendor/three.min.js'),('__SCENE3D_JS__','scripts/scene3d.js')]:result=result.replace(token,(R/path).read_text())
 for name in ['AKADEMIK_ODAKLI_SUNUM.html','PROFESYONEL_SUNUM.html','SINEMATIK_SUNUM.html','CANLI_HARITA.html','GORUNMEZ_CEPHE_ATLAS.html']:(O/name).write_text(result)
 (O/'APA7_KAYNAKCA.md').write_text('# Kaynakça / APA 7\n\n'+'\n\n'.join(r['apa'].replace('<i>','*').replace('</i>','*')+' '+r['url'] for r in refs)+'\n')
 print(f'Built {len(s)} main slides; {len(a)} appendices; {TALK_SECONDS}s talk + {SESSION_SECONDS-TALK_SECONDS}s buffer; GDELT snapshot embedded: {bool(snap)}; HTML {len(result)//1024} KB.')

if __name__=='__main__':main()
