# Hibrit Savaşın Görünmez Cephesi

Rusya bağlantılı olarak raporlanan bir ağın yayımlanmış alan adı göstergeleri üzerine, gerçek OSINT verisine dayanan Türkçe araştırma sunumu.

[Sunum](output/PROFESYONEL_SUNUM.html) · [PowerPoint](output/PROFESYONEL_SUNUM.pptx) · [PDF](output/PROFESYONEL_SUNUM.pdf) · [Konuşma metni / Word](output/KONUSMA_METNI_15_DK.docx) · [Konuşma metni / PDF](output/KONUSMA_METNI_15_DK.pdf) · [APA 7 kaynakça](output/APA7_KAYNAKCA.pdf)

## Açılış

`output/PROFESYONEL_SUNUM.html` dosyasına çift tıklayarak Firefox/Chrome/Edge ile açın. Bu doğrudan açılışta harita dosyanın içindeki Natural Earth verisini kullanır; OpenStreetMap’e döşeme isteği göndermez. Harita, ülke seçimi ve fotoğraflar internet olmadan çalışır. GitHub HTML’yi çalıştırmaz; dosyayı indirin. F11 tam ekran; sağ/sol ok sahne; boşluk 15 dakikalık akış; N o sahnenin konuşma metni. Kaynakça ve konuşma metni üst menüde, sonuç ve kaynakça ayrıca ana sunumun son iki sahnesindedir.

**35 slayt:** 18 ana sahne, 17 yöntem/savunma/kaynakça eki. 900 saniye planlanan akıştır; gerçek konuşma süresi prova ile ölçülmelidir.

## Sunumun yazılı yapısı

Kapakta tam araştırma konusu ve **Akademik Araştırma Sunumu** ifadesi bulunur. 18 ana slaytın her biri bir sav taşıyan başlık, açıklayıcı bir giriş, üç tam cümle ve tek bir ana çıkarım içerir. Akış: araştırma problemi ve sorular → kavramsal çerçeve ve yöntem → gerçek ülke bulguları → GDELT karşılaştırma tasarımı → tartışma ve sonuç → kaynakça. Ülke örnekleri doğrudan ham gösterge kayıtlarından alınır.

[Özel düzenlenebilir PowerPoint](output/AKADEMIK_SUNUM_DUZENLENEBILIR.pptx), ana sunumun da temel PowerPoint sürümüdür. Konuşma metni 1.757 sözcüktür; 15 dakikalık plan, harita duraklamaları ve prova ile kullanılmalıdır. Slayt metinlerinin 1600×900 ve 1280×720 sunum görünümlerinde kesilmeden okunması ayrıca ölçülür: [okunabilirlik raporu](output/SUNUM_OKUNABILIRLIK.json).

## Harita

Harita motoru gerçek **Leaflet 1.9.4**; kütüphane ve lisansı dosyaya gömülüdür. Dosyaya çift tıklayarak açılan `file://` sürümü, gömülü **Natural Earth sınır haritasıyla** başlar. Ülke seçiminde gerçek enlem/boylama uçuş yapılır, fotoğraf penceresi coğrafi referansa bağlı kalır. Kaynak hedef ülkeleri ve GDELT kaynak coğrafyası ayrı katmanlardır.

**OpenStreetMap sokak/kent ayrıntıları için** kök klasörde `BASLAT.sh` çalıştırılabilir. Bu sunuculu HTTP sürümü, tarayıcının normal Referer bilgisiyle OSM standart döşemelerini ister. Erişimin kabul edilmesi OSM ve ağ koşullarına bağlıdır. Döşeme görüntülenmeden önce HTTP durumu ve görüntü içerik türü denetlenir. 403 veya başka bir erişim hatası gelirse çevrimiçi katman tamamen kaldırılır ve gömülü harita gösterilir; hata görselleri haritanın üzerine dizilmez. Haritada hangi tabanın kullanıldığı yazılıdır.

Ekrandaki eski “403 Access blocked” sorunu, reddedilmiş bir görüntünün yüklenmiş harita sanılmasından kaynaklanıyordu. Dosya açılışında OSM isteği göndermemek ve HTTP sürümünde yanıtı görüntülemeden denetlemek bu iki durumu ayırır. Başka sağlayıcıya veya aynaya geçerek erişim engeli aşılmaya çalışılmaz. Toplu döşeme indirmesi veya önceden önbellekleme yapılmaz. Bu bulut ortamında OSM erişimi engelli olduğundan statik PDF/PPTX/video çıktıları da etiketli gömülü sınır haritasıyla üretildi.

Kent işaretleri, fotoğrafların yer/kent referanslarıdır; kamera GPS veya operasyon konumu değildir. IOC verisi hedef ülke düzeyindedir. Fotoğraf kaynakları, lisanslar ve SHA-256: [konum künyesi](assets/locations/locations.json). Paris küçük resminin açık yeniden kullanım lisansı doğrulanmadı; CC0 diye etiketlenmez.

## GDELT Cloud ve verilen anahtar

Cloud, `https://gdeltcloud.com/api/v2` üzerinden **sunucu tarafında** çağrılır. `BASLAT.sh` veya `python scripts/serve_presentation.py` sunuculu sürümü açar. Anahtar `GDELT_API_KEY` çalışma ortamı değişkeninden veya mevcut özel, Git tarafından dışlanan `.env` uygulama yapılandırmasından okunur. Değeri HTTP, HTML, GitHub veya ZIP’e verilmez. Başka bir bilgisayara indirilen paket bu özel anahtarı taşımaz.

Sunucu en fazla 10 Event adayı içeren bir sayfa ister; pencere son 7 tamamlanmış UTC günüdür. Başarılı yanıt 6 saat, başarısız bağlantı 60 saniye saklanır. Her sayfa açılışında sürekli tarama yapılmaz. Yanıtın filtreleri, kayıt kimlikleri ve sayfalama bilgisi doğrulanır. Event kaydı gerçek dünyadaki bağımsız olay veya doğrulanmış dezenformasyon sayısı değildir. Yalnız yanıtta açıkça gelen geçerli koordinatlar haritalanır.

**Verilen anahtarla bu oturumda gerçek istek yapıldı. Ağ/proxy aşamasında engellendi; anahtarın geçerli veya geçersiz olduğu belirlenemedi.** Durum kaydı: [Cloud çalışma kaydı](output/GDELT_CLOUD_RUNTIME_STATUS.json). Sunucunun özel dosyaları dışarı açmadığı ayrıca sınandı.

Cloud sunucusu yoksa HTML ücretsiz **GDELT Project DOC 2.0** sorgusunu otomatik dener. Bu ayrı ürün anahtar gerektirmez. Son 30 günlük pencere UTC başlangıç/bitiş zamanlarıyla sabitlenir; en fazla 250 haber URL’si gelir. Kaynak ülke operasyon hedefi değildir. Önbellek özgün alım tarihiyle etiketlenir. Başarısız veya boş yanıttan gözlem uydurulmaz.

Mevcut bulut ortamının GDELT/OSM ağ izinleri henüz uygulanmış değil. Gerekli alan adları ve sunucu başlangıç talimatı ortam yapılandırma taslağına kaydedildi. Taslağın kaydedilmesi, çalışan ortamın ağ erişiminin açıldığı anlamına gelmez. Harita döşemelerinin düzeltilmesi, GDELT Cloud anahtarını veya canlı veri erişimini doğrulamaz; bunların bağlantı durumları ayrı tutulur.

## Araştırma ve sonuç

**Araştırma sorusu:** Rusya bağlantılı olarak raporlanan bu ağın yayımlanmış alan adı göstergeleri seçilen Avrupa ülkelerinde nasıl dağılıyor?

**Sonuç:** İncelenen 2022 listesinde yayımlanmış alan adı göstergeleri Almanya hedefli etiketlerde yoğunlaşmaktadır: 311 benzersiz göstergenin 298’i (%95,8). Bu vaka içi yoğunluk, bütün operasyonların dağılımını veya kamuoyu etkisini ölçmez.

Meta dosyası: 350 kayıt → 313 alan adı satırı → 311 benzersiz alan adı. İki tekrar çıkarıldı. Almanya 298, Birleşik Krallık 4, Fransa 2, İtalya 2; Letonya 3, Ukrayna 1, çoklu hedef 1. Hedef, `comment` alanındaki kaynak etiketidir. 22 CIB URL ve 15 Telegram URL alan adı sayımında kullanılmadı. Sabit commit ve dosya özeti [manifestte](output/veri_manifest.json) korunur.

Güncel API yanıtı, **2022 ile aynı dönemli GDELT karşılaştırması değildir**. Tarihsel haber karşılaştırması, bağımsız aktör atfı çapraz kontrolü ve iki kodlayıcılı içerik analizi henüz tamamlanmadı. Bu sürümde GDELT haber sayısı veya nedensel etki bulgusu raporlanmaz.

## Kaynaklar ve konuşma metni

14 kaynak APA 7 düzeninde; akademik araştırma, birincil veri, yazılım ve harita kaynakları ayrı türlerle gösterilir. Dört akademik metnin erişilebilir kopyası incelendi; diğer çalışmaların bibliyografik/tam metin erişim sınırları [denetim günlüğünde](AKADEMIK_KAYNAK_DENETIMI.md) açıklanır. Makale PDF kopyaları yeniden dağıtılmaz.

[Araştırma dosyası](output/AKADEMIK_ARASTIRMA_DOSYASI.pdf), [tam APA kaynakça](output/APA7_KAYNAKCA.md), [konuşmacı notları](output/KONUSMACI_NOTLARI.md) ve [kanıt tablosu](output/alan_adi_kanit_tablosu.csv) teslim edilir. Aynı konuşma metni PowerPoint notlarında bulunur. PowerPoint’in ana başlıkları, açıklamaları, üç maddelik anlatısı, çıkarım cümleleri, kaynakları ve bulgu grafikleri yerel, düzenlenebilir metin/şekillerdir. Harita sınırları ve gerçek bağlam fotoğrafları görsel olarak eklenir. PDF, aynı anlatının sabit sayfa çıktısıdır. PowerPoint masaüstü oynatma davranışı bu ortamda test edilmedi; tam etkileşim HTML sürümündedir.

## Yeniden üretim ve doğrulama

```bash
python -m pip install -r requirements.txt
MPLCONFIGDIR=/tmp/sunum-mpl XDG_CACHE_HOME=/tmp/sunum-cache python scripts/build_interactive.py
python scripts/render_cinematic_tour.py
python scripts/export_editorial.py
python scripts/export_academic_documents.py
python scripts/verify_leaflet.py
python scripts/verify_slide_readability.py --check-pptx
python -m unittest discover -s scripts -p 'test_*.py'
```

Tarayıcı çıktıları için `/usr/bin/chromium`, Playwright ve ffmpeg gerekir. Hazır HTML ve belgeler için Python kurulumu gerekmez. Leaflet tarayıcı testleri ve 12 istemci/sunucu testi geçti. Test API yanıtları **sentetiktir**; araştırma bulgusu veya dağıtılan HTML’nin başlangıç verisi değildir. [Tarayıcı denetimi](output/LEAFLET_DOGRULAMA.json) ve [gerçek erişim durumu](output/HARITA_BAGLANTI_DURUMU.json) ayrıdır.
