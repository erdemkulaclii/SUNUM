# Doppelgänger vakasında hedef coğrafyası ve haber görünürlüğü

Meta’nın 2022 CIB gösterge listesi ile GDELT haber verisini birlikte kullanan Türkçe akademik vaka sunumu. Rusya bağlantısı kaynak raporlamasına (Meta; EU DisinfoLab) dayanır; bağımsız bir atıf analizi değildir.

[PowerPoint](output/AKADEMIK_ODAKLI_SUNUM.pptx) · [PDF](output/AKADEMIK_ODAKLI_SUNUM.pdf) · [Etkileşimli sunum (HTML)](output/AKADEMIK_ODAKLI_SUNUM.html) · [Sunucu kartları](output/SUNUCU_KARTLARI.pdf) · [Araştırma dosyası](output/AKADEMIK_ARASTIRMA_DOSYASI.pdf) · [APA 7 kaynakça](output/APA7_KAYNAKCA.md) · [Tam paket](output/PROFESYONEL_TAM_PAKET.zip)

## Akış: 15 ana slayt, 13 dk 30 sn anlatım + 1 dk 30 sn pay

| # | Bölüm | İçerik |
|---|---|---|
| 1 | Kapak | Başlık, alt başlık, yazar/kurum/ders/tarih (`scripts/presentation_meta.json`) |
| 2 | Plan | Giriş · Yöntem · Bulgular · Tartışma |
| 3 | Giriş / vaka | Doppelgänger: EU DisinfoLab (2022) ve Meta (Nimmo ve Agranovich, 2022) |
| 4 | Kavramsal çerçeve | Bilgi düzensizliği; ölçüm ve payda; haber verisinde coğrafya |
| 5 | Araştırma soruları | AS1 hedef coğrafyası · AS2 sözcüksel yapı · AS3 haber görünürlüğü |
| 6 | Veri ve yöntem | Meta CSV · GDELT DOC 2.0 · GDELT GKG (ayrı ölçüm birimleri) |
| 7 | Veri hazırlığı | 350 → 313 → 311 |
| 8–10 | Bulgu 1–3 | Almanya %95,8 · altı son etiket 240 adres · 75 ilk etiket grubu 293 adres |
| 11 | **Bulgu 4: GDELT haritası** | Kaynak ülke (renk) · anılan yer (nokta) · Meta hedefi (kırmızı çerçeve) |
| 12 | Tartışma | Bulguların literatür/raporlarla karşılaştırması |
| 13 | Sınırlılıklar | Seçilim, 250 sonuç sınırı, konum kodlaması |
| 14 | Sonuç | AS1–AS3 yanıtları ve sonraki adım |
| 15 | Kaynakça | Özet; tam APA 7 künyeleri eklerde (11 ek slayt) |

Sunmadan önce `scripts/presentation_meta.json` içindeki köşeli parantezli alanları doldurup sunumu yeniden üretin (ya da PowerPoint’te doğrudan düzenleyin).

## GDELT haritası

Harita slaytı üç katman gösterir:

- **Renk — haberin yayımlandığı ülke.** GDELT DOC 2.0 `artlist`, sabit sorgu `(doppelganger OR "doppelgänger" OR "coordinated inauthentic") (russia OR russian OR meta OR facebook)`, Meta duyuru penceresi 20 Eylül – 11 Ekim 2022, üç günlük dilimler, URL düzeyinde tekilleştirme.
- **Nokta — haberde anılan yer.** GDELT GKG 2.0 `V2Locations`, BigQuery (`scripts/gdelt_gkg_locations.sql`).
- **Kırmızı çerçeve — Meta hedef etiketi** (Almanya kalın çizgi).

Yan panel tekil haber sayısını, en çok haber çıkan ülkeleri, Almanya’nın haber kaynaklarındaki payını (Meta’daki %95,8 ile karşılaştırmalı), 250 sınırına ulaşan dilimleri ve verinin ne zaman, nereden alındığını gösterir. **Kaynak ülke, hedef ülke veya okur ülkesi değildir.**

### Veriyi alma (önerilen: sunumdan önce, kendi bilgisayarınızda)

```bash
python scripts/fetch_gdelt_map.py
```

```bash
python scripts/build_interactive.py && python scripts/export_editorial.py
```

Bu, gerçek yanıtları `research/gdelt/` altına (ham yanıtlar + SHA-256) kaydeder, veriyi HTML’ye gömer ve PowerPoint/PDF harita slaytına statik harita görüntüsü ekler. Anılan yer katmanı için (Google Cloud projesi ve `bq` gerekir; önce `--dry-run` ile taranacak veri miktarını görün):

```bash
python scripts/fetch_gdelt_map.py --bigquery --project GCP_PROJENIZ
```

DOC 2.0 resmî olarak son üç ayı destekler; 2022 penceresi veri döndürmezse GKG/BigQuery yolu tarihsel analiz için doğru yoldur. Güncel izleme için `--window recent30` kullanılabilir.

### Sunum anında

- `BASLAT.sh` → yerel sunucu (`http://127.0.0.1:8765`), GDELT isteklerini sunucu tarafında yapar (tarayıcı CORS engeli olmaz).
- HTML’yi doğrudan açarsanız tarayıcı GDELT’e doğrudan bağlanmayı dener.
- Veri gömülü değilse sunum açılınca 2022 penceresi arka planda bir kez sorgulanır (~1 dk; GDELT 5 saniyede bir isteğe izin verir). Harita slaytında “2022 penceresini sorgula”, “Son 30 gün”, “JSON yükle”, “JSON indir” düğmeleri vardır.
- Başarısız veya boş yanıt “sıfır haber” sayılmaz ve hiçbir koşulda örnek veri gösterilmez.

**Not:** Bu sürüm hazırlanırken çalışma ortamının ağ politikası GDELT’i engellediği için depoda GDELT anlık görüntüsü yoktur; harita kodu yalnız sentetik test yanıtlarıyla sınandı. Canlı veriyi ilk kez kendi bilgisayarınızda alın ve sonuçları sunmadan önce kontrol edin.

## Meta bulguları (tamamlanmış)

Analiz kümesi 350 ham kayıttan seçilen 313 alan adı satırının tekilleştirilmesiyle elde edilen **311 benzersiz alan adıdır**. Ülke, kaynağın `comment` alanındaki hedef etiketinden alınır.

| Analiz | Sonuç |
| --- | --- |
| Hedef ülke | Almanya 298/311: **%95,8**. Birleşik Krallık 4, Fransa 2, İtalya 2, Letonya 3, Ukrayna 1, çoklu hedef 1. |
| Son DNS etiketi | 39 farklı etiket; en sık altısı 240/311 (**%77,2**), tamamı Almanya hedefli. |
| İlk DNS etiketi tekrarı | 93 ilk etiketin 75’i birden fazla son etiketle; **293 adres**. |

Birincil veri: Meta’nın [sabit commit bağlantısındaki CSV](https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv), SHA-256 `9f216a37e15c4772019d20ee620eafabf57a3876d4a7ab72fff5330fa8167d8d`. Kaynak erişim düzeyleri [KAYNAKLAR.md](KAYNAKLAR.md), revizyon gerekçeleri [REVIZYON_KARARLARI.md](REVIZYON_KARARLARI.md) içindedir.

## Yeniden üretim ve testler

```bash
python -m pip install -r requirements.txt
```

```bash
python scripts/build_interactive.py && python scripts/export_editorial.py && python scripts/export_academic_documents.py
```

```bash
python scripts/verify_concise.py --check-pptx
```

```bash
python -m unittest discover -s scripts -p 'test_*.py'
```

Tarayıcı denetimleri Chromium ve Playwright gerektirir. Testlerdeki API yanıtları sentetiktir ve sunum verisine katılmaz. Güncel ZIP paketi: `python scripts/build_release.py`.
