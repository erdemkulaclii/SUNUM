"""Record a short real-data context-map tour; never a simulated operation timeline."""
from pathlib import Path
import io,json,subprocess
from PIL import Image
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'output';T=Path('/tmp/sunum-cinematic-tour');T.mkdir(exist_ok=True)
gif_frames=[];index=0
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
 page.route('https://api.gdeltproject.org/**',lambda route:route.abort())
 page.route('https://tile.openstreetmap.org/**',lambda route:route.abort())
 page.set_content((O/'SINEMATIK_SUNUM.html').read_text());page.add_style_tag(content='.map-actions,.transport,.map-tabs,.map-tools,.chips,.hint,#scope,#notes{display:none!important}.timeline{height:54px}.reading .stage{height:calc(100vh - 54px);min-height:0}.reading .narrative{padding:27px 26px}.reading .narrative h1{font-size:37px}.reading .hero-number{font-size:59px}.reading .narrative .lead{font-size:13px}.reading .fact{font-size:11px;margin-top:18px}.reading #country-card.geo-card{width:290px}.reading .geo-photo{height:125px}.reading .geo-body{padding:10px 13px}.reading .geo-body h2{font-size:22px}.reading .geo-body h2 .count{font-size:29px}.reading .geo-body p{font-size:9px}.reading .geo-body .precision{font-size:8px}.reading .geo-credit{font-size:7px}.reading .geo-body details{display:none}')
 page.evaluate("document.body.classList.add('reading','export-mode');map.invalidateSize(false)")
 for scene,frames in [(5,12),(6,28),(7,28),(8,28),(9,28),(5,12)]:
  page.evaluate('(i)=>go(i)',scene)
  for j in range(frames):
   page.wait_for_timeout(90)
   raw=page.screenshot();(T/f'{index:04}.png').write_bytes(raw)
   if index%2==0:gif_frames.append(Image.open(io.BytesIO(raw)).convert('RGB').resize((960,540)).quantize(colors=96))
   index+=1
 b.close()
gif_frames[0].save(O/'HAREKETLI_HARITA.gif',save_all=True,append_images=gif_frames[1:],duration=250,loop=0,disposal=2)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','8','-i',str(T/'%04d.png'),'-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(O/'HARITA_TURU.mp4')],check=True)
(O/'ANIMASYON_KUNYESI.json').write_text(json.dumps({'frames':index,'video_fps':8,'video_seconds':index/8,'gif_input_frames':len(gif_frames),'gif_frames':Image.open(O/'HAREKETLI_HARITA.gif').n_frames,'gif_seconds':len(gif_frames)*.25,'data_snapshot':'2022-09-27','map_engine':'Leaflet 1.9.4','export_basemap':'Natural Earth boundary fallback; OSM tile network access blocked','interactive_basemap':'OpenStreetMap when accessible','interpretation':'Narrative camera tour with real geographic context images. Not historical event progression, live traffic, or operational routes.','images':'assets/locations/locations.json'},ensure_ascii=False,indent=2))
print('Recorded',index,'frames;',index/8,'second MP4 and matching animated GIF.')
