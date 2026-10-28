"""Export a native, editable academic PowerPoint from the canonical presentation.

Main titles, prose, three supporting statements, takeaways, charts and sources are
real PowerPoint text/shapes. Only geographic outlines and existing context photos
are raster images. No network request or invented scientific observation is used.
"""
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass
import hashlib, html, json, math, os, re
os.environ.setdefault('MPLCONFIGDIR','/tmp/sunum-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
FONT='DejaVu Sans'
FONT_DIR=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('Native','DejaVuSans.ttf'),('NativeBold','DejaVuSans-Bold.ttf'),('NativeItalic','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONT_DIR/file)))
BG='09111C'; PANEL='111F2F'; INK='F2F5F8'; MUTED='B7C7D7'; SOFT='8FA5BC'; LINE='2E435B'; RED='EC6354'; BLUE='78BCE9'
W=13.333333; H=7.5
COUNTRIES={'Germany':('Almanya',298,[10.5,51.1]),'UK':('Birleşik Krallık',4,[-2,54]),'France':('Fransa',2,[2.3,46.5]),'Italy':('İtalya',2,[12.6,42.6])}
ADMIN={'Germany':'Germany','UK':'United Kingdom','France':'France','Italy':'Italy'}
BOUNDS={'Europe':(-13,31,34,62.3),'Germany':(3.8,18,45.5,57.3),'UK':(-12,4,48.2,61.8),'France':(-7,12,40,53.5),'Italy':(3,22,34,50.5)}

def plain(value):
    return html.unescape(re.sub('<[^>]+>','',str(value or ''))).strip()

def line_width(s,size,bold=False):
    return pdfmetrics.stringWidth(s,'NativeBold' if bold else 'Native',size)

def wrapped(value,width_points,size,bold=False):
    """Measure explicit line breaks, including URLs that lack word boundaries."""
    result=[]
    for paragraph in str(value).split('\n'):
        line=''
        for word in paragraph.split():
            if line_width(word,size,bold)>width_points:
                chunks=[];chunk=''
                for char in word:
                    if chunk and line_width(chunk+char,size,bold)>width_points:
                        chunks.append(chunk);chunk=char
                    else:chunk+=char
                if chunk:chunks.append(chunk)
                if line:result.append(line);line=''
                result.extend(chunks[:-1]);line=chunks[-1]
                continue
            trial=(line+' '+word).strip()
            if line and line_width(trial,size,bold)>width_points:
                result.append(line);line=word
            else:line=trial
        result.append(line)
    return result

@dataclass
class Deck:
    prs: Presentation
    layout_checks: list
    def rectangle(self,sl,x,y,w,h,fill,line=None):
        shape=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
        shape.fill.solid();shape.fill.fore_color.rgb=RGBColor.from_string(fill)
        if line:shape.line.color.rgb=RGBColor.from_string(line);shape.line.width=Pt(.7)
        else:shape.line.fill.background()
        return shape
    def text(self,sl,value,x,y,w,max_h,size=17,color=INK,bold=False,name='',align=PP_ALIGN.LEFT,min_size=None,leading=1.22):
        value=plain(value);chosen=size
        while True:
            lines=wrapped(value,w*72-2,chosen,bold)
            height=len(lines)*chosen*leading/72+.035
            if height<=max_h+.0001:break
            if min_size is None or chosen<=min_size:raise RuntimeError(f'Text does not fit ({name}): {height:.2f}>{max_h:.2f}: {value[:120]}')
            chosen-=.5
        shape=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(max_h));shape.name=name or 'Native text'
        tf=shape.text_frame;tf.clear();tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0;tf.word_wrap=False;tf.vertical_anchor=MSO_ANCHOR.TOP
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=FONT;p.font.size=Pt(chosen);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.space_after=Pt(0);p.space_before=Pt(0);p.line_spacing=Pt(chosen*leading);p.alignment=align
        self.layout_checks.append({'shape':shape.name,'slide':len(self.prs.slides),'font_size':chosen,'estimated_text_height_in':round(height,3),'box_height_in':max_h})
        return height
    def slide(self,index,kicker,source):
        sl=self.prs.slides.add_slide(self.prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=RGBColor.from_string(BG)
        self.rectangle(sl,.6,.34,.055,.22,RED)
        self.text(sl,kicker,.79,.34,8.6,.3,8.6,RED,bold=True,name=f'slide_{index+1}_kicker',leading=1.1)
        self.text(sl,'AKADEMİK ARAŞTIRMA SUNUMU',9.5,.34,3.16,.3,8.0,SOFT,align=PP_ALIGN.RIGHT,name=f'slide_{index+1}_type',leading=1.1)
        self.rectangle(sl,.65,6.93,12.03,.012,LINE)
        self.text(sl,source,.65,7.05,11.08,.3,8.0,SOFT,name=f'slide_{index+1}_source',min_size=7.5,leading=1.08)
        self.text(sl,f'{index+1:02}',12.0,7.02,.66,.3,13,RED,bold=True,align=PP_ALIGN.RIGHT,name=f'slide_{index+1}_number',leading=1.1)
        return sl
    def heading(self,sl,s,index):
        self.text(sl,s['title'],.65,.89,12.03,1.08,29,INK,bold=True,min_size=25,name=f'slide_{index+1}_title',leading=1.12)
        self.text(sl,s['lead'],.65,2.03,12.0,.87,15.5,MUTED,min_size=14.5,name=f'slide_{index+1}_lead',leading=1.28)
    def points(self,sl,s,index):
        points=s.get('points')
        if not isinstance(points,list) or len(points)!=3:raise RuntimeError('Canonical narrative needs exactly three points per main slide before editable export.')
        y=3.05
        # Use a common projector-readable body size for the complete column.
        size=17.5;leading=1.25;width=7.43;gap=.10
        while True:
            heights=[len(wrapped(plain(v),width*72-2,size))*size*leading/72+.035 for v in points]
            if sum(heights)+gap*2<=3.04:break
            size-=.5
            if size<16.5:raise RuntimeError(f'Three-point column needs editorial shortening on slide {index+1}')
        for j,(value,h) in enumerate(zip(points,heights)):
            self.text(sl,f'{j+1:02}',.66,y+.015,.35,.32,9.5,RED,bold=True,name=f'slide_{index+1}_point_label_{j+1}',leading=1.1)
            self.text(sl,value,1.13,y,width,h+.025,size,INK,name=f'slide_{index+1}_point_{j+1}',leading=leading)
            y+=h+(gap if j<len(points)-1 else 0)
        if y>6.2:raise RuntimeError(f'Point column overflow slide {index+1}: {y}')
    def takeaway(self,sl,s,index):
        self.rectangle(sl,.65,6.2,.035,.52,RED)
        self.text(sl,s['takeaway'],.86,6.22,11.77,.54,14.5,INK,bold=True,min_size=13.0,name=f'slide_{index+1}_takeaway',leading=1.22)
    def note(self,sl,s):
        photo_note=''
        if s.get('country'):
            location=json.loads((ROOT/'assets/locations/locations.json').read_text())[s['country']]
            photo_note='\n\nFOTOĞRAF KÜNYESİ\n'+location['city']+' / '+location['place']+'\n'+location['credit']+'\n'+location['source']+'\n'+location['license']+'\n'+location['coordinate_basis']
        sl.notes_slide.notes_text_frame.text=f"PLANLANAN SÜRE: {s.get('seconds',0)} saniye\n\nKONUŞMA METNİ\n{s['notes']}\n\nSAHNE YÖNERGESİ (okunmaz)\n{s.get('cue','')}\n\nATIF\n{s['source']}\n\nVERİ / GÖRSEL SINIRI\nSayısal bulgular Meta’nın 2022 tarihli gösterge dosyasındandır. Harita Natural Earth sınır verisinden çevrimdışı üretildi. Fotoğraflar coğrafi bağlamdır, olay veya kamera GPS kanıtı değildir. Başarılı canlı GDELT indirmesi ve 2022 ile aynı dönemli haber karşılaştırması henüz doğrulanmadı."+photo_note
        sl._element.insert_element_before(parse_xml('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>'),'p:timing','p:extLst')


def merc(lat):return math.degrees(math.log(math.tan(math.pi/4+math.radians(lat)/2)))

def map_figure(name,geo):
    bounds=BOUNDS[name];x0,x1,lat0,lat1=bounds;y0,y1=merc(lat0),merc(lat1)
    path=OUT/f'EDITABLE_MAP_{name.upper()}.png'
    fig=plt.figure(figsize=(6.4,4.3),dpi=180,facecolor='#111f2f');ax=fig.add_axes([0,0,1,1]);ax.set_facecolor('#111f2f')
    for feature in geo['features']:
        admin=feature['properties']['ADMIN'];g=feature['geometry'];polygons=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
        focus_admin=set(ADMIN.values()) if name=='Europe' else {ADMIN[name]}
        emphasized=admin in focus_admin
        for polygon in polygons:
            ring=polygon[0]
            if not ring:continue
            # Clip through axes; no invented location or network activity is drawn.
            xy=[(p[0],merc(max(-80,min(80,p[1])))) for p in ring]
            if max(p[0] for p in xy)<x0 or min(p[0] for p in xy)>x1 or max(p[1] for p in xy)<y0 or min(p[1] for p in xy)>y1:continue
            ax.add_patch(Polygon(xy,closed=True,facecolor='#713c3e' if emphasized else '#20354a',edgecolor='#e69c89' if emphasized else '#597088',linewidth=.85 if emphasized else .45))
    ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.axis('off');fig.savefig(path,dpi=180,facecolor=fig.get_facecolor(),metadata={'Title':'Natural Earth geographic context; Meta target-country classification','Description':'Offline country boundaries. Not OSM tiles, event GPS or operational routes.'});plt.close(fig)
    return path,bounds


def add_photo(sl,path,x,y,w,h,contain=False):
    with Image.open(path) as img:iw,ih=img.size
    if contain:
        scale=min(w/iw,h/ih);actual_w=iw*scale;actual_h=ih*scale
        return sl.shapes.add_picture(str(path),Inches(x+(w-actual_w)/2),Inches(y+(h-actual_h)/2),width=Inches(actual_w),height=Inches(actual_h))
    pic=sl.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))
    source_ratio=iw/ih;target_ratio=w/h
    if source_ratio>target_ratio:pic.crop_left=pic.crop_right=(1-target_ratio/source_ratio)/2
    else:pic.crop_top=pic.crop_bottom=(1-source_ratio/target_ratio)/2
    return pic


def map_panel(deck,sl,name,figures,locs,index):
    x=8.75;w=3.92
    deck.rectangle(sl,x,3.01,w,2.93,PANEL,line=LINE)
    if name=='Europe':
        sl.shapes.add_picture(str(figures[name][0]),Inches(x+.03),Inches(3.05),width=Inches(w-.06),height=Inches(2.43))
        # Quantities remain editable even though the country outlines are raster.
        for j,(k,(label,count,_)) in enumerate(COUNTRIES.items()):
            col=j%2;row=j//2
            deck.text(sl,f'{label}: {count}',x+.13+col*1.89,5.52+row*.17,1.83,.17,8.0,MUTED,name=f'slide_{index+1}_map_count_{k}',leading=1.0)
    else:
        sl.shapes.add_picture(str(figures[name][0]),Inches(x+.03),Inches(3.05),width=Inches(w-.06),height=Inches(1.52))
        label,count,_=COUNTRIES[name]
        deck.text(sl,f'{label} · {count} gösterge',x+.15,4.45,w-.3,.29,12.5,INK,bold=True,name=f'slide_{index+1}_map_country',leading=1.1)
        loc=locs[name]
        add_photo(sl,ROOT/'assets/locations'/loc['image'],x+.15,4.82,w-.3,.69,contain=name=='France')
        deck.text(sl,f"{loc['city']} / coğrafi bağlam",x+.15,5.56,w-.3,.18,8.5,BLUE,name=f'slide_{index+1}_photo_label',leading=1.0)
        deck.text(sl,'Kent fotoğrafı operasyon konumu değildir.',x+.15,5.78,w-.3,.18,7.7,SOFT,name=f'slide_{index+1}_photo_limit',leading=1.0)
        credit='© 2018 Wildo Coda / galeri küçük resmi' if name=='France' else 'HDRI Haven / Poly Haven (CC0)'
        deck.text(sl,credit,x+.15,6.0,w-.3,.15,7.0,SOFT,name=f'slide_{index+1}_photo_credit',leading=1.0)


def diagram(deck,sl,items,index,heading=None):
    x=8.77;w=3.88;y=3.01
    if heading:
        deck.text(sl,heading,x,y,w,.45,13,BLUE,bold=True,name=f'slide_{index+1}_diagram_title',leading=1.15);y+=.58
    for j,(label,body) in enumerate(items):
        deck.rectangle(sl,x,y,.035,.43,RED)
        deck.text(sl,label,x+.16,y,w-.2,.25,12.2,INK,bold=True,name=f'slide_{index+1}_diagram_{j}_label',leading=1.12)
        h=deck.text(sl,body,x+.16,y+.28,w-.2,.5,10.5,MUTED,min_size=9.5,name=f'slide_{index+1}_diagram_{j}_body',leading=1.25)
        y+=max(.76,h+.42)
    if y>6.15:raise RuntimeError(f'Diagram overflow slide {index+1}: {y}')


def visual(deck,sl,s,index,figures,locs):
    if index in [5,6,7,8,9]:return map_panel(deck,sl,s.get('country','Europe'),figures,locs,index)
    x=8.78;w=3.87
    if index==1:return diagram(deck,sl,[('AS1 / BETİMSEL','Hedef ülke etiketlerinin dağılımı'),('AS2 / KARŞILAŞTIRMALI','Haber kaynak ve konu coğrafyaları'),('YANIT DÜZEYİ','Vaka bulgusu + uygulanacak protokol')],index)
    if index==2:return diagram(deck,sl,[('İÇERİK','Doğruluk ve kasıt'),('DAVRANIŞ','Koordineli sahte davranış / CIB'),('AKTÖR','Kaynağa dayanan atıf')],index)
    if index==3:return diagram(deck,sl,[('VERİ KAYNAĞI','Meta gösterge dosyası'),('ANALİZ BİRİMİ','Benzersiz alan adı'),('MEKÂNSAL DÜZEY','Hedef ülke etiketi')],index)
    if index==4:
        for j,(n,label) in enumerate([('350','ham kayıt'),('313','alan adı satırı'),('311','benzersiz alan adı')]):
            deck.text(sl,n,x,3.0+j*.91,w,.61,40,INK,bold=True,name=f'slide_{index+1}_audit_{j}',leading=1.0)
            deck.text(sl,label,x,3.63+j*.91,w,.22,10,BLUE,name=f'slide_{index+1}_audit_label_{j}',leading=1.0)
        return
    if index==10:return diagram(deck,sl,[('T / HEDEF','Meta comment'),('S / KAYNAK','GDELT sourcecountry'),('M / ANILAN YER','GKG veya insan kodlaması')],index)
    if index==11:return diagram(deck,sl,[('GDELT CLOUD','Kodlanmış Event adayları'),('GDELT PROJECT / DOC','Sorguya uyan haber URL’leri'),('ZAMAN AYRIMI','Güncel sorgu ≠ 2022 karşılaştırması')],index)
    if index==12:return diagram(deck,sl,[('1 / PİLOT','Kod kitabı ve uygunluk incelemesi'),('2 / BAĞIMSIZ KODLAMA','İki kodlayıcı; özgün kararlar'),('3 / UYUM','Cohen κ + ham uyum; henüz hesaplanmadı')],index)
    if index==13:return diagram(deck,sl,[('SORGU','Ad varyasyonları + bağlam'),('ZAMAN','Başlangıç / bitiş / UTC'),('KANIT KAYDI','Ham yanıt + kaynak + alım zamanı')],index)
    if index==14:
        deck.text(sl,'Benzersiz alan adı',x,3.02,w,.3,13,BLUE,bold=True,name=f'slide_{index+1}_chart_title')
        y=3.7
        for k,(label,count,_) in COUNTRIES.items():
            deck.text(sl,label,x,y,w-.6,.22,11,MUTED,name=f'slide_{index+1}_bar_label_{k}',leading=1.1)
            deck.text(sl,str(count),x+w-.6,y,.6,.22,11,INK,bold=True,align=PP_ALIGN.RIGHT,name=f'slide_{index+1}_bar_value_{k}',leading=1.1)
            deck.rectangle(sl,x,y+.29,w,.085,LINE)
            deck.rectangle(sl,x,y+.29,w*count/298,.085,RED)
            y+=.52
        deck.text(sl,'Lineer ölçek · Meta (2022)',x,5.93,w,.17,8,SOFT,name=f'slide_{index+1}_chart_note',leading=1)
        return
    if index==15:return diagram(deck,sl,[('HABER GÖRÜNÜRLÜĞÜ','İndekslenen yayınlar'),('KULLANICI MARUZİYETİ','Ayrı kullanıcı düzeyi veri'),('TUTUM / DAVRANIŞ','Ayrı etki araştırması')],index)
    if index==16:
        deck.rectangle(sl,x,3.0,w,2.96,PANEL,line=LINE)
        deck.text(sl,'%95,8',x+.2,3.4,w-.4,.9,47,INK,bold=True,name=f'slide_{index+1}_finding_share',leading=1)
        deck.text(sl,'298 / 311',x+.2,4.47,w-.4,.5,25,RED,bold=True,name=f'slide_{index+1}_finding_fraction',leading=1)
        deck.text(sl,'İncelenen listede Almanya hedefli etiketlerin payı.',x+.2,5.15,w-.4,.55,12,MUTED,name=f'slide_{index+1}_finding_scope',leading=1.25)
        return
    if index==17:return diagram(deck,sl,[('BİRİNCİL KANIT','Meta (2022) gösterge dosyası'),('AKADEMİK DAYANAK','Lazer; Allen; Grinberg; Vosoughi'),('TAM KÜNYELER','APA 7 kaynakça ve erişim günlüğü')],index)
    return diagram(deck,sl,[('KANIT','Yayımlanmış alan adı göstergeleri'),('SORU','Hedef dağılımı ve haber görünürlüğü'),('KAPSAM','Betimsel vaka incelemesi')],index)


def cover(deck,sl,s,figures):
    deck.text(sl,s['title'],.65,1.0,7.44,1.35,36,INK,bold=True,min_size=31,name='slide_1_title',leading=1.08)
    deck.text(sl,s.get('subtitle',''),.65,2.40,7.34,1.10,21,INK,bold=True,min_size=19,name='slide_1_subtitle',leading=1.2)
    deck.text(sl,s['lead'],.65,3.65,7.34,.90,14.5,MUTED,min_size=14,name='slide_1_lead',leading=1.3)
    sl.shapes.add_picture(str(figures['Europe'][0]),Inches(8.55),Inches(1.10),width=Inches(4.13),height=Inches(3.15))
    deck.text(sl,'Meta 2022 / 311 benzersiz gösterge',8.6,4.40,4.0,.24,11,BLUE,name='slide_1_visual_count',leading=1.1)
    deck.rectangle(sl,.65,4.69,12.03,.012,LINE)
    for j,p in enumerate(s['points']):
        x=.65+j*4.13
        deck.text(sl,f'{j+1:02} / SUNUM AKIŞI',x,4.85,3.74,.18,8.0,RED,bold=True,name=f'slide_1_point_label_{j+1}',leading=1.0)
        deck.text(sl,p,x,5.10,3.74,.98,14,INK,min_size=13.5,name=f'slide_1_point_{j+1}',leading=1.2)
    deck.takeaway(sl,s,0)


def apa_block(deck,sl,r,y,index,n):
    value=r['apa']+' '+r['url'];flat=plain(value);size=13.5;leading=1.65
    lines=wrapped(flat,11.65*72,size);height=(len(lines)+.3)*size*leading/72+.12
    if y+height>6.62:raise RuntimeError('APA references exceed readable appendix area')
    tx=sl.shapes.add_textbox(Inches(.9),Inches(y),Inches(11.67),Inches(height));tx.name=f'slide_{index+1}_APA_{n}'
    tf=tx.text_frame;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0;tf.word_wrap=True
    p=tf.paragraphs[0];p.font.name=FONT;p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(INK);p.line_spacing=Pt(size*leading)
    pr=p._p.get_or_add_pPr();pr.set('marL',str(int(Pt(18))));pr.set('indent',str(-int(Pt(18))))
    italic=False
    for token in re.split('(<i>|</i>)',r['apa']):
        if token=='<i>':italic=True
        elif token=='</i>':italic=False
        elif token:
            run=p.add_run();run.text=html.unescape(token);run.font.italic=italic
    link=p.add_run();link.text=' '+r['url'];link.hyperlink.address=r['url'];link.font.color.rgb=RGBColor.from_string(BLUE)
    deck.layout_checks.append({'shape':tx.name,'slide':index+1,'font_size':size,'estimated_text_height_in':height,'box_height_in':height})
    return y+height+.33


def validate(prs,narrative,appendices,path,layout_checks):
    expected=len(narrative)+len(appendices)
    assert len(prs.slides)==expected==35
    assert sum(s['seconds'] for s in narrative)==900
    native_core_counts=[]
    for i,slide in enumerate(prs.slides):
        assert slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip(),f'Empty notes: {i+1}'
        for shape in slide.shapes:
            assert shape.left>=0 and shape.top>=0,f'Negative position: {i+1}/{shape.name}'
            assert shape.left+shape.width<=prs.slide_width+10000,f'Horizontal shape overflow: {i+1}/{shape.name}'
            assert shape.top+shape.height<=prs.slide_height+10000,f'Vertical shape overflow: {i+1}/{shape.name}'
        if i<len(narrative):
            byname={s.name:s for s in slide.shapes};source=narrative[i]
            if i==0 and source.get('subtitle'):
                assert ' '.join(byname['slide_1_subtitle'].text.split())==' '.join(source['subtitle'].split())
            for suffix,value in [('title',source['title']),('lead',source['lead']),('takeaway',source['takeaway'])]+[(f'point_{j+1}',v) for j,v in enumerate(source['points'])]:
                shape=byname[f'slide_{i+1}_{suffix}'];assert shape.has_text_frame
                normalized=lambda x:' '.join(plain(x).split())
                assert normalized(shape.text)==normalized(value),f'Native text mismatch: {i+1}/{suffix}'
            native_core_counts.append(sum(s.has_text_frame and bool(s.text.strip()) for s in slide.shapes))
    assert all(c['estimated_text_height_in']<=c['box_height_in']+.001 for c in layout_checks)
    reloaded=Presentation(path);assert len(reloaded.slides)==35
    return {'checks_passed':True,'slides':expected,'core_slides':18,'appendices':17,'planned_seconds':900,'all_main_titles_leads_points_takeaways_editable':True,'native_main_text_shapes':native_core_counts,'all_notes_nonempty':True,'shape_bounds_within_slide':True,'font_metrics_layout_checked':True,'desktop_PowerPoint_render_verified':False,'GDELT_live_observations_generated':False,'map_basis':'Offline Natural Earth boundaries; Meta target-country counts. No OSM network tiles.','photo_role':'Geographic context, not operation or camera GPS evidence.','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    narrative=json.loads((ROOT/'scripts/cinematic_narrative.json').read_text());appendices=json.loads((ROOT/'scripts/academic_appendices.json').read_text());references={r['id']:r for r in json.loads((ROOT/'scripts/academic_references.json').read_text())}
    if any(len(s.get('points',[]))!=3 or not s.get('takeaway') for s in narrative):raise SystemExit('Editable export waits for the final narrative with three points and one takeaway per scene.')
    OUT.mkdir(exist_ok=True);geo=json.loads((ROOT/'research/countries.geojson').read_text());locs=json.loads((ROOT/'assets/locations/locations.json').read_text())
    figures={name:map_figure(name,geo) for name in BOUNDS}
    prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H);prs.core_properties.title='Hibrit Savaşın Görünmez Cephesi — Akademik Araştırma Sunumu';prs.core_properties.subject='Düzenlenebilir 35 slayt, gerçek Meta gösterge verisi ve GDELT haber görünürlüğü araştırma tasarımı.'
    deck=Deck(prs,[])
    for i,s in enumerate(narrative):
        sl=deck.slide(i,s['kicker'],s['source'])
        if i==0:cover(deck,sl,s,figures)
        else:deck.heading(sl,s,i);deck.points(sl,s,i);visual(deck,sl,s,i,figures,locs);deck.takeaway(sl,s,i)
        deck.note(sl,s)
    for j,s in enumerate(appendices):
        index=len(narrative)+j;sl=deck.slide(index,s['kicker'],s['source']);deck.text(sl,s['title'],.65,.95,12.0,1.0,27.5,INK,bold=True,min_size=25,name=f'slide_{index+1}_title',leading=1.12);y=2.15
        if s.get('reference_ids'):
            for k,rid in enumerate(s['reference_ids']):y=apa_block(deck,sl,references[rid],y,index,k)
        else:
            for k,value in enumerate(s['bullets']):
                deck.rectangle(sl,.67,y+.1,.06,.06,RED)
                h=deck.text(sl,value,.96,y,11.6,1.02,16.5,INK,min_size=15.5,name=f'slide_{index+1}_appendix_point_{k+1}',leading=1.3);y+=h+.23
            if y>6.7:raise RuntimeError(f'Appendix text overflow slide {index+1}: {y}')
        deck.note(sl,s)
    output=OUT/'AKADEMIK_SUNUM_DUZENLENEBILIR.pptx';prs.save(output)
    report=validate(prs,narrative,appendices,output,deck.layout_checks);(OUT/'DUZENLENEBILIR_SUNUM_DOGRULAMA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(f'Exported editable academic presentation: {len(prs.slides)} slides; all 18 core titles/leads/three points/takeaways native; 900 seconds.')
    print('PowerPoint desktop rendering is not verified; native geometry and font-metric layout checks passed.')

if __name__=='__main__':main()
