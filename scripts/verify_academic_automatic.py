"""Behavioral contracts. API fixtures are SYNTHETIC TEST ONLY, never research data."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'output';HTML=(O/'SINEMATIK_SUNUM.html').read_text()
fixture={'articles':[{'url':'https://example.invalid/a?utm_source=TEST_ONLY','title':'SYNTHETIC TEST ONLY A','sourcecountry':'Germany','seendate':'20261001T120000Z'},{'url':'https://example.invalid/a','title':'DUPLICATE TEST','sourcecountry':'Germany'},{'url':'https://example.invalid/b','title':'SYNTHETIC TEST ONLY B','sourcecountry':'France'},{'url':'javascript:alert(1)','title':'INVALID TEST','sourcecountry':'Germany'}]}
timeline={'timeline':[{'series':'Article Count','data':[{'date':'20261001T000000Z','value':1,'norm':100},{'date':'20261002T000000Z','value':2,'norm':100}]}]}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);c=b.new_context(viewport={'width':1600,'height':1000},accept_downloads=True);calls=[];errors=[]
 c.route('https://sunum.test/**',lambda r:r.fulfill(content_type='text/html',body=HTML))
 def api(r):
  calls.append(r.request.url);r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body=json.dumps(timeline if 'mode=timelinevolraw' in r.request.url else fixture))
 c.route('https://api.gdeltproject.org/**',api)
 c.add_init_script('const originalSetTimeout=window.setTimeout;window.setTimeout=(fn,ms,...args)=>originalSetTimeout(fn,ms===6500?60:ms,...args);')
 page=c.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto('https://sunum.test/index.html');page.wait_for_function("newsState?.articles.length===2");page.wait_for_function("newsState?.timeline!==null")
 assert len(calls)==2,calls
 assert 'startdatetime=' in calls[0] and 'enddatetime=' in calls[0] and 'timespan=' not in calls[0]
 assert 'startdatetime=' in calls[1] and 'mode=timelinevolraw' in calls[1]
 assert page.evaluate('newsState.duplicates')==1 and page.evaluate('newsState.rejected')==1
 assert page.locator('#auto-gdelt-state').inner_text()=='GDELT · 2 haber'
 page.evaluate('go(11)');assert page.locator('#scene-gdelt-count').inner_text()=='2 benzersiz haber URL’si';assert page.locator('#scene-gdelt-headlines li').count()==2
 page.locator('#gdelt-layer').click();assert page.locator('.article-marker').count()==2;assert 'hedef ülke değildir' in page.locator('.map-disclaimer').inner_text()
 page.locator('#ioc-layer').click();assert page.locator('.country.target').count()==4
 receipt=page.evaluate('newsState.loadedAt');cached=c.new_page();cached.goto('https://sunum.test/cached.html');cached.wait_for_timeout(1100)
 assert len(calls)==2,'Fresh cache must not cause another request'
 assert cached.evaluate('newsState.origin')=='cached_api_response';assert cached.evaluate('newsState.loadedAt')==receipt
 assert 'ÖNBELLEK' in cached.locator('#news-provenance').inner_text()
 cached.locator('#open-api').click()
 with cached.expect_download() as dl:cached.locator('#export-gdelt').click()
 path=dl.value.path();export=json.loads(Path(path).read_text());assert export['origin']=='cached_api_response' and export['loadedAt']==receipt and export['window']['startUTC']
 cached.keyboard.press('Escape');cached.locator('#academic-open').click();assert cached.locator('#academic-body .apa-entry').count()==12
 assert cached.locator('#academic-body i').count()>=12
 cached.locator('[data-academic-tab="method"]').click();assert cached.locator('#academic-body .method-entry').count()==10
 cached.locator('[data-academic-tab="speech"]').click();assert cached.locator('#academic-body .speech-entry').count()==18
 with cached.expect_download() as dl:cached.locator('#academic-body>button').click()
 speech=Path(dl.value.path()).read_text();assert 'Araştırma sorusu' in speech and 'APA 7 KAYNAKÇA' in speech
 cached.keyboard.press('Escape');cached.evaluate('go(1)');assert 'Meta, 2022' in cached.locator('#slide-citation').inner_text()
 cached.set_viewport_size({'width':390,'height':844});cached.wait_for_timeout(600);assert cached.evaluate('document.documentElement.scrollWidth<=innerWidth')
 cached.locator('#academic-open').click();assert cached.evaluate('document.documentElement.scrollWidth<=innerWidth')
 # Expired cache: preserve original receipt on network failure; automatic attempt is bounded.
 page.evaluate("()=>{const c=JSON.parse(localStorage.getItem(AUTO_CACHE_KEY));c.loadedAt=new Date(Date.now()-7*60*60*1000).toISOString();localStorage.setItem(AUTO_CACHE_KEY,JSON.stringify(c))}")
 c.unroute('https://api.gdeltproject.org/**');failed=[]
 def fail(r):failed.append(r.request.url);r.fulfill(status=503,headers={'Access-Control-Allow-Origin':'*'},body='unavailable')
 c.route('https://api.gdeltproject.org/**',fail)
 c.add_init_script('const nativeSetTimeout=window.setTimeout;window.setTimeout=(fn,ms,...args)=>nativeSetTimeout(fn,ms===30000?60:ms,...args);')
 old=c.new_page();old.goto('https://sunum.test/stale.html');old.wait_for_function('autoAttempts===2 && !newsBusy')
 assert len(failed)==2 and old.evaluate('newsState.origin')=='cached_api_response'
 assert old.locator('#news-output .news-row').count()==2
 # Empty valid response never becomes a claim of zero operations.
 emptyc=b.new_context();emptyc.route('https://sunum.test/**',lambda r:r.fulfill(content_type='text/html',body=HTML));emptycalls=[]
 def empty(r):emptycalls.append(r.request.url);r.fulfill(status=200,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'},body='{"articles":[]}')
 emptyc.route('https://api.gdeltproject.org/**',empty);ep=emptyc.new_page();ep.goto('https://sunum.test/empty.html');ep.wait_for_function('newsState!==null');assert ep.locator('#map-gdelt').is_disabled();assert 'operasyon olmadığı anlamına gelmez' in ep.locator('#api-status').inner_text();assert len(emptycalls)==1
 # Entirely offline boot retains embedded real IOC evidence and does not require a manual import.
 off=b.new_context(offline=True,viewport={'width':1600,'height':1000});op=off.new_page();op.set_content(HTML);op.wait_for_timeout(1100);assert op.locator('.cell').count()==311 and op.locator('#news-output .news-row').count()==0;assert 'Çevrimdışı' in op.locator('#auto-gdelt-state').inner_text()
 assert not errors,errors
 b.close()
(O/'AKADEMIK_OTOMATIK_TESTLER.json').write_text(json.dumps({'checks_passed':True,'test_data':'SYNTHETIC UI FIXTURES ONLY; not bundled as findings','live_GDELT_download_verified':False,'core_scenes':18,'appendices':16,'APA_references':12,'planned_seconds':900,'checks':['automatic startup without click','frozen UTC query window','automatic timeline uses same window','deduplication and unsafe URL rejection','live scene summary updates','fresh cache avoids repeat requests','cached origin and original receipt retained','export preserves date and origin','bounded retry and stale cache fallback','empty response is not zero operations','offline IOC atlas','APA/method/speech tabs and speech download','mobile no horizontal overflow'],'javascript_errors':errors},ensure_ascii=False,indent=2))
print('PASS: academic dossier + automatic GDELT success/cache/failure/offline contracts. Fixtures only.')
