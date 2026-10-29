# Meta 2022 CIB listesinde hedef coğrafyası ve alan adı yapısı

Gerçek OSINT verisine dayanan Türkçe akademik vaka sunumu. Rusya bağlantısı kaynak raporlamasına dayanır; inceleme Meta’nın yayımladığı alan adı göstergelerinin hedef coğrafyasını ve sözcüksel yapısını çözümler.

[Tam paket](output/PROFESYONEL_TAM_PAKET.zip) · [PowerPoint](output/AKADEMIK_ODAKLI_SUNUM.pptx) · [PDF](output/AKADEMIK_ODAKLI_SUNUM.pdf) · [Etkileşimli sunum](output/AKADEMIK_ODAKLI_SUNUM.html) · [Sunucu kartları](output/SUNUCU_KARTLARI.pdf) · [APA 7 kaynakça](output/APA7_KAYNAKCA.pdf)

## Sunumu açma

Sunum salonunda **`output/AKADEMIK_ODAKLI_SUNUM.pptx`** dosyasını kullanın; aynı sayfa düzenindeki PDF yedeği yanında bulunsun. Başlıklar, metinler ve bulgu grafikleri PowerPoint’te düzenlenebilir; PDF metni seçilebilir. Masaüstü PowerPoint’in görüntüleme davranışı bu ortamda ayrıca sınanmadı.

Etkileşimli kullanım için `output/AKADEMIK_ODAKLI_SUNUM.html` dosyasını indirip tarayıcıda açın. GitHub dosya görünümü HTML’yi çalıştırmaz. Sağ/sol ok slayt değiştirir; boşluk planlanan akışı başlatır/durdurur; **N** anlatıcı kartlarını açar. Üst menüde veri tablosu, kaynakça ve yardımcı atlas bulunur. Tarayıcıda F11 tam ekran kullanılabilir. `PROFESYONEL_SUNUM` ve `SINEMATIK_SUNUM` adları uyumlu kopyalar olarak korunur.

**11 ana slayt, 13 dakika anlatım ve 2 dakika oturum payı.** Sekiz veri/yöntem/kaynakça ekiyle toplam 19 slayt vardır. Süreler anlatım planıdır; gerçek süre prova ile ölçülmelidir. Ana slaytlarda kısa metin, yüksek kontrast ve veri grafikleri kullanılır. Kent fotoğrafları kullanılmaz.

## Araştırma sorusu ve tamamlanmış bulgular

**Araştırma sorusu:** Bu listede hedef ülke etiketleri ile alan adlarının sözcüksel yapısı nasıl bir örüntü oluşturuyor?

Analiz kümesi, 350 ham kayıttan seçilen 313 alan adı satırının tekilleştirilmesiyle elde edilen **311 benzersiz alan adıdır**. CIB ve Telegram bağlantıları bu paydada sayılmaz. Ülke, uzantıdan veya IP’den tahmin edilmez; kaynağın `comment` alanındaki hedef etiketinden alınır.

| Tamamlanmış analiz | Sonuç |
| --- | --- |
| Hedef ülke dağılımı | Almanya 298/311: **%95,8**. Birleşik Krallık 4, Fransa 2, İtalya 2, Letonya 3, Ukrayna 1, çoklu hedef 1. |
| Son DNS etiketi dağılımı | 39 farklı son etiket vardır. En sık altı etiket (`online`, `website`, `site`, `space`, `pw`, `fun`) 240/311 alan adını, **%77,2**’yi kapsar. Bu 240 kaydın tamamı Almanya hedeflidir. |
| İlk DNS etiketinin tekrarı | 93 ayrı ilk etiketin 75’i birden fazla son etiketle kullanılır. Bu gruplar **293 alan adını** kapsar. |

**Sonuç cümlesi:** İncelenen vaka, Almanya hedefli etiketlerdeki yoğunlaşma ile yinelenen ilk DNS etiketleri çevresinde oluşan adres çeşitliliğinin birlikte görülmesiyle tanımlanır.

İlk/son DNS etiketi, metnin ilk/son noktasına göre ayrılan gerçek dize parçasıdır. Bu hesap etkin kayıt son ekini, fiyatı, barındırma ülkesini veya ortak operatörü belirlemez. Bütün kayıtlarda `ds=2022-09-27` olduğu için faaliyet zaman serisi üretilmez. Bulgular yayımlanmış bu listeye aittir; bütün operasyonlara veya kamuoyu etkisine genellenmez.

## Veri, kaynakça ve anlatıcı belgeleri

Birincil veri, Meta’nın [sabit commit bağlantısındaki CSV dosyasıdır](https://github.com/facebook/threat-research/blob/2d664e985e55fb754de7b1175f713e11f73cf8c8/indicators/csv/2022_09_removing_coordinated_inauthentic_behavior_from_china_and_russia.csv). SHA-256:

```text
9f216a37e15c4772019d20ee620eafabf57a3876d4a7ab72fff5330fa8167d8d
```

[Yapısal analiz](output/IOC_YAPISAL_ANALIZ.json), [311 kayıtlık kanıt tablosu](output/IOC_YAPISAL_KANIT.csv), [son etiket dağılımı](output/IOC_SON_ETIKET_DAGILIMI.csv), [ülke × son etiket](output/IOC_HEDEF_SON_ETIKET.csv) ve [ilk etiket grupları](output/IOC_GOVDE_AILELERI.csv) kaynak sıra numaralarıyla yeniden denetlenebilir. Etkileşimli HTML’de kayıtlar aranabilir ve süzülmüş tablo CSV olarak indirilebilir.

[Sunucu kartları / PDF](output/SUNUCU_KARTLARI.pdf) ve [Word](output/SUNUCU_KARTLARI.docx), her slayt için 3–4 anahtar cümle içerir. [Ayrıntılı prova metni / PDF](output/KONUSMA_METNI_15_DK.pdf) ve [Word](output/KONUSMA_METNI_15_DK.docx) hazırlık içindir; zorunlu okuma metni değildir. [Konuşmacı notları](output/KONUSMACI_NOTLARI.md) ve PowerPoint notları aynı anlatı kaynağından üretilir.

[Araştırma dosyası](output/AKADEMIK_ARASTIRMA_DOSYASI.pdf) soru, yöntem, tamamlanmış analizler ve kapsamı açıklar. [Seçilmiş APA 7 kaynakça](output/APA7_KAYNAKCA.md) **altı kullanılan kaynak** içerir: iki akademik metin, birincil veri, yazılım ve iki harita kaynağı. Kaynak türleri birbirinin yerine geçmez. Erişim düzeyleri [kaynak kaydında](KAYNAKLAR.md), geçmiş geniş bibliyografyanın erişim denetimi [ayrı günlükte](AKADEMIK_KAYNAK_DENETIMI.md) korunur. Makale kopyaları pakette yeniden dağıtılmaz.

## Yardımcı harita ve GDELT’nin yeri

Ana bulgu, aynı lineer ölçekteki yatay çubuk grafiklerle sunulur. **Yardımcı atlas** Leaflet 1.9.4 kullanır ve hedef ülke etiketlerini ülke düzeyinde gösterir. Doğrudan dosya açılışında gömülü Natural Earth sınır verisi kullanılır; OpenStreetMap döşemesi istenmez. Harita operasyonun, sunucunun veya fotoğrafın konumunu göstermiyor.

İsteğe bağlı HTTP kullanımında kök klasörde `BASLAT.sh` çalıştırılabilir. OSM erişimi ağ koşullarına bağlıdır. Döşeme yanıtları gösterilmeden önce denetlenir; erişim reddedildiğinde çevrimiçi katman kaldırılır ve gömülü sınır haritası kalır. OSM atfı ve kullanılan taban haritada yazılıdır. Toplu döşeme indirmesi yapılmaz.

**GDELT, tek bir ileri araştırma slaytında ele alınır.** 2022 vakası için aynı dönemli haber arşivi, açık örnekleme kapsamı ve kaynak ülkesi/anılan yer ayrımı gerekir. Bu tarihsel karşılaştırma tamamlanmadı; sunumda GDELT haber sayısı veya etki bulgusu yoktur. Ana sunum API anahtarı, elle veri bağlama veya canlı haber yanıtı gerektirmez.

Önceki özel GDELT sunucu bağlantısı teknik araç olarak korunur. Anahtar yalnız sunucu tarafındaki özel yapılandırmada tutulur; HTML, GitHub ve dağıtım paketlerine eklenmez. Ağ engeli nedeniyle başarılı canlı GDELT alımı doğrulanmadı; anahtar geçerliliği hakkında sonuç çıkarılmadı. Güncel bir API seçkisi tarihsel 2022 karşılaştırmasının yerine geçmez.

## Yeniden üretim

```bash
python -m pip install -r requirements.txt
python scripts/build_interactive.py
python scripts/export_editorial.py
python scripts/export_academic_documents.py
python scripts/verify_leaflet.py
python scripts/verify_slide_readability.py --check-pptx
python -m unittest discover -s scripts -p 'test_*.py'
```

Hazır HTML ve belgeleri açmak için Python gerekmez. Yeniden üretimde tarayıcı denetimleri için Chromium ve Playwright gerekir. Yerel regresyon testlerindeki yapay API yanıtları araştırma bulgusu değildir ve dağıtılan sunum verisine katılmaz. Eleştiriden çıkarılan kararlar ve uygulanmayan önerilerin gerekçeleri [revizyon kaydındadır](REVIZYON_KARARLARI.md).

Önizlemeler ve doğrulama raporlarıyla güncel ZIP paketini yeniden oluşturmak için `python scripts/build_release.py` kullanılır. Yardımcı ülke kamerasının videosu `python scripts/render_cinematic_tour.py` ile ayrıca üretilebilir.
