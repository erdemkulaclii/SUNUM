# GDELT veri bağlantısı

Sunum açıldığında bağlantı otomatik denenir. Veri kaydı düğmesi sağlayıcıyı, sorguyu, alım zamanını ve bağlantı durumunu açar.

- **Sunuculu sürüm:** `BASLAT.sh` veya `python scripts/serve_presentation.py`. GDELT Cloud anahtarı sunucuda kalır. Önce Cloud’un son 7 tamamlanmış UTC günü için en çok 10 Event adayı sorgulanır. Yanıt yoksa DOC denenir.
- **Tek HTML:** `PROFESYONEL_SUNUM.html`. Özel Cloud sunucusu olmadan ücretsiz GDELT Project DOC sorgusu otomatik çalışır. En çok 250 haber URL’si; son 30 gün, UTC başlangıç/bitiş sabitlenir.
- **Harita:** Leaflet. Dosyaya çift tıklanan `file://` sürümü, OSM isteği göndermeden gömülü Natural Earth sınır haritasını gösterir. `BASLAT.sh` ile açılan HTTP sürümü OSM’yi normal tarayıcı Referer bilgisiyle deneyebilir. HTTP durumu ve görüntü türü denetlenir; reddedilen döşemeler görüntülenmez ve çevrimiçi katman kaldırılır. IOC hedef ülkeleri ile haber kaynakları veya Cloud Event konumları ayrı katmanlardır. Koordinatı dönmeyen bir Event’e konum uydurulmaz.

Cloud Event kaydı, haber URL’si, alan adı göstergesi ve gerçek dünyadaki bağımsız operasyon farklı birimlerdir. Otomatik eşleşme içerik doğruluğu veya bağımsız aktör atfı değildir.

Tarihli önbellek, bu oturumda canlı doğrulanmış diye sunulmaz. Sunucudaki anahtar başka bilgisayara indirilen GitHub/ZIP paketine aktarılmaz. Güncel sonuçlar 2022 tarihsel karşılaştırmasının yerine geçmez.

Bu bulut ortamında verilen anahtarla gerçek Cloud isteği yapıldı; ağ/proxy erişimi engellendi. Anahtarın geçerliliği doğrulanamadı. Teknik belge okuma ve sentetik işlev testleri gerçek veri indirmesi sayılmaz. Ayrıntı: `GDELT_CLOUD_RUNTIME_STATUS.json` ve `HARITA_BAGLANTI_DURUMU.json`.

Haritadaki “403 Access blocked” döşeme sorununun giderilmesi, GDELT API’sinin çalıştığı veya Cloud anahtarının doğrulandığı anlamına gelmez. OSM tabanı ile haber sağlayıcısı ayrı bağlantılardır. OSM erişim engeli başka alan adı, ayna veya proxy ile aşılmaya çalışılmaz.
