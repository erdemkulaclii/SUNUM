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
INK='10263B';MUTED='3F556C';BLUE='164F7A';RED='AD3F32';LINE='C8D3DF';PALE='EDF3F8';PAPER='FFFFFF';DARK='0D2238'
FONT='DejaVu Sans';FONTDIR=Path('/usr/share/fonts/truetype/dejavu')
for name,file in [('CNormal','DejaVuSans.ttf'),('CBold','DejaVuSans-Bold.ttf'),('CItalic','DejaVuSans-Oblique.ttf')]:pdfmetrics.registerFont(TTFont(name,str(FONTDIR/file)))

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
        if core:text+=f"\n\nPLANLANAN ANLATIM: {s.get('seconds',0)} saniye. Ana akış 13 dakika; 15 dakikalık oturumda 2 dakika pay bırakılmıştır."
        text+='\n\nKAYNAK\n'+s.get('source','Meta, 2022; ilgili kaynak künyeleri eklerde.')
        sl.notes_slide.notes_text_frame.text=text
        sl._element.insert_element_before(parse_xml('<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med"><p:fade/></p:transition>'),'p:timing','p:extLst')
    def finish(self):self.pdf.showPage()


def points(d,sl,s,index,dark=False):
    color=PAPER if dark else INK;visual=s['visual'];x=.78;y=2.5;w=5.55
    if visual=='cover':
        y=3.30;w=10.7
        if s.get('subtitle'):d.text(sl,s['subtitle'],x,2.40,10.7,.65,18,'C7D8E8',name='cover_subtitle',leading=1.25)
        for j,value in enumerate(s['display_points']):
            d.text(sl,value,x,y,w,.56,24,color,bold=False,name=f's{index+1}_point{j+1}',leading=1.2);y+=.77
    elif visual=='conclusion':
        y=2.8;w=6.65
        for j,value in enumerate(s['display_points']):
            d.rect(sl,x,y+.16,.075,.075,RED);h=d.text(sl,value,x+.27,y,w-.27,.83,23,color,bold=True,min_size=22,name=f's{index+1}_point{j+1}',leading=1.3);y+=h+.35
    else:
        for j,value in enumerate(s['display_points']):
            d.rect(sl,x,y+.16,.065,.065,RED);h=d.text(sl,value,x+.25,y,w-.25,1.17,23,color,min_size=21,name=f's{index+1}_point{j+1}',leading=1.35);y+=h+.34
    takeaway_y=6.02;d.rect(sl,.76,takeaway_y,.04,.59,'E58A78' if dark else RED)
    d.text(sl,s['takeaway'],.98,takeaway_y+.025,11.65,.61,19,color,bold=True,min_size=18,name=f's{index+1}_takeaway',leading=1.2)


def bars(d,sl,items,x,y,w,row_h=.60,size=18,max_value=None):
    max_value=max_value or max(v for _,v in items)
    for label,value in items:
        d.text(sl,label,x,y,w-.65,.34,size,INK,name='chart_label',leading=1.05)
        d.text(sl,str(value),x+w-.65,y,.65,.34,size,INK,bold=True,align=PP_ALIGN.RIGHT,name='chart_count',leading=1.05)
        d.rect(sl,x,y+.38,w,.075,PALE);d.rect(sl,x,y+.38,w*value/max_value,.075,BLUE)
        y+=row_h


def visual(d,sl,s,stats):
    kind=s['visual'];f=stats['findings'];x=7.10;w=5.2;y=2.45
    if kind=='cover':
        d.rect(sl,10.3,3.22,2.0,.025,'7690AA');d.text(sl,'META 2022',10.3,3.43,2.0,.45,15,'C7D8E8',bold=True,leading=1.0)
        return
    if kind=='question':
        for j,(num,label) in enumerate([('01','Hedef coğrafyası'),('02','Son DNS etiketi'),('03','İlk etiket tekrarı')]):
            yy=y+j*.92;d.text(sl,num,x,yy,.55,.5,24,RED,bold=True,name='question_number',leading=1.0);d.text(sl,label,x+.78,yy+.025,w-.78,.50,20,INK,bold=True,name='question_dimension',leading=1.2)
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
    elif kind=='limits':
        for j,(name,value) in enumerate([('Birim','alan adı göstergesi'),('Kapsam','yayımlanmış seçki'),('ds','kaynak kayıt tarihi')]):
            yy=y+j*.93;d.text(sl,name,x,yy,w,.34,16,RED,bold=True,name='limit_label',leading=1.1);d.text(sl,value,x,yy+.42,w,.40,20,INK,name='limit_value',leading=1.1)
    elif kind=='future':
        for j,(label,value) in enumerate([('DÖNEM','2022 ile eşleşen haber arşivi'),('KAPSAM','dil, kaynak ve eksik gün günlüğü'),('KODLAMA','uygunluk, konu ve haberin işlevi')]):
            yy=y+j*.94;d.text(sl,label,x,yy,w,.28,12,RED,bold=True,name='future_label',leading=1.0);d.text(sl,value,x,yy+.38,w,.53,18,INK,name='future_step',leading=1.25)
    elif kind=='conclusion':
        d.text(sl,'298 / 311',8.2,y+.2,4.1,.85,41,BLUE,bold=True,name='conclusion_country',leading=1.0)
        d.text(sl,'Almanya hedefli etiket',8.2,y+1.2,4.1,.4,17,INK,name='conclusion_country_label',leading=1.1)
        d.text(sl,'75 grup / 293 adres',8.2,y+2.2,4.1,.5,22,BLUE,bold=True,name='conclusion_lexical',leading=1.1)
    elif kind=='references':
        for j,label in enumerate(['Meta (2022)','Lazer ve ark. (2018)','Allen ve ark. (2020)']):d.text(sl,label,x,y+j*.82,w,.55,21,BLUE,bold=True,name='selected_reference',leading=1.15)
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

def reference(d,sl,r,y,index):
    x=.92;w=11.5;size=12.8;leading=1.67;indent=18;lines=[];line=[];used=0
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
    h=len(lines)*size*leading/72+.08
    if y+h>6.65:raise ValueError('APA source does not fit appendix')
    tx=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tx.name=f'APA_reference_{index}';tf=tx.text_frame;tf.clear();tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0;tf.word_wrap=False
    for j,line in enumerate(lines):
        p=tf.paragraphs[0] if j==0 else tf.add_paragraph();p.font.name=FONT;p.font.size=Pt(size);p.font.color.rgb=RGBColor.from_string(INK);p.line_spacing=Pt(size*leading);p.space_after=Pt(0);p.space_before=Pt(0)
        if j:p._p.get_or_add_pPr().set('marL',str(int(Pt(indent))))
        xx=x*72+(indent if j else 0);yy=H*72-y*72-size-j*size*leading
        for k,(word,italic,link) in enumerate(line):
            value=(' ' if k else '')+word;run=p.add_run();run.text=value;run.font.italic=italic
            if link:run.hyperlink.address=link;run.font.color.rgb=RGBColor.from_string(BLUE)
            font='CItalic' if italic else 'CNormal';d.pdf.setFont(font,size);d.pdf.setFillColor('#'+(BLUE if link else INK));d.pdf.drawString(xx,yy,value);amount=pdfmetrics.stringWidth(value,font,size)
            if link:d.pdf.linkURL(link,(xx,yy-2,xx+amount,yy+size),relative=0,thickness=0)
            xx+=amount
    d.checks.append({'slide':d.slide_index+1,'name':tx.name,'font_pt':size,'estimated_height_in':h,'box_height_in':h})
    return y+h+.32


def validate(prs,narrative,appendices,layout,pptx,pdf):
    assert len(prs.slides)==len(narrative)+len(appendices)
    assert len(narrative)==11 and sum(int(s['seconds']) for s in narrative)==780
    authored_words=[sum(len(clean(t).split()) for t in [s['title'],s.get('subtitle',''),*s['display_points'],s['takeaway']]) for s in narrative]
    assert max(authored_words)<=30,('Authored main-slide text exceeds30words',authored_words)
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
    return {'checks_passed':True,'main_slides':len(narrative),'appendix_slides':len(appendices),'total_slides':len(prs.slides),'planned_talk_seconds':780,'remaining_session_buffer_seconds':120,'main_text_editable':True,'authored_main_slide_word_counts':authored_words,'maximum_authored_main_words':max(authored_words),'matched_native_PDF_pages':True,'all_notes_nonempty':True,'bounds_and_font_metrics_checked':True,'no_photos_used':True,'live_GDELT_observations_generated':False,'desktop_PowerPoint_render_verified':False,'pptx_sha256':hashlib.sha256(pptx.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest()}


def main():
    narrative=json.loads((ROOT/'scripts/concise_narrative.json').read_text());appendices=json.loads((ROOT/'scripts/concise_appendices.json').read_text());refs={r['id']:r for r in json.loads((ROOT/'scripts/concise_references.json').read_text())};stats=json.loads((OUT/'IOC_YAPISAL_ANALIZ.json').read_text())
    OUT.mkdir(exist_ok=True);prs=Presentation();prs.slide_width=Inches(W);prs.slide_height=Inches(H);prs.core_properties.title='Meta 2022 CIB listesinde hedef coğrafyası ve alan adı yapısı';prs.core_properties.author='SUNUM';prs.core_properties.subject='Tamamlanmış Meta gösterge analizleri; 11 ana slayt, 13 dakika anlatım ve 2 dakika oturum payı.'
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
