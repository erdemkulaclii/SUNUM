from pathlib import Path
import io,json
from PIL import Image
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches

R=Path(__file__).resolve().parents[1];O=R/'output'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
    errors=[];requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('request',lambda r:requests.append(r.url))
    page.set_content((O/'CANLI_HARITA.html').read_text(),wait_until='load')
    assert page.locator('.cell').count()==311
    assert page.locator('.country.target').count()==4
    page.locator('#country-chips button').filter(has_text='Almanya').click()
    assert page.locator('#country-card .count').inner_text()=='298'
    page.locator('#country-evidence').click()
    assert page.locator('#evidence-rows tr').count()==298
    page.locator('#search').fill('spiegel')
    assert 0<page.locator('#evidence-rows tr').count()<298
    page.keyboard.press('Escape')
    assert page.locator('#evidence-modal').is_hidden()
    page.locator('#open-evidence').click()
    page.locator('#country-filter').select_option('UK')
    assert page.locator('#evidence-rows tr').count()==4
    with page.expect_download() as download:
        page.locator('#download-csv').click()
    download.value.save_as('/tmp/sunum-uk-evidence.csv')
    assert 'UK' in Path('/tmp/sunum-uk-evidence.csv').read_text(encoding='utf-8-sig')
    page.keyboard.press('Escape')
    page.locator('#gdelt-layer').click()
    assert page.locator('#layer-alert').is_visible()
    assert 'HTTP 403' in page.locator('#layer-alert').inner_text()
    page.locator('#back-ioc').click()
    page.locator('#scope').click()
    assert page.locator('.country.target').count()==6
    page.locator('#scope').click()
    page.locator('#zoom-in').click()
    assert '1.25' in page.locator('#viewport').get_attribute('style')
    page.locator('#zoom-reset').click()
    page.evaluate('go(6)')
    assert page.locator('#country-card .count').inner_text()=='298'
    page.locator('#notes').click()
    assert len(page.locator('#notes-body').inner_text())>300
    page.keyboard.press('Escape')
    page.evaluate('go(0)')
    page.keyboard.press('ArrowRight')
    assert page.locator('#page').inner_text()=='02 / 14'
    page.locator('#play').click()
    page.wait_for_timeout(2100)
    assert page.locator('#clock').inner_text()=='00:42 / 15:00'
    page.locator('#play').click()
    page.evaluate('go(0)')
    page.evaluate("document.getElementById('toast').hidden=true")
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(650)
    page.screenshot(path=str(O/'ETKILESIMLI_ONIZLEME.png'),full_page=False)
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    page.locator('#country-chips button').filter(has_text='Fransa').click()
    assert page.locator('#country-card .count').inner_text()=='2'
    page.screenshot(path=str(O/'MOBIL_ONIZLEME.png'),full_page=True)
    page.set_viewport_size({'width':1600,'height':900})
    page.evaluate('go(5)')
    page.evaluate('window.scrollTo(0,0)')
    page.wait_for_timeout(900)
    frames=[]
    for target in [None,'Germany','UK','France','Italy',None]:
        page.evaluate('(k)=>k?selectCountry(k):clearCountry()',target)
        for step in range(7):
            page.wait_for_timeout(100)
            img=Image.open(io.BytesIO(page.screenshot())).convert('RGB').resize((1280,720))
            frames.append(img.quantize(colors=128))
    frames[0].save(O/'HAREKETLI_HARITA.gif',save_all=True,append_images=frames[1:],duration=160,loop=0,disposal=2)
    assert not errors,errors
    assert not requests,requests
    browser.close()
assert Image.open(O/'HAREKETLI_HARITA.gif').n_frames>1
prs=Presentation(O/'SUNUM_15dk.pptx')
slide=prs.slides[5]
for shape in list(slide.shapes):
    el=shape._element;el.getparent().remove(el)
slide.shapes.add_picture(str(O/'HAREKETLI_HARITA.gif'),0,0,width=prs.slide_width,height=prs.slide_height)
slide.notes_slide.notes_text_frame.text+='\n\nHareketli görsel: tek tarihli IOC verisinin vurgu animasyonudur; zaman serisi veya canlı trafik değildir. GIF oynatma, kullanılan PowerPoint sürümüne bağlıdır. Tam etkileşim için CANLI_HARITA.html dosyasını tarayıcıda açın.'
prs.save(O/'SUNUM_HAREKETLI.pptx')
(O/'ETKILESIM_DOGRULAMA.json').write_text(json.dumps({'browser':'Chromium','javascript_errors':errors,'external_requests':requests,'unique_records':311,'checks':['country evidence 298','UK filter and CSV export 4','domain search','GDELT unavailable layer','six-country scope','zoom','keyboard navigation','speaker notes','timed playback','mobile without horizontal overflow','animated GIF and embedded PPTX']},ensure_ascii=False,indent=2))
print('PASS: interactive controls, filtered evidence, download, animation, mobile layout; zero external requests / JS errors.')
