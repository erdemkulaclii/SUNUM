"""Render the authored narrative as a matching presentation and PDF."""
from pathlib import Path
import textwrap,shutil
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
R=Path(__file__).resolve().parents[1];O=R/'output';T=Path('/tmp/sunum-editorial-pages');T.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1600,'height':900},device_scale_factor=1)
 page.set_content((O/'CANLI_HARITA.html').read_text());page.add_style_tag(content='.transport,.map-tabs,.map-tools,.chips,.hint,#scope,#notes{display:none!important}.timeline{height:70px}.reading .stage{height:calc(100vh - 70px)}.story-caption{font-size:12px}.evidence-short{font-size:10px}')
 page.evaluate("document.body.classList.add('reading')")
 slides=page.evaluate('D.slides')
 main_count=page.evaluate('D.narrative.length')
 for i in range(main_count):
  page.evaluate('(i)=>go(i)',i);page.wait_for_timeout(1800 if i in [6,7,8,9] else 700);page.screenshot(path=str(T/f'{i:02}.png'))
 b.close()
prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
prs.core_properties.title='Görünmez Cephe — Sinematik OSINT Sunumu';prs.core_properties.subject='18 ana sahne, 15 dakika, gerçek konum bağlamı. Ülke düzeyindeki Meta IOC verisi; konum görselleri operasyon kanıtı değildir.'
pdfmetrics.registerFont(TTFont('Atlas','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('AtlasSerif','/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'))
pdf=canvas.Canvas(str(O/'ATLAS_SUNUMU.pdf'),pagesize=(960,540))
for i,s in enumerate(slides):
 sl=prs.slides.add_slide(prs.slide_layouts[6])
 if i<main_count:
  sl.shapes.add_picture(str(O/'HAREKETLI_HARITA.gif') if i==5 else str(T/f'{i:02}.png'),0,0,width=prs.slide_width,height=prs.slide_height)
  pdf.drawImage(str(T/f'{i:02}.png'),0,0,width=960,height=540)
 else:
  sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,0,0,prs.slide_width,prs.slide_height);sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string('F3F0E8');sh.line.fill.background()
  pdf.setFillColor('#f3f0e8');pdf.rect(0,0,960,540,fill=1,stroke=0)
  def text(value,x,y,w,size=18,color='34442E',serif=False):
   lines=[]
   for paragraph in value.split('\n'):
    line=''
    for word in paragraph.split():
     trial=(line+' '+word).strip()
     if pdfmetrics.stringWidth(trial,'AtlasSerif' if serif else 'Atlas',size)>w*72 and line:lines.append(line);line=word
     else:line=trial
    lines.append(line)
   tx=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(1.4));tf=tx.text_frame;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
   for j,line in enumerate(lines):
    p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.text=line;p.font.name='DejaVu Serif' if serif else 'DejaVu Sans';p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(0);p.line_spacing=1.2
   pdf.setFillColor('#'+color);pdf.setFont('AtlasSerif' if serif else 'Atlas',size)
   for j,line in enumerate(lines):pdf.drawString(x*72,540-y*72-size-j*size*1.2,line)
   return len(lines)*size*1.2/72
  text('GÖRÜNMEZ CEPHE / ARAŞTIRMA DEFTERİ',.65,.4,11,10,'A03D2C')
  text(s['title'],.65,.95,12,28,'293A2D',True)
  y=2.1
  for item in s['bullets']:
   h=text('— '+item,.7,y,11.8,17);y+=h+.24
  assert y<6.8,(i,y)
  text(s['source'],.7,7.05,10.9,8,'66715B');text(f'{i+1:02d}',12,6.93,.7,24,'A03D2C',True)
 sl.notes_slide.notes_text_frame.text=f"Süre: {s['seconds']} saniye\n\n{s['notes']}\n\nKaynak: {s['source']}\n\nYeni sürüm: CANLI_HARITA.html dosyasında GDELT API bağlantısı ve JSON içe aktarma vardır. API canlı indirmesi bu ortamda doğrulanmadı. 6. slayttaki GIF yalnızca tarihsel veriyi vurgular; gerçek zamanlı trafik değildir."
 transition=parse_xml('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>')
 sl._element.insert_element_before(transition,'p:timing','p:extLst')
 pdf.showPage()
prs.save(O/'ATLAS_SUNUMU.pptx');pdf.save()
shutil.copyfile(O/'ATLAS_SUNUMU.pptx',O/'SINEMATIK_SUNUM.pptx');shutil.copyfile(O/'ATLAS_SUNUMU.pdf',O/'SINEMATIK_SUNUM.pdf')
print(f'Exported {len(slides)} slides: {main_count} core + {len(slides)-main_count} appendices; fade transitions + animated map; matching PDF.')
