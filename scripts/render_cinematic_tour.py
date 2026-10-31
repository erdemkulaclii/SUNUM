"""Render a real-country camera tour of the auxiliary atlas, without photos.

Camera movement highlights source target-country labels. It does not represent
operation movement, activity dates, routing or live traffic.
"""
from pathlib import Path
import io,json,subprocess
from PIL import Image
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'output';T=Path('/tmp/sunum-concise-tour');T.mkdir(exist_ok=True)
frames=[];index=0;requests=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=next(x for x in ['/usr/bin/chromium','/opt/pw-browsers/chromium'] if __import__('os').path.exists(x)),headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
 page.on('request',lambda req:requests.append(req.url))
 page.set_content((O/'AKADEMIK_ODAKLI_SUNUM.html').read_text());page.evaluate('openAtlas()')
 page.add_style_tag(content='.modal-backdrop{padding:0;background:#fff}.modal{max-width:none;max-height:none;height:100vh;border:0;padding:20px 35px;box-shadow:none}.modal-head{padding-bottom:9px;margin-bottom:12px}.modal-head h2{font-size:22px}.modal-head button{display:none}.atlas-wrap{height:430px}.atlas-note{font-size:11px!important;line-height:1.5!important}.atlas-controls{margin-bottom:8px}.atlas-focus{margin-bottom:10px!important}')
 page.evaluate('map.invalidateSize(false);focusAtlas("Europe",false)');page.wait_for_timeout(300)
 for key in ['Europe','Germany','UK','France','Italy','Europe']:
  page.evaluate('(key)=>focusAtlas(key)',key)
  for j in range(22):
   page.wait_for_timeout(100);raw=page.screenshot();(T/f'{index:04}.png').write_bytes(raw)
   if index%2==0:frames.append(Image.open(io.BytesIO(raw)).convert('RGB').resize((960,540)).quantize(colors=96))
   index+=1
 b.close()
assert not requests,requests
frames[0].save(O/'HAREKETLI_HARITA.gif',save_all=True,append_images=frames[1:],duration=250,loop=0,disposal=2)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(T/'%04d.png'),'-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'HARITA_TURU.mp4')],check=True)
(O/'ANIMASYON_KUNYESI.json').write_text(json.dumps({'frames':index,'video_fps':8,'video_seconds':index/8,'gif_seconds':len(frames)*.25,'map_engine':'Leaflet1.9.4','basemap':'Embedded Natural Earth boundaries','source':'Meta2022CIB indicator CSV; source target-country labels','camera_targets':['Europe','Germany','UK','France','Italy','Europe'],'photos_used':False,'external_requests':requests,'interpretation':'Country camera tour only. No historical activity timeline, operation routes, live traffic or precise operational locations.'},ensure_ascii=False,indent=2))
print('Recorded',index,'frames;',index/8,'second real-country camera tour;zero external requests.')
