# Hibrit Savaşın Görünmez Cephesi

17 ana slayt · yaklaşık 20 dakika anlatım · soru-cevap yok · slaytları sunucu geçirir.

Bu dosya sunucu kartlarını içerir. Ayrıntılı prova metni KONUSMA_METNI_15_DK dosyalarındadır; ezberlenmesi veya aynen okunması gerekmez.

## 01. Hibrit Savaşın Görünmez Cephesi · 00:00–00:45

- Hibrit savaşın görünmez cephesi bilgi alanıdır; bu sunum Rusya’nın Batı Avrupa’ya yönelik dezenformasyon operasyonlarını GDELT verisiyle haritalıyor.
- İki soruya bakıyorum: göstergeler kimi hedefliyor ve vaka haberlerde nerede görünür oldu?
- Birinci kaynak 311 alan adı; ikinci kaynak GDELT arşivindeki 5,9 milyon haber kaydı.
- Sunum yaklaşık 20 dakika.

**Ana mesaj:** Hedeflenen coğrafya ile görünür olan coğrafya.

**Atıf:** Meta, 2022; The GDELT Project, 2015

## 02. Sunum planı · 00:45–01:15

- Sunum dört bölümden oluşuyor.
- Önce vakayı ve literatürü konumlandırıyorum.
- Ardından iki veri kaynağını ve ölçüm kurallarını açıklıyorum.
- Bulgulardan sonra tartışma, sınırlılıklar ve sonuçla bitiriyorum.

**Ana mesaj:** Üç araştırma sorusu, iki veri kaynağı, beş bulgu.

**Atıf:** Sunum yapısı

## 03. Doppelgänger: tanınmış haber sitelerinin taklit edilmesi · 01:15–02:30

- EU DisinfoLab, kampanyanın en az Mayıs 2022’den beri sürdüğünü raporladı.
- Rapor, Bild, Spiegel, The Guardian ve ANSA gibi en az 17 markanın taklit edildiğini gösterdi.
- Meta aynı gün ağı kaldırdığını ve öncelikli hedefin Almanya olduğunu açıkladı.
- Meta ayrıca alan adı göstergelerini açık bir CSV dosyası olarak yayımladı.

**Ana mesaj:** Vaka, kamuya açık göstergelerle incelenebilir.

**Atıf:** Alaphilippe et al., 2022; Nimmo & Agranovich, 2022

## 04. Kavramsal çerçeve · 02:30–04:00

- Bennett ve Livingston dezenformasyonu, haber ya da belgesel biçimini taklit eden kasıtlı yanlışlar olarak tanımlar; taklit haber siteleri tam bu biçimdir.
- Wardle ve Derakhshan’ın çerçevesinde bu siteler üretim ve dağıtım altyapısıdır.
- Lazer ve Allen ile arkadaşları, neyin hangi paydaya göre sayıldığının açık olmasını ister.
- Leetaru ve Schrodt GDELT’i tanıtır; Kwak ve An GDELT ile haber coğrafyasının bölgesel olduğunu gösterir.

**Ana mesaj:** Bu çalışma: altyapı ve haber coğrafyası birlikte.

**Atıf:** Bennett & Livingston, 2018; Wardle & Derakhshan, 2017; Lazer et al., 2018; Allen et al., 2020; Kwak & An, 2014

## 05. Araştırma soruları · 04:00–05:00

- Birinci soru hedef coğrafyasını soruyor.
- İkinci soru alan adlarının sözcüksel yapısını soruyor.
- Üçüncü soru, kaldırma haberinin ne zaman ve hangi ülkelerin medyasında görünür olduğunu soruyor.
- İlk iki sorunun birimi alan adı, üçüncüsünün birimi haber makalesidir.

**Ana mesaj:** Birimler: 311 alan adı ve GDELT haberleri.

**Atıf:** Meta, 2022; The GDELT Project, 2015

## 06. Veri ve yöntem: iki kaynak, ayrı birimler · 05:00–06:20

- Meta dosyasından hedef etiketi ile ilk ve son DNS etiketi çıkarıldı.
- GDELT verisini API’den değil, literatürde kullanılan ham GKG arşivinden aldım: 20 Eylül – 11 Ekim 2022, 4.209 dosya.
- Haberler iki sabit kuralla seçildi; kaynak ülke GDELT’in alan adı listesinden, anılan yerler GKG konum alanından geliyor.
- Her ölçüm kendi biriminde ve taranan bütün kayıtlarla paydalanarak raporlanıyor.

**Ana mesaj:** Kaynak ülke, hedef ülke değildir.

**Atıf:** Meta, 2022; The GDELT Project, 2015, 2018; Leetaru & Schrodt, 2013

## 07. Denetlenmiş analiz kümesi 311 benzersiz alan adıdır. · 06:20–07:10

- Ham dosyada 350 kayıt, alan adı türünde 313 satır bulunuyor.
- İki yinelenen değer çıkarılınca analiz kümesi 311 oluyor.
- CIB ve Telegram bağlantıları farklı birimler olduğu için bu sayımdan ayrıldı.
- Her dönüşüm kaynak satırına ve dosya özetine bağlandı.

**Ana mesaj:** Farklı kayıt türleri aynı paydada toplanmadı.

**Atıf:** Meta, 2022

## 08. GDELT verisi test edilebilir: MD5, payda, isabet · 07:10–08:15

- Her arşiv dosyası, GDELT’in yayımladığı MD5 özetiyle karşılaştırıldı; 4.209 dosyanın hepsi eşleşti.
- Toplam 5.944.850 haber kaydı tarandı ve 511 tekil haber kurallarla eşleşti.
- Sabit tohumlu rastgele 32 başlıkta isabet yüzde 90,6; yüzde 95 güven aralığı 76 ile 97 arasında.
- Yanlış pozitifler kayıtlı; örneğin Putin’in dublörleri haberi. İkinci kodlayıcı için sütun açık.

**Ana mesaj:** Aynı komut, aynı dosyalarla aynı sayıları üretir.

**Atıf:** The GDELT Project, 2015; Wang et al., 2016; Hammond & Weidmann, 2014

## 09. Almanya, bu listenin hedef coğrafyasında baskındır. · 08:15–09:35

- Listenin 298 kaydı Almanya hedefli; bütün listedeki payı yüzde 95,8.
- Birleşik Krallık, Fransa ve İtalya birlikte sekiz kayıttır.
- Kalan beş kayıt Letonya, Ukrayna ve çoklu hedef kategorilerindedir.
- Grafik, ülke dağılımını gösterir; neden veya etkiyi açıklamaz.

**Ana mesaj:** Bu oran, yayımlanmış vakanın dağılımını betimler.

**Atıf:** Meta, 2022

## 10. Altı son etiket, 240 alan adında birleşir. · 09:35–10:50

- En sık son etiketler online, website, site, space, pw ve fun.
- Bu altı etiket toplam 240 alan adı içeriyor.
- Bu 240 kaydın tamamı kaynakta Almanya hedefli etiketlenmiş.
- Yapısal dağılımı ölçüyorum; fiyat, barındırma ve operatör bilgisi çıkarmıyorum.

**Ana mesaj:** Bu 240 kaydın tamamı Almanya hedeflidir.

**Atıf:** Meta, 2022

## 11. Aynı ilk DNS etiketi farklı son etiketlerle yinelenir. · 10:50–12:05

- Alan adları, soldaki ilk DNS etiketinin tam eşleşmesine göre gruplandı.
- 93 ayrı ilk etiketin 75’i birden fazla son etiketle yer alıyor.
- Bu gruplar 293 adresi kapsıyor; spiegel dokuz, bild sekiz, dailymail üç örnek içeriyor.
- Dize tekrarı, sahiplik veya içerik hakkında bağımsız hüküm vermiyor.

**Ana mesaj:** Adres çeşitliliği, yinelenen ilk etiketler çevresinde oluşur.

**Atıf:** Meta, 2022

## 12. Görünürlük iki günlük bir dalgadır · 12:05–13:35

- Meta’nın duyurduğu 27 Eylül’de 392 haber, ertesi gün 100 haber var.
- 511 haberin yüzde 96,3’ü bu iki günde; sonra görünürlük hızla sönüyor.
- Çizgi, aynı gün taranan bütün kayıtlara oranı gösteriyor; zirve haber hacmindeki dalgalanmadan kaynaklanmıyor.
- 511 adres yalnız 145 farklı başlık taşıyor; aynı ajans haberi çok sayıda sitede yayımlanmış.

**Ana mesaj:** Kaldırma haberi kısa ömürlü bir haber olayıdır.

**Atıf:** The GDELT Project, 2015 (GKG 2.0 ham arşivi); bu çalışmanın taraması

## 13. Hedef Avrupa; haber kaynağı ağırlıkla ABD · 13:35–15:35

- Harita gün gün birikiyor: renk, haberin yayımlandığı ülke.
- Meta hedeflerinin yüzde 95,8’i Almanya iken haberlerin yalnız 29’u, yani yüzde 5,7’si Alman kaynaklı; 373 haber ABD kaynaklı.
- Taranan kayıt sayısına oranlandığında Almanya ikinci sırada: 100 bin kayıtta 15,4 haber.
- Noktalar haberlerde anılan yerler; haberlerin yüzde 63,6’sı Almanya’yı anıyor.

**Ana mesaj:** Hedef coğrafyası ile haber coğrafyası örtüşmez.

**Atıf:** The GDELT Project, 2015, 2018; Kwak & An, 2014; Meta, 2022

## 14. Tartışma: hedeflenen kamu, görünür olan medya · 15:35–17:05

- Almanya’nın yüzde 95,8’lik payı, Meta ve EU DisinfoLab’ın nitel Almanya vurgusunu sayısal olarak destekliyor.
- Ama kaldırma haberi ağırlıkla ABD’de ve İngilizce üretildi; bu, Kwak ve An’ın bölgesel haber coğrafyası bulgusuyla karşılaştırılmaya değer.
- Ajans dağıtımı görünürlüğü çoğaltıyor: 511 adres, 145 başlık.
- Kampanya adı 2022 haberlerinde neredeyse hiç geçmiyor; adlandırma sonradan yaygınlaştı.

**Ana mesaj:** İki veri türü birbirinin yerine geçmez.

**Atıf:** Nimmo & Agranovich, 2022; Alaphilippe et al., 2022; Auswärtiges Amt, 2024; Kwak & An, 2014

## 15. Sınırlılıklar · 17:05–18:10

- Meta listesi bir örneklem değil, platformun tespit ve yayımlama seçimidir; bütün kayıtların tarihi aynı.
- GDELT yalnız izlediği kaynakları kapsar; ABD kaynakları fazla temsil edilir, bu yüzden oranlı ölçü de verildi.
- Kaynak ülke listesi 2018 tarihli ve okurun değil, yayının ülkesini verir.
- Kural isabeti yüzde 90,6; otomatik konumlar hata içerebilir (Hammond ve Weidmann, 2014).

**Ana mesaj:** Bulgular betimseldir; niyet veya etki iddiası yoktur.

**Atıf:** Meta, 2022; Allen et al., 2020; Hammond & Weidmann, 2014; Wang et al., 2016

## 16. Sonuç: yoğun hedef, tekrarlanan adres, uzak görünürlük · 18:10–19:30

- AS1: Göstergelerin yüzde 95,8’i Almanya hedefli.
- AS2: Altı son etiket 240 adresi kapsıyor; 75 ilk etiket farklı son etiketlerle tekrar ediyor.
- AS3: Kaldırma haberi iki günlük bir dalga; ağırlıkla ABD ve İngilizce medyada görünür oldu.
- Sonraki adım: ikinci kodlayıcıyla isabet ve yanlış negatif ölçümü, içerik çözümlemesi.

**Ana mesaj:** Katkı: altyapı ve haber coğrafyası, test edilebilir biçimde birlikte.

**Atıf:** Meta, 2022; The GDELT Project, 2015

## 17. Kaynakça · 19:30–20:00

- Kaynakçanın tamamı, 19 kaynak, bu tek sayfada APA 7 biçiminde.
- Birincil veriler Meta’nın gösterge dosyası ve GDELT GKG arşivi.
- Vaka bilgisi EU DisinfoLab, Meta ve Alman Dışişleri raporlarından.
- Kuram ve yöntem: Bennett ve Livingston, Wardle ve Derakhshan, Lazer, Allen, Leetaru ve Schrodt, Kwak ve An, Wang ve arkadaşları.

**Ana mesaj:** APA 7 · 19 kaynak · erişim ve doğrulama kayıtları KAYNAKLAR.md içinde

**Atıf:** APA 7; 19 kaynağın tamamı bu sayfada
