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

## Makale

**[makale/makale.pdf](makale/makale.pdf)** · [Word](makale/makale.docx) · [Markdown kaynağı](makale/makale.md) · [kaynak doğrulama kaydı](makale/KAYNAK_DOGRULAMA.md)

“Hibrit Savaşın Görünmez Cephesi: Doppelgänger Ağının Alan Adı Altyapısı ve Uluslararası Haber Görünürlüğü (2022)”. Türkçe özet ve İngilizce abstract, kuramsal çerçeve, vaka, yöntem, bulgular (iki tablo, iki şekil), tartışma, sınırlılıklar, veri erişilebilirliği, APA 7 kaynakça (37 kaynak).

Makaledeki her sayı ham veriden yeniden hesaplanır ve otomatik testle metne karşı denetlenir:

```bash
python scripts/build_makale.py && python -m unittest scripts/test_makale.py
```

## Akış: 19 ana slayt, yaklaşık 20 dakika (soru-cevap yok)

| # | Bölüm | İçerik |
|---|---|---|
| 1 | Kapak | Hibrit Savaşın Görünmez Cephesi — Erdem Kulaçlı |
| 2 | Sorun ve katkı | Operasyonu değil, izlerini ölçmek; vakaya özgü hakemli literatürün azlığı |
| 3 | Kavramsal çerçeve I | Hibrit savaştan hibrit müdahaleye: Hoffman, Renz, Galeotti, Fridman, Caliskan; çalışma tanımı (Wigell; Hybrid CoE; Mumford ve Carlucci) |
| 4 | Kavramsal çerçeve II | Görünmez cephenin mekanizması: stratejik anlatı → yorumlayıcı modeller → ödünç güvenilirlik |
| 5 | Vaka | Doppelgänger 2022–2025: ifşa, atıf (SDA/Structura), evrim |
| 6 | Araştırma soruları | AS1–AS3 ve kuramsal beklentiler |
| 7–9 | Yöntem | Veri ve yöntem · Meta veri hazırlığı · GDELT test edilebilirliği |
| 10–12 | Bulgular (Meta) | Almanya %95,8 · wrongTLD deseni · 75 marka etiketi |
| 13–14 | Bulgular (GDELT) | İki günlük dalga · “Almanya hakkında, ama Almanya’da değil” haritası |
| 15–16 | Tartışma | Altyapı ≠ erişim ≠ etki ≠ görünürlük · algı korsanlığı ve seçilim |
| 17–18 | Sınırlılıklar, sonuç | |
| 19 | Kaynakça | 29 kaynak tek sayfada (APA 7) |

Akademik gerekçeler ve kaynak doğrulama etiketleri: [araştırma raporu](reports/Doppelgänger%20vakası%20akademik%20derinleştirme.md).

Sunmadan önce `scripts/presentation_meta.json` içindeki boş alanları (kurum, ders, tarih) doldurup sunumu yeniden üretebilirsiniz; boş bırakılırsa kapakta yalnızca ad soyad görünür (ya da PowerPoint’te doğrudan düzenleyin).

## 3B sahneler

Sunumda üç 3B sahne vardır (three.js, dosyaya gömülü; internet gerekmez):

- **Kapak:** hedef ülkeleri kırmızı gösteren, yavaş dönen küre.
- **Alan adı takımyıldızı (Bulgu 2):** 311 alan adının her biri bir nokta. Dört aşama: üç sınıf → marka taklitleri (beyaz çekirdek = gerçek marka adı) → harf karışımı aileleri → en sık altı uzantı.
- **GDELT küresi (Bulgu 5):** ülkelerin üzerinde yükselen sütunlar. Üç aşama: gün gün biriken haber sayısı → aktif kuruluş başına oran (ABD sütunu iner, Almanya yükselir) → haberlerde anılan yerler ve Meta hedefleri.

Aşamaları sunucu ilerletir: **→ / Boşluk** önce sahnenin aşamasını, son aşamadan sonra slaytı değiştirir; **←** geri alır. Alttaki numaralı düğmelerle doğrudan bir aşamaya geçilebilir, sahne fareyle döndürülebilir. Oran aşamasında yalnızca en az 5 haberi ve 100 aktif kuruluşu olan ülkeler gösterilir. WebGL yoksa slaytlar 2B haritaya ve çubuk grafiğe düşer; küre slaytındaki “2B harita” düğmesi de elle geçiş sağlar. PowerPoint ve PDF sürümleri 2B görselleri kullanır.

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
