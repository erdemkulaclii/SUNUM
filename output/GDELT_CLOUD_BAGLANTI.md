# GDELT Cloud sunucu bağlantısı

Verilen anahtar özel uygulama yapılandırmasına bağlandı ve gerçek istekte kullanıldı. Ağ/proxy aşamasındaki engel nedeniyle anahtarın geçerliliği doğrulanamadı. Güncel kayıt: `GDELT_CLOUD_RUNTIME_STATUS.json`.

Sunucu: `scripts/serve_presentation.py`. Başlatıcı: kök klasördeki `BASLAT.sh`. Anahtar yalnız `GDELT_API_KEY` ortam değişkeninden veya mevcut özel `.env` uygulama yapılandırmasından okunur. Değeri tarayıcıya ve indirilen pakete verilmez. `/health` yalnız yapılandırmanın mevcut olup olmadığını bildirir. Özel dosyalar HTTP üzerinden sunulmaz.

Resmî REST V2: https://gdeltcloud.com/api/v2 . Bu ürün GDELT Project DOC 2.0’dan ayrıdır. Sunucu sabit bir sorguyla son 7 tamamlanmış UTC gününü, tek sayfa ve en çok 10 Event adayı sınırıyla ister. Yanıt filtreleri, kimlikleri ve sayfalama durumu denetlenir; kapsam tamamlanmış varsayılmaz.

Aynı güncel arama, 2022 IOC dağılımının tarihsel doğrulaması değildir. Event sayısı operasyon sayısı sayılmaz. Kaynak haber URL’leri ve kapsam metaverisi geldikleri biçimde korunur; bilinmeyen koordinat veya etki üretilmez.

Bu ortamın `gdeltcloud.com`, `api.gdeltproject.org` ve `tile.openstreetmap.org` erişimi için izinler ortam taslağına kaydedildi. Taslağı kaydetmek çalışan ağ politikasını uygulamaz; ortam ayarlarında gözden geçirilip uygulanması gerekir.
