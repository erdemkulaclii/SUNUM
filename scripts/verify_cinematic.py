"""Real presentation behavior checks; no remote data or invented observations."""
from pathlib import Path
import json,math
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'output'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1600,'height':1000});errors=[];requests=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
 page.set_content((O/'SINEMATIK_SUNUM.html').read_text());page.wait_for_timeout(700)
 assert page.locator('#track button').count()==18 and page.evaluate('D.slides.length')==26
 assert page.evaluate('offsets.at(-1)')==900
 assert page.locator('.cell').count()==311
 assert page.locator('#location-context-pins .location-pin').count()==4
 for i,k,n in [(6,'Germany','298'),(7,'UK','4'),(8,'France','2'),(9,'Italy','2')]:
  page.evaluate('(i)=>go(i)',i);page.wait_for_timeout(1800)
  assert page.locator('#country-card .count').inner_text()==n
  assert page.locator('.geo-photo img').evaluate('(e)=>e.complete&&e.naturalWidth>0')
  assert 'kamera GPS' in page.locator('.precision').inner_text()
  d=page.evaluate('''(k)=>{const pin=document.getElementById('geo-pin-'+k),pt=new DOMPoint(0,0).matrixTransform(pin.getScreenCTM()),r=document.querySelector('.map-zone').getBoundingClientRect(),c=document.getElementById('country-card');return{x:pt.x-r.left,y:pt.y-r.top,cardX:+c.dataset.anchorX,cardY:+c.dataset.anchorY}}''',k)
  assert math.hypot(d['x']-d['cardX'],d['y']-d['cardY'])<2,d
  page.locator('#country-evidence').click();assert page.locator('#evidence-rows tr').count()==int(n);page.keyboard.press('Escape')
  page.evaluate('(i)=>go(i)',i)
 page.evaluate('go(6)');page.wait_for_timeout(1800);page.locator('#zoom-in').click();page.wait_for_timeout(1800)
 assert page.locator('#photo-leader').is_visible()
 rect=page.locator('#map').bounding_box();page.mouse.move(rect['x']+60,rect['y']+260);page.mouse.down();page.mouse.move(rect['x']+100,rect['y']+295,steps=6);page.mouse.up();page.wait_for_timeout(200)
 d=page.evaluate("()=>{const p=new DOMPoint(0,0).matrixTransform(document.getElementById('geo-pin-Germany').getScreenCTM()),r=document.querySelector('.map-zone').getBoundingClientRect(),c=document.getElementById('country-card');return [p.x-r.left,p.y-r.top,+c.dataset.anchorX,+c.dataset.anchorY]}")
 assert math.hypot(d[0]-d[2],d[1]-d[3])<2
 page.locator('.geo-card .close').click();assert page.locator('#photo-leader').is_hidden()
 page.evaluate('go(1)');assert page.locator('#editorial-panel').is_visible()
 page.keyboard.press('ArrowRight');assert page.locator('#page').inner_text()=='03 / 18'
 page.evaluate('go(0)');page.locator('#play').click();page.wait_for_timeout(2100);assert page.locator('#clock').inner_text()=='00:02 / 15:00';page.locator('#play').click()
 page.locator('#country-tour').click();assert page.locator('#page').inner_text()=='07 / 18';page.locator('#country-tour').click()
 page.locator('#motion').click();assert 'reduced' in page.locator('body').get_attribute('class')
 page.locator('#cinema-style').click();assert 'atlas-mode' in page.locator('body').get_attribute('class');page.locator('#cinema-style').click()
 page.evaluate('go(0)');page.wait_for_timeout(700);page.screenshot(path=str(O/'SINEMATIK_KAPAK.png'))
 page.evaluate('go(6)');page.wait_for_timeout(1800);page.screenshot(path=str(O/'SINEMATIK_BERLIN.png'))
 page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(1800)
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 zone=page.locator('.map-zone').bounding_box();card=page.locator('#country-card').bounding_box()
 assert card['x']>=0 and card['x']+card['width']<=390
 assert card['y']>=zone['y']+100 and card['y']+card['height']<=zone['y']+zone['height']-45,(card,zone)
 page.screenshot(path=str(O/'SINEMATIK_MOBIL.png'),full_page=True)
 assert not errors,errors
 assert not requests,requests
 b.close()
(O/'SINEMATIK_TESTLER.json').write_text(json.dumps({'checks_passed':True,'main_scenes':18,'slides_with_appendices':26,'seconds':900,'unique_indicators':311,'real_context_images':4,'camera_GPS_verified':False,'context_is_operation_evidence':False,'javascript_errors':errors,'external_network_requests_on_startup':requests,'checks':['four images decoded offline','four evidence filters correct','photo anchors within 2 pixels of SVG geographic references','zoom/close/photo leader','keyboard and autoplay','country tour','reduced motion','light/dark mode','mobile no overflow; card stays in map']},ensure_ascii=False,indent=2))
print('PASS: 18 scenes / 900 seconds; geographic photo anchors, evidence, camera and responsive behavior.')
