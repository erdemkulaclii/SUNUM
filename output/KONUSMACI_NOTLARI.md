# Konuşmacı metni — 15 dakika

Durum: Gerçek Meta IOC verisi analiz edildi; GDELT sonuçları henüz elde edilmedi. Bu not, sunumda korunmalıdır.

## 1. Hibrit savaşın görünmez cephesi · 00:00–00:40

Bugün görünmez cepheyi, yani haber ve platform ağlarında dolaşıma giren etki operasyonlarını tartışacağım. Temel sorum, Rusya bağlantılı olarak raporlanan ağların Batı Avrupa yönelimini coğrafi olarak nasıl inceleyebileceğimiz. Burada iki farklı kanıt türünü ayırıyorum: Meta tarafından yayımlanmış somut alan adı göstergeleri ve bu vakaların haberlerdeki görünürlüğünü ölçmek için tasarlanan GDELT katmanı. İlk katman gerçek verilerden hesaplandı. GDELT katmanı ağ erişimi nedeniyle henüz indirilmedi. Bu nedenle sunum, tamamlanmış bir GDELT bulgu raporu olarak değil, doğrulanabilir vaka analizi ve uygulanabilir araştırma tasarımı olarak okunmalıdır.

Kaynak: Meta IOC listesi [1–2]; GDELT sonuçları üretilmedi

## 2. Asıl soru: Nerede, hangi kanıtla? · 00:40–01:45

Bir coğrafi haritanın ikna edici görünmesi, doğru şeyi ölçtüğü anlamına gelmez. Bu çalışmada önce ölçülen nesneyi tanımlıyorum. İlk soruda birimimiz, yayımlanmış bir listede bulunan benzersiz alan adıdır. İkinci soruda birimimiz GDELT tarafından indekslenen haber URL’si olacaktır. Bir haberin Fransa hakkında olması, Fransa’daki bir kaynaktan yayımlanması ve Fransa’daki seçmenleri hedeflemesi farklı önermelerdir. Hipotezimiz bunların örtüşmek zorunda olmadığıdır. Dolayısıyla tek bir yoğunluk haritası yerine, kaynak konumu ve doğrulanmış hedef konumu için ayrı katmanlar gerekir. Bu ayrım, araştırmanın geçerliliğini belirler.

Kaynak: Yöntemsel değerlendirme

## 3. Hibrit tehditten ölçülebilir vakaya · 01:45–02:45

Hibrit savaş kavramını, her çevrim içi tartışmayı savaş faaliyeti sayacak kadar genişletmemek gerekir. Bu sunum, askerî sonuçları ölçmüyor; bilgi alanındaki manipülasyon mekanizmalarını inceliyor. Dezenformasyon içerikle ve yanıltma amacıyla ilgilidir. FIMI ise davranışın yabancı aktörlerle bağlantısı, koordinasyonu ve manipülatif niteliği üzerinde durur. Meta’nın CIB kategorisi de içerikteki her önermenin yanlış olduğunu söylemez; hesapların ve varlıkların davranışsal koordinasyonunu tanımlar. Bu nedenle IOC listesinde bulunmak ile bir haber metninin yanlışlığı ayrı ayrı doğrulanmalıdır. Operasyon düzeyindeki etiketleri otomatik olarak bütün kullanıcı ve haber kayıtlarına taşımıyoruz.

Kaynak: Kavramsal çerçeve; Meta README [2]. FIMI resmî kaynak doğrulaması bekliyor.

## 4. Kanıt zinciri: Atıf → gösterge → haber · 02:45–03:50

Araştırmanın omurgası kanıt zinciridir. Aktör atfı için ilk adım platform veya kamu kurumu raporudur. İkinci adım, bu raporla ilişkilendirilen somut göstergeleri ve metaveriyi kaydetmektir. Üçüncü adım, GDELT üzerinde kampanya adı ve gerekirse doğrulanmış göstergelerle ilişkili haberleri aramaktır. Son adımda, haberin operasyonu yayması ile operasyonu eleştirmesini ayırırız. Burada önemli bir sınırlılık var: Meta veri dosyası indirildi ve kaynağı arşivlendi; atfı bağımsız kamu raporlarıyla çapraz doğrulama bu ortamda henüz tamamlanmadı. Bu nedenle Rusya atfını bizim keşfimiz gibi değil, kaynağın değerlendirmesi olarak sunuyoruz.

Kaynak: Meta veri dosyası, index.json ve README [1–3]

## 5. Gerçek veri: 350 kayıt, 313 alan adı · 03:50–05:00

Bu slayttaki bütün sayılar doğrudan indirilen CSV dosyasından hesaplandı. Dosyada toplam üç yüz elli kayıt bulunuyor. Bunların üç yüz on üçü alan adı satırı, yirmi ikisi CIB URL’si ve on beşi Telegram URL’sidir. Aynı alan adının tekrarını önlemek için küçük harfe dönüştürülmüş değerler üzerinde benzersizlik kontrolü yaptım. İki yinelenen alan adı çıkarıldı; üç yüz on bir benzersiz alan adı kaldı. Dosyanın başlığı hem Çin hem Rusya vakalarını içerdiği için başlığa bakarak bütün satırları tek operasyon saymadım. Özellikle Çin etiketli iki dilekçe URL’si, alan adı filtresinin dışında kaldı. Bu seçim kuralı ve ham veri dosyası teslim paketinde bulunuyor.

Kaynak: [1] CSV; [3] index.json. Ham dosya + SHA-256 teslim paketinde.

## 6. Harita: Yayımlanan hedef etiketleri · 05:00–06:15

Haritada görülen noktalar alan adlarının sunucu koordinatları değildir. Kaynak dosyanın hedef ülke etiketlerini ülke düzeyindeki temsil noktalarında gösteriyorum. Böylece ağ altyapısının bulunduğu yer ile hedef kitlenin bulunduğu yeri karıştırmıyorum. Almanya, Fransa, Birleşik Krallık ve İtalya bu vaka için çalışma odağını oluşturuyor. İtalya ve Birleşik Krallık farklı coğrafi sınıflandırmalarda başka Avrupa alt bölgelerine yerleştirilebilir; bu yüzden kullandığım kapsamı açıkça operasyonel bir seçim olarak belirtiyorum. Harita yalnızca yayımlanmış göstergeleri içeriyor. İşaret bulunmayan başka ülkeler için operasyon olmadığı sonucuna varılamaz. Bu ülkelerde gözlemimiz bulunmaması ile gerçek dünyada faaliyet bulunmaması farklıdır.

Kaynak: [1] Hedef etiketleri; [4] Natural Earth ülke sınırları

## 7. Almanya yoğunluğu: Güçlü ama dar bulgu · 06:15–07:30

Grafik, yayımlanan listenin Almanya yönelimini çok açık gösteriyor. Ancak tam olarak hangi paydayı kullandığımızı belirtmeliyiz. İki yüz doksan sekiz alan adı, üç yüz on bir benzersiz alan adının yüzde doksan beş virgül sekizidir. Yalnızca odak ülkeleri kapsayan üç yüz altı kayıt içinde ise pay yüzde doksan yedi virgül dörttür. Bu oranlar seçilmiş bir gösterge listesinin kompozisyonunu anlatır. İki yüz doksan sekiz alan adı, iki yüz doksan sekiz ayrı operasyon demek değildir. Aynı ağ çok sayıda alan adını döndürebilir. Ayrıca Meta’nın tespit ettiği ve yayımlamayı seçtiği varlıklar bütün evreni oluşturmaz. Bu nedenle grafiği Avrupa’daki toplam dezenformasyonun ülkelere dağılımı olarak okumuyoruz.

Kaynak: [1] Yeniden hesaplanan değerler; hedef_ulke_sayimlari.csv

## 8. Mekanizma: Haber markasının taklidi · 07:30–08:35

Alan adları, mekanizmayı somutlaştırıyor. Bild, Spiegel veya Daily Mail gibi tanınan haber markalarına benzeyen adlar, farklı uzantılarla kullanılıyor. Böyle bir tasarım, kullanıcının tanıdığı bir medya kuruluşunun güvenilirliğini ödünç alma girişimiyle tutarlıdır. Bununla birlikte yalnızca benzer bir ad görmek, tek başına koordinasyon veya Rusya atfı sağlamaz. Burada örnekleri zaten kaynak dosyada CIB göstergesi olarak listelendikleri için tartışıyoruz. Örnek alan adlarını güvenli biçimde, köşeli parantezli noktayla gösteriyorum; sunum sırasında bunları ziyaret etmek gerekmiyor. Özellikle güncel sahiplik, kapanma veya yeniden kayıt durumu bu tarihsel veri dosyasından çıkarılamaz.

Kaynak: [1] Örnekler doğrudan CSV kayıtları; güncel siteler ziyaret edilmedi.

## 9. GDELT: Neyi ölçer, neyi söylemez? · 08:35–09:45

GDELT dünya haberlerini tarayan bir veri altyapısıdır. Bu araştırma için DOC API üzerinden haber seçkileri, GKG üzerinden de haberlerde tanınan yerler ve temalar kullanılabilir. Fakat haberin kaynak ülkesi ile haberin konuştuğu ülke aynı değildir. Örneğin Birleşik Krallık merkezli bir yayın, Almanya’yı hedefleyen sahte haber ağını eleştiren bir haber yayımlayabilir. Böyle bir kayıt kaynak coğrafyasında Birleşik Krallık, olay veya konu coğrafyasında Almanya ile ilişkilendirilebilir. Hedef ülkeyi ise yalnızca bu iki alandan otomatik türetmek doğru olmaz. Ayrıca GDELT’in indeksleme zamanı, içeriğin ilk üretim veya operasyonun başlangıç zamanı olarak kabul edilmemelidir.

Kaynak: [5–6] Resmî GDELT dokümantasyon bağlantıları; canlı veri doğrulanmadı.

## 10. GDELT sorgusu: Tekrarlanabilir protokol · 09:45–10:55

Önerdiğim sorgu önce kampanya adlarını kullanarak ilgili haberlere ulaşmayı amaçlıyor. Bu adlar aynı kampanyayı ifade etmediği için son analizde hepsini tek kategoriye yığmamak gerekir. Dil varyasyonlarını eklemek ve çıkan haberleri elle elemek gerekir. Teslim edilen betik DOC API için ham yanıtları ve sorgu metaverisini kaydedecek şekilde hazırlandı; fakat gerçek indirme henüz başarılmadı. Güncel keşif penceresi iki bin yirmi altı yılı içindedir. Bu pencereyi iki bin yirmi iki tarihli IOC sayımlarıyla doğrudan zaman karşılaştırmasına sokmuyoruz. İki bin yirmi iki için GKG arşivi veya BigQuery kullanmak gerekir. API’nin iki yüz elli haber sınırı tam evren sağlamaz.

Kaynak: scripts/fetch_gdelt.py; bu protokol henüz ampirik sonuç üretmedi.

## 11. Üç harita, üç farklı değişken · 10:55–12:00

Tamamlanmış çalışmada üç ayrı harita sunmak istiyorum. Birinci harita hedef coğrafyasını gösterecek; bugün bu harita Meta’nın yayımladığı etiketlerle üretildi. İkinci harita GDELT’te ilgili haberleri yayımlayan kaynakların coğrafyasını gösterecek. Üçüncü harita haber metinlerinde anılan yerleri gösterecek. Bu üç haritanın birbirinden ayrılması, bir yerde fazla haber üretilmesinin o yerin daha çok hedeflendiği anlamına gelmediğini anlatacak. Veri eksikliği olduğunda ülkeyi sıfır değerle boyamak yerine veri yok olarak işaretlemek gerekir. Özellikle kaynak listesine alınmayan bir ülke için haritada beyaz alan bırakmak bile yanlış yorumlanabileceğinden, açıklama ve kapsam etiketleri gereklidir.

Kaynak: Yöntemsel değerlendirme

## 12. Geçerlilik: Görünürlük, etki değildir · 12:00–13:10

Çalışmanın en kritik sınırı, görünürlüğü etkiyle karıştırma riskidir. Bir operasyon hakkında çok haber çıkması, o operasyonun başarılı olduğu anlamına gelmez. Tam tersine, kapsamlı bir ifşa raporu haber hacmini yükseltmiş olabilir. Haberleri kaynak ülkenin toplam haber hacmine bölerek karşılaştırmak bazı hacim farklarını azaltır, ama dil ve indeksleme yanlılığını ortadan kaldırmaz. Meta listesinde de platformun tespit ve yayım süreçleri belirleyicidir. Kamuoyunun ikna edilip edilmediğini göstermek için anket, maruziyet verisi veya uygun araştırma tasarımı gerekir. Bu çalışmanın bugün savunabileceği iddia daha dardır: yayımlanmış göstergelerin ülke etiketleri ve gelecekte ölçülecek haber görünürlüğü.

Kaynak: Yöntemsel değerlendirme

## 13. Bulgu, yorum ve açık kalan iş · 13:10–14:10

Sonuçları üç düzeyde ayırarak bitiriyorum. Birinci düzey doğrudan veri bulgusudur: incelenen alan adı listesinde Almanya hedefli etiketler baskındır. İkinci düzey, bu listenin belirli bir vaka içindeki yönelimi gösterdiği yorumudur. Üçüncü düzey ise henüz desteklenmeyen iddialardır: bütün Rusya bağlantılı operasyonların dağılımı, hedef toplumdaki gerçek erişim ve kamuoyu etkisi bu veriyle hesaplanamaz. GDELT katmanı tamamlandığında, bu yönelimin haber görünürlüğüyle nasıl ilişkilendiği araştırılabilir. Ancak bugün bu ilişkiyi kurulmuş gibi sunmuyorum. Araştırmanın akademik değeri yalnızca bir harita üretmesinde değil, haritanın hangi kanıttan ve hangi sınırlılıkla üretildiğini göstermesindedir.

Kaynak: Yöntemsel değerlendirme

## 14. Ana mesaj: Haritayı kanıtla birlikte okuyun · 14:10–15:00

Bu sunumdan kalmasını istediğim ana fikir şu: bilgi operasyonlarının haritasını çıkarmak yalnızca coğrafi veri bulmak değildir. Önce neresi sorusunun neyi ifade ettiğini belirlemek gerekir. Hedef ülke mi, kaynak ülke mi, haber metnindeki ülke mi? İkinci olarak sayılan şeyin ne olduğunu açık tutmalıyız: alan adı mı, haber mi, kullanıcı mı? Üçüncü olarak belirsizliği saklamamalıyız. Bugünkü analiz gerçek bir IOC dosyasına dayanıyor, fakat GDELT sonuçları tamamlanmış değil. Bu ayrımlara sadık kalındığında, hem daha dürüst hem de tekrar üretilebilir bir akademik araştırma kurulabilir. Ek slaytlar, veri ve yöntem sorularını ayrıntılandırıyor.

Kaynak: Yöntemsel değerlendirme

## 15. EK A · Veri sözlüğü ve dönüşümler · Soru-cevap eki

Bir alan adını coğrafi olarak kodlamak için ülke uzantısını kullanmadım. Kaynağın açık hedef etiketi varsa onu aldım. Çoklu hedef etiketi ayrı tutuldu. Böylece kaynakta olmayan ayrıntı uydurulmadı.

Kaynak: [1]; scripts/build_presentation.py

## 16. EK B · GDELT kodlama ve kalite kontrolü · Soru-cevap eki

Bu ek bir uygulanmış kalite raporu değil, önceden belirlenmiş protokoldür. Kodlayıcı sayısı ve uyum katsayısı gerçekleşmeden sonuç olarak yazılamaz. Dil bazlı hata ve kapsam ayrıca raporlanmalıdır.

Kaynak: Yöntemsel değerlendirme

## 17. EK C · Tarihsel GDELT için doğru yol · Soru-cevap eki

Tarihsel eşleştirme yapılacaksa öncelikle aynı dönemden GKG veya başka yetkili arşiv verisi gerekir. Tek bir on beş dakikalık dosyayı indirip bütün ayı temsil ediyormuş gibi göstermek uygun olmaz. Tam kapsam mümkün değilse örneklem tasarımı açıkça belirtilmelidir.

Kaynak: [5–6]; tarihsel analiz henüz yürütülmedi.

## 18. EK D · Jürinin sorabileceği sorular · Soru-cevap eki

Zor sorular geldiğinde verinin cevaplamadığı bir soruya tahminle cevap vermeyin. Özellikle atıf, nedensellik ve etki sorularında kaynak türünü ve ölçüm birimini tekrar edin.

Kaynak: Yöntemsel değerlendirme

## 19. EK E · Kaynakça: Erişilen kanıtlar · Soru-cevap eki

Aktif kaynak bağlantıları KAYNAKLAR.md dosyasında bulunuyor. Veri dosyaları yerel olarak teslim ediliyor. Meta verisi MIT lisansıyla, Natural Earth ise kamu malı olarak yayımlanmıştır. Kaynağın sonraki değişikliklerine karşı arşiv özeti ve dosya hashleri saklanmıştır.

Kaynak: Tam URL’ler ve SHA-256: KAYNAKLAR.md / veri_manifest.json

## 20. EK F · Kaynakça: Erişim bekleyenler · Soru-cevap eki

Bu slayt, erişilmiş kaynakları erişilmemiş kaynaklarla karıştırmamak için ayrıdır. Resmî raporlar açılıp sayfa ve bölüm düzeyinde denetlenmeden onlardan yeni sayı veya kesin bulgu aktarılmamalıdır.

Kaynak: Yöntemsel değerlendirme

## 21. EK G · Teslim ve tamamlanma durumu · Soru-cevap eki

Sunumun kapsamı ve veri durumu her paylaşımda korunmalıdır. Ağ erişimi açılıp veri analizi yapılırsa bu slayt ve ana sonuç bölümü gerçek yeni bulgularla güncellenmelidir.

Kaynak: Yöntemsel değerlendirme
