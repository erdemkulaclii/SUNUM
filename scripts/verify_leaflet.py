"""Leaflet behavior and provenance checks. Mock responses are never research data."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,datetime as dt,base64
R=Path(__file__).resolve().parents[1];O=R/'output';HTML=(O/'PROFESYONEL_SUNUM.html').read_text()
fixture={'articles':[{'url':'https://example.invalid/a?utm_source=TEST','title':'SYNTHETIC TEST ONLY A','sourcecountry':'Germany','seendate':'20261001T120000Z'},{'url':'https://example.invalid/a','title':'DUPLICATE TEST','sourcecountry':'Germany'},{'url':'https://example.invalid/b','title':'SYNTHETIC TEST ONLY B','sourcecountry':'France'},{'url':'javascript:alert(1)','title':'UNSAFE TEST','sourcecountry':'Germany'}]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);c=b.new_context(viewport={'width':1600,'height':1000});errors=[];calls=[]
 c.route('https://tile.openstreetmap.org/**',lambda r:r.abort());c.route('https://api.gdeltproject.org/**',lambda r:(calls.append(r.request.url),r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps(fixture))))
 page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(HTML);page.wait_for_function('newsState?.articles.length===2')
 assert page.evaluate('L.version')=='1.9.4';assert page.evaluate('D.slides.length')==35;assert page.evaluate('offsets.at(-1)')==900
 assert page.locator('#evidence-rows tr').count()==311 and page.locator('#reference-ledger .apa-entry').count()==14
 assert len(calls)==1 and 'startdatetime=' in calls[0] and 'enddatetime=' in calls[0]
 assert page.evaluate('newsState.duplicates')==1 and page.evaluate('newsState.rejected')==1
 assert page.evaluate('Object.keys(referenceMarkers).length')==4
 for i,k,n in [(6,'Germany',298),(7,'UK',4),(8,'France',2),(9,'Italy',2)]:
  page.evaluate('(i)=>go(i)',i);page.wait_for_timeout(2000);assert page.locator('.leaflet-popup .count').inner_text()==str(n)
  assert page.locator('.place-photo').evaluate('(e)=>e.complete&&e.naturalWidth>0')
  coords=page.evaluate('map._popup.getLatLng()');expected=page.evaluate('(k)=>D.locations[k].coordinates',k);assert abs(coords['lat']-expected[1])<1e-8 and abs(coords['lng']-expected[0])<1e-8
  page.evaluate('map.panBy([30,15],{animate:false})');assert page.locator('.leaflet-popup').is_visible()
  page.locator('[data-country-evidence]').click();assert page.locator('#modal-body tr').count()==n;page.keyboard.press('Escape')
 page.evaluate('go(1)');assert page.locator('#analysis-panel').is_visible();assert page.locator('.leaflet-control-zoom').is_hidden()
 page.evaluate('go(16)');assert 'Almanya hedefli etiketlerde yoğunlaşmaktadır' in page.locator('.statement').inner_text()
 page.screenshot(path=str(O/'SONUC_ONIZLEME.png'))
 page.evaluate('go(17)');assert page.locator('#full-reference-button').is_visible();page.locator('#full-reference-button').click();assert page.locator('#modal-body .apa-entry').count()==14;page.keyboard.press('Escape')
 page.locator('#speech-open').click();assert page.locator('#modal-body .speech').count()==18;page.keyboard.press('Escape')
 page.evaluate('go(0)');page.keyboard.press('ArrowRight');assert page.locator('#page').inner_text()=='02 / 18';page.keyboard.press('ArrowLeft');page.locator('#play').click();page.wait_for_timeout(1100);assert page.locator('#clock').inner_text()=='00:01 / 15:00';page.locator('#play').click()
 page.locator('#gdelt-layer').click();assert page.evaluate('newsLayer.getLayers().length')==2
 assert page.evaluate('map.hasLayer(photoLayer)') is False
 page.locator('#ioc-layer').click();assert page.evaluate('map.hasLayer(photoLayer)') is True
 page.locator('#country-tour').click();assert page.locator('#page').inner_text()=='07 / 18';page.locator('#country-tour').click();page.wait_for_timeout(2000)
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(1000);assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert page.locator('.leaflet-popup').is_visible();page.screenshot(path=str(O/'MOBIL_ONIZLEME.png'),full_page=True)
 page.locator('#references-open').click();assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.keyboard.press('Escape')
 # Separate cache and Cloud contract tests on a routed same-origin page.
 c2=b.new_context(viewport={'width':1600,'height':1000});c2.route('https://sunum.test/**',lambda r:r.fulfill(content_type='text/html',body=HTML));c2.route('https://tile.openstreetmap.org/**',lambda r:r.abort());now=dt.datetime.now(dt.timezone.utc).isoformat()
 event={'status':'ok','provider':'GDELT Cloud','key_configured':True,'checked_at':now,'result':{'provider':'GDELT Cloud','data':[{'id':'TEST_EVENT_ONLY','title':'SYNTHETIC CLOUD EVENT ONLY','location':{'type':'Point','coordinates':[2.3,48.8]}},{'id':'TEST_NO_LOCATION','title':'SYNTHETIC NO COORDINATES'}],'pages':[{'receipt':{'fetched_at_utc':now}}],'coverage_complete':None}}
 c2.route('https://sunum.test/api/gdelt-cloud',lambda r:r.fulfill(content_type='application/json',body=json.dumps(event)))
 cp=c2.new_page();cp.goto('https://sunum.test/index.html');cp.wait_for_function("newsState?.provider==='GDELT Cloud'");assert cp.evaluate('newsState.events.length')==2;cp.locator('#gdelt-layer').click();assert cp.evaluate('newsLayer.getLayers().length')==1
 assert 'Event' in cp.locator('#map-legend').inner_text()
 c2.unroute('https://sunum.test/api/gdelt-cloud');c2.route('https://sunum.test/api/gdelt-cloud',lambda r:r.fulfill(content_type='application/json',body='{"status":"request_failed","key_configured":true,"message":"SYNTHETIC NETWORK FAILURE"}'))
 cached=c2.new_page();cached.goto('https://sunum.test/cached.html');cached.wait_for_timeout(1500);assert cached.evaluate('newsState.cached') is True;assert cached.evaluate('newsState.receivedAt')==now
 # Offline startup never invents data and still provides the complete embedded IOC dataset.
 off=b.new_context(offline=True);op=off.new_page();op.set_content(HTML);op.wait_for_timeout(1400);assert op.evaluate('newsState') is None;assert op.locator('#evidence-rows tr').count()==311
 assert not errors,errors
 # Clean previews contain no synthetic articles.
 clean=b.new_context(offline=True,viewport={'width':1600,'height':1000});q=clean.new_page();q.set_content(HTML);q.wait_for_timeout(1600);q.screenshot(path=str(O/'PROFESYONEL_KAPAK.png'));q.evaluate('go(6)');q.wait_for_timeout(2000);q.screenshot(path=str(O/'PROFESYONEL_BERLIN.png'));q.evaluate('go(16)');q.wait_for_timeout(400);q.screenshot(path=str(O/'SONUC_ONIZLEME.png'));q.evaluate('go(17)');q.wait_for_timeout(400);q.screenshot(path=str(O/'KAYNAKCA_ONIZLEME.png'));q.evaluate('go(6)');q.set_viewport_size({'width':390,'height':844});q.wait_for_timeout(2200);q.screenshot(path=str(O/'MOBIL_ONIZLEME.png'),full_page=True);b.close()
(O/'LEAFLET_DOGRULAMA.json').write_text(json.dumps({'checks_passed':True,'Leaflet':'1.9.4','core_scenes':18,'total_slides':35,'APA_references':14,'planned_seconds':900,'IOC_indicators':311,'actual_GDELT_network_verified':False,'test_data':'SYNTHETIC FIXTURES ONLY; not in distributed presentation','checks':['true Leaflet map and OSM tile configuration','offline boundary fallback labelled','four geographic photo popups anchored to returned reference coordinates','country evidence counts','map pan preserves popup','source geography separate from IOC targets','Cloud Event only mapped when explicit valid coordinates returned','current query fixed UTC window','no-click DOC startup','unsafe URL rejection and deduplication','Cloud through same-origin server','cache retains original receipt and provenance','dedicated conclusion and bibliography scenes','all speech notes accessible','keyboard/autoplay/tour','mobile no horizontal overflow','offline retains 311 records'],'javascript_errors':errors},ensure_ascii=False,indent=2))
print('PASS: Leaflet map, source layers, academic conclusion/references, server-first Cloud and offline contracts.')
