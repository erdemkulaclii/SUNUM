# Hibrit Savaşın Görünmez Cephesi

[Etkileşimli atlas](output/GORUNMEZ_CEPHE_ATLAS.html) · [PowerPoint](output/ATLAS_SUNUMU.pptx) · [PDF](output/ATLAS_SUNUMU.pdf) · [GDELT Cloud bağlantısı](output/GDELT_CLOUD_BAGLANTI.md)

GitHub, HTML sunumunu doğrudan çalıştırmaz. Atlas dosyasını **Download raw file** ile indirip Chrome veya Edge ile açın. İndirme ZIP'leri ve eski sunum çıktıları Git geçmişine dahil edilmez; güncel atlas, PowerPoint, PDF, kaynak veriler ve üretim kodları depoda bulunur. Python bağımlılıkları `requirements.txt` içindedir; Chromium yalnız tarayıcı testleri ve görsel dışa aktarım için gerekir.

Türkçe, akademik, 15 dakikalık sunum paketi. **Bu sürüm tamamlanmış GDELT araştırması değildir.** Gerçek Meta gösterge verisinden üretilmiş vaka analizi ve GDELT araştırma tasarımıdır. Ağ erişimi açılmadan GDELT sonucu üretilmemiştir.

## Son sürüm: Sinematik konum dosyaları ve 18 sahnelik anlatı

Öncelikle `output/GORUNMEZ_CEPHE_ATLAS.html` dosyasını açın. Yeni baskıda kâğıt tonları, serif başlıklar, kaynak gösteren harita, veri temizleme ve kanıt zinciri diyagramları kullanılır. Güncel PowerPoint/PDF: `output/ATLAS_SUNUMU.pptx` ve `output/ATLAS_SUNUMU.pdf`. Eski sürümler arşiv için korunmuştur.

“GDELT verisini bağla” düğmesiyle kampanya ve dönem seçip doğrudan resmî DOC API’ye istek gönderilebilir. API anahtarı gerekmez. Mevcut ortamın GDELT erişimi hâlâ engelli; bu nedenle burada başarılı canlı indirme doğrulanmadı. Kullanıcının kendi tarayıcısındaki ağ/CORS koşulları da sonucu etkileyebilir. İstek başarısızsa resmî sorgu bağlantısını açıp kaydedilen JSON dosyasını içeri aktarma yolu vardır.

Gerçek API yanıtı geldiğinde haber URL’leri tekilleştirilir; kaynak ülkeleri mavi katmanda haritalanır. IOC hedefleri kırmızı katmanda kalır. İçe aktarılan dosya açıkça “kaynak bağımsız doğrulanmadı” etiketi alır. Yanıt, sorgu, dönem ve yükleme zamanı birlikte indirilebilir. Haberler otomatik dezenformasyon veya operasyon etiketi almaz. Arayüz testleri sentetik yanıtlarla yapıldı; bu yanıtlar sunumda veya araştırma bulgularında kullanılmadı.

Detaylar: `output/GDELT_API_REHBERI.md`.

## Sinematik sunum

Önce [SINEMATIK_SUNUM.html](output/SINEMATIK_SUNUM.html) dosyasını indirip Chrome/Edge ile açın. [PowerPoint](output/SINEMATIK_SUNUM.pptx), [PDF](output/SINEMATIK_SUNUM.pdf) ve [17 saniyelik harita turu](output/HARITA_TURU.mp4) aynı anlatımı tamamlar. 18 ana sahne, 8 ek; konuşmacı zaman planı tam 900 saniyedir.

Ülke seçildiğinde kamera gerçek bir yer/kent referansına yaklaşır. Fotoğraf kartı, SVG coğrafi işaretine bağlı kalır; sürükleme, yakınlaşma ve ekran boyutu değişiminde bağlantı çizgisi yeniden hesaplanır. Berlin/Potsdamer Platz, Londra/Adams Place Bridge, Paris/Eiffel Kulesi ve Venedik kıyısı için gerçek arşiv görselleri gömülüdür. “Ülke turu” 4 dosyayı sırayla açar. Sinematik ve açık atlas görünümleri arasında geçilebilir; azaltılmış hareket tercihleri korunur.

**Coğrafi kesinlik:** Koordinatlar yer işareti/kent referansıdır; kamera GPS konumu doğrulanmış değildir. Fotoğraflar operasyon anını veya operasyonun şehirde gerçekleştiğini göstermez. IOC verisi hedef ülke düzeyindedir. Künye, kaynak URL, işleme, lisans açıklaması ve SHA-256: [assets/locations/locations.json](assets/locations/locations.json). Paris görseli açık lisanslı diye etiketlenmez; kaynak galerinin küçük resmi ve telif künyesi korunur.

PowerPoint 26 slaytta yumuşak geçiş içerir; 6. slaytta döngüsel harita animasyonu bulunur. PowerPoint masaüstü oynatma davranışı bu ortamda test edilemedi; en kapsamlı etkileşim HTML sürümündedir. PDF statiktir. Video, tarihsel bir olay zaman çizelgesi veya gerçek zamanlı trafik değildir.

Yeniden üretim: `python scripts/prepare_location_assets.py`, `python scripts/build_interactive.py`, `python scripts/render_cinematic_tour.py`, `python scripts/export_editorial.py`. Tarayıcı çıktısı ve video için Chromium/Playwright ile ffmpeg gerekir. Hazır yerel JPEG varlıkları zaten depoda olduğundan yeniden indirme gerekmez. `python scripts/verify_cinematic.py`, fotoğrafın coğrafi işaretine piksel hizası, kanıt filtreleri, 18 sahne/900 saniye, mobil yerleşim ve sıfır başlangıç ağ isteğini denetler.

## Etkileşimli atlasın kullanımı

**Önerilen dosya: `output/CANLI_HARITA.html`.** İndirip Chrome veya Edge ile açın. Harita, veri, tasarım ve kod tek dosyada gömülüdür. İnternet veya sunucu gerektirmez. Başlangıçta dış ağ isteği yapılmaz. Kaynak bağlantıları ve yeni GDELT veri getirme düğmesi, kullanıcı tıkladığında ilgili dış servise bağlanır.

- Ülke sınırına, işaretine veya ülke düğmesine tıklayın: sayı, kaynak etiketi ve gerçek alan adı örnekleri açılır.
- “Kanıt kayıtlarını incele”: kaynak satırlarını arayın, ülke filtresi uygulayın, filtrelenmiş CSV indirin.
- Haritayı sürükleyin; + / − ile yakınlaşın. Konum simgesi görünümü sıfırlar.
- “Tüm hedef etiketleri”: Letonya ve Ukrayna da görünür. Çoklu hedef kaydı yapay bir konuma atanmaz.
- Ok tuşları: 18 anlatım sahnesi. Boşluk / oynat: toplam 15 dakikalık zamanlı ilerleme. Bu ilerleme veri zaman serisi değildir.
- “Sunum modu”: uygun tarayıcıda tam ekran. Escape ile çıkın. N ile konuşmacı notlarını açın.
- “Hareket açık/kapalı”: dekoratif ışıma ve geçişleri kapatır. Sisteminizin azaltılmış hareket tercihi de desteklenir.
- Alttaki 311 kare, 311 gerçek benzersiz alan adını temsil eder. Kareler coğrafi konum değildir.

`output/SUNUM_HAREKETLI.pptx`, 6. slaytta yaklaşık 7 saniyelik döngüsel harita GIF'i içerir. Hareketli GIF'in PowerPoint'te oynatılması sürüme bağlıdır; en güvenilir etkileşimli deneyim HTML dosyasıdır. Bu ortamda gerçek PowerPoint uygulamasında oynatma testi yapılamadı; GIF'in çok kareli olduğu ve PPTX'e gömüldüğü doğrulandı. PDF doğası gereği statiktir.

Tarayıcı kontrolleri, arama, filtreleme, CSV indirme, zamanlı ilerleme, mobil yatay taşma ve JavaScript hataları Chromium ile denetlendi. Sonuç: `output/ETKILESIM_DOGRULAMA.json`. Haritayı yeniden oluşturmak için `python scripts/build_interactive.py`; test, görsel ve hareketli PowerPoint üretmek için `python scripts/verify_interactive.py` kullanılır. İkinci komut Playwright, Chromium ve Pillow gerektirir.

Işımalar, renk geçişleri ve ülke odağı animasyonları yalnızca sunum vurgusudur. Gerçek zamanlı operasyon akışı, tarihsel hareket veya Rusya'dan ülkelere saldırı rotası gösterilmez. GDELT katmanında erişim engeli açıkça belirtilir; uydurma haber veya konum yoktur. Yeni sürümde kendi tarayıcından API isteği ve JSON içe aktarma desteklenir.

## Açılacak dosyalar

- `output/SUNUM_15dk.pptx`: düzenlenebilir PowerPoint; konuşmacı notları gömülü.
- `output/SUNUM_15dk.pdf`: aynı içeriğin taşınabilir sürümü.
- `output/KONUSMACI_NOTLARI.md`: 00:00–15:00 zaman planı ve Türkçe konuşma metni.
- `output/alan_adi_kanit_tablosu.csv`: tekilleştirilmiş, güvenli biçimde gösterilen 311 alan adı.
- `output/hedef_ulke_sayimlari.csv`: ülke sayımları.
- `output/veri_manifest.json`: ham dosyaların SHA-256 değerleri ve veri durumu.
- `KAYNAKLAR.md`: erişilen kaynaklar, doğrudan bağlantılar ve sınırlılıklar.

## Gerçek hesaplama

Meta'nın 27 Eylül 2022 tarihli dosyası 350 kayıt içerir. Bunlardan 313'ü alan adı satırıdır. İki tekrar çıkarıldığında 311 benzersiz alan adı kalır: Almanya 298; Birleşik Krallık 4; Fransa 2; İtalya 2; Letonya 3; Ukrayna 1; çoklu hedef 1. İlk dört ülkenin toplamı 306'dır. Yüzdeler yuvarlandığında Almanya tüm alan adlarının %95,8'ini, odak kümenin %97,4'ünü oluşturur.

İki tekrarlanan değer: `lnruzdeknn[.]online`, `lrneuzdenken[.]online`. Etiket çelişkisi yoktur. Hedef ülkeler kaynak dosyanın `comment` alanından alınır; IP adresi, ülke uzantısı veya haber metninden tahmin edilmez. Kaynakta listelenmemiş ülke için sıfır faaliyet iddia edilmez.

Liste bir platformun yayımladığı gösterge seçkisidir. Sayılar, operasyon sayısı, haber sayısı, erişilen kullanıcı veya ikna etkisi değildir. Rusya atfı kaynak raporlamasına aittir; bu paket bağımsız aktör atfı gerçekleştirmez. Dosya adı Çin ve Rusya vakalarını birlikte içerir; iki açık Çin dilekçesi URL'si alan adı analizine dahil edilmez. Alan adı analizi kendi başına hangi operatörün her bir alan adını yönettiğini kanıtlamaz.

## Yeniden üretim

Çalışma dizini: `/workspace/SUNUM`. Mevcut checkout kullanılır; kullanıcı istemedikçe yeni Git worktree oluşturulmaz.

Gereken Python paketleri: python-pptx, matplotlib, reportlab. Kaynak verileri zaten `research/` altında arşivlidir; yeniden indirme gerekmez.

```bash
cd /workspace/SUNUM
MPLCONFIGDIR=/tmp/sunum-mpl XDG_CACHE_HOME=/tmp/sunum-cache python scripts/build_presentation.py
```

Bu komut ham CSV'yi tekrar okur, tekilleştirir, iki CSV çıktı, iki görsel, PDF, PPTX, konuşmacı metni ve manifesti oluşturur. Harita, Natural Earth açık sınır verisini kullanır. Başlık, kaynak ve dipnotların taşması betikte denetlenir. PDF ile PPTX aynı içerik modelinden üretilir.

## GDELT için açık işler

Gerçek ağ testi: `api.gdeltproject.org` erişiminde proxy `HTTP 403 Forbidden` döndürdü. TLS doğrulaması kapatılmadı, ağ politikası aşılmadı, yapay yanıt veya örnek veri gerçekmiş gibi kullanılmadı. Ortamın bağlı olduğu süreçte GitHub indirmeleri başarılıdır.

Gerekli alan adları ortam ayar taslağına kaydedildi. Taslak kaydı tek başına çalışan ortama ağ erişimi sağlamaz. Ayarlarda gözden geçirip kaydetmek ve ortamı yayımlamak gerekir. Güncel keşif için:

```bash
python scripts/fetch_gdelt.py --start 20260730000000 --end 20261027235959
```

Betik gerçek DOC yanıtını doğrular ve ham JSON ile sorgu/tarih/hash metaverisini saklar. İndirme başarısızsa sonuç üretmeden hata verir. Bu betik yanıt şemasına ve gerçek ağ hatasına karşı sınandı; **başarılı canlı indirme henüz doğrulanmadı**. Artlist en fazla 250 sonuç döndürdüğü için tam evren sayımı değildir. Bu genel keşif sorgusu kampanya adı, dil ve konu yönünden elle doğrulama gerektirir. Her kampanya ayrı analiz edilmeli; sonuçlar doğrudan tek Rusya operasyonu kategorisine yığılmamalıdır.

Tarihsel 2022 vaka eşleştirmesi için DOC güncel penceresi yerine GKG arşivi veya BigQuery gerekir. 2026 keşif verisi, 2022 IOC sayımlarının aynı dönemli doğrulaması değildir. GDELT verisi geldiğinde haberleri kodlamak, tekilleştirmek, kaynak ve hedef ülkelerini ayırmak, uygun payda ile görünürlüğü hesaplamak ve yeni sonuç slaytları üretmek gerekir. Mevcut sunum GDELT verisi geldi diye kendiliğinden güncellenmez.

Çapraz atıf için Meta'nın asıl 2022 raporu ve bağımsız resmî belgeler canlı olarak okunup bölüm/sayfa düzeyinde doğrulanmalıdır. Erişilemeyen belgelerden sayı aktarılmadı. Açık işler tamamlanmadan sunumun “GDELT sonuçları yok” notu kaldırılmamalıdır.
