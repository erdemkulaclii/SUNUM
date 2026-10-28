"""Readable speaker script, research dossier and APA 7 references; no invented results."""
from pathlib import Path
import json,re,html
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from docx import Document
from docx.shared import Pt,Cm,RGBColor
R=Path(__file__).resolve().parents[1];O=R/'output'
N=json.loads((R/'scripts/cinematic_narrative.json').read_text());A=json.loads((R/'scripts/academic_appendices.json').read_text());F=json.loads((R/'scripts/academic_references.json').read_text())
for name,file in [('Body','DejaVuSans.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf'),('BodyBold','DejaVuSans-Bold.ttf'),('Heading','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',italic='BodyItalic',bold='BodyBold',boldItalic='BodyItalic')
styles={
 'title':ParagraphStyle('title',fontName='Heading',fontSize=25,leading=32,textColor='#14263a',spaceAfter=20),
 'h':ParagraphStyle('h',fontName='Heading',fontSize=17,leading=23,textColor='#14263a',spaceBefore=15,spaceAfter=12,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=19,textColor='#26384b',spaceAfter=12),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.5,leading=14,textColor='#64788c',spaceAfter=10),
 'apa':ParagraphStyle('apa',fontName='Body',fontSize=9.5,leading=19,leftIndent=18,firstLineIndent=-18,spaceAfter=14,textColor='#26384b'),
}
def para(t,style='body',markup=False):return Paragraph(t.replace('&','&amp;') if markup else html.escape(t),styles[style])
def footer(c,d):
 c.setStrokeColorRGB(.65,.69,.59);c.line(48,43,547,43);c.setFont('Body',8);c.setFillColorRGB(.4,.45,.35);c.drawString(48,29,'GÖRÜNMEZ CEPHE · Akademik araştırma sunumu · 29 Ekim 2026');c.drawRightString(547,29,str(d.page))
def pdf(name,flow):SimpleDocTemplate(str(O/name),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=58,title='Görünmez Cephe — '+name.replace('_',' '),author='SUNUM').build(flow,onFirstPage=footer,onLaterPages=footer)
word=Document();section=word.sections[0];section.top_margin=Cm(2);section.bottom_margin=Cm(2);section.left_margin=Cm(2.3);section.right_margin=Cm(2.3)
normal=word.styles['Normal'];normal.font.name='Calibri';normal.font.size=Pt(12);normal.paragraph_format.line_spacing=1.5
word.core_properties.title='Görünmez Cephe — 15 dakikalık konuşma metni'
word.add_heading('Görünmez Cephe',0);word.add_paragraph('15 dakikalık akademik sunum — doğrudan okunabilir konuşma metni')
word_count=sum(len(x['notes'].split()) for x in N)
intro=f'18 ana sahne; planlanan toplam 900 saniye. Yaklaşık {word_count} sözcük. Gerçek süre konuşmacının hızına ve harita duraklamalarına bağlıdır; sunum öncesi prova yapılmalıdır. Köşeli sahne yönergeleri okunmaz. Güncel GDELT seçkisi, 2022 tarihsel karşılaştırmasının yerine geçmez.'
word.add_paragraph(intro)
flow=[para('Görünmez Cephe','title'),para('15 dakikalık akademik konuşma metni','h'),para(intro,'small')];elapsed=0
for i,s in enumerate(N):
 end=elapsed+s['seconds'];slot=f'{elapsed//60:02}:{elapsed%60:02}–{end//60:02}:{end%60:02}';heading=f'{i+1}. {s["title"]} | {slot}'
 flow += [para(heading,'h'),para(s['notes'])];word.add_heading(heading,1);word.add_paragraph(s['notes'])
 if s.get('cue'):
  cue='[Sahne yönergesi — okunmaz: '+s['cue']+']';flow.append(para(cue,'small'));p=word.add_paragraph(cue);p.runs[0].italic=True
 flow.append(para('Metin içi atıf: '+s['source'],'small'));word.add_paragraph('Metin içi atıf: '+s['source'],style='Caption')
 elapsed=end
flow += [PageBreak(),para('Savunma için kısa yanıtlar','title')]
for s in A[6:8]:
 flow.append(para(s['title'],'h'));flow += [para('• '+x) for x in s['bullets']]
word.add_page_break();word.add_heading('Savunma için kısa yanıtlar',0)
for x in A[6]['bullets']:word.add_paragraph(x)
flow += [PageBreak(),para('Kaynakça — APA 7','title')];word.add_page_break();word.add_heading('Kaynakça — APA 7',0)
for r in F:
 flow.append(para(r['apa']+' '+r['url'],'apa',True));p=word.add_paragraph();p.paragraph_format.left_indent=Cm(.635);p.paragraph_format.first_line_indent=Cm(-.635);p.paragraph_format.line_spacing=2
 italic=False
 for token in re.split('(<i>|</i>)',r['apa']+' '+r['url']):
  if token=='<i>':italic=True
  elif token=='</i>':italic=False
  elif token:p.add_run(token).italic=italic
flow.append(para('Erişim ve doğrulama düzeyleri AKADEMIK_KAYNAK_DENETIMI.md dosyasında açıklanır. Doğrudan incelenmeyen özgün çalışmaların erişim sınırı korunmalıdır.','small'))
pdf('KONUSMA_METNI_15_DK.pdf',flow);word.save(O/'KONUSMA_METNI_15_DK.docx')
abstract='Bu çalışma, Rusya bağlantılı olarak raporlanan bir koordineli sahte davranış vakasının yayımlanmış altyapı göstergelerini betimsel olarak inceler. Amaç, hedef coğrafyası ile haber görünürlüğünün kaynak ve konu coğrafyalarını ayıran izlenebilir bir OSINT tasarımı kurmaktır. Meta’nın 27 Eylül 2022 tarihli dosyasındaki 350 kayıttan 313 alan adı satırı seçilmiş; iki tekrar çıkarılarak 311 benzersiz alan adı elde edilmiştir. Hedef ülkeler, uzantı veya IP çıkarımı yerine kaynak etiketlerinden kodlanmıştır. Almanya 298, Birleşik Krallık 4, Fransa 2 ve İtalya 2 göstergeyle yer almaktadır. Almanya’nın bütün dosyadaki payı %95,8’dir. Bu oran operasyon sıklığını, kullanıcı maruziyetini veya kamuoyu etkisini ölçmez. Platformun tespit ve yayım seçimi dış geçerliliği sınırlar. GDELT DOC 2.0 için güncel otomatik sorgu, köken kaydı ve ayrı kaynak-ülke katmanı hazırlanmıştır; 2022 ile aynı dönemli GDELT karşılaştırması ve insan kodlaması henüz tamamlanmamıştır. Katkı, hedef–kaynak–konu ayrımı, kayıt düzeyinde tekrar üretim ve görsel kesinliğin veri çözünürlüğüyle sınırlandırılmasıdır.'
dossier=[para('Hibrit savaşın görünmez cephesi','title'),para('Araştırma soruları, yöntem ve savunma dosyası','h'),para('Özet','h'),para(abstract),para('Anahtar sözcükler: OSINT; dezenformasyon; GDELT; koordineli sahte davranış; coğrafi haritalama; kaynak eleştirisi.','small'),para('Bu belge tamamlanmış bir doktora tezi veya GDELT ile tamamlanmış tarihsel ampirik çalışma değildir. İleri akademik standartlara göre yapılandırılmış bir vaka sunumunun araştırma dosyasıdır.','small')]
for s in A:
 if s.get('reference_ids'):continue
 dossier.extend([para(s['title'],'h')]+[para('• '+x) for x in s['bullets']]+[para(s['notes'],'small'),para('Atıf: '+s['source'],'small')])
dossier += [PageBreak(),para('Kaynakça — APA 7','title')]
for r in F:dossier.extend([para(r['apa']+' '+r['url'],'apa',True),para(r['kind']+' · '+r['access'],'small')])
pdf('AKADEMIK_ARASTIRMA_DOSYASI.pdf',dossier)
pdf('APA7_KAYNAKCA.pdf',[para('Kaynakça — APA 7','title'),para('Kaynak türleri ve erişim düzeyleri: AKADEMIK_KAYNAK_DENETIMI.md. Kaynaklar alfabetik sıradadır.','small')]+[para(r['apa']+' '+r['url'],'apa',True) for r in F])
print('Exported speaker PDF + Word, academic research dossier, APA 7 bibliography.')
