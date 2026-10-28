# GDELT Cloud bağlantısı

Bu servisin anahtarları `gdelt_sk_…` biçimindedir. **GDELT Cloud**, anahtarsız GDELT Project DOC 2.0 API'den farklı bir üründür. Cloud Event kodlaması, Story kümelemesi ve metrikleri GDELT Cloud'a atfedilmelidir; bir Event kaydı otomatik dezenformasyon operasyonu değildir.

Doğrulanan REST adresi: `https://gdeltcloud.com/api/v2`. Kimlik doğrulama: `Authorization: Bearer` başlığı. Kaynak: https://github.com/gdelt-cloud/plugins ve https://github.com/gdelt-cloud/demos . Belgeler bu çalışma sırasında okundu.

## Bu ortamda gereken son adım

Ortam ayar taslağına aşağıdakiler kaydedildi:

- Ağ izinleri: `gdeltcloud.com` ve `docs.gdeltcloud.com`; önceki izinler korundu.
- Secret gereksinimi: `GDELT_API_KEY`, yalnız `gdeltcloud.com` hedefine bağlı.

**Anahtar değerini ortamın Secrets alanındaki `GDELT_API_KEY` değişkenine gir; ayarları kaydet ve ortamı yayımla.** Sohbette yazılmış bir anahtar otomatik olarak çalışma ortamına enjekte edilmez. Bu oturumun ayar aracı gizli değer değil, yalnızca gereksinim ve hedef kaydedebilir. Anahtar bu dosyaya, HTML'ye, koda veya ZIP'e eklenmedi.

Taslak kaydı, çalışan ağ politikasını veya gizli değişkeni kendiliğinden etkinleştirmez. Son kontrolde bu alan adları çalışan ortamın izinlerinde yoktu ve `GDELT_API_KEY` enjekte edilmemişti. Dolayısıyla anahtarın geçerliliği veya hesabın API erişimi henüz doğrulanamadı.

## Hazırlanan istemci

```bash
cd /workspace/SUNUM
python scripts/fetch_gdelt_cloud.py
```

Kendi bilgisayarında ortam sırrı tanımlamadan denemek istersen:

```bash
python scripts/fetch_gdelt_cloud.py --prompt-key
```

Bu seçenek anahtarı terminalde gizli olarak ister; komut satırı geçmişine veya dosyaya yazmaz. Anahtarı argüman olarak verme.

İstemci varsayılan olarak tamamlanmış son 7 UTC günü için Rusya bağlantılı dezenformasyon/Doppelganger/Batı Avrupa konulu anlamsal Event adaylarını arar. Bir ücretsiz maliyet-metaverisi okuması ve en fazla 10 kayıtlık bir kanıt sayfası alır. İsteğe bağlı ikinci sayfa, aynı sorgu ve limit korunarak alınabilir. Kota, yetki, ağ ve sözleşme hatalarında durur; otomatik tekrar veya arka plan taraması yapmaz.

Başarılı gerçek indirmede `output/GDELT_CLOUD_EVENTS.json` oluşturulur. Ham sayfalar, sorgu, uygulanan filtreler, cursor durumu ve kapsam metaverisi korunur. Terminal cursor, tarihsel kapsamın tam olduğunu veya tüm operasyonların bulunduğunu kanıtlamaz. Sonuçlar gerçek yanıt incelendikten sonra sunuma ayrı GDELT Cloud katmanı olarak bağlanmalıdır; mevcut DOC JSON içe aktarıcısı Cloud Event şeması yerine kullanılamaz.

## Yapılan kontroller

8 sentetik sözleşme testi geçti: filtrelerin korunması, sayfa sınırı, ilerlemeyen cursor, kapsam belirsizliğinin korunması, yinelenen Event kimlikleri, izinli hedef kısıtı ve kimlik bilgisinin yalnız başlıkta tutulması. Test verileri araştırma bulgusu veya gerçek indirme sayılmadı. Gerçek anahtar dosyalara yazılmadı; bu kontrollerde kullanılmadı.
