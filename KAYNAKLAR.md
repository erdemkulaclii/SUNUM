# Kaynak ve kanıt kaydı

Erişim tarihi: 28 Ekim 2026. Ampirik veri yalnızca indirilen dosyalardan üretilmiştir. Aşağıdaki kaynakların kurumsal niteliği, aktör atfını bağımsız olarak doğruladığımız anlamına gelmez.

## İndirilen ve incelenen

1. **Meta, 27 Eylül 2022 gösterge CSV'si.** Sabit commit bağlantısı: https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv
   - Yerel kopya: `research/meta/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv`.
   - Kullanılan alanlar: `indicator_type`, `indicator_value`, `comment`, `ds`.
   - Bu dosya hedef ülke etiketleri ve göstergeler için doğrudan kanıttır; toplam operasyon evreni ve kamuoyu etkisi için değildir.
2. **Meta Threat Research Indicators README ve MIT lisansı.** https://github.com/facebook/threat-research/tree/2d664e985e55fb754de7b1175f713e11f73cf8c8
   - README, göstergelerin internetin bütün tarihsel görünümünü temsil etmediğini ve yalnızca bir operasyonun bağlantısını paylaşmanın kullanıcı atfı için yeterli olmadığını belirtir.
3. **Meta index.json.** https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/index.json
   - İlgili öğenin `reported_ds` değeri 2022-09-27, `added_ds` değeri 2022-10-11'dir. Gösterge tarihi, depoya eklenme tarihi ve erişim tarihi farklıdır.
   - Kaynak raporun URL'sini verir. Rapor metni bu çalışma oturumunda açılamadı.
4. **Natural Earth, Admin 0 Countries 1:110m.** https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson
   - Yerel kopya: `research/countries.geojson`.
   - Kamu malı coğrafi sınır tabanı; çizilen semboller tarafımızdan ülke temsil noktalarına yerleştirildi. Operasyon veya sunucu konumu değildir.

Meta depo arşivi: https://codeload.github.com/facebook/threat-research/zip/refs/heads/main

ZIP arşivi yorum alanındaki commit: `2d664e985e55fb754de7b1175f713e11f73cf8c8`. Kaynakların SHA-256 özeti `output/veri_manifest.json` içindedir. Depoda başka tarihlere ait dosyalar da bulunur; bu sunumun nicel bulgularında yalnızca belirtilen 2022 CSV dosyası kullanıldı.

## Yalnızca yöntem / tamamlanacak doğrulama için bağlantılar

5. GDELT DOC 2.0 API tanıtımı: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
6. GDELT veri erişimi: https://www.gdeltproject.org/data.html
7. GKG arşivi: https://data.gdeltproject.org/gdeltv2/
8. Meta 2022 kaynak raporu; URL, indirilen index.json'da yer alır: https://about.fb.com/news/2022/09/removing-coordinated-inauthentic-behavior-from-china-and-russia/

GDELT API canlı testi ve betik testi, `CONNECT tunnel failed, response 403` ile başarısız oldu. **Haber sayımı, zaman serisi, GDELT ülke dağılımı veya içerik doğruluk sonucu üretilmedi.**

VIGINUM, EEAS/AB Konseyi ve ABD Adalet Bakanlığı belgeleri bağımsız çapraz kontrol için önerilen birincil kaynaklardır. Bu oturumda belge metinleri incelenmediğinden bunlara belirli sayı, tarih, alıntı veya operasyon bulgusu atfedilmedi.

## Desteklenmeyen iddialar

- “Avrupa'daki Rus operasyonlarının %95,8'i Almanya'dadır.” → Bu veriden çıkarılamaz.
- “GDELT 311 dezenformasyon haberi buldu.” → Yanlış: 311 benzersiz Meta alan adı göstergesi sayıldı.
- “298 alan adı 298 ayrı operasyondur.” → Yanlış.
- “Almanya'nın ikna edilme oranı yüksektir.” → Bu veri etki ölçmez.
- “Haberde adı geçen ülke hedef ülkedir.” → Otomatik olarak çıkarılamaz.
- “Kaynakta olmayan ülkelerde operasyon yoktur.” → Çıkarılamaz.
- “Birincil veri indirildi; aktör atfı bağımsız doğrulandı.” → Hayır; bunlar farklı doğrulama düzeyleridir.

## GDELT bağlantısı için ayrıca incelenen teknik kaynak

Üçüncü taraf açık kaynak istemci: https://github.com/alex9smith/gdelt-doc-api . README, `gdeltdoc/api_client.py` ve `gdeltdoc/filters.py` indirildi; kopyaları `research/gdelt_docs/` altındadır. Bu kaynak GDELT'in kurumsal yayını değildir. Resmî DOC uç noktası, ArtList alan adları, 250 sonuç sınırı ve TimelineVolRaw yanıt yapısı bu kodla karşılaştırıldı. Belgelerin okunması, GDELT'ten haber indirildiği anlamına gelmez.

Yeni atlas, kullanıcının kendi tarayıcısından resmî API'ye istek gönderme ve JSON dosyası içe aktarma özellikleri içerir. Bir dosyanın yanıt şemasına uyması köken doğrulaması sayılmaz; böyle dosyalar ayrı etiket alır. Entegrasyon testlerindeki sentetik yanıtlar araştırma bulgularına veya dağıtılan atlasın başlangıç verisine eklenmedi.

## Sinematik coğrafi bağlam görselleri

Berlin/Potsdamer Platz, Londra/Adams Place Bridge ve Venice Sunset gerçek 360° HDR panoramalarıdır. Kaynak HDRI Haven / Poly Haven; indirilen kopyalar `pmndrs/drei-assets/hdri` deposundadır. Kaynak deponun README'si HDRI Haven atfını taşır. Panoramalar ekranda gösterim için JPEG'e dönüştürüldü; üretken görsel kullanılmadı.

Paris/Eiffel Kulesi görseli, `eddyte/paris-photoblog` deposunun `dev/images/toureiffelmini.jpg` galeri küçük resmidir. Galeri bunu “Tour Eiffel” olarak adlandırır ve © 2018 Wildo Coda künyesi taşır. Açık yeniden kullanım lisansı doğrulanmadı; bu görsel CC0 olarak sunulmaz.

Her dosyanın kaynak URL'si, lisans açıklaması, işleme bilgisi ve SHA-256 değeri `assets/locations/locations.json` içinde bulunur. Koordinatlar yer işareti/kent referanslarıdır; fotoğrafların kamera GPS konumu doğrulanmadı. Ülke etiketli IOC verisinden bu şehirlerde operasyon gerçekleştiği çıkarılamaz. Fotoğraflar olay kanıtı veya aynı döneme ait operasyon görüntüsü değildir. Harita bağlantı çizgisi fotoğrafı yer referansına bağlar; saldırı rotası göstermez.


## Akademik kaynakça ve erişim günlüğü

APA 7 tam kaynakça: [output/APA7_KAYNAKCA.md](output/APA7_KAYNAKCA.md). Yayıncıya erişim, okunmuş yazar/depo kopyası ve bibliyografik karşılaştırma ayrı düzeylerdir: [AKADEMIK_KAYNAK_DENETIMI.md](AKADEMIK_KAYNAK_DENETIMI.md). Dört erişilebilir akademik metnin özgün yöntem dersleri araştırma dosyasına işlendi; ABD/Twitter bulguları Batı Avrupa etkisi olarak aktarılmadı.


## Leaflet / OpenStreetMap

Leaflet 1.9.4: https://github.com/Leaflet/Leaflet/releases/tag/v1.9.4 . Lisans ve dosya özetleri assets/vendor/ içindedir. OpenStreetMap: https://www.openstreetmap.org/copyright . Standart döşemeler yalnız normal etkileşim sırasında istenir; toplu indirme yapılmaz. Canlı erişim yoksa kullanılan Natural Earth sınır katmanı ayrıca etiketlenir.
