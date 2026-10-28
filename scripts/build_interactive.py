"""Build an offline, self-contained interactive presentation from archived evidence."""
import base64,csv, json, pathlib,re,runpy
R=pathlib.Path(__file__).resolve().parents[1]
slides=runpy.run_path(str(R/'scripts/build_presentation.py'))['S']
narrative=json.loads((R/'scripts/cinematic_narrative.json').read_text())
assert len(narrative)==18 and sum(x['seconds'] for x in narrative)==900
slides=[{'title':x['title'],'kicker':x['kicker'],'bullets':[x['lead'],re.sub('<[^>]+>','',x['fact'])],'notes':x['notes'],'seconds':x['seconds'],'source':x['source']} for x in narrative]+slides[14:]
slides.append({'title':'EK H · Konum görselleri ve coğrafi kesinlik','kicker':'GÖRSEL KÜNYESİ / BAĞLAM KATMANI','bullets':['Berlin: Potsdamer Platz; Londra: Adams Place Bridge; Venedik: Venice Sunset. HDRI Haven / Poly Haven panoramaları; pmndrs/drei-assets kopyaları.','Paris: Eiffel Kulesi, Wildo Coda galeri küçük resmi (2018). Kaynak açık yeniden kullanım lisansı belirtmiyor; CC0 değildir.','Koordinatlar yer işareti/kent referansıdır. Kamera GPS konumu doğrulanmadı. Ülke etiketli veriden şehirde operasyon gerçekleştiği çıkarılamaz.','Görseller operasyon anını, hedef kişileri veya doğrulanmış olay yerini göstermez. Animasyonlar anlatım vurgusudur.'],'notes':'Fotoğrafların kaynağını ve bağlam rolünü açıklayın. Kaynak URL’leri, işleme bilgisi, SHA-256 ve koordinat temeli assets/locations/locations.json içinde korunur.','seconds':0,'source':'assets/locations/locations.json; gerçek coğrafi bağlam, operasyon kanıtı değil.'})
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
payload={'records':data,'features':features,'slides':slides,'narrative':narrative,'locations':locations,
 'source':'https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv',
 'hash':json.loads((R/'output/veri_manifest.json').read_text())['files'][str(raw.relative_to(R))]['sha256']}
template=(R/'scripts/interactive.html').read_text()
result=template.replace('__PAYLOAD__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
result=result.replace('</head>','<style>'+(R/'scripts/editorial.css').read_text()+'</style></head>')
result=result.replace('</body>','<script>'+(R/'scripts/editorial.js').read_text()+'</script></body>')
result=result.replace('</body>','<script>'+(R/'scripts/editorial_story.js').read_text()+'</script></body>')
result=result.replace('</head>','<style>'+(R/'scripts/cinematic.css').read_text()+'</style></head>')
result=result.replace('</body>','<script>'+(R/'scripts/cinematic.js').read_text()+'</script></body>')
(R/'output/CANLI_HARITA.html').write_text(result,encoding='utf8')
(R/'output/GORUNMEZ_CEPHE_ATLAS.html').write_text(result,encoding='utf8')
(R/'output/SINEMATIK_SUNUM.html').write_text(result,encoding='utf8')
notes=['# Görünmez Cephe — sinematik sunum konuşma metni','', '18 ana sahne · 15 dakika · 8 soru-cevap eki. Konum görselleri yalnızca bağlamdır; GDELT canlı sonuçları henüz elde edilmedi.',''];elapsed=0
for i,s in enumerate(slides):
 end=elapsed+s['seconds'];slot=f'{elapsed//60:02}:{elapsed%60:02}–{end//60:02}:{end%60:02}' if i<len(narrative) else 'Soru-cevap eki'
 notes.extend([f"## {i+1}. {s['title']} · {slot}",'',s['notes'],'',f"Kaynak: {s['source']}",'']);elapsed=end
(R/'output/KONUSMACI_NOTLARI.md').write_text('\n'.join(notes),encoding='utf8')
print('Offline cinematic atlas:',len(data),'unique indicators;',len(narrative),'timed scenes;',len(slides),'slides; 4 real context images.')
