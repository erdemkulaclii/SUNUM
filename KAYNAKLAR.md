# Kaynak ve kanıt kaydı

Bu sürümün nicel bulguları yalnız aşağıdaki sabit Meta CSV dosyasının yeniden analizinden gelir. Rusya bağlantısı kaynak raporlamasına aittir; bağımsız aktör atfı yapıldığı ileri sürülmez. Kullanılan on iki kaynağın APA 7 künyeleri [kaynakçada](output/APA7_KAYNAKCA.md) bulunur.

## Birincil veri ve yeniden üretim

**Meta, 27 Eylül 2022 gösterge CSV’si:**
https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv

- Yerel kopya: `research/meta/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv`.
- Sabit commit: `2d664e985e55fb754de7b1175f713e11f73cf8c8`.
- SHA-256: `9f216a37e15c4772019d20ee620eafabf57a3876d4a7ab72fff5330fa8167d8d`.
- Kullanılan alanlar: `indicator_type`, `indicator_value`, `comment`, `ds`.
- 350 ham kayıt → 313 `domain_name` satırı → 311 küçük harfle tekilleştirilmiş tam alan adı. İki yinelenen değer çıkarılır; 22 CIB ve 15 Telegram URL’si alan adı paydasına eklenmez.
- Hedef ülke, kaynak yorum alanındaki etikettir. İlk/son DNS etiketi, alan adı dizesinin ilk/son noktayla ayrılan parçasıdır; public suffix veya tescil sınırı hesaplanmaz.
- Bütün 350 kaydın `ds` değeri `2022-09-27`’dir. Bu alan faaliyet takvimini veya zaman içindeki değişimi göstermez.

[Analiz betiği](scripts/analyze_ioc_structure.py), dosya özetini doğrular ve hedef dağılımını, son etiket dağılımını, ülke × son etiket tablosunu ve tam ilk etiket eşleşmelerini yeniden hesaplar. [Analiz JSON’u](output/IOC_YAPISAL_ANALIZ.json) yöntem ve sınırları; [kanıt CSV’si](output/IOC_YAPISAL_KANIT.csv) kaynak kayıt sıra numaralarını korur.

Kaynak deponun README ve MIT lisansı da yerel Meta arşivinde korunur. Kaynak `index.json`, ilgili öğe için `reported_ds=2022-09-27` ve `added_ds=2022-10-11` bildirir. Gösterge tarihi ile depoya eklenme tarihi birbirinden ayrıdır. Kaynak rapor bağlantısının varlığı, rapor metninin incelendiği anlamına gelmez.

## Akademik metinlerin kullanım düzeyi

**Allen et al. (2020), “Evaluating the fake news problem at the scale of the information ecosystem.”** https://doi.org/10.1126/sciadv.aay3539

Erişilebilir makale metni incelendi; başlık, yazarlar, yayın bilgileri ve DOI karşılaştırıldı. Sunumda payda, kapsam ve altyapı göstergesinden maruziyet/etki sonucuna geçmeme ayrımı için kullanılır. Makalenin kendi ampirik sonuçları bu vakaya aktarılmaz.

**Lazer et al. (2018), “The science of fake news.”** https://doi.org/10.1126/science.aao2998

Erişilebilir yazar sürümü incelendi. Bu kopyadaki dizgi öncesi sayfa yer tutucuları nedeniyle nihai cilt/sayfa bilgileri Allen et al. (2020) kaynakçasıyla karşılaştırıldı. Haber adı veya biçimi ile doğruluk süreçlerinin ayrılması için kavramsal destek sağlar; listedeki alan adlarının içerik incelemesinin yerine geçmez.

Geçmiş geniş kaynak taramasının ayrıntılı erişim günlüğü [AKADEMIK_KAYNAK_DENETIMI.md](AKADEMIK_KAYNAK_DENETIMI.md) dosyasındadır. O günlükte bulunmak, bir çalışmanın bu sürümde kullanıldığı anlamına gelmez. Okunmayan veya mevcut analizle ilişkisi kalmayan çalışmalar seçilmiş kaynakçaya taşınmadı.

## Kartografik veri ve yazılım

**Natural Earth — Admin 0 Countries, 1:110m.**
https://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/

Kamu malı sınır verisinin GeoJSON kopyası `research/countries.geojson` içindedir; kullanılan dosyanın özeti veri manifestinde bulunur. Veri `nvkelso/natural-earth-vector` deposundaki `ne_110m_admin_0_countries.geojson` kopyasından alınmıştır. Harita geometrisi operasyon veya sunucu konumu kanıtı değildir.

**Leaflet 1.9.4.** https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4

JavaScript/CSS dosyaları yerel olarak gömülüdür. BSD-2-Clause lisansı `assets/vendor/LEAFLET_LICENSE.txt` dosyasında korunur. Leaflet bir harita yazılımıdır; ampirik bulgu kaynağı değildir.

**OpenStreetMap.** https://www.openstreetmap.org/copyright

İsteğe bağlı HTTP atlasında standart `tile.openstreetmap.org` döşemeleri yapılandırılmıştır. Canlı erişim ağ koşullarına bağlıdır; başarısız yanıtlar harita olarak gösterilmez. Dosyaya doğrudan açılışta döşeme isteği gönderilmez. Harita atfı görünürdür. OSM, IOC bulgularının kaynağı değildir.

Yeni sunum ve dağıtım için kent fotoğrafı kullanılmaz. Önceki Paris küçük resminin açık yeniden kullanım lisansı doğrulanmadığından görsel yeni teslimata alınmadı.

## GDELT: ileri araştırma

2022 ile aynı dönemli GDELT haber analizi tamamlanmadı. Haber sayımı, tarihsel kaynak ülke dağılımı, kodlayıcı uyumu veya kamuoyu etkisi sonucu raporlanmaz. Güncel DOC sorgusu geçmiş 2022 dönemi için doğrulama oluşturmaz; GKG’de anılan yerler de otomatik olarak yayıncı ülkesi sayılmaz.

Teknik başvuru adresleri, seçilmiş ampirik kaynakçadan ayrıdır:

- GDELT DOC 2.0: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- Veri erişimi: https://www.gdeltproject.org/data.html
- GKG arşivi: https://data.gdeltproject.org/gdeltv2/

Önceki bağlantı araçları korunur; başarılı canlı alım doğrulanmadı. Ana sunum bu araçlara bağımlı değildir. Testlerdeki sentetik yanıtlar teknik doğrulama içindir ve bulgulara eklenmez.

## Çıkarım sınırı

Bu liste, yayımlanmış göstergelerin dağılımını gösterir. Alan adı sayısı operasyon sayısı değildir; hedef etiketi maruziyet veya ikna oranı değildir; son DNS etiketi fiyat veya barındırma ülkesi değildir; aynı ilk etiket ortak sahiplik veya operatör kanıtı değildir. Kaynakta yer almayan ülkeler için faaliyet yokluğu sonucu çıkarılamaz.


## 31 Ekim 2026 revizyonunda eklenen kaynaklar

Aşağıdaki künyeler yayıncı sayfaları ve bağımsız ikincil kayıtlarla bibliyografik olarak karşılaştırıldı. Bu bulut ortamından disinfo.eu ve about.fb.com tam metinlerine erişilemedi; sunumda yalnız künyede ve özetlerde doğrulanan genel bilgiler kullanılır. Sunumdan önce tam metinlerin okunması önerilir.

- **Alaphilippe, Machado, Miguel ve Poldi (2022), EU DisinfoLab** — kampanyanın en az Mayıs 2022’den beri sürdüğü; en az 17 medya markasının (ör. Bild, The Guardian, ANSA) taklit edildiği. https://www.disinfo.eu/doppelganger/
- **Nimmo ve Agranovich (2022), Meta** — Rusya kaynaklı ağın öncelikle Almanya’yı, ayrıca Fransa, İtalya, Ukrayna ve Birleşik Krallık’ı hedeflediği; 60’tan fazla taklit haber sitesi çevresinde kurulduğu. Not: yazarlar Ben Nimmo ve David Agranovich’tir.
- **Wardle ve Derakhshan (2017), Council of Europe DGI(2017)09** — bilgi düzensizliği çerçevesi (ajan/mesaj/yorumlayıcı; oluşturma/üretim/dağıtım).
- **Leetaru ve Schrodt (2013), ISA** — GDELT veri kümesinin tanıtımı.
- **Hammond ve Weidmann (2014), Research & Politics 1(2), doi:10.1177/2053168014539924** — GDELT’in elle kodlanmış verilerle karşılaştırılması; otomatik konum kodlamasının doğrulama gerektirdiği. Makalenin sayısal doğruluk oranları sunumda aktarılmaz.
- **The GDELT Project (2017), DOC 2.0 API** — artlist modu ve `sourcecountry` alanı; resmî destek son üç aydır.

## GDELT haber verisi

GDELT gözlemleri depoya ancak gerçek bir yanıt alındığında `research/gdelt/GDELT_HARITA_VERISI.json` olarak girer (bkz. `scripts/fetch_gdelt_map.py`). Her dilim için uç nokta, zaman damgası, dönen makale sayısı, 250 sınırına ulaşıp ulaşmadığı ve ham yanıtın SHA-256 özeti saklanır. Bu revizyon hazırlanırken çalışma ortamının ağ politikası `api.gdeltproject.org` erişimini engellediği için depoda GDELT anlık görüntüsü yoktur; sunumda GDELT sayısı uydurulmaz.

## 31 Ekim 2026 (ikinci revizyon): ham GDELT arşivi ve ek akademik kaynaklar

**GDELT verisi artık API’den değil, akademik çalışmalarda kullanılan ham GKG 2.0 arşivinden gelir.** `scripts/gdelt_gkg_archive.py`, 20 Eylül – 11 Ekim 2022 arasındaki bütün 15 dakikalık İngilizce ve çeviri (translingual) GKG dosyalarını GDELT’in Google Cloud Storage aynasından indirir. Her dosya, GDELT’in `masterfilelist.txt` ve `masterfilelist-translation.txt` içinde yayımladığı **boyut ve MD5** değerleriyle karşılaştırılır; uyuşmayan dosya sayıma girmez ve manifestte hata olarak kalır. Kaynak ülke, GDELT’in 2018 alan adı–ülke dosyasından (SHA-256 manifestte) alınır.

Eşleşme kuralları sabittir ve birim testleriyle korunur:
- **R1 (kampanya adı):** başlık/URL’de “doppelgänger” yazımlarından biri **ve** Rusya bağlamı (başlık/URL’de Rusya terimi ya da makalenin GKG konumlarında RS).
- **R2 (kaldırma haberi):** başlık/URL’de Meta/Facebook/Instagram **ve** Rusya terimi **ve** ağ/sahte/dezenformasyon/propaganda/kaldırma terimlerinden biri (çok dilli).

Kuralların isabeti `scripts/gdelt_validation.py` ile sabit tohumlu (2022) rastgele örneklemde ölçülür; birinci kodlama yapay zekâ destekli ön kodlamadır ve ikinci (insan) kodlayıcı sütunu bırakılmıştır.

Eklenen hakemli/kurumsal kaynaklar (künyeler web aramasıyla doğrulandı; tam metinler bu ortamda okunmadı):
- Wang, Kennedy, Lazer ve Ramakrishnan (2016), *Science* 353(6307) — GDELT/ICEWS olay kodlamasının geçerlilik sorunları; bu çalışmadaki isabet denetiminin gerekçesi. DOI doğrulanamadığından yazar kopyası bağlantısı verildi.
- Kwak ve An (2014), SocInfo, doi:10.1007/978-3-319-13734-6_22 — GDELT ile haber coğrafyası; bölgeselcilik.
- Bennett ve Livingston (2018), *European Journal of Communication* 33(2), doi:10.1177/0267323118760317 — dezenformasyonun “haber ya da taklit belgesel biçimleri” tanımı.
- Freelon ve Wells (2020), *Political Communication* 37(2) — dezenformasyon bir siyasal iletişim olgusu olarak.
- Auswärtiges Amt (2024) teknik raporu — Almanya’nın kampanya hedefi olmayı sürdürdüğü.
- The GDELT Project (2018) alan adı–ülke eşleştirme belgesi ve GKG 2.0 veri kümesi.
