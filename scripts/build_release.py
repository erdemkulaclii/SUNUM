"""Package only the current evidence-led presentation and its reproducible inputs."""
from pathlib import Path
import hashlib,json,runpy,shutil,zipfile
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parents[1];O=R/'output'
for name in ['build_concise_presentation.py','export_editorial.py','export_academic_documents.py']:
    runpy.run_path(str(R/'scripts'/name),run_name='__main__')

with sync_playwright() as p:
    exe=next((x for x in ['/usr/bin/chromium','/opt/pw-browsers/chromium'] if Path(x).exists()),None)
    browser=p.chromium.launch(**({'executable_path':exe,'args':['--no-sandbox']} if exe else {}),headless=True)
    page=browser.new_context(viewport={'width':1600,'height':900},device_scale_factor=1,offline=True).new_page()
    requests=[];errors=[]
    page.on('request',lambda req:requests.append(req.url))
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.set_content((O/'AKADEMIK_ODAKLI_SUNUM.html').read_text())
    for i,name in [(0,'PROFESYONEL_KAPAK'),(8,'ULKE_DAGILIMI'),(9,'DNS_ETIKETLERI'),(10,'ILK_ETIKET_TEKRARI'),(5,'ALAN_ADI_ANATOMISI'),(11,'GDELT_DALGA_ONIZLEME'),(12,'GDELT_HARITA_ONIZLEME'),(15,'SONUC_ONIZLEME'),(16,'KAYNAKCA_ONIZLEME')]:
        page.evaluate('(i)=>go(i)',i);page.wait_for_timeout(600 if i in (11,12) else 0);page.screenshot(path=str(O/f'{name}.png'))
    page.evaluate('openAtlas()');page.wait_for_timeout(250);page.screenshot(path=str(O/'ATLAS_ONIZLEME.png'))
    page.evaluate('closeModal();go(8)');page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(O/'MOBIL_ONIZLEME.png'),full_page=True)
    assert not requests and not errors,(requests,errors)
    browser.close()
for src,dests in {
    'PROFESYONEL_KAPAK.png':['SINEMATIK_KAPAK.png','ETKILESIMLI_ONIZLEME.png'],
    'ULKE_DAGILIMI.png':['PROFESYONEL_BERLIN.png','SINEMATIK_BERLIN.png','alan_adi_dagilimi.png'],
    'MOBIL_ONIZLEME.png':['SINEMATIK_MOBIL.png'],
    'ATLAS_ONIZLEME.png':['hedef_haritasi.png'],
}.items():
    for dest in dests:shutil.copyfile(O/src,O/dest)

# Validate the exact rebuilt files before archiving their reports and hashes.
for name in ['verify_concise.py','verify_basemap.py']:
    runpy.run_path(str(R/'scripts'/name),run_name='__main__')

output_names=[
 'BURADAN_BASLA.txt','AKADEMIK_ODAKLI_SUNUM.html','AKADEMIK_ODAKLI_SUNUM.pptx','AKADEMIK_ODAKLI_SUNUM.pdf',
 'PROFESYONEL_SUNUM.html','PROFESYONEL_SUNUM.pptx','PROFESYONEL_SUNUM.pdf',
 'SINEMATIK_SUNUM.html','SINEMATIK_SUNUM.pptx','SINEMATIK_SUNUM.pdf',
 'SUNUCU_KARTLARI.pdf','SUNUCU_KARTLARI.docx','KONUSMA_METNI_15_DK.pdf','KONUSMA_METNI_15_DK.docx',
 'KONUSMACI_NOTLARI.md','APA7_KAYNAKCA.pdf','APA7_KAYNAKCA.md','AKADEMIK_ARASTIRMA_DOSYASI.pdf',
 'IOC_YAPISAL_ANALIZ.json','IOC_YAPISAL_KANIT.csv','IOC_SON_ETIKET_DAGILIMI.csv','IOC_HEDEF_SON_ETIKET.csv','IOC_GOVDE_AILELERI.csv',
 'PROFESYONEL_KAPAK.png','ULKE_DAGILIMI.png','DNS_ETIKETLERI.png','ILK_ETIKET_TEKRARI.png','ALAN_ADI_ANATOMISI.png','SONUC_ONIZLEME.png','KAYNAKCA_ONIZLEME.png','GDELT_HARITA_ONIZLEME.png','GDELT_DALGA_ONIZLEME.png','GDELT_HARITA.png','ATLAS_ONIZLEME.png','MOBIL_ONIZLEME.png',
 'HARITA_TURU.mp4','HAREKETLI_HARITA.gif','ANIMASYON_KUNYESI.json',
 'ODAKLI_SUNUM_DOGRULAMA.json','ODAKLI_WEB_DOGRULAMA.json','ODAKLI_BELGE_DOGRULAMA.json','BASEMAP_DOGRULAMA.json',
]
script_names=[
 'build_release.py','analyze_ioc_structure.py','build_concise_presentation.py','export_concise_deck.py','export_concise_documents.py',
 'build_interactive.py','build_presentation.py','export_editorial.py','export_academic_documents.py','export_editable_presentation.py',
 'concise.html','concise.css','concise.js','concise_narrative.json','concise_appendices.json','concise_references.json','basemap.js','presentation_meta.json',
 'gdelt_map.js','gdelt_common.py','gdelt_map_png.py','gdelt_gkg_locations.sql','fetch_gdelt_map.py','test_gdelt_map.py','gdelt_gkg_archive.py','gdelt_validation.py','test_gdelt_archive.py','test_gdelt_snapshot.py',
 'render_cinematic_tour.py','verify_concise.py','verify_leaflet.py','verify_slide_readability.py','verify_basemap.py',
 'serve_presentation.py','fetch_gdelt.py','fetch_gdelt_cloud.py','test_gdelt_cloud.py','test_presentation_server.py',
]
files=[R/name for name in ['README.md','KAYNAKLAR.md','REVIZYON_KARARLARI.md','AKADEMIK_KAYNAK_DENETIMI.md','requirements.txt','BASLAT.sh','.env.example']]
files += [O/name for name in output_names]+[R/'scripts'/name for name in script_names]
files += list((R/'assets/vendor').glob('*'))
files += [R/'research/countries.geojson',R/'research/meta/README.md',R/'research/meta/index.json',R/'research/meta/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv']
assert all(path.is_file() for path in files),[str(p) for p in files if not p.is_file()]
assert all(p.name!='.env' and 'locations' not in p.parts for p in files)
snap=R/'research/gdelt/GDELT_HARITA_VERISI.json'
if snap.is_file():files.append(snap)
files += [p for p in [R/'research/gdelt/validation_sample.csv',R/'research/gdelt/gkg_archive/manifest.json',R/'research/gdelt/gkg_archive/matches.jsonl',R/'research/gdelt/gkg_archive/totals.json'] if p.is_file()]
manifest={'main_slides':len(json.loads((R/'scripts/concise_narrative.json').read_text())),'appendix_slides':len(json.loads((R/'scripts/concise_appendices.json').read_text())),'planned_seconds':810,'buffer_seconds':90,'unique_source_domains':311,'photos_included':False,'gdelt_snapshot_included':snap.is_file(),'synthetic_GDELT_observations':False,'files':{str(path.relative_to(R)):{'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()} for path in sorted(files)}}
manifest_path=O/'TESLIM_MANIFEST.json';manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');files.append(manifest_path)
bundle=O/'PROFESYONEL_TAM_PAKET.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for path in sorted(files):z.write(path,str(path.relative_to(R)))
with zipfile.ZipFile(bundle) as z:
    assert z.testzip() is None
    assert not any('/locations/' in name or name.endswith('/.env') for name in z.namelist())
for name in ['AKADEMIK_TAM_PAKET.zip','SINEMATIK_TAM_PAKET.zip','ATLAS_TAM_PAKET.zip','HAREKETLI_SUNUM_PAKETI.zip','SUNUM_TUM_DOSYALAR.zip']:shutil.copyfile(bundle,O/name)
print(f'Packaged {len(files)} files, {bundle.stat().st_size} bytes; no photos or private configuration.')
