"""Build an offline, self-contained interactive presentation from archived evidence."""
import base64,csv, json, pathlib,re,runpy
R=pathlib.Path(__file__).resolve().parents[1]
slides=runpy.run_path(str(R/'scripts/build_presentation.py'))['S']
narrative=json.loads((R/'scripts/cinematic_narrative.json').read_text())
references=json.loads((R/'scripts/academic_references.json').read_text())
appendices=json.loads((R/'scripts/academic_appendices.json').read_text())
assert len(narrative)==18 and sum(x['seconds'] for x in narrative)==900
slides=[{'title':x['title'],'kicker':x['kicker'],'bullets':[x['lead'],re.sub('<[^>]+>','',x['fact'])],'notes':x['notes'],'cue':x.get('cue',''),'seconds':x['seconds'],'source':x['source'],'citations':x['citations']} for x in narrative]+appendices
locations=json.loads((R/'assets/locations/locations.json').read_text())
for location in locations.values():location['src']='data:image/jpeg;base64,'+base64.b64encode((R/'assets/locations'/location['image']).read_bytes()).decode()
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
payload={'records':data,'features':features,'slides':slides,'narrative':narrative,'locations':locations,'references':references,
 'source':'https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv',
 'hash':json.loads((R/'output/veri_manifest.json').read_text())['files'][str(raw.relative_to(R))]['sha256']}
template=(R/'scripts/professional.html').read_text()
result=template.replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
result=result.replace('__LEAFLET_CSS__',(R/'assets/vendor/leaflet.css').read_text()).replace('__LEAFLET_JS__',re.sub(r'//# sourceMappingURL=.*','',(R/'assets/vendor/leaflet.js').read_text()))
result=result.replace('__STYLE__',(R/'scripts/professional.css').read_text()).replace('__SCRIPT__',(R/'scripts/basemap.js').read_text()+'\n'+(R/'scripts/professional.js').read_text())
for name in ['PROFESYONEL_SUNUM.html','CANLI_HARITA.html','GORUNMEZ_CEPHE_ATLAS.html','SINEMATIK_SUNUM.html']:
 (R/'output'/name).write_text(result,encoding='utf8')
notes=['# Görünmez Cephe — akademik konuşma metni','', f"18 ana sahne · 15 dakika · {len(appendices)} yöntem/kaynakça eki. Yaklaşık {sum(len(x['notes'].split()) for x in narrative)} sözcük; 104 sözcük/dakika ve harita duraklamalarıyla prova edilmelidir. 900 saniye planlanan süredir, gerçek okuma süresi konuşmacıya bağlıdır.",'', 'Konum görselleri bağlamdır. Güncel otomatik GDELT yanıtı gelmesi, 2022 tarihsel analizinin tamamlandığı anlamına gelmez.',''];elapsed=0
for i,s in enumerate(slides):
 end=elapsed+s['seconds'];slot=f'{elapsed//60:02}:{elapsed%60:02}–{end//60:02}:{end%60:02}' if i<len(narrative) else 'Soru-cevap eki'
 notes.extend([f"## {i+1}. {s['title']} · {slot}",'',s['notes'],'',f"Sahne yönergesi (okunmaz): {s['cue']}" if s.get('cue') else '',f"Metin içi atıf: {s['source']}",'']);elapsed=end
notes.extend(['## APA 7 kaynakça','']+[re.sub('<[^>]+>','',r['apa'])+' '+r['url']+'\n' for r in references])
(R/'output/KONUSMACI_NOTLARI.md').write_text('\n'.join(notes),encoding='utf8')
(R/'output/APA7_KAYNAKCA.md').write_text('# APA 7 kaynakça\n\nAlfabetik sıra. Erişim türleri ve denetim sınırları AKADEMIK_KAYNAK_DENETIMI.md içindedir.\n\n'+'\n\n'.join(r['apa'].replace('<i>','*').replace('</i>','*')+' '+r['url'] for r in references),encoding='utf8')
print('Leaflet research presentation:',len(data),'unique indicators;',len(narrative),'timed scenes;',len(slides),'slides; 4 real context images.')
