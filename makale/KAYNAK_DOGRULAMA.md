# Makale kaynaklarının doğrulama kaydı

31 Ekim – 1 Kasım 2026. “Doğrulandı” sütunu, künyenin bu çalışmada nasıl kontrol edildiğini gösterir. Bu çalışma ortamında doi.org, Crossref ve bazı yayıncı siteleri erişime kapalıydı; “DOI çözülmedi” notu taşıyan kaynakların DOI’si göndermeden önce doi.org’da açılmalıdır.

| Kaynak | Doğrulandı | Not |
|---|---|---|
| Alaphilippe vd. (2022) | Rapor PDF’i ve ikincil kayıtlar | Gri literatür |
| Aras ve Yıldırım (2022) | DOAJ dizin kaydı (başlık, dergi, Eylül 2022) | Yazar adları ve sayfa aralığı dergi sayfasından kontrol edilmeli |
| Auswärtiges Amt (2024a) | Ocak 2024 raporu bağlantısı (inceleme notundan) | 50.000 hesap / 1,8 milyon gönderi bu rapordan; dönem 20.12.2023–20.01.2024 |
| Auswärtiges Amt (2024b) | Haziran 2024 raporu bağlantısı ve basın kayıtları | Resmî rapor |
| Bennett ve Livingston (2018) | Yayıncı künyesi ve DOI | |
| Caliskan (2019) | Künye | DOI çözülmedi |
| Eady vd. (2023) | Yayıncı sayfası, DOI | |
| Fridman (2018) | OUP katalog kaydı | |
| Galeotti (2018) | Foreign Policy bağlantısı | Gri literatür |
| Galtung ve Ruge (1965) | Künye (klasik çalışma) | DOI çözülmedi |
| Golovchenko (2020) | IDEAS/RePEc kaydı | DOI, kayıt URL’sinden |
| Hammond ve Weidmann (2014) | Depo kaydı, DOI | |
| Hoffman (2007) | Künye | DOI yok |
| Hoffmann vd. (2022) | Yayıncı künyesi, DOI | |
| Hybrid CoE (t.y.) | Kurum sayfası | |
| Jungherr ve Rauchfleisch (2024) | Yayıncı künyesi, DOI | |
| Karlsen (2019) | DOI bağlantısı | Dergi bugün *Humanities and Social Sciences Communications* adını taşıyor |
| Korczyński vd. (2018) | Künye | DOI çözülmedi |
| Kwak ve An (2014) | Springer kaydı, DOI | |
| Lanoszka (2016) | Künye | DOI çözülmedi |
| Lazer vd. (2018) | Yazar sürümü okundu | |
| Leetaru ve Schrodt (2013) | Künye | Bildiri, DOI yok |
| Meta (2022) | Sabit commit, SHA-256 | Birincil veri |
| Meister (2016) | NATO Review sayfası ve arşiv kopyası | Lisa vakası |
| Ministère de l’Europe et des Affaires étrangères (2023) | Bakanlık açıklaması (13.06.2023) | VIGINUM tespiti; yaptırım değil |
| Miskimmon vd. (2013) | Künye | DOI çözülmedi |
| Mumford ve Carlucci (2023) | Depo kaydı, DOI | |
| Nemeth (2002) | NPS Calhoun kaydı | Yüksek lisans tezi |
| Nimmo ve Agranovich (2022) | Yayıncı bağlantısı ve basın kayıtları | Platform raporu |
| Özdemir ve Eminoğlu (2022) | CEEOL kaydı | 15(1), 67–84 |
| Pamment ve Tsurtsumia (2025) | Rapor PDF bağlantısı | Gri literatür |
| Paul ve Matthews (2016) | Künye | DOI çözülmedi |
| Renz (2016) | Depo kaydı, DOI | |
| Rogers ve Righetti (2025) | Yayıncı künyesi, DOI | Cilt/sayı henüz yok |
| The GDELT Project (2015, 2018) | Veri dosyaları indirildi, MD5/SHA-256 | Birincil veri |
| Tian vd. (2018) | Künye | DOI çözülmedi |
| Wang vd. (2016) | Cilt, sayı, sayfa | DOI (10.1126/science.aaf6758) iki bağımsız kaynakta aynı, doi.org’da çözülmedi |
| Wardle ve Derakhshan (2017) | Kurum yayını | |
| Watanabe (2017) | LSE depo kaydı, DOI | |
| Wigell (2019) | Künye | DOI çözülmedi |
| Council of the European Union (2023) | EEAS basın açıklaması (28.07.2023) okundu | SDA ve Structura “RRN” kampanyası nedeniyle listelendi; tüzük numarası yerine basın açıklamasına atıf yapıldı |
| U.S. Department of the Treasury (2024) | Basın bülteni JY-2195, ikincil kopyalar | 20.03.2024 |
| U.S. Department of Justice (2024) | Basın bülteni (justice.gov) | 04.09.2024; 32 alan adı |

## Kodlamalar

Bütün isabet ve duyarlılık kodlamaları yapay zekâ destekli tek bir kodlayıcı tarafından yapılmıştır (makale, Bölüm 7). Yazarın bağımsız kodlaması için `makale/kodlama/insan_kodlama_formu.csv` hazırdır; doldurulduğunda `python scripts/gdelt_census.py` uyum oranını ve Cohen κ değerini hesaplar.
