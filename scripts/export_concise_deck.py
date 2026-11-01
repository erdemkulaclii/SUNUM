"""Native editable slides and a matching text PDF for the completed Meta case.

No network access, photos, generated observations or live GDELT claims. Authored
main text is deliberately short; charts are built from the audited JSON report.
"""
from __future__ import annotations
from pathlib import Path
import html,json,re,hashlib
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';W=13.333333;H=7.5
import sys;sys.path.insert(0,str(Path(__file__).resolve().parent))
SHORT={'auswaertiges2024':'Germany targeted by … “Doppelgänger” (teknik rapor)','bennett2018':'The disinformation order (Eur. J. of Communication)','gdeltgkg':'GDELT 2.0 GKG ham arşivi [Data set]','wang2016':'Growing pains for global monitoring… (Science)','kwak2014':'Global news coverage of disasters… GDELT (SocInfo)','disinfolab2022':'Doppelganger: Media clones serving Russian propaganda','allen2020':'Evaluating the fake news problem… (Science Advances)','gdeltdoc':'GDELT DOC 2.0 API debuts! (API belgesi)','hammond2014':'Machine-coded event data… (Research & Politics)','lazer2018':'The science of fake news (Science)','leetaru2013':'GDELT: Global data on events, location, and tone','meta2022':'CIB gösterge listesi, CSV [Data set]','nimmo2022':'Removing CIB from China and Russia (Meta)','wardle2017':'Information disorder (Council of Europe)'}
META={};REFS={};GDELT=None;TALK=1200
INK='10263B';MUTED='3F556C';BLUE='164F7A';RED='AD3F32';LINE='C8D3DF';PALE='EDF3F8';PAPER='FFFFFF';DARK='0D2238'
FONT='DejaVu Sans';FONTDIR=Path('/usr/share/fonts/truetype/dejavu')
def font_file(file):
    # DejaVu Sans Oblique is missing on some systems; fall back without changing metrics family much.
    for cand in [FONTDIR/file,Path('/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf'),FONTDIR/'DejaVuSans.ttf']:
        if cand.is_file():return str(cand)
    raise FileNotFoundError(file)
for name,file in [('CNormal','DejaVuSans.ttf'),('CBold','DejaVuSans-Bold.ttf'),('CItalic','DejaVuSans-Oblique.ttf')]:pdfmetrics.registerFont(TTFont(name,font_file(file)))

def clean(s):return html.unescape(re.sub('<[^>]+>','',str(s or ''))).strip()
def normalize(s):return re.sub(r'\s+',' ',clean(s)).strip()
def note_text(s):
    value=s.get('notes','');return '\n'.join(str(x) for x in value) if isinstance(value,list) else str(value)
def width(s,size,bold=False,italic=False):return pdfmetrics.stringWidth(s,'CBold' if bold else 'CItalic' if italic else 'CNormal',size)
def wrap(text,w,size,bold=False):
    lines=[]
    for para in clean(text).split('\n'):
        line=''
        for word in para.split():
            if width(word,size,bold)>w:
                pieces=[];part=''
                for c in word:
                    if part and width(part+c,size,bold)>w:pieces.append(part);part=c
                    else:part+=c
                if part:pieces.append(part)
                if line:lines.append(line);line=''
                lines.extend(pieces[:-1]);line=pieces[-1];continue
            trial=(line+' '+word).strip()
            if line and width(trial,size,bold)>w:lines.append(line);line=word
            else:line=trial
        lines.append(line)
    return lines

class Dual:
    def __init__(self,prs,pdf):self.prs=prs;self.pdf=pdf;self.checks=[];self.slide_index=0
    def rect(self,sl,x,y,w,h,color,line=None):
        sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=RGBColor.from_string(color)
        if line:sh.line.color.rgb=RGBColor.from_string(line);sh.line.width=Pt(.6)
        else:sh.line.fill.background()
        self.pdf.setFillColor('#'+color);self.pdf.setStrokeColor('#'+(line or color));self.pdf.setLineWidth(.6);self.pdf.rect(x*72,(H-y-h)*72,w*72,h*72,fill=1,stroke=bool(line));return sh
    def text(self,sl,value,x,y,w,h,size=22,color=INK,bold=False,name='',leading=1.25,min_size=None,align=PP_ALIGN.LEFT):
        plain=clean(value);chosen=size
        while True:
            lines=wrap(plain,w*72-1.5,chosen,bold);needed=len(lines)*chosen*leading/72+.025
            if needed<=h+.001:break
            if min_size is None or chosen<=min_size:raise ValueError(f'Text overflow slide {self.slide_index+1}/{name}: {needed:.2f}>{h:.2f}: {plain[:80]}')
            chosen-=.5
        box=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));box.name=name or 'Editable text';tf=box.text_frame;tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=False
        self.pdf.setFillColor('#'+color);self.pdf.setFont('CBold' if bold else 'CNormal',chosen)
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name=FONT;p.font.size=Pt(chosen);p.font.bold=bold;p.font.color.rgb=RGBColor.from_string(color);p.line_spacing=Pt(chosen*leading);p.space_before=Pt(0);p.space_after=Pt(0);p.alignment=align
            if align==PP_ALIGN.RIGHT:self.pdf.drawRightString((x+w)*72,H*72-y*72-chosen-i*chosen*leading,line)
            elif align==PP_ALIGN.CENTER:self.pdf.drawCentredString((x+w/2)*72,H*72-y*72-chosen-i*chosen*leading,line)
            else:self.pdf.drawString(x*72,H*72-y*72-chosen-i*chosen*leading,line)
        self.checks.append({'slide':self.slide_index+1,'name':box.name,'font_pt':chosen,'estimated_height_in':needed,'box_height_in':h})
        return needed
    def base(self,index,s,core=True):
        self.slide_index=index;sl=self.prs.slides.add_slide(self.prs.slide_layouts[6]);dark=core and s.get('visual')=='cover';bg=DARK if dark else PAPER;ink=PAPER if dark else INK
        sl.background.fill.solid();sl.background.fill.fore_color.rgb=RGBColor.from_string(bg);self.pdf.setFillColor('#'+bg);self.pdf.rect(0,0,W*72,H*72,fill=1,stroke=0)
        self.rect(sl,.62,.35,.055,.24,'E46E5D' if dark else RED)
        self.text(sl,s.get('kicker','YÖNTEM VE KAYNAKÇA EKLERİ'),.8,.36,8.8,.29,9.3,'E9A497' if dark else RED,bold=True,name=f's{index+1}_kicker',leading=1.0)
        self.text(sl,'AKADEMİK ARAŞTIRMA SUNUMU',9.4,.36,3.22,.27,8.8,'BFD1E3' if dark else MUTED,align=PP_ALIGN.RIGHT,name=f's{index+1}_type',leading=1.0)
        self.rect(sl,.65,6.96,12.03,.012,'4C657F' if dark else LINE)
        self.text(sl,s.get('source','Meta, 2022; yeniden sayım ve yapısal çözümleme.'),.65,7.06,11.10,.28,8.0,'C5D4E3' if dark else MUTED,name=f's{index+1}_source',leading=1.08,min_size=7.5)
        self.text(sl,f'{index+1:02}',12.05,7.035,.57,.3,13,'EBA494' if dark else RED,bold=True,align=PP_ALIGN.RIGHT,name=f's{index+1}_page',leading=1.0)
        if core:
            self.text(sl,s['title'],.68,1.0,11.93,1.20,34 if dark else 31,ink,bold=True,min_size=29 if dark else 28,name=f's{index+1}_title',leading=1.12)
        else:self.text(sl,s['title'],.68,.97,11.93,.93,27,INK,bold=True,min_size=24,name=f's{index+1}_title',leading=1.15)
        return sl,dark
    def notes(self,sl,s,core=True):
        text=f"KONUŞMA İPUÇLARI\n{note_text(s)}"
        if s.get('full_notes'):text+='\n\nPROVA İÇİN TAM METİN\n'+str(s['full_notes'])
        if core:text+=f"\n\nPLANLANAN ANLATIM: {s.get('seconds',0)} saniye. Toplam anlatım yaklaşık 20 dakika; soru-cevap yok. Süreler yalnız prova içindir; slaytlar kendiliğinden geçmez."
        text+='\n\nKAYNAK\n'+s.get('source','Meta, 2022; ilgili kaynak künyeleri eklerde.')
        sl.notes_slide.notes_text_frame.text=text
        adv=''  # slayt geçişi sunucuda: otomatik ilerleme yok
        sl._element.insert_element_before(parse_xml(f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"{adv}><p:fade/></p:transition>'),'p:timing','p:extLst')
    def finish(self):self.pdf.showPage()


def points(d,sl,s,index,dark=False):
    color=PAPER if dark else INK;visual=s['visual'];x=.78;y=2.5;w=5.55
    if visual=='cover':
        y=3.30;w=10.7
        if s.get('subtitle'):d.text(sl,s['subtitle'],x,2.40,10.7,.65,18,'C7D8E8',name='cover_subtitle',leading=1.25)
        for j,value in enumerate(s['display_points']):
            d.text(sl,value,x,y,w,.56,24,color,bold=False,name=f's{index+1}_point{j+1}',leading=1.2);y+=.77
    elif visual=='references':
        d.text(sl,s['takeaway'],.7,1.58,11.9,.28,11,MUTED,name=f's{index+1}_takeaway',leading=1.0,min_size=9)
        return
    else:
        many=len(s['display_points'])>=3;size=20 if many else 23;gap=.24 if many else .34
        if visual=='gdelt_map':w=4.6
        for j,value in enumerate(s['display_points']):
            d.rect(sl,x,y+.14,.065,.065,RED);h=d.text(sl,value,x+.25,y,w-.25,1.17,size,color,min_size=size-3,name=f's{index+1}_point{j+1}',leading=1.3);y+=h+gap
        if y>5.95:raise ValueError(f'Point overflow slide {index+1}: {y:.2f}')
    takeaway_y=6.02;d.rect(sl,.76,takeaway_y,.04,.59,'E58A78' if dark else RED)
    d.text(sl,s['takeaway'],.98,takeaway_y+.025,11.65,.61,19,color,bold=True,min_size=18,name=f's{index+1}_takeaway',leading=1.2)


def bars(d,sl,items,x,y,w,row_h=.60,size=18,max_value=None):
    max_value=max_value or max(v for _,v in items)
    for label,value in items:
        d.text(sl,label,x,y,w-.65,.34,size,INK,name='chart_label',leading=1.05)
        d.text(sl,str(value),x+w-.65,y,.65,.34,size,INK,bold=True,align=PP_ALIGN.RIGHT,name='chart_count',leading=1.05)
        d.rect(sl,x,y+.38,w,.075,PALE);d.rect(sl,x,y+.38,w*value/max_value,.075,BLUE)
        y+=row_h


def steps(d,sl,items,x,y,w):
    for j,(head,sub) in enumerate(items):
        yy=y+j*.86;d.rect(sl,x,yy-.06,w,.012,LINE)
        d.text(sl,f'{j+1:02}',x,yy+.04,.55,.36,17,RED,bold=True,name='step_number',leading=1.0)
        d.text(sl,head,x+.62,yy+.03,w-.62,.32,15.5,INK,bold=True,name='step_head',leading=1.05,min_size=12)
        d.text(sl,sub,x+.62,yy+.38,w-.62,.42,11.5,MUTED,name='step_sub',leading=1.2,min_size=9)


def wave(d,sl,x,y,w):
    daily=(GDELT or {}).get('daily') or []
    if not daily:
        d.text(sl,'GDELT günlük serisi yok.',x,y,w,.4,14,MUTED,name='wave_empty',leading=1.1);return
    mx=max(r['matches'] for r in daily) or 1;h=2.7;bw=w/len(daily);base=y+.35+h
    d.text(sl,f'Günlük eşleşen haber (en çok {mx})',x,y,w,.28,11,MUTED,name='wave_axis',leading=1.0)
    for i,r in enumerate(daily):
        bh=h*r['matches']/mx
        if bh>0:d.rect(sl,x+i*bw+.02,base-bh,bw-.04,bh,RED if r['day']=='20220927' else '9EC1E0')
        mi=[q['day'] for q in daily].index('20220927') if any(q['day']=='20220927' for q in daily) else -9
        if (i%3==0 and abs(i-mi)>1) or i==mi:d.text(sl,f"{r['day'][6:]}.{r['day'][4:6]}",x+i*bw-.1,base+.05,bw+.2,.22,8.5,MUTED,name='wave_tick',leading=1.0,align=PP_ALIGN.CENTER)
    d.rect(sl,x,base,w,.012,LINE)
    peak=max(daily,key=lambda r:r['matches']);d.text(sl,f"Zirve {peak['day'][6:]}.{peak['day'][4:6]}: {peak['matches']} haber · kırmızı: 27.09 Meta duyurusu",x,base+.32,w,.26,10.5,INK,name='wave_note',leading=1.0,min_size=9)


def gdelt_line():
    if not GDELT:return 'Kaynak ülke ve anılan yer katmanları (HTML sunumunda canlı)'
    from gdelt_map_png import summary
    return summary(GDELT)['line']


def gdelt_visual(d,sl):
    x,y,w,h=5.55,2.1,7.1,3.45
    if GDELT:
        from gdelt_map_png import render,summary
        png=OUT/'GDELT_HARITA.png';render(GDELT,png,width_in=w,height_in=h);sl.shapes.add_picture(str(png),Inches(x),Inches(y),Inches(w),Inches(h))
        d.pdf.drawImage(str(png),x*72,(H-y-h)*72,w*72,h*72)
        sm=summary(GDELT);d.text(sl,sm['caption'],x,y+h+.05,w,.3,9.5,MUTED,name='gdelt_caption',leading=1.1,min_size=8)
        return
    d.rect(sl,x,y,w,h,PALE,line=LINE)
    d.text(sl,'CANLI GDELT HARİTASI · HTML SUNUMUNDA',x+.25,y+.2,w-.5,.3,12,RED,bold=True,name='gdelt_live_label',leading=1.0)
    d.text(sl,'Bu kopyada henüz GDELT anlık görüntüsü yok.',x+.25,y+.62,w-.5,.4,17,INK,bold=True,name='gdelt_empty',leading=1.15,min_size=14)
    for j,line in enumerate(['1) python scripts/fetch_gdelt_map.py  →  DOC 2.0 kaynak ülke verisi','2) İsteğe bağlı: --bigquery --project <GCP>  →  GKG anılan yerler','3) python scripts/build_interactive.py && python scripts/export_editorial.py','Bu adımlardan sonra bu slaytta gerçek harita görüntüsü yer alır.']):
        d.text(sl,line,x+.25,y+1.25+j*.5,w-.5,.42,12,MUTED if j==3 else INK,name='gdelt_step',leading=1.2,min_size=9.5)


def visual(d,sl,s,stats):
    kind=s['visual'];f=stats['findings'];x=7.10;w=5.2;y=2.45
    if kind=='bars' and s.get('bars'):
        bars(d,sl,[tuple(b) for b in s['bars']],x,y+.1,w,row_h=.95,size=18);d.text(sl,s.get('bars_caption',''),x,y+3.05,w,.3,11,MUTED,name='bars_caption',leading=1.0,min_size=9);return
    if kind=='steps' and s.get('steps'):
        steps(d,sl,[tuple(t) for t in s['steps']],x-.2,y-.15,w+.25);return
    if kind=='quote':
        d.rect(sl,x-.2,y-.15,w+.3,3.2,PALE);d.rect(sl,x-.2,y-.15,.06,3.2,RED)
        d.text(sl,s['quote'],x+.05,y,w-.05,2.25,15.5,INK,bold=True,name='definition_quote',leading=1.35,min_size=12)
        d.text(sl,s.get('quote_note',''),x+.05,y+2.35,w-.05,.65,10,MUTED,name='definition_note',leading=1.3,min_size=8.5);return
    if kind=='table' and s.get('table'):
        t=s['table'];widths=[1.45,1.95,2.1];xx=x-.4;rh=.56
        for k,hd in enumerate(t['headers']):d.text(sl,hd,xx+sum(widths[:k]),y-.1,widths[k]-.08,.26,11,MUTED,bold=True,name='layer_head',leading=1.0)
        for i,row in enumerate(t['rows']):
            yy=y+.25+i*rh;d.rect(sl,xx,yy-.04,sum(widths),.012,LINE)
            for k,v in enumerate(row):d.text(sl,v,xx+sum(widths[:k]),yy+.04,widths[k]-.1,rh-.08,11.5,('14532D' if k==2 and v.startswith('Ölçüldü') else INK),bold=(k==0 or (k==2 and v.startswith('Ölçüldü'))),name='layer_cell',leading=1.2,min_size=9)
        return
    if kind=='cover':
        m=META;xx=8.25;d.rect(sl,xx-.2,3.30,.04,1.85,'E58A78')
        d.text(sl,m['author'],xx,3.28,4.4,.45,20,PAPER,bold=True,name='cover_author',leading=1.1,min_size=15)
        for j,k in enumerate(['affiliation','course','date']):d.text(sl,m[k],xx,3.86+j*.42,4.4,.36,14,'C7D8E8',name='cover_'+k,leading=1.1,min_size=11)
        return
    if kind in('question','outline','conclusion'):
        items={'question':[('AS1 · Hedef coğrafyası','Birim: alan adı · Meta hedef etiketi'),('AS2 · Sözcüksel yapı','Birim: alan adı · ilk ve son DNS etiketi'),('AS3 · Haber görünürlüğü','Birim: haber makalesi · GDELT GKG: gün, kaynak ülke, anılan yer')],
               'outline':[('Giriş','Vaka ve kavramsal çerçeve'),('Yöntem','Meta CSV + GDELT GKG ham arşivi (MD5)'),('Bulgular','Hedef ülke, DNS yapısı, haber dalgası ve haritası'),('Tartışma','Literatür, sınırlılıklar, sonuç')],
               'conclusion':[('AS1 · %95,8','298/311 gösterge Almanya hedefli'),('AS2 · 240 + 293','Altı son etiket 240 adres; 75 ilk etiket grubu 293 adres'),('AS3 · GDELT haritası',gdelt_line()),('Sonraki adım','GKG ile tam 2022 taraması; iki kodlayıcılı içerik analizi')]}[kind]
        steps(d,sl,items,x,y-.1,w)
    elif kind=='context':
        for j,(when,what,who) in enumerate([('Mayıs 2022','Kampanyanın bilinen başlangıcı','Alaphilippe vd., 2022'),('27.09.2022','EU DisinfoLab: en az 17 medya markası taklit edildi','Bild · Spiegel · The Guardian · ANSA'),('27.09.2022','Meta kaldırma raporu ve açık gösterge listesi','Nimmo ve Agranovich, 2022')]):
            yy=y+j*1.12;d.rect(sl,x,yy+.06,.13,.13,RED if j==2 else BLUE);d.text(sl,when,x+.32,yy,w-.32,.28,12.5,RED,bold=True,name='context_date',leading=1.0)
            d.text(sl,what,x+.32,yy+.32,w-.32,.5,15,INK,name='context_event',leading=1.2,min_size=13);d.text(sl,who,x+.32,yy+.80,w-.32,.26,11,MUTED,name='context_source',leading=1.0,min_size=9.5)
    elif kind in('literature','limits'):
        cells={'literature':[('Bilgi düzensizliği','Ajan · mesaj · yorumlayıcı; oluşturma → üretim → dağıtım','Wardle ve Derakhshan, 2017'),('Ölçüm ve payda','Neyin, hangi evrende sayıldığı açık tanımlanmalı','Lazer vd., 2018; Allen vd., 2020'),('Haber coğrafyası','Haberler kaynak ülke ve anılan yerle kodlanır','Leetaru ve Schrodt, 2013'),('Bu çalışmanın konumu','Taklit altyapısı ile haber görünürlüğünü aynı vakada yan yana okumak','')],
               'limits':[('Meta listesi','Tespit ve yayımlama seçilimi; bütün kayıtlarda ds = 27.09.2022','Allen vd., 2020'),('GDELT','Dilim başına ≤ 250 makale; kapsam eşit değil; DOC resmî desteği son 3 ay','The GDELT Project, 2017'),('Coğrafya','Kaynak ülke ≠ okur ülkesi; otomatik konum kodlaması hata içerebilir','Hammond ve Weidmann, 2014'),('Sonuç','Betimsel bulgular; niyet, maruziyet veya etki iddiası yok','')]}[kind]
        cw=(w-.15)/2;ch=1.62
        for j,(h,t,src) in enumerate(cells):
            cx=x+(j%2)*(cw+.15);cy=y-.1+(j//2)*(ch+.15);dark=j==3
            d.rect(sl,cx,cy,cw,ch,INK if dark else PALE,line=None if dark else LINE)
            d.text(sl,h,cx+.12,cy+.1,cw-.24,.3,13.5,PAPER if dark else INK,bold=True,name='cell_head',leading=1.0,min_size=11)
            d.text(sl,t,cx+.12,cy+.45,cw-.24,.85,11.5,'E7EEF5' if dark else INK,name='cell_text',leading=1.3,min_size=9.5)
            if src:d.text(sl,src,cx+.12,cy+ch-.3,cw-.24,.22,9,MUTED,name='cell_source',leading=1.0,min_size=8)
    elif kind=='method':
        cols=[('Meta CSV · 27.09.2022','350 kayıt → 311 alan adı','Hedef etiketi; ilk / son DNS etiketi','AS1 · AS2'),('GDELT DOC 2.0','20.09–11.10.2022; 3 günlük dilim; URL tekilleştirme','Haberin kaynak ülkesi','AS3 · renk'),('GDELT GKG','BigQuery · V2Locations','Haberde anılan yer + koordinat','AS3 · nokta')]
        cw=(w+.3-.2)/3;xx0=x-.3
        for j,(h,a,b,tag) in enumerate(cols):
            cx=xx0+j*(cw+.1);d.rect(sl,cx,y-.05,cw,.05,BLUE);d.rect(sl,cx,y,cw,2.75,PALE)
            d.text(sl,h,cx+.1,y+.1,cw-.2,.5,12.5,INK,bold=True,name='method_head',leading=1.15,min_size=10)
            d.text(sl,a,cx+.1,y+.68,cw-.2,.8,10.5,MUTED,name='method_detail',leading=1.3,min_size=9)
            d.text(sl,b,cx+.1,y+1.5,cw-.2,.8,11.5,INK,name='method_measure',leading=1.3,min_size=9.5)
            d.text(sl,tag,cx+.1,y+2.42,cw-.2,.25,10,RED,bold=True,name='method_tag',leading=1.0)
        d.text(sl,'Hedef etiketi ≠ kaynak ülke ≠ anılan yer',xx0,y+2.95,w+.3,.3,12,MUTED,name='method_units',leading=1.0)
    elif kind=='gdelt_map':
        gdelt_visual(d,sl)
    elif kind=='gdelt_wave':
        wave(d,sl,x-.6,y-.2,w+.6)
    elif kind=='validity':
        v=(GDELT or {}).get('validation') or {};a=(GDELT or {}).get('archive') or {};allv=v.get('by_rule',{}).get('all') or {}
        prec=f"%{allv['precision']*100:.0f} isabet (n={allv['n']}; %95 GA {allv['wilson95'][0]*100:.0f}–{allv['wilson95'][1]*100:.0f})".replace('.',',') if allv.get('n') else 'Örneklem denetimi bekleniyor'
        steps(d,sl,[('MD5 doğrulaması',f"{a.get('files_md5_verified',0):,} / {a.get('files',0):,} ham GKG dosyası".replace(',','.')),('Tarama kapsamı',f"{a.get('rows_scanned',0):,} haber kaydı · 20.09–11.10.2022".replace(',','.')),('Eşleşme isabeti',prec),('Yeniden üretim','python scripts/gdelt_gkg_archive.py · test_gdelt_archive.py')],x,y-.1,w)
    elif kind=='discussion':
        rows=[('Almanya %95,8 hedef','Öncelikli hedef Almanya (Nimmo ve Agranovich, 2022; Auswärtiges Amt, 2024)','Uyumlu'),('Kaynak: ABD 373/511','Haber coğrafyası bölgeseldir (Kwak ve An, 2014)','Asimetri'),('511 adres, 145 başlık','Dağıtım altyapısı (Wardle ve Derakhshan, 2017)','Ajans çoğaltması'),('“Doppelgänger”: 1 ilgili haber','Ad EU DisinfoLab raporuyla (2022) doğdu','Sonradan yaygınlaştı*')]
        widths=[1.5,2.6,1.25];xx=x-.15;rh=.72
        for k,hd in enumerate(['Bulgu','Literatür / raporlar','İlişki']):d.text(sl,hd,xx+sum(widths[:k]),y,widths[k]-.08,.26,11,MUTED,bold=True,name='disc_head',leading=1.0)
        for i,row in enumerate(rows):
            yy=y+.35+i*rh;d.rect(sl,xx,yy-.04,sum(widths),.012,LINE)
            for k,v in enumerate(row):d.text(sl,v,xx+sum(widths[:k]),yy+.06,widths[k]-.1,rh-.12,12.5,INK,bold=k==0,name='disc_cell',leading=1.25,min_size=10)
        d.text(sl,'* Yalnız 2022 penceresi tarandı.',xx,y+.45+4*rh,sum(widths),.3,10,MUTED,name='disc_note',leading=1.1,min_size=9)
    elif kind=='audit':
        nums=[(stats['audit']['raw_records'],'toplam kayıt'),(stats['audit']['domain_rows'],'alan adı satırı'),(stats['audit']['unique_domains'],'benzersiz alan adı')]
        for j,(n,label) in enumerate(nums):
            xx=x+j*1.76;d.text(sl,str(n),xx,y+.25,1.5,.78,37,BLUE,bold=True,name='audit_count',leading=1.0);d.text(sl,label,xx,y+1.18,1.55,.78,15,INK,name='audit_unit',leading=1.35)
            if j<2:d.text(sl,'→',xx+1.4,y+.50,.38,.36,17,RED,name='audit_arrow',leading=1.0)
        d.text(sl,'22 CIB URL + 15 Telegram URL',x,y+2.42,w,.44,15,MUTED,name='audit_exclusions',leading=1.2)
    elif kind=='countries':
        n=f['target_country_counts']['Germany'];total=stats['audit']['unique_domains'];bars(d,sl,[('Almanya',n),('Diğer hedef etiketleri',total-n)],x,y+.08,w,row_h=.92,size=19,max_value=n)
        d.text(sl,'Birleşik Krallık 4 · Fransa 2 · İtalya 2',x,y+2.10,w,.58,15,MUTED,name='small_country_counts',leading=1.35)
        d.text(sl,'Diğer/çoklu: 5 · bütün liste: 311',x,y+2.87,w,.38,14,MUTED,name='other_country_counts',leading=1.15)
    elif kind=='tlds':
        values=[('.'+r['last_dns_label'],r['domain_count']) for r in f['top_six_last_dns_labels']];bars(d,sl,values,x,y-.15,w,row_h=.49,size=17,max_value=max(v for _,v in values))
        d.text(sl,'Son noktanın sağındaki etiket',x,y+3.03,w,.3,11.5,MUTED,name='tld_definition',leading=1.0)
    elif kind=='reuse':
        d.text(sl,str(f['multi_suffix_first_label_families']),x,y,w,.84,48,BLUE,bold=True,name='reuse_groups',leading=1.0)
        d.text(sl,'Çoklu son etiketli ilk DNS etiketi',x,y+1.0,w,.38,17,INK,name='reuse_definition',leading=1.05)
        examples={r['first_dns_label']:r for r in stats['first_label_families']}
        for j,label in enumerate(['spiegel','bild','dailymail']):
            n=examples[label]['distinct_last_label_count'];d.text(sl,f'{label}  →  {n} son etiket',x,y+1.70+j*.48,w,.4,17,INK,name='reuse_example',leading=1.1)
    elif kind=='anatomy':
        d.text(sl,'theguardian[.]co[.]com',x,y+.1,w,.62,24,BLUE,bold=True,name='anatomy_address',leading=1.15)
        parts=[('theguardian','ilk etiket'),('co','ara etiket'),('com','son etiket')]
        for j,(atom,label) in enumerate(parts):
            xx=x+j*1.78;d.rect(sl,xx,y+1.1,1.6,.65,PALE,line=LINE);d.text(sl,atom,xx+.07,y+1.27,1.46,.34,14 if j==0 else 19,INK,bold=True,name='dns_atom',leading=1.0);d.text(sl,label,xx,y+1.96,1.6,.33,12.5,MUTED,name='dns_atom_role',leading=1.1)
        d.text(sl,'Son etiket ≠ kayıt edilebilir alan adı sınırı',x,y+2.8,w,.63,14,MUTED,name='psl_caution',leading=1.35)
    elif kind=='references':
        reference_page(d,sl,REFS)
    else:raise ValueError('Unknown main visual: '+kind)


def table(d,sl,headers,rows):
    cols=len(headers);x=.8;y=2.1;w=11.73
    widths=[w/cols]*cols
    if cols==2:widths=[w*.72,w*.28]
    elif cols==3:widths=[w*.52,w*.24,w*.24]
    row_h=min(.48,4.45/(len(rows)+1));font=min(16,max(12.2,row_h*72*.68));header_font=min(15,font)
    d.rect(sl,x,y,w,row_h,BLUE)
    xx=x
    for k,v in enumerate(headers):d.text(sl,v,xx+.12,y+.01,widths[k]-.24,row_h-.005,header_font,PAPER,bold=True,name='table_header',leading=1.0);xx+=widths[k]
    y+=row_h
    for i,row in enumerate(rows):
        if i%2==0:d.rect(sl,x,y,w,row_h,PALE)
        xx=x
        for k,v in enumerate(row):d.text(sl,str(v),xx+.12,y+.01,widths[k]-.24,row_h-.005,font,INK,name='table_cell',leading=1.0,min_size=11.5);xx+=widths[k]
        d.rect(sl,x,y+row_h-.006,w,.006,LINE);y+=row_h
    if y>6.65:raise ValueError('Appendix table exceeds readable area')


def ref_tokens(r):
    tokens=[];italic=False
    for span in re.split('(<i>|</i>)',r['apa']):
        if span=='<i>':italic=True
        elif span=='</i>':italic=False
        elif span:
            for word in html.unescape(span).split():tokens.append((word,italic,None))
    tokens.append((r['url'],False,r['url']));return tokens

def ref_lines(r,w,size,indent):
    lines=[];line=[];used=0
    for word,italic,link in ref_tokens(r):
        font='CItalic' if italic else 'CNormal';remaining=word
        while remaining:
            limit=w*72-(indent if lines else 0);space=pdfmetrics.stringWidth(' ',font,size) if line else 0;amount=pdfmetrics.stringWidth(remaining,font,size)
            if used+space+amount<=limit:line.append((remaining,italic,link));used+=space+amount;remaining=''
            elif line:lines.append(line);line=[];used=0
            else:
                part=''
                for c in remaining:
                    if part and pdfmetrics.stringWidth(part+c,font,size)>limit:break
                    part+=c
                line=[(part,italic,link)];lines.append(line);line=[];used=0;remaining=remaining[len(part):]
    if line:lines.append(line)
    return lines


def reference(d,sl,r,y,index,x=.92,w=11.5,size=12.8,leading=1.67,indent=18,gap=.32,bottom=6.65):
    lines=ref_lines(r,w,size,indent)
    h=len(lines)*size*leading/72+.04
    if y+h>bottom:raise ValueError('APA source does not fit: '+r['id'])
    tx=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tx.name=f'APA_reference_{index}';tf=tx.text_frame;tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=False
    for j,line in enumerate(lines):
        p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.font.name=FONT;p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(INK);p.line_spacing=Pt(size*leading);p.space_after=Pt(0);p.space_before=Pt(0)
        if j:p._p.get_or_add_pPr().set('marL',str(int(Pt(indent))))
        xx=x*72+(indent if j else 0);yy=H*72-y*72-size-j*size*leading
        for k,(word,italic,link) in enumerate(line):
            value=(' ' if k else '')+word;run=p.add_run();run.text=value;run.font.italic=italic;run.font.size=Pt(size)
            if link:run.hyperlink.address=link;run.font.color.rgb=RGBColor.from_string(BLUE)
            font='CItalic' if italic else 'CNormal';d.pdf.setFont(font,size);d.pdf.setFillColor('#'+(BLUE if link else INK));d.pdf.drawString(xx,yy,value);amount=pdfmetrics.stringWidth(value,font,size)
            if link:d.pdf.linkURL(link,(xx,yy-2,xx+amount,yy+size),relative=0,thickness=0)
            xx+=amount
    d.checks.append({'slide':d.slide_index+1,'name':tx.name,'font_pt':size,'estimated_height_in':h,'box_height_in':h})
    return y+h+gap


def reference_page(d,sl,refs,top=1.95,bottom=6.88):
    """All references on one slide: 2 or 3 columns, APA 7 hanging indent, clickable URLs."""
    order=sorted(refs.values(),key=lambda r:re.sub(r'^The ','',clean(r['apa'])).lower())
    for ncol,xs,colw in [(2,[.70,6.85],5.78),(3,[.6,4.72,8.84],3.82)]:
        size=8.6
        while size>=6.6:
            lead=1.22;gap=.05;hs=[len(ref_lines(r,colw,size,10))*size*lead/72+.04+gap for r in order]
            cols=[[]];acc=[0.0]
            for r,h in zip(order,hs):
                if acc[-1]+h>bottom-top and len(cols)<ncol:cols.append([]);acc.append(0.0)
                cols[-1].append(r);acc[-1]+=h
            if max(acc)<=bottom-top:break
            size-=.2
        if size>=6.6 and max(acc)<=bottom-top:break
    else:raise ValueError('References do not fit one page')
    n=0
    for c,col in enumerate(cols):
        y=top
        for r in col:y=reference(d,sl,r,y,n,x=xs[c],w=colw,size=size,leading=lead,indent=10,gap=gap,bottom=bottom+.01);n+=1
    for c in range(1,len(cols)):d.rect(sl,xs[c]-.12,top,.008,bottom-top,LINE)
    return size


def validate(prs,narrative,appendices,layout,pptx,pdf):
    assert len(prs.slides)==len(narrative)+len(appendices)
    assert sum(int(s['seconds']) for s in narrative)==TALK
    authored_words=[sum(len(clean(t).split()) for t in [s['title'],s.get('subtitle',''),*s['display_points'],s['takeaway']]) for s in narrative]
    assert max(authored_words)<=34,('Authored main-slide text exceeds 34 words',authored_words)
    for i,sl in enumerate(prs.slides):
        assert sl.notes_slide.notes_text_frame.text.strip()
        for shape in sl.shapes:
            assert shape.left>=0 and shape.top>=0,(i,shape.name)
            assert shape.left+shape.width<=prs.slide_width+10000,(i,shape.name,'right')
            assert shape.top+shape.height<=prs.slide_height+10000,(i,shape.name,'bottom')
        if i<len(narrative):
            text=normalize(' '.join(sh.text for sh in sl.shapes if sh.has_text_frame))
            for item in [narrative[i]['title'],narrative[i].get('subtitle',''),*narrative[i]['display_points'],narrative[i]['takeaway']]:assert normalize(item) in text,(i,item)
    assert all(r['estimated_height_in']<=r['box_height_in']+.001 for r in layout)
    from pypdf import PdfReader
    reader=PdfReader(pdf);assert len(reader.pages)==len(prs.slides)
    assert all(page.extract_text().strip() for page in reader.pages)
    return {'checks_passed':True,'main_slides':len(narrative),'appendix_slides':len(appendices),'total_slides':len(prs.slides),'planned_talk_seconds':TALK,'remaining_session_buffer_seconds':0,'main_text_editable':True,'authored_main_slide_word_counts':authored_words,'maximum_authored_main_words':max(authored_words),'matched_native_PDF_pages':True,'all_notes_nonempty':True,'bounds_and_font_metrics_checked':True,'no_photos_used':True,'gdelt_snapshot_embedded':bool(GDELT),'synthetic_GDELT_observations':False,'desktop_PowerPoint_render_verified':False,'pptx_sha256':hashlib.sha256(pptx.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}


def main():
    global META,REFS,GDELT
    META.update(json.loads((ROOT/'scripts/presentation_meta.json').read_text()));snap=ROOT/'research/gdelt/GDELT_HARITA_VERISI.json';GDELT=json.loads(snap.read_text()) if snap.is_file() else None
    narrative=json.loads((ROOT/'scripts/concise_narrative.json').read_text());appendices=json.loads((ROOT/'scripts/concise_appendices.json').read_text());refs={r['id']:r for r in json.loads((ROOT/'scripts/concise_references.json').read_text())};REFS.update(refs);stats=json.loads((OUT/'IOC_YAPISAL_ANALIZ.json').read_text())
    OUT.mkdir(exist_ok=True);prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H);prs.core_properties.title=narrative[0]['title'];prs.core_properties.author=META.get('author','SUNUM');prs.core_properties.subject=f'Akademik sunum: {len(narrative)} ana slayt, {TALK//60} dk {TALK%60} sn anlatım; Meta 2022 göstergeleri ve GDELT haber haritası.'
    pdf_path=OUT/'AKADEMIK_ODAKLI_SUNUM.pdf';pdf=canvas.Canvas(str(pdf_path),pagesize=(W*72,H*72));pdf.setTitle(prs.core_properties.title);pdf.setAuthor('SUNUM');d=Dual(prs,pdf)
    for i,s in enumerate(narrative):
        sl,dark=d.base(i,s);points(d,sl,s,i,dark);visual(d,sl,s,stats);d.notes(sl,s);d.finish()
    for j,s in enumerate(appendices):
        index=len(narrative)+j;sl,_=d.base(index,s,core=False);kind=s['kind']
        if kind=='table':table(d,sl,s['headers'],s['rows'])
        elif kind=='bullets':
            y=2.18
            for k,value in enumerate(s['bullets']):
                d.rect(sl,.8,y+.13,.06,.06,RED);h=d.text(sl,value,1.05,y,11.25,1.1,17.5,INK,min_size=16.5,name=f'appendix_{j}_point{k}',leading=1.30);y+=h+.18
            if y>6.7:raise ValueError('Appendix bullet overflow')
        elif kind=='references':
            y=2.10
            for k,rid in enumerate(s['reference_ids']):y=reference(d,sl,refs[rid],y,k)
        else:raise ValueError('Unknown appendix kind: '+kind)
        d.notes(sl,s,core=False);d.finish()
    pptx=OUT/'AKADEMIK_ODAKLI_SUNUM.pptx';prs.save(pptx);pdf.save();report=validate(prs,narrative,appendices,d.checks,pptx,pdf_path);(OUT/'ODAKLI_SUNUM_DOGRULAMA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
