import csv, collections, hashlib, json, math, textwrap, zipfile
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
RAW=ROOT/'research'; META=RAW/'meta'
SOURCE=next((META/'indicators/csv').glob('2022_09*'))
rows=list(csv.DictReader(SOURCE.open(encoding='utf-8-sig')))
domain_rows=[r for r in rows if r['indicator_type']=='domain_name']
domains=list({r['indicator_value'].lower():r for r in domain_rows}.values())
counts=collections.Counter(r['comment'].split('-targeting')[0] for r in domains)
assert len(rows)==350 and len(domain_rows)==313 and len(domains)==311
countries={'Germany':('Almanya',10.5,51.1),'UK':('Birleşik Krallık',-2,54),
           'France':('Fransa',2.3,46.5),'Italy':('İtalya',12.6,42.6)}
with (OUT/'hedef_ulke_sayimlari.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['source_target_label','unique_domains','in_focus','unit'])
 for c,n in counts.items():w.writerow([c,n,c in countries,'published domain indicator'])
with (OUT/'alan_adi_kanit_tablosu.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['defanged_indicator','source_target_label','source_date','source_file'])
 for r in domains:w.writerow([r['indicator_value'].replace('.','[.]'),r['comment'],r['ds'],SOURCE.name])
BG='#0C1727'; PANEL='#17283D'; TEXT='#F1F5FA'; MUTED='#B0C2D4'; CYAN='#4DD8CD'; GOLD='#F5BB63'
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':TEXT,'axes.labelcolor':TEXT,
 'xtick.color':MUTED,'ytick.color':TEXT,'axes.edgecolor':PANEL,'figure.facecolor':BG,'axes.facecolor':BG})
geo=json.loads((RAW/'countries.geojson').read_text())
fig,ax=plt.subplots(figsize=(11,6)); targets={'Germany':'Germany','France':'France','United Kingdom':'UK','Italy':'Italy'}
for f in geo['features']:
 name=f['properties'].get('ADMIN'); geom=f['geometry']; polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
 for poly in polys:
  ax.add_patch(Polygon(poly[0],facecolor='#274052' if name in targets else '#18273A',edgecolor='#516279',linewidth=.45))
for c,(label,x,y) in countries.items():
 n=counts[c];ax.scatter(x,y,s=65+180*math.sqrt(n),color=CYAN,alpha=.72,edgecolor=TEXT,linewidth=.7,zorder=4)
 dx,dy={'Germany':(3.0,1.5),'UK':(-7.3,3),'France':(-8,-2.2),'Italy':(3.3,-1)}[c]
 ax.annotate(f'{label}\n{n} alan adı',(x,y),xytext=(x+dx,y+dy),fontsize=12,color=TEXT,
             arrowprops=dict(arrowstyle='-',color=MUTED),zorder=5)
ax.set_xlim(-15,29);ax.set_ylim(35,62);ax.set_aspect(1.4);ax.axis('off')
ax.text(0,-.02,'Semboller ülke temsil noktasıdır; sunucu, olay veya kullanıcı konumu değildir.',transform=ax.transAxes,color=MUTED,fontsize=10)
fig.savefig(OUT/'hedef_haritasi.png',dpi=180,bbox_inches='tight');plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5));labels=[v[0] for v in countries.values()]; vals=[counts[c] for c in countries]
bars=ax.barh(labels[::-1],vals[::-1],color=[CYAN,CYAN,CYAN,GOLD]);ax.set_xlim(0,335)
for b,n in zip(bars,vals[::-1]):ax.text(n+4,b.get_y()+b.get_height()/2,str(n),va='center',fontsize=17)
ax.set_xlabel('Yayımlanan benzersiz alan adı göstergesi');ax.spines[['top','right','left']].set_visible(False)
ax.tick_params(axis='y',length=0,labelsize=13);fig.tight_layout();fig.savefig(OUT/'alan_adi_dagilimi.png',dpi=180);plt.close(fig)

# One content model generates the PowerPoint, matching PDF, and speaker script.
S=[]
def add(title,kicker,bullets,notes,seconds=0,image=None,source='Yöntemsel değerlendirme',takeaway=None):
 S.append(dict(title=title,kicker=kicker,bullets=bullets,notes=notes,seconds=seconds,image=image,source=source,takeaway=takeaway))
add('Hibrit savaşın\ngörünmez cephesi','GDELT • RUSYA • BATI AVRUPA',[
 'Rusya’nın Batı Avrupa’ya yönelik dezenformasyon operasyonlarının coğrafi haritalanması',
 'Doppelganger vaka verisi ve GDELT ile ölçüm tasarımı',
 '15 dakikalık akademik sunum · 14 ana slayt + 7 ek',
 'VERİ DURUMU: Gerçek Meta OSINT analizi hazır. GDELT sonuçları erişim bekliyor.'
], 'Bugün görünmez cepheyi, yani haber ve platform ağlarında dolaşıma giren etki operasyonlarını tartışacağım. Temel sorum, Rusya bağlantılı olarak raporlanan ağların Batı Avrupa yönelimini coğrafi olarak nasıl inceleyebileceğimiz. Burada iki farklı kanıt türünü ayırıyorum: Meta tarafından yayımlanmış somut alan adı göstergeleri ve bu vakaların haberlerdeki görünürlüğünü ölçmek için tasarlanan GDELT katmanı. İlk katman gerçek verilerden hesaplandı. GDELT katmanı ağ erişimi nedeniyle henüz indirilmedi. Bu nedenle sunum, tamamlanmış bir GDELT bulgu raporu olarak değil, doğrulanabilir vaka analizi ve uygulanabilir araştırma tasarımı olarak okunmalıdır.',40,source='Meta IOC listesi [1–2]; GDELT sonuçları üretilmedi')
add('Asıl soru: Nerede, hangi kanıtla?','01 / ARAŞTIRMA PROBLEMİ',[
 'Soru: Yayımlanan operasyon göstergeleri hangi hedef ülkelerde yoğunlaşıyor?',
 'İkinci soru: Bu vakalar GDELT haber derleminde nerede ve ne zaman görünür oluyor?',
 'Analiz birimleri ayrı: alan adı göstergesi • haber URL’si • ülke etiketi',
 'Hipotez: Vaka göstergeleri ve haber görünürlüğü aynı coğrafi dağılımı vermeyebilir.'
], 'Bir coğrafi haritanın ikna edici görünmesi, doğru şeyi ölçtüğü anlamına gelmez. Bu çalışmada önce ölçülen nesneyi tanımlıyorum. İlk soruda birimimiz, yayımlanmış bir listede bulunan benzersiz alan adıdır. İkinci soruda birimimiz GDELT tarafından indekslenen haber URL’si olacaktır. Bir haberin Fransa hakkında olması, Fransa’daki bir kaynaktan yayımlanması ve Fransa’daki seçmenleri hedeflemesi farklı önermelerdir. Hipotezimiz bunların örtüşmek zorunda olmadığıdır. Dolayısıyla tek bir yoğunluk haritası yerine, kaynak konumu ve doğrulanmış hedef konumu için ayrı katmanlar gerekir. Bu ayrım, araştırmanın geçerliliğini belirler.',65)
add('Hibrit tehditten ölçülebilir vakaya','02 / KAVRAMSAL ÇERÇEVE',[
 'Hibrit tehdit: askerî olmayan araçların diğer baskı araçlarıyla birlikte kullanılması.',
 'Dezenformasyon: yanıltma amacı içeren içerik; her yanlış haber bu sınıfa girmez.',
 'FIMI: yabancı aktörlerle ilişkili, kasıtlı ve koordineli manipülasyon davranışları.',
 'CIB: Meta’nın koordineli sahte davranış sınıfı; tek başına içerik doğruluk etiketi değildir.'
], 'Hibrit savaş kavramını, her çevrim içi tartışmayı savaş faaliyeti sayacak kadar genişletmemek gerekir. Bu sunum, askerî sonuçları ölçmüyor; bilgi alanındaki manipülasyon mekanizmalarını inceliyor. Dezenformasyon içerikle ve yanıltma amacıyla ilgilidir. FIMI ise davranışın yabancı aktörlerle bağlantısı, koordinasyonu ve manipülatif niteliği üzerinde durur. Meta’nın CIB kategorisi de içerikteki her önermenin yanlış olduğunu söylemez; hesapların ve varlıkların davranışsal koordinasyonunu tanımlar. Bu nedenle IOC listesinde bulunmak ile bir haber metninin yanlışlığı ayrı ayrı doğrulanmalıdır. Operasyon düzeyindeki etiketleri otomatik olarak bütün kullanıcı ve haber kayıtlarına taşımıyoruz.',60,source='Kavramsal çerçeve; Meta README [2]. FIMI resmî kaynak doğrulaması bekliyor.')
add('Kanıt zinciri: Atıf → gösterge → haber','03 / TASARIM',[
 'A · Atıf: Birincil rapor aktör ve kampanya ilişkisini hangi gerekçeyle kuruyor?',
 'B · IOC: Yayımlanan alan adları, tarihler ve hedef etiketleri.',
 'C · GDELT: İndekslenmiş haberler; aktör atfını tek başına doğrulamaz.',
 'D · Elle kodlama: Hedef ülke, anlatı, alıntılama/çürütme ve belirsizlik.'
], 'Araştırmanın omurgası kanıt zinciridir. Aktör atfı için ilk adım platform veya kamu kurumu raporudur. İkinci adım, bu raporla ilişkilendirilen somut göstergeleri ve metaveriyi kaydetmektir. Üçüncü adım, GDELT üzerinde kampanya adı ve gerekirse doğrulanmış göstergelerle ilişkili haberleri aramaktır. Son adımda, haberin operasyonu yayması ile operasyonu eleştirmesini ayırırız. Burada önemli bir sınırlılık var: Meta veri dosyası indirildi ve kaynağı arşivlendi; atfı bağımsız kamu raporlarıyla çapraz doğrulama bu ortamda henüz tamamlanmadı. Bu nedenle Rusya atfını bizim keşfimiz gibi değil, kaynağın değerlendirmesi olarak sunuyoruz.',65,source='Meta veri dosyası, index.json ve README [1–3]')
add('Gerçek veri: 350 kayıt, 313 alan adı','04 / VERİ DENETİMİ',[
 'Kaynak: facebook/threat-research · resmî açık gösterge deposu.',
 'Dosya tarihi: 27 Eylül 2022. 350 satır = 313 alan adı + 22 CIB URL + 15 Telegram URL.',
 'Yalnızca domain_name kayıtları sayıldı; 311 benzersiz alan adı bulundu; 2 tekrar çıkarıldı.',
 'Dosya Çin ve Rusya vakalarını birlikte adlandırıyor: 2 “China: CIB Petition” kaydı alan adı analizine alınmadı.'
], 'Bu slayttaki bütün sayılar doğrudan indirilen CSV dosyasından hesaplandı. Dosyada toplam üç yüz elli kayıt bulunuyor. Bunların üç yüz on üçü alan adı satırı, yirmi ikisi CIB URL’si ve on beşi Telegram URL’sidir. Aynı alan adının tekrarını önlemek için küçük harfe dönüştürülmüş değerler üzerinde benzersizlik kontrolü yaptım. İki yinelenen alan adı çıkarıldı; üç yüz on bir benzersiz alan adı kaldı. Dosyanın başlığı hem Çin hem Rusya vakalarını içerdiği için başlığa bakarak bütün satırları tek operasyon saymadım. Özellikle Çin etiketli iki dilekçe URL’si, alan adı filtresinin dışında kaldı. Bu seçim kuralı ve ham veri dosyası teslim paketinde bulunuyor.',70,source='[1] CSV; [3] index.json. Ham dosya + SHA-256 teslim paketinde.')
add('Harita: Yayımlanan hedef etiketleri','05 / COĞRAFİ BULGU',[
 'Odak: Almanya, Fransa, Birleşik Krallık ve İtalya.',
 'Dört ülke, bu vakaya yönelik çalışma kapsamıdır; tüm Batı Avrupa’yı temsil etmez.',
 'Semboller kaynak dosyadaki hedef ülke etiketine dayanır.',
 'Sembol alanı sayıyla doğrusal ölçekli değildir; kesin değer etiketlerden okunmalıdır.'
], 'Haritada görülen noktalar alan adlarının sunucu koordinatları değildir. Kaynak dosyanın hedef ülke etiketlerini ülke düzeyindeki temsil noktalarında gösteriyorum. Böylece ağ altyapısının bulunduğu yer ile hedef kitlenin bulunduğu yeri karıştırmıyorum. Almanya, Fransa, Birleşik Krallık ve İtalya bu vaka için çalışma odağını oluşturuyor. İtalya ve Birleşik Krallık farklı coğrafi sınıflandırmalarda başka Avrupa alt bölgelerine yerleştirilebilir; bu yüzden kullandığım kapsamı açıkça operasyonel bir seçim olarak belirtiyorum. Harita yalnızca yayımlanmış göstergeleri içeriyor. İşaret bulunmayan başka ülkeler için operasyon olmadığı sonucuna varılamaz. Bu ülkelerde gözlemimiz bulunmaması ile gerçek dünyada faaliyet bulunmaması farklıdır.',75,image='hedef_haritasi.png',source='[1] Hedef etiketleri; [4] Natural Earth ülke sınırları')
add('Almanya yoğunluğu: Güçlü ama dar bulgu','06 / SAYISAL BULGU',[
 'Almanya 298 • Birleşik Krallık 4 • Fransa 2 • İtalya 2.',
 'Odak küme toplamı: 306 benzersiz alan adı.',
 'Almanya: tüm alan adı listesinin %95,8’i; odak kümenin %97,4’ü.',
 'Diğer: Letonya 3 • Ukrayna 1 • çoklu hedef 1. Bunlar odak toplamına alınmadı.'
], 'Grafik, yayımlanan listenin Almanya yönelimini çok açık gösteriyor. Ancak tam olarak hangi paydayı kullandığımızı belirtmeliyiz. İki yüz doksan sekiz alan adı, üç yüz on bir benzersiz alan adının yüzde doksan beş virgül sekizidir. Yalnızca odak ülkeleri kapsayan üç yüz altı kayıt içinde ise pay yüzde doksan yedi virgül dörttür. Bu oranlar seçilmiş bir gösterge listesinin kompozisyonunu anlatır. İki yüz doksan sekiz alan adı, iki yüz doksan sekiz ayrı operasyon demek değildir. Aynı ağ çok sayıda alan adını döndürebilir. Ayrıca Meta’nın tespit ettiği ve yayımlamayı seçtiği varlıklar bütün evreni oluşturmaz. Bu nedenle grafiği Avrupa’daki toplam dezenformasyonun ülkelere dağılımı olarak okumuyoruz.',75,image='alan_adi_dagilimi.png',source='[1] Yeniden hesaplanan değerler; hedef_ulke_sayimlari.csv')
add('Mekanizma: Haber markasının taklidi','07 / GÖSTERGEYİ OKUMAK',[
 'Örnek göstergeler: bild[.]pics • spiegel[.]ltd • dailymail[.]top.',
 'Fransa / İtalya örnekleri: 20minuts[.]com • repubblica[.]life.',
 'Tanıdık marka adı + farklı alan adı uzantısı, taklit şüphesi için incelenebilir.',
 'Dize benzerliği tek başına niyet veya aktör kanıtı değildir; örnekler kaynağın CIB etiketli listesindendir.'
], 'Alan adları, mekanizmayı somutlaştırıyor. Bild, Spiegel veya Daily Mail gibi tanınan haber markalarına benzeyen adlar, farklı uzantılarla kullanılıyor. Böyle bir tasarım, kullanıcının tanıdığı bir medya kuruluşunun güvenilirliğini ödünç alma girişimiyle tutarlıdır. Bununla birlikte yalnızca benzer bir ad görmek, tek başına koordinasyon veya Rusya atfı sağlamaz. Burada örnekleri zaten kaynak dosyada CIB göstergesi olarak listelendikleri için tartışıyoruz. Örnek alan adlarını güvenli biçimde, köşeli parantezli noktayla gösteriyorum; sunum sırasında bunları ziyaret etmek gerekmiyor. Özellikle güncel sahiplik, kapanma veya yeniden kayıt durumu bu tarihsel veri dosyasından çıkarılamaz.',65,source='[1] Örnekler doğrudan CSV kayıtları; güncel siteler ziyaret edilmedi.')
add('GDELT: Neyi ölçer, neyi söylemez?','08 / İKİNCİ VERİ KATMANI',[
 'DOC API: haber URL’si, başlık, kaynak alan adı, kaynak ülkesi, dil ve indeksleme zamanı.',
 'GKG: haber metninden çıkarılmış yerler, temalar ve diğer zenginleştirilmiş alanlar.',
 'Kaynak ülkesi ≠ metinde geçen ülke ≠ hedef ülke.',
 'GDELT satırı, otomatik olarak dezenformasyon örneği ya da doğrulanmış operasyon değildir.'
], 'GDELT dünya haberlerini tarayan bir veri altyapısıdır. Bu araştırma için DOC API üzerinden haber seçkileri, GKG üzerinden de haberlerde tanınan yerler ve temalar kullanılabilir. Fakat haberin kaynak ülkesi ile haberin konuştuğu ülke aynı değildir. Örneğin Birleşik Krallık merkezli bir yayın, Almanya’yı hedefleyen sahte haber ağını eleştiren bir haber yayımlayabilir. Böyle bir kayıt kaynak coğrafyasında Birleşik Krallık, olay veya konu coğrafyasında Almanya ile ilişkilendirilebilir. Hedef ülkeyi ise yalnızca bu iki alandan otomatik türetmek doğru olmaz. Ayrıca GDELT’in indeksleme zamanı, içeriğin ilk üretim veya operasyonun başlangıç zamanı olarak kabul edilmemelidir.',70,source='[5–6] Resmî GDELT dokümantasyon bağlantıları; canlı veri doğrulanmadı.')
add('GDELT sorgusu: Tekrarlanabilir protokol','09 / HENÜZ ÇALIŞTIRILMAMIŞ ANALİZ',[
 'Ad keşfi: Doppelganger / Doppelgänger / “Portal Kombat” / “Voice of Europe”.',
 'Sonra her kampanyayı ayrı derlemde, çok dilli eşanlamlılarla incele.',
 'Güncel keşif penceresi: 30 Temmuz–27 Ekim 2026 UTC; tarihsel 2022 incelemesi ayrı arşiv gerektirir.',
 'DOC artlist üst sınırı 250: tam sayım değildir. Ham yanıt + sorgu + indirme zamanı saklanır.'
], 'Önerdiğim sorgu önce kampanya adlarını kullanarak ilgili haberlere ulaşmayı amaçlıyor. Bu adlar aynı kampanyayı ifade etmediği için son analizde hepsini tek kategoriye yığmamak gerekir. Dil varyasyonlarını eklemek ve çıkan haberleri elle elemek gerekir. Teslim edilen betik DOC API için ham yanıtları ve sorgu metaverisini kaydedecek şekilde hazırlandı; fakat gerçek indirme henüz başarılmadı. Güncel keşif penceresi iki bin yirmi altı yılı içindedir. Bu pencereyi iki bin yirmi iki tarihli IOC sayımlarıyla doğrudan zaman karşılaştırmasına sokmuyoruz. İki bin yirmi iki için GKG arşivi veya BigQuery kullanmak gerekir. API’nin iki yüz elli haber sınırı tam evren sağlamaz.',70,source='scripts/fetch_gdelt.py; bu protokol henüz ampirik sonuç üretmedi.')
add('Üç harita, üç farklı değişken','10 / ANALİZ TASARIMI',[
 '1 · Operasyon hedefi: doğrulanmış rapordaki ülke etiketi → bugünkü gerçek vaka haritası.',
 '2 · Haber kaynağı: GDELT sourcecountry → haber görünürlüğünün üretim coğrafyası.',
 '3 · Anılan yerler: GKG konumları → haber metninin konu coğrafyası.',
 'İkinci ve üçüncü harita henüz üretilmedi; eksik veri sıfır olarak gösterilmez.'
], 'Tamamlanmış çalışmada üç ayrı harita sunmak istiyorum. Birinci harita hedef coğrafyasını gösterecek; bugün bu harita Meta’nın yayımladığı etiketlerle üretildi. İkinci harita GDELT’te ilgili haberleri yayımlayan kaynakların coğrafyasını gösterecek. Üçüncü harita haber metinlerinde anılan yerleri gösterecek. Bu üç haritanın birbirinden ayrılması, bir yerde fazla haber üretilmesinin o yerin daha çok hedeflendiği anlamına gelmediğini anlatacak. Veri eksikliği olduğunda ülkeyi sıfır değerle boyamak yerine veri yok olarak işaretlemek gerekir. Özellikle kaynak listesine alınmayan bir ülke için haritada beyaz alan bırakmak bile yanlış yorumlanabileceğinden, açıklama ve kapsam etiketleri gereklidir.',65)
add('Geçerlilik: Görünürlük, etki değildir','11 / SINIRLILIKLAR',[
 'Tespit ve yayım yanlılığı: platformun gördüğü alan, toplam operasyon evreni değildir.',
 'Haber yanlılığı: dil, yayın hacmi, erişilebilir kaynaklar ve tekrar basımlar.',
 'İfşa etkisi: operasyonu açığa çıkaran rapor, haber sayısını artırabilir.',
 'İkna / erişim / oy davranışı için GDELT dışında bağımsız ölçüm gerekir.'
], 'Çalışmanın en kritik sınırı, görünürlüğü etkiyle karıştırma riskidir. Bir operasyon hakkında çok haber çıkması, o operasyonun başarılı olduğu anlamına gelmez. Tam tersine, kapsamlı bir ifşa raporu haber hacmini yükseltmiş olabilir. Haberleri kaynak ülkenin toplam haber hacmine bölerek karşılaştırmak bazı hacim farklarını azaltır, ama dil ve indeksleme yanlılığını ortadan kaldırmaz. Meta listesinde de platformun tespit ve yayım süreçleri belirleyicidir. Kamuoyunun ikna edilip edilmediğini göstermek için anket, maruziyet verisi veya uygun araştırma tasarımı gerekir. Bu çalışmanın bugün savunabileceği iddia daha dardır: yayımlanmış göstergelerin ülke etiketleri ve gelecekte ölçülecek haber görünürlüğü.',70)
add('Bulgu, yorum ve açık kalan iş','12 / SONUÇ',[
 'BULGU: İncelenen 311 benzersiz alan adının 298’i kaynakta Almanya hedefli etiketlenmiş.',
 'YORUM: Liste, bu tarihsel vaka içinde güçlü Almanya yönelimi gösteriyor.',
 'SINIR: Bunu tüm Rus operasyonlarına veya toplumsal etkiye genelleyemeyiz.',
 'AÇIK İŞ: GDELT verisini indirmek, haberleri kodlamak ve atfı bağımsız birincil kaynaklarla çapraz doğrulamak.'
], 'Sonuçları üç düzeyde ayırarak bitiriyorum. Birinci düzey doğrudan veri bulgusudur: incelenen alan adı listesinde Almanya hedefli etiketler baskındır. İkinci düzey, bu listenin belirli bir vaka içindeki yönelimi gösterdiği yorumudur. Üçüncü düzey ise henüz desteklenmeyen iddialardır: bütün Rusya bağlantılı operasyonların dağılımı, hedef toplumdaki gerçek erişim ve kamuoyu etkisi bu veriyle hesaplanamaz. GDELT katmanı tamamlandığında, bu yönelimin haber görünürlüğüyle nasıl ilişkilendiği araştırılabilir. Ancak bugün bu ilişkiyi kurulmuş gibi sunmuyorum. Araştırmanın akademik değeri yalnızca bir harita üretmesinde değil, haritanın hangi kanıttan ve hangi sınırlılıkla üretildiğini göstermesindedir.',60)
add('Ana mesaj: Haritayı kanıtla birlikte okuyun','13 / KAPANIŞ',[
 'Hedef ülkeyi, haber kaynağını ve metindeki yeri birbirinden ayır.',
 'Alan adı sayısını operasyon veya etki sayısı olarak sunma.',
 'Her sayıyı ham kayda ve dönüşüm kuralına bağla.',
 'Sorular için eklerde: kodlama şeması, yöntem, kaynaklar ve veri denetimi.'
], 'Bu sunumdan kalmasını istediğim ana fikir şu: bilgi operasyonlarının haritasını çıkarmak yalnızca coğrafi veri bulmak değildir. Önce neresi sorusunun neyi ifade ettiğini belirlemek gerekir. Hedef ülke mi, kaynak ülke mi, haber metnindeki ülke mi? İkinci olarak sayılan şeyin ne olduğunu açık tutmalıyız: alan adı mı, haber mi, kullanıcı mı? Üçüncü olarak belirsizliği saklamamalıyız. Bugünkü analiz gerçek bir IOC dosyasına dayanıyor, fakat GDELT sonuçları tamamlanmış değil. Bu ayrımlara sadık kalındığında, hem daha dürüst hem de tekrar üretilebilir bir akademik araştırma kurulabilir. Ek slaytlar, veri ve yöntem sorularını ayrıntılandırıyor.',50)
add('EK A · Veri sözlüğü ve dönüşümler','EKLER / ANA SÜREYE DAHİL DEĞİL',[
 'indicator_type: yalnız domain_name. indicator_value: küçük harf + tekilleştirme (313 → 311).',
 'comment: hedef ülke kaynak etiketinden çıkarılır; uzantıdan ülke tahmin edilmez.',
 'ds: raporlanan gösterge tarihi; tescil veya faaliyet başlangıcı değildir.',
 'Multiple-targeting ayrı kategori; birden çok ülkeye yapay olarak çoğaltılmaz.',
 'Çıktılar: alan_adi_kanit_tablosu.csv ve hedef_ulke_sayimlari.csv.'
], 'Bir alan adını coğrafi olarak kodlamak için ülke uzantısını kullanmadım. Kaynağın açık hedef etiketi varsa onu aldım. Çoklu hedef etiketi ayrı tutuldu. Böylece kaynakta olmayan ayrıntı uydurulmadı.',source='[1]; scripts/build_presentation.py')
add('EK B · GDELT kodlama ve kalite kontrolü','HENÜZ UYGULANMADI',[
 'URL normalizasyonu: izleme parametrelerini ayır; özgün URL’yi koru; yönlendirmeleri denetle.',
 'Tekilleştirme: aynı URL + aynı yayın; ajans tekrarlarını ayrıca işaretle.',
 'Kodlar: kampanya • kaynak ülke • hedef ülke • anlatı • çürütme / aktarma / belirsiz.',
 'İki kodlayıcı: bağımsız kodlama, anlaşmazlık çözümü ve Cohen κ raporu.',
 'Görünürlük oranı = eşleşen haber / aynı kaynak-ülke ve dönem toplam indeksli haber; ikna oranı değildir.'
], 'Bu ek bir uygulanmış kalite raporu değil, önceden belirlenmiş protokoldür. Kodlayıcı sayısı ve uyum katsayısı gerçekleşmeden sonuç olarak yazılamaz. Dil bazlı hata ve kapsam ayrıca raporlanmalıdır.')
add('EK C · Tarihsel GDELT için doğru yol','2022 VAKASI İLE ZAMANSAL EŞLEŞME',[
 'DOC API’nin güncel arama penceresini 2022’ye uygulanmış gibi sunma.',
 'GKG 2.1 arşivi / BigQuery: önceden tanımlanmış tarih aralığı ve kaynak kapsamı.',
 'Örnek pencere: 20 Eylül–11 Ekim 2022; rapor çevresindeki haber görünürlüğü.',
 'İlk tarama: kampanya/rapor adları; ikinci tarama: doğrulanmış alan adı ve haber bağlantıları.',
 'Rapor tarihinin çevresindeki artış, operasyon başlangıcı veya nedensel etki kanıtı değildir.'
], 'Tarihsel eşleştirme yapılacaksa öncelikle aynı dönemden GKG veya başka yetkili arşiv verisi gerekir. Tek bir on beş dakikalık dosyayı indirip bütün ayı temsil ediyormuş gibi göstermek uygun olmaz. Tam kapsam mümkün değilse örneklem tasarımı açıkça belirtilmelidir.',source='[5–6]; tarihsel analiz henüz yürütülmedi.')
add('EK D · Jürinin sorabileceği sorular','KISA YANITLAR',[
 '“Rusya atfını siz mi yaptınız?” → Hayır. Kaynağın atfını aktarıyoruz; bağımsız çapraz doğrulama açık iş.',
 '“Neden Almanya bu kadar yüksek?” → Listede 298 benzersiz gösterge var; nedeni bu veri tek başına açıklamaz.',
 '“298 operasyon mu?” → Hayır, 298 benzersiz alan adı göstergesi.',
 '“GDELT sonuçları nerede?” → Erişim engeli nedeniyle henüz yok; sonuç diye sunulmuyor.',
 '“Batı Avrupa’nın tamamı mı?” → Hayır, dört ülkeli vaka odağı; genelleme yapılmıyor.'
], 'Zor sorular geldiğinde verinin cevaplamadığı bir soruya tahminle cevap vermeyin. Özellikle atıf, nedensellik ve etki sorularında kaynak türünü ve ölçüm birimini tekrar edin.')
add('EK E · Kaynakça: Erişilen kanıtlar','İNDİRİLEN VE İNCELENEN',[
 '[1] Meta. 2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv. ds: 2022-09-27.',
 '[2] Meta. Threat Research Indicators Repository, README ve lisans. github.com/facebook/threat-research',
 '[3] Meta. index.json: rapor tarihi 2022-09-27, eklenme tarihi 2022-10-11; birincil rapor bağlantısı.',
 '[4] Natural Earth. Admin 0 – Countries, 1:110m, GeoJSON; sınır taban haritası.',
 'Erişim: 28 Ekim 2026. Depo arşivi commit: 2d664e985e55fb754de7b1175f713e11f73cf8c8.'
], 'Aktif kaynak bağlantıları KAYNAKLAR.md dosyasında bulunuyor. Veri dosyaları yerel olarak teslim ediliyor. Meta verisi MIT lisansıyla, Natural Earth ise kamu malı olarak yayımlanmıştır. Kaynağın sonraki değişikliklerine karşı arşiv özeti ve dosya hashleri saklanmıştır.',source='Tam URL’ler ve SHA-256: KAYNAKLAR.md / veri_manifest.json')
add('EK F · Kaynakça: Erişim bekleyenler','BAĞLANTILAR BULGU YERİNE KULLANILMADI',[
 '[5] GDELT DOC 2.0 API: blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/',
 '[6] GDELT veri erişimi: www.gdeltproject.org/data.html ; data.gdeltproject.org/gdeltv2/',
 'Meta 27 Eylül 2022 raporu: index.json içindeki about.fb.com bağlantısı.',
 'Çapraz atıf için: VIGINUM, AB Konseyi / EEAS ve ABD Adalet Bakanlığı birincil belgeleri.',
 'Bu kaynakların canlı metinleri bu çalışma oturumunda doğrulanmadı; nicel veri çıkarılmadı.'
], 'Bu slayt, erişilmiş kaynakları erişilmemiş kaynaklarla karıştırmamak için ayrıdır. Resmî raporlar açılıp sayfa ve bölüm düzeyinde denetlenmeden onlardan yeni sayı veya kesin bulgu aktarılmamalıdır.')
add('EK G · Teslim ve tamamlanma durumu','ŞEFFAFLIK NOTU',[
 'HAZIR: gerçek ham veri, sayım betiği, hedef haritası, grafik, PPTX, PDF ve konuşma notları.',
 'ENGELLİ: GDELT indirme; ağ proxy’si api.gdeltproject.org için HTTP 403 döndürüyor.',
 'BEKLİYOR: bağımsız atıf doğrulaması, haber kodlama ve GDELT coğrafi sonuçları.',
 'Bu sürüm akademik vaka + yöntem taslağıdır; “GDELT ile tamamlanmış ampirik araştırma” değildir.'
], 'Sunumun kapsamı ve veri durumu her paylaşımda korunmalıdır. Ağ erişimi açılıp veri analizi yapılırsa bu slayt ve ana sonuç bölümü gerçek yeni bulgularla güncellenmelidir.')

assert len(S)==21
total=sum(s['seconds'] for s in S)
# Exact 15-minute schedule; rescale rounded slot allocations, retain final correction.
times=[round(s['seconds']*900/total) for s in S[:14]];times[-1]+=900-sum(times)
for s,t in zip(S,times):s['seconds']=t
prs=Presentation();prs.core_properties.title='Hibrit Savaşın Görünmez Cephesi: GDELT ile Araştırma Tasarımı';prs.core_properties.subject='Gerçek Meta IOC verisi; GDELT canlı sonuçları henüz yok';prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
pdfmetrics.registerFont(TTFont('DV','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DVB','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdf=canvas.Canvas(str(OUT/'SUNUM_15dk.pdf'),pagesize=(960,540))
def rgb(h):return RGBColor.from_string(h.lstrip('#'))
def rect(sl,x,y,w,h,color):
 sh=sl.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=rgb(color);sh.line.fill.background()
 pdf.setFillColor(color);pdf.rect(x*72,540-(y+h)*72,w*72,h*72,stroke=0,fill=1)
def txt(sl,text,x,y,w,h,size=20,color=TEXT,bold=False):
 box=sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));tf=box.text_frame;tf.word_wrap=True;tf.margin_left=0;tf.margin_right=0;tf.margin_top=0;tf.margin_bottom=0
 # Use identical line breaks in both formats and measured width for safe wrapping.
 lines=[]
 for original in text.split('\n'):
  current=''
  for word in original.split():
   test=(current+' '+word).strip()
   if pdfmetrics.stringWidth(test,'DVB' if bold else 'DV',size)>w*72 and current:
    lines.append(current);current=word
   else:current=test
  lines.append(current)
 for i,line in enumerate(lines):
  p=tf.paragraphs[0] if i==0 else tf.add_paragraph();p.text=line;p.font.name='DejaVu Sans';p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(0);p.line_spacing=1.15
 pdf.setFillColor(color);pdf.setFont('DVB' if bold else 'DV',size)
 for i,line in enumerate(lines):pdf.drawString(x*72,540-y*72-size-i*size*1.15,line)
 return len(lines)*size*1.15/72
for idx,s in enumerate(S):
 sl=prs.slides.add_slide(prs.slide_layouts[6]);rect(sl,0,0,13.333,7.5,BG);rect(sl,.45,.4,.08,.24,CYAN)
 txt(sl,s['kicker'],.7,.4,11,.4,11,CYAN,True)
 title_size=31 if idx==0 else 27
 txt(sl,s['title'],.7,.96,12,1.35,title_size,TEXT,True)
 y=2.45 if idx==0 else 2.03
 if s['image']:
  img=OUT/s['image']; sl.shapes.add_picture(str(img),Inches(5.1),Inches(2),width=Inches(7.6),height=Inches(4.6))
  pdf.drawImage(str(img),5.1*72,540-6.6*72,width=7.6*72,height=4.6*72,mask='auto')
  width=4.0;size=16
 else:width=11.8;size=20 if idx<14 else 17
 for b in s['bullets']:
  rect(sl,.72,y+.12,.065,.065,GOLD)
  height=txt(sl,b,1.0,y,width-.3,1.35,size)
  y+=height+.24
 if y>6.8:raise RuntimeError(f'Overflow slide {idx+1}: {y}')
 rect(sl,.7,6.95,11.9,.012,'#35465C')
 txt(sl,s['source'],.7,7.07,10.8,.28,8,MUTED)
 txt(sl,f'{idx+1:02d}',12.05,7.05,.5,.3,11,CYAN,True)
 sl.notes_slide.notes_text_frame.text=f"Süre: {s['seconds']} saniye\n\n{s['notes']}\n\nKaynak: {s['source']}"
 pdf.showPage()
prs.save(OUT/'SUNUM_15dk.pptx');pdf.save()
notes=['# Konuşmacı metni — 15 dakika','', 'Durum: Gerçek Meta IOC verisi analiz edildi; GDELT sonuçları henüz elde edilmedi. Bu not, sunumda korunmalıdır.','']
elapsed=0
for i,s in enumerate(S):
 if i<14:
  end=elapsed+s['seconds'];slot=f'{elapsed//60:02}:{elapsed%60:02}–{end//60:02}:{end%60:02}';elapsed=end
 else:slot='Soru-cevap eki'
 notes.extend([f"## {i+1}. {s['title'].replace(chr(10),' ')} · {slot}",'',s['notes'],'',f"Kaynak: {s['source']}",''])
(OUT/'KONUSMACI_NOTLARI.md').write_text('\n'.join(notes),encoding='utf8')
manifest={'download_date':'2026-10-28','meta_commit':'2d664e985e55fb754de7b1175f713e11f73cf8c8','gdelt_status':'NOT_DOWNLOADED_NETWORK_BLOCKED','counts':dict(counts),'files':{}}
for p in [SOURCE,RAW/'meta-threat-research.zip',RAW/'countries.geojson']:
 manifest['files'][str(p.relative_to(ROOT))]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
(OUT/'veri_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'slides':len(S),'main_slides':14,'seconds':elapsed,'rows':len(rows),'domains':len(domains),'counts':dict(counts)},ensure_ascii=False))
