"""UI integration tests use explicit synthetic responses; no research findings generated."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'output'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1600,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('https://api.gdeltproject.org/**',lambda r:r.fulfill(status=503,headers={'Access-Control-Allow-Origin':'*'},body='unavailable'))
 page.set_content((O/'CANLI_HARITA.html').read_text());page.wait_for_timeout(1200)
 assert page.locator('.cell').count()==311
 page.locator('#open-api').click()
 assert 'api.gdeltproject.org/api/v2/doc/doc?' in page.locator('#direct-api').get_attribute('href')
 # A failed network request must never be replaced by invented observations.
 page.route('https://api.gdeltproject.org/**',lambda route:route.fulfill(status=503,headers={'Access-Control-Allow-Origin':'*'},body='unavailable'))
 page.locator('#fetch-gdelt').click();page.wait_for_function("document.getElementById('api-status').textContent.includes('Veri alınamadı')")
 assert page.locator('#map-gdelt').is_disabled()
 assert page.locator('#news-output .news-row').count()==0
 page.unroute('https://api.gdeltproject.org/**')
 fixture={'articles':[
  {'url':'https://example.invalid/a?utm_source=test','title':'SYNTHETIC TEST ONLY A','sourcecountry':'Germany','seendate':'20261001T120000Z'},
  {'url':'https://example.invalid/a','title':'DUPLICATE TEST','sourcecountry':'Germany'},
  {'url':'https://example.invalid/b','title':'SYNTHETIC TEST ONLY B','sourcecountry':'France'},
  {'url':'javascript:alert(1)','title':'INVALID LINK','sourcecountry':'Germany'}]}
 page.route('https://api.gdeltproject.org/**',lambda route:route.fulfill(status=200,headers={'Access-Control-Allow-Origin':'*','Content-Type':'application/json'},body=json.dumps(fixture)))
 page.locator('#fetch-gdelt').click();page.wait_for_function("document.querySelectorAll('#news-output .news-row').length===2")
 assert '4 ham haber → 2 benzersiz URL' in page.locator('#api-status').inner_text()
 assert 'DOĞRUDAN GDELT API' in page.locator('#news-provenance').inner_text()
 page.locator('#map-gdelt').click()
 assert page.locator('.article-marker').count()==2
 assert 'kaynak ülkeleri' in page.locator('#map-heading').text_content()
 page.locator('#ioc-layer').click()
 assert page.locator('.country.target').count()==4
 assert page.locator('#gdelt-markers').is_hidden()
 page.locator('#country-chips button').filter(has_text='Almanya').click()
 assert page.locator('#country-card .count').inner_text()=='298'
 page.locator('#open-api').click()
 page.unroute('https://api.gdeltproject.org/**')
 timeline={'timeline':[{'series':'Article Count','data':[{'date':'20261001T000000Z','value':1,'norm':100},{'date':'20261002T000000Z','value':2,'norm':100}]}]}
 page.route('https://api.gdeltproject.org/**',lambda route:route.fulfill(status=200,headers={'Access-Control-Allow-Origin':'*','Content-Type':'application/json'},body=json.dumps(timeline if 'mode=timelinevolraw' in route.request.url else fixture)))
 page.locator('#fetch-timeline').click()
 page.wait_for_function("document.querySelectorAll('#timeline-output svg').length===1")
 imported={'articles':[{'url':'https://example.invalid/import','title':'LOCAL TEST ONLY','sourcecountry':'France'}]}
 page.locator('#json-file').set_input_files({'name':'synthetic-test-only.json','mimeType':'application/json','buffer':json.dumps(imported).encode()})
 page.wait_for_function("document.getElementById('news-provenance').textContent.includes('KAYNAK BAĞIMSIZ DOĞRULANMADI')")
 assert page.locator('#fetch-timeline').is_disabled()
 with page.expect_download() as dl:page.locator('#export-gdelt').click()
 dl.value.save_as('/tmp/gdelt-ui-test-export.json')
 exported=json.loads(Path('/tmp/gdelt-ui-test-export.json').read_text())
 assert exported['origin']=='local_import_unverified'
 page.locator('#json-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':b'{"timeline": []}'})
 page.wait_for_function("document.getElementById('api-status').textContent.includes('Dosya kabul edilmedi')")
 assert not errors,errors
 # Fresh page verifies that the final presentation ships without any test articles.
 fresh=b.new_page(viewport={'width':1600,'height':1000});fresh.route('https://api.gdeltproject.org/**',lambda r:r.abort());fresh.set_content((O/'CANLI_HARITA.html').read_text());fresh.wait_for_timeout(700)
 assert fresh.locator('#news-output .news-row').count()==0
 fresh.screenshot(path=str(O/'ATLAS_ONIZLEME.png'))
 fresh.set_viewport_size({'width':390,'height':844})
 assert fresh.evaluate('document.documentElement.scrollWidth<=innerWidth')
 fresh.locator('#open-api').click()
 assert fresh.locator('#api-modal').is_visible()
 assert fresh.evaluate('document.documentElement.scrollWidth<=innerWidth')
 b.close()
(O/'GDELT_BAGLANTI_TESTI.json').write_text(json.dumps({'checks_passed':True,'test_type':'synthetic UI responses, not scientific observations','live_GDELT_download_verified':False,'javascript_errors':errors,'checks':['network failure yields no observations','URL deduplication and invalid protocol rejection','source-country map separated from IOC targets','IOC layer restored after news map','imported provenance explicitly unverified','export preserves provenance','bad schema rejected','fresh startup has no sample articles','mobile API dialog does not overflow']},ensure_ascii=False,indent=2))
print('PASS: GDELT UI success/failure/import/export/source mapping. Synthetic fixtures only; live GDELT still unverified.')
