# Gerçek GDELT verisini bağlama

Güncel sunum: **GORUNMEZ_CEPHE_ATLAS.html**. Bilgisayarına indir, Chrome veya Edge ile aç. “GDELT verisini bağla” düğmesi, doğrudan resmî servise giden bir API bağlantısı içerir. API anahtarı istenmez.

1. Kampanya ve dönem seç. Kampanyalar tek bir operasyon kategorisinde birleştirilmez.
2. “GDELT’ten veriyi getir”e bas. Başarılı JSON yanıtı gelmeden haber veya harita gözlemi gösterilmez.
3. Başarılıysa haber başlıklarını ve URL’leri incele; kaynak ülke filtresini kullan.
4. “Kaynak ülkelerini haritala” ile mavi haber katmanını aç. Bu coğrafya, kırmızı operasyon hedeflerinden farklıdır.
5. “Veri + sorguyu indir” ile ham yanıtı, sorguyu, dönemi ve yükleme zamanını kaydet.
6. İstersen ayrı “Zaman serisini getir” düğmesini kullan. Bu TimelineVolRaw yanıtıdır; 250 URL seçkisinden türetilmiş bir toplam değildir.

Tarayıcı erişimi başarısız olursa “Resmî haber sorgusunu aç” bağlantısını kullan. Açılan JSON yanıtını bilgisayarına .json olarak kaydet ve sunumdaki “JSON dosyası içeri aktar” düğmesinden yükle. Elde veri yoksa program sonuç uydurmaz. Bir dosyanın GDELT biçimine uyması, kökeninin bağımsız doğrulanması değildir; içe aktarımlar bu sınırlılıkla etiketlenir.

## Hazır resmî sorgular

- [Doppelganger / Rusya bağlamı — son 30 gün, ArtList](https://api.gdeltproject.org/api/v2/doc/doc?query=%28Doppelganger%20OR%20%22Doppelg%C3%A4nger%22%29%20%28Russia%20OR%20Russian%20OR%20Russie%20OR%20Russland%20OR%20Rusya%29&mode=artlist&format=json&maxrecords=250&sort=datedesc&timespan=30days)
- [Portal Kombat — son 3 ay, ArtList](https://api.gdeltproject.org/api/v2/doc/doc?query=%22Portal%20Kombat%22&mode=artlist&format=json&maxrecords=250&sort=datedesc&timespan=3months)
- [Doppelganger / Rusya bağlamı — son 30 gün, TimelineVolRaw](https://api.gdeltproject.org/api/v2/doc/doc?query=%28Doppelganger%20OR%20%22Doppelg%C3%A4nger%22%29%20%28Russia%20OR%20Russian%20OR%20Russie%20OR%20Russland%20OR%20Rusya%29&mode=timelinevolraw&format=json&timespan=30days)

Bu bağlantılar sorgudur; bu dosyada indirilmiş araştırma sonucu değildir. API, ağ/CORS veya servis kısıtı nedeniyle hata verebilir. Buradaki bulut ortamında DOC uç noktası ve GKG arşivi yeniden kontrol edildi; ikisi de proxy HTTP 403 ile engellendi. Kaydedilmiş ağ izni taslağının çalışan ortama uygulanmadığı durum bilgisiyle doğrulandı. Ağ politikası aşılmadı.

## Yanıt sözlüğü

ArtList yanıtındaki `articles` dizisi kullanılır: `url`, `title`, `seendate`, `domain`, `language`, `sourcecountry`. Aynı URL’nin takip parametreli tekrarları temizlenir. Geçersiz http/https bağlantıları elenir; ham kayıt, tekrar ve elenen kayıt sayısı ayrı gösterilir. Başlıklar HTML olarak işlenmez. Sosyal görseller otomatik yüklenmez.

`sourcecountry` haber kaynağının ülkesidir; operasyonun hedefi veya metinde anılan ülke değildir. Avrupa haritası dışında kalan ve belirtilmemiş ülkeler haber listesinde korunur. Bunlar başka ülkelere dağıtılmaz. ArtList en fazla 250 sonuçluk seçkidir; tam evren veya etki sayımı değildir.

2022 IOC listesiyle aynı dönem karşılaştırması için tarihsel GKG arşivi veya BigQuery gerekir. Son 30 gün/3 ay haberleri 2022 verisinin eşzamanlı doğrulaması sayılamaz. Haberlerin konu uygunluğu, çürütme/aktarma niteliği ve aktör atfı ayrıca elle denetlenmelidir.

## Doğrulanan belge ve kod kaynakları

- Resmî API uç noktası: https://api.gdeltproject.org/api/v2/doc/doc
- Resmî API belge bağlantısı: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/ — bu ortamda canlı metni açılamadı.
- Erişilip incelenen üçüncü taraf açık kaynak istemci: https://github.com/alex9smith/gdelt-doc-api — README, `gdeltdoc/api_client.py`, `gdeltdoc/filters.py`. ArtList alanları, 250 kayıt sınırı, zaman serisi yapısı ve resmî uç nokta bu kodla karşılaştırıldı. Bu istemci GDELT’in kurumsal yayını değildir.
- UI doğrulaması: `GDELT_BAGLANTI_TESTI.json`. Başarı/hata, içe/dışa aktarma, kaynak haritası ve IOC katmanına dönüş sentetik test yanıtlarıyla sınandı. **Canlı GDELT indirmesi başarılıymış gibi raporlanmadı.**
