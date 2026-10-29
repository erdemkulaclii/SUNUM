"""Current speaker cards, optional rehearsal text and completed-analysis dossier."""
from pathlib import Path
import html,json,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from docx import Document
from docx.shared import Pt,Cm,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from pypdf import PdfReader
R=Path(__file__).resolve().parents[1];O=R/'output';INK='#14263a'
for name,file in [('Body','DejaVuSans.ttf'),('BodyItalic','DejaVuSans-Oblique.ttf'),('BodyBold','DejaVuSans-Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Body',normal='Body',italic='BodyItalic',bold='BodyBold',boldItalic='BodyItalic')
ST={
 'title':ParagraphStyle('title',fontName='BodyBold',fontSize=24,leading=31,textColor=INK,spaceAfter=22),
 'h':ParagraphStyle('heading',fontName='BodyBold',fontSize=15,leading=21,textColor=INK,spaceBefore=16,spaceAfter=12,keepWithNext=True),
 'body':ParagraphStyle('body',fontName='Body',fontSize=11,leading=18,textColor=INK,spaceAfter=12),
 'cue':ParagraphStyle('cue',fontName='Body',fontSize=16,leading=27,textColor=INK,spaceAfter=22),
 'small':ParagraphStyle('small',fontName='Body',fontSize=8.5,leading=13,textColor='#4a5a6c',spaceAfter=10),
 'apa':ParagraphStyle('apa',fontName='Body',fontSize=9.5,leading=19,leftIndent=18,firstLineIndent=-18,textColor=INK,spaceAfter=18,splitLongWords=True),
 'cell':ParagraphStyle('cell',fontName='Body',fontSize=10,leading=15,textColor=INK)}
def para(value,style='body'):return Paragraph(html.escape(str(value)),ST[style])
def stamp(s):return f'{s//60:02}:{s%60:02}'
def footer(c,d):
 c.setStrokeColor(colors.HexColor('#bcc6d1'));c.line(48,43,547,43);c.setFont('Body',8);c.setFillColor(colors.HexColor('#4a5a6c'));c.drawString(48,29,'META 2022 CIB · Hedef coğrafyası ve alan adı yapısı');c.drawRightString(547,29,str(d.page))
def pdf(name,flow,title):SimpleDocTemplate(str(O/name),pagesize=(595.28,841.89),leftMargin=48,rightMargin=48,topMargin=48,bottomMargin=60,title=title,author='SUNUM').build(flow,onFirstPage=footer,onLaterPages=footer)
def reference(r):
 entry=r['apa'].replace('&','&amp;');url=html.escape(r['url'],quote=True)
 return Paragraph(entry+f' <link href="{url}" color="#174b78">{url}</link>',ST['apa'])
def references(refs,access=False):
 flow=[para('Kaynakça — APA 7','title')]
 for r in refs:
  parts=[reference(r)]
  if access:parts.append(para(r['kind']+' · '+r['access'],'small'))
  flow.append(KeepTogether(parts))
 return flow
def table(headers,rows,widths):
 t=Table([[para(x,'cell') for x in headers]]+[[para(x,'cell') for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9eef3')),('LINEBELOW',(0,0),(-1,0),.8,colors.HexColor('#7b8b9b')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d4dce4')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]));return t
def document(title):
 d=Document();s=d.sections[0];s.top_margin=s.bottom_margin=Cm(2);s.left_margin=s.right_margin=Cm(2.3)
 normal=d.styles['Normal'];normal.font.name='DejaVu Sans';normal.font.size=Pt(12);normal.font.color.rgb=RGBColor.from_string('14263A');normal.paragraph_format.line_spacing=1.4;normal.paragraph_format.space_after=Pt(12)
 for st in ['Title','Heading 1','Heading 2']:d.styles[st].font.name='DejaVu Sans';d.styles[st].font.color.rgb=RGBColor.from_string('14263A')
 d.core_properties.title=title;d.core_properties.subject='Tamamlanmış Meta IOC analizi; 11 ana slayt, 13 dakika anlatım ve 2 dakika oturum payı.';d.core_properties.author='SUNUM';return d
def hyperlink(p,text,url):
 link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True));run=OxmlElement('w:r');pr=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'174B78');pr.append(color);run.append(pr);tx=OxmlElement('w:t');tx.text=text;run.append(tx);link.append(run);p._p.append(link)
def word_refs(d,refs):
 d.add_page_break();d.add_heading('Kaynakça — APA 7',0)
 for r in refs:
  p=d.add_paragraph();p.paragraph_format.left_indent=Cm(.635);p.paragraph_format.first_line_indent=Cm(-.635);p.paragraph_format.line_spacing=2;italic=False
  for tok in re.split('(<i>|</i>)',r['apa']):
   if tok=='<i>':italic=True
   elif tok=='</i>':italic=False
   elif tok:p.add_run(html.unescape(tok)).italic=italic
  p.add_run(' ');hyperlink(p,r['url'],r['url'])
def main():
 O.mkdir(exist_ok=True);N=json.loads((R/'scripts/concise_narrative.json').read_text());F=json.loads((R/'scripts/concise_references.json').read_text());A=json.loads((O/'IOC_YAPISAL_ANALIZ.json').read_text());f,a,src=(A[k] for k in ['findings','audit','source'])
 assert len(N)==11 and sum(s['seconds'] for s in N)==780 and len(F)==6
 title='Meta 2022 CIB listesinde hedef coğrafyası ve alan adı yapısı'
 cueflow=[];md=[f'# {title}','','11 ana slayt · 13 dakika planlanan anlatım · 2 dakika soru ve geçiş payı.','','Bu dosya sunucu kartlarını içerir. Ayrıntılı prova metni KONUSMA_METNI_15_DK dosyalarındadır; ezberlenmesi veya aynen okunması gerekmez.','']
 cuedoc=document(title+' — Sunucu kartları');fullword=document(title+' — İsteğe bağlı prova metni');fullword.add_heading(title,0)
 intro='İsteğe bağlı prova metni. 15 dakikalık oturumun 13 dakikası anlatıma, 2 dakikası soru ve geçişlere ayrılmıştır. Metin, düşünce akışını çalışmak içindir; konuşma hızına göre prova edilerek kısaltılabilir. Sunum sırasında kısa sunucu kartları kullanılabilir.'
 fullword.add_paragraph(intro);fullflow=[para(title,'title'),para('İsteğe bağlı prova metni','h'),para(intro)];elapsed=0
 for i,s in enumerate(N):
  end=elapsed+s['seconds'];slot=f'{stamp(elapsed)}–{stamp(end)}';heading=f'{i+1:02d}. {s["title"]}';cues=s['cue_sentences'];assert 3<=len(cues)<=4
  if i:cueflow.append(PageBreak());cuedoc.add_page_break()
  cueflow += [para(f'SUNUCU KARTI {i+1:02d} / 11 · {slot}','small'),para(s['title'],'title')];cuedoc.add_paragraph(f'SUNUCU KARTI {i+1:02d} / 11 · {slot}',style='Subtitle');cuedoc.add_heading(s['title'],0)
  for cue in cues:
   cueflow.append(para(cue,'cue'));p=cuedoc.add_paragraph(cue);p.paragraph_format.space_after=Pt(20)
   for run in p.runs:run.font.size=Pt(16)
  cueflow += [Spacer(1,18),para('Ana mesaj: '+s['takeaway']),para('Atıf: '+s['source'],'small')];cuedoc.add_paragraph('Ana mesaj: '+s['takeaway']);cuedoc.add_paragraph('Atıf: '+s['source'],style='Caption')
  fullflow += [para(heading+' · '+slot,'h'),para(s['full_notes']),para('Atıf: '+s['source'],'small')];fullword.add_heading(heading+' · '+slot,1);fullword.add_paragraph(s['full_notes']);fullword.add_paragraph('Atıf: '+s['source'],style='Caption')
  md += [f'## {heading} · {slot}','']+['- '+x for x in cues]+['','**Ana mesaj:** '+s['takeaway'],'','**Atıf:** '+s['source'],''];elapsed=end
 md += ['## Oturum payı','','13:00–15:00: soru, geçiş ve süre tamponu. İleri araştırma slaydı, tamamlanmış GDELT bulgusu içermez.','']
 word_refs(fullword,F);fullflow += [PageBreak()]+references(F)
 pdf('SUNUCU_KARTLARI.pdf',cueflow,title+' — Sunucu kartları');cuedoc.save(O/'SUNUCU_KARTLARI.docx');pdf('KONUSMA_METNI_15_DK.pdf',fullflow,title+' — İsteğe bağlı prova metni');fullword.save(O/'KONUSMA_METNI_15_DK.docx');(O/'KONUSMACI_NOTLARI.md').write_text('\n'.join(md),encoding='utf8');pdf('APA7_KAYNAKCA.pdf',references(F,True),title+' — APA 7 kaynakça')
 abstract='Bu çalışma, Meta’nın 27 Eylül 2022 tarihli koordineli sahte davranış gösterge dosyasındaki alan adlarını hedef coğrafyası ve sözcüksel yapı bakımından betimsel olarak inceler. 350 ham kayıttan 313 alan adı satırı seçilmiş, iki yinelenen değer çıkarılarak 311 benzersiz alan adı elde edilmiştir. Almanya hedefli 298 alan adı listenin %95,8’ini oluşturur. En sık altı son DNS etiketi 240 alan adını (%77,2) kapsar ve bu kayıtların tamamı Almanya hedeflidir. 93 farklı ilk DNS etiketinden 75’i birden fazla son etiketle kullanılır; bu gruplar 293 alan adını kapsar. Katkı, hedef ülke yoğunlaşmasını ve adres yapısındaki tekrarları aynı kaynak kayıtları üzerinde yeniden üretilebilir biçimde birlikte göstermektir. Sonuçlar yayımlanan gösterge listesiyle sınırlıdır; operasyon sayısı, kullanıcı maruziyeti veya kamuoyu etkisi ölçülmemiştir.'
 dossier=[para(title,'title'),para('Araştırma dosyası — tamamlanmış veri analizi','h'),para('Özet','h'),para(abstract),para('Anahtar sözcükler: OSINT; koordineli sahte davranış; alan adı; DNS; hedef coğrafyası; kaynak eleştirisi.','small'),para('Araştırma sorusu','h'),para('Yayımlanmış bu gösterge listesinde hedef ülke etiketleri ile alan adlarının sözcüksel yapısı nasıl bir örüntü oluşturur?'),para('Kapsam ve kaynak atfı','h'),para('İnceleme, dosyanın alan adı alt kümesinin ikincil analizidir. Rusya bağlantısı kaynak raporlamasına dayanır; bağımsız aktör atfı yapılmaz. Dosyanın başlığında Çin ve Rusya birlikte geçmektedir; bulgular, incelenen alan adı kayıtlarıyla sınırlandırılır.')]
 dossier += [PageBreak(),para('Veri kökeni ve yeniden üretim','title'),reference(next(r for r in F if r['id']=='meta2022')),para('Sabit kaynak commit’i: '+src['commit'],'small'),para('Ham dosyanın SHA-256 özeti: '+src['sha256'],'small'),table(['Aşama','Kayıt sayısı'],[['Ham dosya',a['raw_records']],['Alan adı satırı',a['domain_rows']],['Çıkarılan tekrar',a['duplicate_rows_removed']],['Benzersiz alan adı',a['unique_domains']],['CIB bağlantısı (ayrı birim)',a['raw_record_types']['cib_url']],['Telegram bağlantısı (ayrı birim)',a['raw_record_types']['telegram_url']]],[360,139]),para('Tekilleştirme ve izlenebilirlik','h'),para('Alan adı dizilerinin çevresindeki boşluklar çıkarılır ve harfler küçültülür; tam dize eşitliğine göre tekilleştirilir. Tekrarlanan iki değer lnruzdeknn[.]online ve lrneuzdenken[.]online’dır. Hedef ülke etiketleri, kaynak yorum alanından alınır.'),para('Her gösterge için kaynak kayıt sırası ve fiziksel CSV satır sonu korunur. Yeniden üretim komutu: python scripts/analyze_ioc_structure.py. Hesaplamalar ağ isteği yapmaz. Kanıt dosyası: output/IOC_YAPISAL_KANIT.csv; toplu hesap: output/IOC_YAPISAL_ANALIZ.json.','small')]
 dossier += [PageBreak(),para('Ölçüm tanımları','title'),table(['Değişken','İşlemsel tanım'],[['Analiz birimi','Benzersiz, küçük harfe dönüştürülmüş tam alan adı dizisi.'],['Hedef ülke','Kaynağın yorum alanındaki açık hedef etiketi; DNS uzantısından veya IP adresinden çıkarılmaz.'],['Son DNS etiketi','Son noktadan sonraki tam metin; etkin genel son ek veya kaydedilebilir alan adı sınırı hesaplanmaz.'],['İlk DNS etiketi','İlk noktadan önceki tam metin; yalnız tam dize eşitliği kullanılır.'],['Çoklu son etiket grubu','Aynı ilk DNS etiketinin birden fazla farklı son DNS etiketiyle kullanıldığı grup.'],['ds tarihi','Kaynak kayıt tarihi. Faaliyet başlangıcı, tescil tarihi veya haber yayın tarihi olarak yorumlanmaz.']],[125,374]),para('Örnek ayrıştırma','h'),para('theguardian[.]co[.]com → ilk etiket: theguardian; ara etiket: co; son etiket: com. Bu kayıt son etiket tablosunda com kategorisindedir. dailymail[.]top → ilk etiket: dailymail; son etiket: top.'),para('Tanıdık bir dizeyle eşleşmek; yayıncı kimliğini, içerik taklidini, ortak mülkiyeti veya operatörü doğrulamaz. Fiyat ve barındırma ülkesi bu değişkenlerden ölçülmemiştir.')]
 c=f['target_country_counts'];labels={'Germany':'Almanya','UK':'Birleşik Krallık','France':'Fransa','Italy':'İtalya','Latvia':'Letonya','Ukraine':'Ukrayna','Multiple':'Çoklu hedef'}
 dossier += [PageBreak(),para('Bulgu 1 — hedef coğrafyası','title'),para('Almanya hedefli 298 alan adı, 311 benzersiz alan adının %95,8’ini oluşturur. Birleşik Krallık, Fransa ve İtalya birlikte sekiz; diğer üç kategori birlikte beş kayıt içerir.'),table(['Kaynak hedef etiketi','Alan adı','Pay (%)'],[[labels[k],c[k],f'{c[k]/311*100:.2f}'.replace('.',',')] for k in ['Germany','UK','France','Italy','Latvia','Ukraine','Multiple']],[290,100,109]),para('Yorum','h'),para('Bu dağılım, yayımlanan vakanın hedef etiketlerinde Almanya ağırlığını gösterir. Platformun tespit ve yayımlama seçimi ile gerçek faaliyet yoğunluğunun katkıları bu dosyayla ayrılamaz. Payda bütün listeyi oluşturan 311 benzersiz alan adıdır.'),para('Denetim dosyası: IOC_YAPISAL_KANIT.csv; kaynak: Meta (2022).','small')]
 dossier += [PageBreak(),para('Bulgu 2 — son etiket yoğunlaşması','title'),para('39 farklı son DNS etiketinden en sık altısı 240 alan adını kapsar: 240/311 = %77,2. Bu 240 kaydın tamamı kaynakta Almanya hedefli olarak etiketlenmiştir.'),table(['Son DNS etiketi','Alan adı','Pay (%)'],[[x['last_dns_label'],x['domain_count'],f"{x['share_percent']:.2f}".replace('.',',')] for x in f['top_six_last_dns_labels']],[290,100,109]),para('Yorum','h'),para('Hedef yoğunlaşmasına belirli son etiketlerin yoğun kullanımı eşlik eder. Buradaki ölçüm adres yapısına aittir; fiyat, barındırma ülkesi, tescil tarihi veya altyapı sahipliği incelenmemiştir.'),para('Tam dağılım: IOC_SON_ETIKET_DAGILIMI.csv. Ülke × son etiket çapraz tablosu: IOC_HEDEF_SON_ETIKET.csv.','small')]
 fam={r['first_dns_label']:r for r in A['first_label_families']}
 dossier += [PageBreak(),para('Bulgu 3 — ilk etiketin tekrarı','title'),para('311 alan adında 93 farklı ilk DNS etiketi bulunur. Bunların 75’i birden fazla son etiketle yer alır. Bu gruplar 293 adresi, yani listenin %94,2’sini kapsar. Kalan 18 grup tek bir alan adından oluşur.'),table(['İlk DNS etiketi','Alan adı','Farklı son etiket'],[[k,fam[k]['domain_count'],fam[k]['distinct_last_label_count']] for k in ['spiegel','bild','dailymail']],[260,110,129]),para('Yorum','h'),para('Adres çeşitliliğinin büyük bir bölümü yinelenen ilk etiketler çevresinde oluşur. Ölçüm, tam dize eşitliğine dayandığı için benzer yazımları birleştiren bir sınıflandırıcı içermez. Sözcüksel tekrar, ortak sahiplik veya operatör kanıtı olarak kullanılmaz.'),para('Tam 93 grup: IOC_GOVDE_AILELERI.csv. Her grubun üyeleri ve kaynak kayıt sıraları korunur.','small'),para('Sonuç','h'),para('Bu vaka, hedef etiketlerinde Almanya ağırlığı ve farklı son DNS etiketleri üzerinde yinelenen ilk etiketlerle tanımlanır. Çalışmanın katkısı, hedef coğrafyasıyla sözcüksel yapıyı aynı kayıt düzeyinde birlikte ve denetlenebilir biçimde göstermektir.')]
 dossier += [PageBreak(),para('Geçerlilik ve araştırma sınırları','title'),para('Seçilim ve genelleme','h'),para('Gösterge listesi olasılıklı bir operasyon örneklemi değildir. Bulgular, Avrupa’daki bütün operasyonlara veya toplumsal etkilere genellenmez. Alan adı sayısı; operasyon, içerik, kullanıcı veya maruziyet sayısıyla aynı ölçüm değildir (Allen et al., 2020).'),para('Zaman çözünürlüğü','h'),para('350 ham kaydın ve 311 benzersiz alan adının tamamında ds = 2022-09-27 bulunur. Bu alandan faaliyet zaman çizelgesi, büyüme eğrisi veya önce–sonra karşılaştırması üretilemez.'),para('Ad, içerik ve atıf','h'),para('Lazer ve arkadaşlarının (2018) haber biçimi ile doğrulama süreçlerini ayıran kavramsal tartışması, tanıdık adların neden dikkat çektiğini açıklamak için kullanılmıştır. Burada web içeriği, niyet ve kullanıcı etkisi kodlanmamıştır. Aktör bağlantısı Meta’nın raporlamasına ait olarak sunulur.'),para('İleri araştırma — GDELT','h'),para('GDELT ile ayrı bir haber görünürlüğü araştırması kurulabilir. 2022 vakası için aynı dönemi kapsayan tarihsel derlem ve açık kaynak kapsamı gerekir. Haber kaynağının ülkesi ile haberde anılan yerler ayrı değişkenler olmalıdır. Güncel haber seçkisi, 2022 karşılaştırmasının yerine geçmez. Bu karşılaştırma tamamlanmış bir sonuç olarak bu çalışmaya dahil edilmemiştir.'),para('Sunum planı','h'),para('11 ana slayt, 780 saniye (13 dakika) planlanan anlatım ve 120 saniye soru/geçiş payı. Ek tablolar ve tam kaynakça, ana anlatının dışında soru–cevap için tutulur.')]
 dossier += [PageBreak()]+references(F,True);pdf('AKADEMIK_ARASTIRMA_DOSYASI.pdf',dossier,title+' — Araştırma dosyası')
 report={}
 for name in ['SUNUCU_KARTLARI.pdf','KONUSMA_METNI_15_DK.pdf','APA7_KAYNAKCA.pdf','AKADEMIK_ARASTIRMA_DOSYASI.pdf']:
  reader=PdfReader(O/name);texts=[p.extract_text() or '' for p in reader.pages];assert all(len(t.strip())>40 for t in texts),(name,'empty page');report[name]={'pages':len(reader.pages),'text_selectable':True,'characters':sum(map(len,texts))}
 assert report['SUNUCU_KARTLARI.pdf']['pages']==11
 for name in ['SUNUCU_KARTLARI.docx','KONUSMA_METNI_15_DK.docx']:
  doc=Document(O/name);text='\n'.join(p.text for p in doc.paragraphs);assert all(s['title'] in text for s in N),name;report[name]={'all_11_sections_present':True,'paragraphs':len(doc.paragraphs)}
 report.update({'main_slides':11,'planned_talk_seconds':780,'session_buffer_seconds':120,'cue_sentence_count':sum(len(s['cue_sentences']) for s in N),'cue_word_count':sum(len(x.split()) for s in N for x in s['cue_sentences']),'rehearsal_word_count':sum(len(s['full_notes'].split()) for s in N),'selected_references':len(F),'desktop_Word_render_verified':False});(O/'ODAKLI_BELGE_DOGRULAMA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
