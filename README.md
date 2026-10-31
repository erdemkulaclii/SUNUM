# Doppelgänger vakasında hedef coğrafyası ve haber görünürlüğü

Meta’nın 2022 CIB gösterge listesi ile GDELT haber verisini birlikte kullanan Türkçe akademik vaka sunumu. Rusya bağlantısı kaynak raporlamasına (Meta; EU DisinfoLab) dayanır; bağımsız bir atıf analizi değildir.

[PowerPoint](output/AKADEMIK_ODAKLI_SUNUM.pptx) · [PDF](output/AKADEMIK_ODAKLI_SUNUM.pdf) · [Etkileşimli sunum (HTML)](output/AKADEMIK_ODAKLI_SUNUM.html) · [Sunucu kartları](output/SUNUCU_KARTLARI.pdf) · [Araştırma dosyası](output/AKADEMIK_ARASTIRMA_DOSYASI.pdf) · [APA 7 kaynakça](output/APA7_KAYNAKCA.md) · [Tam paket](output/PROFESYONEL_TAM_PAKET.zip)

## Tek komutla başlatma

```bash
python sunum.py
```

Yerel sunucuyu açar, sunumu Chrome/Edge varsa tam ekran uygulama penceresinde (yoksa varsayılan tarayıcıda) açar ve otomatik oynatır. Ekrandaki “Sunumu başlat” düğmesine tıklarsanız tam ekrana geçer; tıklamazsanız 5 saniye sonra kendiliğinden başlar. Kapatmak için komut penceresinde Ctrl+C.

Çift tıklama: Windows’ta **`BASLAT.bat`**, macOS’ta **`BASLAT.command`**, Linux’ta `./BASLAT.sh`. Yalnız Python 3 gerekir; ek paket gerekmez.

| Komut | Ne yapar |
|---|---|
| `python sunum.py` | Sunucu + tam ekran + otomatik oynatma |
| `python sunum.py --elle` | Otomatik oynatma olmadan (ok tuşları / Boşluk) |
| `python sunum.py --pptx` · `--pdf` | PowerPoint ya da PDF yedeğini açar |
| `python sunum.py --yeniden-uret` | HTML, PPTX, PDF ve belgeleri yeniden üretip başlatır |
| `python sunum.py --kontrol` | Bütün testleri ve sunum doğrulamasını çalıştırır |

## Akış: 17 ana slayt, yaklaşık 20 dakika (soru-cevap yok)

| # | Bölüm | İçerik |
|---|---|---|
| 1–2 | Kapak, plan | Başlık, yazar alanları (`scripts/presentation_meta.json`), sunum planı |
| 3 | Giriş / vaka | Doppelgänger: EU DisinfoLab (2022), Meta (Nimmo ve Agranovich, 2022) |
| 4 | Kavramsal çerçeve | Bennett ve Livingston; Wardle ve Derakhshan; Lazer/Allen; Kwak ve An; Wang vd. |
| 5 | Araştırma soruları | AS1 hedef · AS2 alan adı yapısı · AS3 haber görünürlüğü (zaman ve mekân) |
| 6–8 | Yöntem | Veri ve yöntem · Meta veri hazırlığı · **GDELT test edilebilirliği (MD5, payda, isabet)** |
| 9–11 | Bulgu 1–3 (Meta) | Almanya %95,8 · altı son etiket 240 adres · 75 ilk etiket grubu |
| 12 | **Bulgu 4 (GDELT)** | Görünürlük iki günlük dalga: 27.09’da 392, 28.09’da 100 haber (%96,3) |
| 13 | **Bulgu 5 (GDELT haritası)** | Kaynak ülke: ABD 373, Almanya 29; oranlı ölçüde Almanya 2.; haberlerin %63,6’sı Almanya’yı anıyor |
| 14–16 | Tartışma, sınırlılıklar, sonuç | Hedef–görünürlük asimetrisi, ajans dağıtımı, isabet ve kapsam sınırları |
| 17 | Kaynakça | 19 kaynağın tamamı tek sayfada, iki sütunlu APA 7 listesi (ek slayt: 6) |

Sunmadan önce `scripts/presentation_meta.json` içindeki köşeli parantezli alanları doldurup sunumu yeniden üretin (ya da PowerPoint’te doğrudan düzenleyin).

## Sunumu siz yönetirsiniz

Slaytlar kendiliğinden geçmez, yazılar süreyle açılmaz: her slaytın içeriği hemen görünür. Geçiş: →, Boşluk, PageDown (sunum kumandası) ya da tıklama; geri: ←. Harita slaytı girişte bir kez oynar (≈14 sn; gün gün birikim → Meta hedefleri → anılan yerler), haber dalgası grafiği girişte çizilir. Saat, başladığınız andan itibaren geçen süreyi 20:00’ye karşı gösterir. N: konuşma notları.

## GDELT verisi: ham arşivden, test edilebilir

GDELT verisi API'den değil, GDELT literatüründe (Leetaru ve Schrodt, 2013; Kwak ve An, 2014) kullanılan **ham GKG 2.0 arşivinden** gelir:

- 20 Eylül – 11 Ekim 2022 arasındaki bütün 15 dakikalık İngilizce ve çeviri (translingual) GKG dosyaları; her biri GDELT'in yayımladığı **MD5** değeriyle doğrulanır (`research/gdelt/gkg_archive/manifest.json`).
- Sabit, birim testli eşleşme kuralları: **R1** “doppelgänger” + Rusya bağlamı; **R2** Meta/Facebook + Rusya + ağ/sahte/dezenformasyon terimi (çok dilli).
- Kaynak ülke: GDELT'in 2018 alan adı–ülke listesi. Anılan yerler: aynı haberlerin `V2Locations` alanı. Payda: taranan bütün kayıtlar (gün ve ülke bazında).
- İsabet testi: sabit tohumlu rastgele örneklem, Wilson %95 güven aralığı (`scripts/gdelt_validation.py`, `research/gdelt/validation_sample.csv`). Birinci kodlama yapay zekâ destekli ön kodlamadır; ikinci (insan) kodlayıcı sütunu boştur ve doldurulması önerilir (Cohen κ otomatik hesaplanır).

Yeniden üretmek için (~10 dk, ~40 GB akış; disk gerekmez):

```bash
python scripts/gdelt_gkg_archive.py
```

```bash
python scripts/gdelt_validation.py score && python scripts/build_interactive.py && python scripts/export_editorial.py
```

İsteğe bağlı güncel izleme için DOC 2.0 API yolu (`scripts/fetch_gdelt_map.py`, harita slaytındaki düğmeler) korunur; ancak sunumdaki bulgular ham arşivdendir.

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

Tarayıcı denetimleri Chromium ve Playwright gerektirir. Testlerdeki API/arşiv yanıtları sentetik fikstürlerdir ve sunum verisine katılmaz. Güncel ZIP paketi: `python scripts/build_release.py`.
