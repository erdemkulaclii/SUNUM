"""Measure actual slide text visibility; no network data or synthetic observations.

Default: verify all 18 narrative scenes in two presentation-sized viewports.
Optional --check-pptx also verifies editable native heading/point/takeaway text
in the newly exported PowerPoint. It is not inferred from screenshot pixels.
"""
from pathlib import Path
import argparse,datetime as dt,json,re
from playwright.sync_api import sync_playwright

R=Path(__file__).resolve().parents[1]
O=R/'output'


def normalize(text):
    return re.sub(r'\s+', ' ', str(text)).strip()


def check_editable_pptx(path,narrative):
    from pptx import Presentation
    prs=Presentation(path)
    assert len(prs.slides)>=len(narrative), 'PowerPoint is missing narrative slides'
    rows=[]
    for i,s in enumerate(narrative):
        slide=prs.slides[i]
        shapes=[shape for shape in slide.shapes if shape.has_text_frame and shape.text.strip()]
        text=normalize(' '.join(shape.text for shape in shapes))
        required=[s['title'],*s['points']]
        if i!=0:required.append(s['takeaway'])
        missing=[t for t in required if normalize(t) not in text]
        assert not missing, f'PowerPoint scene {i+1} lacks editable text: {missing}'
        assert shapes, f'PowerPoint scene {i+1} contains no native text'
        for shape in shapes:
            assert shape.left>=0 and shape.top>=0, f'Native text outside slide: {i+1}'
            assert shape.left+shape.width<=prs.slide_width+10000, f'Native text exceeds slide width: {i+1}'
            assert shape.top+shape.height<=prs.slide_height+10000, f'Native text exceeds slide height: {i+1}'
        rows.append({'scene':i+1,'native_text_shapes':len(shapes),'heading_points_takeaway_editable':True})
    return {'verified':True,'path':str(path.resolve().relative_to(R)),'total_slides':len(prs.slides),'main_slides':rows}


MEASURE="""() => {
  const aside=document.querySelector('.narrative'),ar=aside.getBoundingClientRect();
  const textNodes=[...aside.querySelectorAll('h1,.lead,.cover-topic,.cover-agenda li,.slide-points li,.slide-takeaway p,.deck-meta')];
  return {
    scene:scene+1,title:CIN[scene].title,
    viewport:{width:innerWidth,height:innerHeight},
    aside:{x:ar.x,y:ar.y,width:ar.width,height:ar.height,top:ar.top,bottom:ar.bottom,left:ar.left,right:ar.right,scroll:aside.scrollHeight,visible:aside.clientHeight,scrollTop:aside.scrollTop},
    pointCount:aside.querySelectorAll('.slide-points li').length,
    agendaCount:aside.querySelectorAll('.cover-agenda li').length,
    coverLabel:document.getElementById('eyebrow').textContent,
    text:textNodes.map(e=>{
      const r=e.getBoundingClientRect(),cs=getComputedStyle(e),range=document.createRange();range.selectNodeContents(e);const tr=range.getBoundingClientRect();
      return {selector:e.tagName.toLowerCase()+'.'+e.className,text:e.textContent.trim(),fontSize:parseFloat(cs.fontSize),display:cs.display,visibility:cs.visibility,opacity:+cs.opacity,
              rect:{top:r.top,bottom:r.bottom,left:r.left,right:r.right,width:r.width,height:r.height},
              textRect:{top:tr.top,bottom:tr.bottom,left:tr.left,right:tr.right,width:tr.width,height:tr.height},
              mainProse:e.matches('.lead,.cover-topic,.cover-agenda li,.slide-points li,.slide-takeaway p')};
    })
  };
}"""


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-pptx',action='store_true')
    parser.add_argument('--html',type=Path,default=O/'PROFESYONEL_SUNUM.html')
    parser.add_argument('--pptx',type=Path,default=O/'PROFESYONEL_SUNUM.pptx')
    args=parser.parse_args()
    html=args.html.read_text()
    narrative=json.loads((R/'scripts/cinematic_narrative.json').read_text())
    assert len(narrative)==18 and sum(s['seconds'] for s in narrative)==900
    assert all(len(s.get('points',[]))==3 and s.get('takeaway') for s in narrative), 'Authored slide writing is incomplete'
    report={'checks_passed':False,'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
            'test_kind':'Actual DOM text measurements; no API data or synthetic observations',
            'viewports':[],'native_powerpoint':{'verified':False,'reason':'Not requested; use --check-pptx after export'},
            'violations':[],'javascript_errors':[],'external_requests':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        try:
            for width,height in [(1600,900),(1280,720)]:
                context=browser.new_context(viewport={'width':width,'height':height},offline=True)
                page=context.new_page()
                page.on('pageerror',lambda e:report['javascript_errors'].append(str(e)))
                page.on('request',lambda r:report['external_requests'].append(r.url) if r.url.startswith(('http:','https:')) else None)
                page.set_content(html)
                page.evaluate("document.body.classList.add('reading','export-mode');map.invalidateSize(false)")
                page.wait_for_timeout(350)
                viewport_report={'width':width,'height':height,'minimum_prose_font_px':16 if width==1600 else 15,'scenes':[]}
                for i in range(18):
                    page.evaluate('(i)=>go(i)',i)
                    page.wait_for_timeout(100)
                    m=page.evaluate(MEASURE)
                    errors=[];ar=m['aside'];minimum=viewport_report['minimum_prose_font_px']
                    if ar['scroll']>ar['visible']+2:errors.append(f"narrative requires scrolling: {ar['scroll']}px > {ar['visible']}px")
                    if ar['scrollTop']>1:errors.append('narrative is already scrolled')
                    if ar['top']<-2 or ar['bottom']>height+2:errors.append('narrative itself extends outside viewport')
                    if ar['left']<-2 or ar['right']>width+2:errors.append('narrative extends horizontally outside viewport')
                    if i==0:
                        if 'AKADEMİK ARAŞTIRMA SUNUMU' not in m['coverLabel']:errors.append('cover lacks explicit presentation label')
                        if m['agendaCount']!=3:errors.append('cover lacks its three-part agenda')
                        if not any('cover-topic' in t['selector'] and len(t['text'])>60 for t in m['text']):errors.append('cover lacks a complete research topic')
                        if not any('deck-meta' in t['selector'] and '15 dakika' in t['text'] for t in m['text']):errors.append('cover lacks presentation metadata')
                    elif m['pointCount']!=3:errors.append(f"expected 3 substantive points, found {m['pointCount']}")
                    for t in m['text']:
                        if not t['text']:errors.append('empty presentation text node: '+t['selector']);continue
                        r=t['rect'];tr=t['textRect']
                        if t['display']=='none' or t['visibility']=='hidden' or t['opacity']<.9:errors.append('authored text is hidden: '+t['selector'])
                        if r['width']<=0 or r['height']<=0:errors.append('authored text has no visible area: '+t['selector'])
                        if min(r['top'],tr['top'])<ar['top']-2 or max(r['bottom'],tr['bottom'])>ar['bottom']+2:errors.append('text crosses visible vertical boundary: '+t['text'][:85])
                        if min(r['left'],tr['left'])<ar['left']-2 or max(r['right'],tr['right'])>ar['right']+2:errors.append('text crosses visible horizontal boundary: '+t['text'][:85])
                        if tr['bottom']>r['bottom']+2 or tr['right']>r['right']+2:errors.append('text overflows its own box: '+t['text'][:85])
                        if t['mainProse'] and t['fontSize']<minimum-.1:errors.append(f"main prose font too small ({t['fontSize']}px < {minimum}px): "+t['text'][:85])
                    viewport_report['scenes'].append({'scene':i+1,'title':m['title'],'aside_visible_px':ar['visible'],'aside_content_px':ar['scroll'],'prose_fonts_px':sorted(set(t['fontSize'] for t in m['text'] if t['mainProse'])),'prose_nodes':len(m['text']),'violations':errors})
                    if errors:
                        screenshot=Path('/tmp')/f'sunum-readable-{width}x{height}-scene-{i+1:02}.png'
                        page.screenshot(path=str(screenshot))
                        report['violations'].append({'viewport':f'{width}x{height}','scene':i+1,'title':m['title'],'errors':errors,'failure_screenshot':str(screenshot)})
                report['viewports'].append(viewport_report)
                context.close()
        finally:browser.close()
    if args.check_pptx:
        try:report['native_powerpoint']=check_editable_pptx(args.pptx,narrative)
        except AssertionError as e:report['violations'].append({'powerpoint':str(e)})
    if report['javascript_errors']:report['violations'].append({'javascript_errors':report['javascript_errors']})
    if report['external_requests']:report['violations'].append({'unexpected_external_requests':report['external_requests']})
    report['checks_passed']=not report['violations']
    (O/'SUNUM_OKUNABILIRLIK.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    for failure in report['violations']:print(json.dumps(failure,ensure_ascii=False))
    assert report['checks_passed'], 'Slide prose is not fully readable; see output/SUNUM_OKUNABILIRLIK.json'
    print('PASS: all 18 slides readable without scrolling at 1600x900 and 1280x720; heading, agenda, points and takeaways measured.')
    print('Native editable PowerPoint:', 'VERIFIED' if report['native_powerpoint']['verified'] else 'NOT CHECKED')


if __name__=='__main__':main()
