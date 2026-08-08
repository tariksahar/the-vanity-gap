# Faz 0 — Fizibilite Test Raporu

**Tarih:** 6 Ağustos 2026
**Kapsam:** DESIGN.md §7.1, §7.4, §7.6, §7.7, §7.9, §7.10 (teşhis testleri)
**Yöntem:** mavi.com üzerinde canlı tarayıcı incelemesi — ham HTML çekimi, ağ isteği izleme,
DOM geometrisi ölçümü, 60 ürünlük rastgele örneklem, 254 yorumluk toplu analiz
**Toplam istek:** yaklaşık 180, hepsi 200 ile döndü, engellenme yok

---

## Özet tablo

| Test | Konu | Sonuç | Etki |
|---|---|---|---|
| §7.1 | Ürün meta verisi | ✅ **GEÇTİ** | Tasarım ayakta, tüm eksenler mevcut |
| §7.2 | Katalog (bonus) | ✅ **GEÇTİ** | 5.629 renk varyantı / 3.582 model |
| §7.4 | Sıfır sorusu | ✅ **ÇÖZÜLDÜ** | `0` = cevaplanmamış |
| §7.5 | Stok tavanı (bonus) | ✅ **DOĞRULANDI** | 6'da kesiliyor |
| §7.6 | SKU düzeyi kalıp puanı | ❌ **YOK** | Plandan çıkar |
| §7.7 | Beden tablosu | ❌ **YOK** | §5.3 düzeltmesi yeniden kurulmalı |
| §7.9 | İl bazında stok | ❌ **YOK** | §1.9 bölgesel test iptal |
| §7.10 | `reviewDisplayStatus` | ✅ **ÇÖZÜLDÜ** | Moderasyon değil, kalıp bayrağı |
| — | **Yeni: farklı eksik oranı** | ⚠️ **TEHDİT** | DiD varsayımını doğrudan zorluyor |
| — | **Yeni: hacim tahmini** | ⚠️ **DÜŞÜK** | Hedefin yarısı civarı |

---

## §7.1 — Ürün meta verisi ✅

**Soru:** Cinsiyet, kategori ve kalıp ham HTML'de her üründe güvenilir biçimde var mı?

**Ne yapıldı:** Pilot ürünün ham HTML'inde `Slim Fit` metninin geçtiği üç konum tarandı.
Üçüncüsü `google_tag_params` adlı, sunucu tarafında basılmış bir JavaScript nesnesi çıktı.

### Bulunan blok

```js
'pagetype': 'product',
'prodid': '065574-620',
'baseProduct': '065574',
'pname': "Beyaz Basic Tişört",
'pvalue': '369.99',
'p_actual_price': '369.99',
'theme': ["Yeni Sezon", "Back to School"],
'waist': "",
'fit': "Slim Fit / Dar Kesim",
'cuff': "",
'zipOrButton': "Düğmesiz",
'CD_Color': "Beyaz",
'pcat': "Tişört",
'psubcat': "Basic",
'pgender': "Erkek",
'sleeve': "Kısa Kol",
'otherinfo': [...]
```

### Alan eşlemesi

| Alan | Anlamı | Şemadaki karşılığı |
|---|---|---|
| `prodid` | Renk varyantı kodu | `colour_variant_id` |
| `baseProduct` | **Model kodu** | `style_id` — §1.7 kümeleme birimi |
| `pgender` | Cinsiyet | Karşılaştırma ekseni 2 |
| `pcat` | Kategori | Karşılaştırma ekseni 1 |
| `psubcat` | Alt kategori | Alt kırılım |
| `fit` | **Kalıp** | Karşılaştırma ekseni 3 |
| `pvalue` | Güncel fiyat | §5.13 |
| `p_actual_price` | Liste fiyatı | §5.13 — indirim = fark |
| `waist`, `sleeve`, `cuff` | Giysi nitelikleri | Ek kontrol |
| `CD_Color` | Renk | Stok analizi için |

### Kapsama testi — 60 rastgele ürün

| Alan | Dolu | Oran |
|---|---|---|
| `prodid` | 60/60 | 100% |
| `baseProduct` | 60/60 | 100% |
| `pname` | 60/60 | 100% |
| `pvalue` | 60/60 | 100% |
| `p_actual_price` | 60/60 | 100% |
| `pgender` | 60/60 | 100% |
| `pcat` | 60/60 | 100% |
| `psubcat` | 60/60 | 100% |
| `CD_Color` | 56/60 | 93% |
| `sleeve` | 34/60 | 57% |
| `fit` | 42/60 | 70% |
| `waist` | 8/60 | 13% |

**Kritik ayrım:** `fit` boş çıkan 18 ürünün tamamı aksesuar, çorap, çanta, kozmetik gibi
kalıbı olmayan ürünler. **Hedef kategorilerde (yetişkin Tişört / Gömlek / Jean) kapsama
26/26 = %100.**

### Yan bulgular

- Breadcrumb cinsiyet ve kategoriyi ikinci kez taşıyor (`Anasayfa | Kadın | Jean | New York`)
  — çapraz doğrulama için kullanılabilir.
- Jeanlarda kalıp daha zengin: `Straight, Yüksek Bel, Düz Paça` (kesim + bel yüksekliği + paça).
  Üst giyimde tek boyut. Alt giyim kontrolü için ek granülerlik.
- İndirim gerçekten görünür: `101441-86391` ürününde 1.259,99 TL / 1.799,99 TL = **-%30**.
  §5.13'ün uygulanabilir olduğu doğrulandı.

**Verdict: GEÇTİ.** Tasarımın üç ekseni de tek bir sunucu tarafı bloktan geliyor. Ayrıştırıcı
tek bir regex ile yazılabilir.

---

## §7.2 — Katalog (bonus) ✅

`sitemap.xml` bir indeks; içindeki `Product-tr-TRY-*.xml` dosyası `http://` ile listeleniyor,
`https://` olarak yeniden yazılması gerekiyor (aksi halde karışık içerik hatası).

| Ölçüm | Değer |
|---|---|
| Ürün sitemap boyutu | 1.825.296 bayt |
| `/p/` içeren URL girdisi | 5.629 |
| Benzersiz renk varyantı | 5.629 |
| **Benzersiz model kodu** | **3.582** |

**Uyarı:** Katalog hedef kapsamdan çok geniş. 60 ürünlük örneklemde 28 farklı kategori çıktı —
Beauty, Cüzdan, Çanta, Çorap, Aksesuar, Plaj dahil. Ayrıca **çocuk ürünleri var**
(Kız Çocuk, Erkek Çocuk). Filtreleme zorunlu.

### Örneklemde cinsiyet dağılımı

| Cinsiyet | Ürün |
|---|---|
| Kadın | 16 |
| Erkek | 10 |
| Kız Çocuk | 3 |
| Erkek Çocuk | 1 |

*(ilk 30'luk örneklem)*

---

## §7.4 — Sıfır sorusu ✅ ÇÖZÜLDÜ

**Soru:** `percentageSizeRating = 0` "çok dar" mı, "cevaplanmadı" mı?

**Cevap: cevaplanmadı.** Üç bağımsız kanıt hattı aynı yönü gösteriyor.

### Kanıt 1 — Widget işaretçisinin konumu

Sayfadaki Dar/İdeal/Geniş çubuğunda siyah noktanın konumu piksel cinsinden ölçüldü ve çubuk
genişliğine oranlandı.

| Ürün | n | Sıfır | Sıfırlı ortalama | Sıfırsız ortalama | Sıfırsız medyan | **Ölçülen işaretçi** |
|---|---|---|---|---|---|---|
| `065574-620` | 163 | 89 | 24,5 | 54,1 | 50 | **%50,0** |
| `1211290-90160` | 10 | 3 | 52,5 | 75,0 | 75 | **%75,7** |

İşaretçi her iki üründe de sıfırsız değere oturuyor, sıfırlı değerden çok uzak.

### Kanıt 2 — Tamamı sıfır olan ürün

`0612315-71538` ürününün 7 yorumunun **tamamında** `pct = 0`.

Eğer 0 skalada gerçek bir değer olsaydı (çok dar), işaretçi çubuğun **sol ucunda, %0'da**
durmalıydı. Ölçülen konum: **%-24,3** — yani çubuğun tamamen dışında. Bu bir "veri yok"
render artefaktı, skalada bir konum değil.

### Kanıt 3 — `reviewDisplayStatus` ile birebir örtüşme

254 yorumluk çapraz tablo:

| | pct=0 | pct=25 | pct=50 | pct=75 | pct=100 |
|---|---|---|---|---|---|
| **disp = false** | 100 | 3 | 4 | 0 | 0 |
| **disp = true** | 7 | 12 | 103 | 16 | 9 |

`disp=false ⟺ pct=0` eşdeğerliği **240/254 = %94** vakada tutuyor.

### Kanıt 4 — Yıldız profili

| pct | n | Ortalama yıldız |
|---|---|---|
| 0 | 107 | 3,93 |
| 25 | 15 | 4,07 |
| 50 | 107 | 4,60 |
| 75 | 16 | 3,69 |
| 100 | 9 | 3,67 |

Sıfır grubunun yıldız profili uç bir gruba değil, genel popülasyona benziyor.

**Karar:** `0` → eksik. `fit_score` eşlemesi DESIGN.md §1.3'teki haliyle kalıyor.

---

## §7.5 — Stok tavanı (bonus) ✅

60 üründe gözlenen `stockLevel` maksimumu: **6**. Hiçbir üründe aşılmadı.

Gözlenen değerler: `{0, 2, 3, 4, 5, 6}`

**Karar:** `min(gerçek, 6)` yorumu doğrulandı. Sağdan sansürlü modelleme zorunlu (§5.8).
Sezon başı popüler ürünlerde daha geniş bir örneklemle teyit edilmeli.

---

## §7.6 — SKU düzeyi `averageSizeRating` ❌

269 SKU tarandı. **Dolu olan: 0.**

Alan varyant dizisinde duruyor ama hiçbir zaman doldurulmuyor. `averageLengthRating` de aynı.

**Karar:** Şemadan ve plandan çıkar. Beden bazında kalıp algısı yalnızca yorum verisinden
türetilecek.

---

## §7.7 — Beden tablosu ❌ ÖNEMLİ

`/beden-tablosu` sayfası çekildi ve tarayıcıda render edildi.

| Ölçüm | Sonuç |
|---|---|
| HTTP durumu | 200 |
| Ham HTML boyutu | 335.138 bayt |
| Ham HTML'de `<table>` | **0** |
| Render sonrası `<table>` | **0** |
| `Göğüs` geçişi | 0 |
| `Kalça` geçişi | 0 |
| Beden tablosu görseli | 0 |
| iframe | 0 |
| Toplam metin | 6.736 karakter |

Sayfa bir pazarlama içeriği — beden seçimi hakkında düz yazı, ölçü tablosu yok.
Ürün sayfalarında da beden rehberi bağlantısı veya modalı bulunamadı.

**Sonuç: Mavi vücut ölçüsü — etiket eşlemesini yayınlamıyor.**

### Etkisi

DESIGN.md §5.3'teki etiket şişmesi düzeltmesi, markanın yayınlanmış tablosuyla yapılamaz.
Kadın kolu bu düzeltme olmadan yorumlanamaz, dolayısıyla alternatif gerekli.

### Üç yedek yol

1. **Alt giyim için sorun yok.** Jean bedenleri zaten bel inç cinsinden; etiket doğrudan ölçü.
2. **Manken ölçüleri.** Her ürün sayfasında markanın kendi beyanı duruyor:
   *"Boy: 189 cm / Bel: 78 cm / Göğüs: 94 cm / Kalça: 88 cm, Üst: L, Alt: Bel 32"*.
   Bu, markanın "şu vücut L giyer" ifadesidir. Yüzlerce ürün üzerinden toplanınca cinsiyet ve
   kategori bazında **ima edilen santimetre-etiket eşlemesi** çıkarılabilir. Kusurlu ama gerçek.
   Bu alanın kapsamı ayrıca test edilmeli — yeni bir Faz 0 maddesi.
3. **Dükkân ölçümü.** Aile dükkânında fiziksel ölçüm; küçük örneklem ama altın standart
   doğrulama.

---

## §7.9 — İl bazında stok ❌ İPTAL

**Ne yapıldı:** "Mağazada Bul" modalı açıldı, beden 27 / boy 30 seçildi, İstanbul → Beşiktaş
seçildi, "Ara" tıklandı, ağ isteği yakalandı.

### Bulunan iki endpoint

```
GET /magazalar/get/districts?provinceCode=P_ISTANBUL

GET /magazalar/get-stores
    ?province=P_ISTANBUL
    &district=D_ISTANBUL_BESIKTAS
    &size=27
    &length=30
    &barcode=8684080545884
    &page=0
```

Barkod alanı, varyant dizisindeki EAN ile aynı — yani eşleştirme mümkün.

### Ama çalışmıyor

Üç varyantla test edildi:

| İstek | Durum | Yanıt boyutu |
|---|---|---|
| Tam parametre | 200 | 19.856 bayt |
| `district` kaldırıldı | 200 | 19.856 bayt |
| `size` ve `length` kaldırıldı | 200 | **19.856 bayt** |

**Yanıtlar bayt bayt aynı.** Beden ve barkod parametreleri sonucu değiştirmiyor.

Yanıt içeriği (9 mağaza döndü):

```
features, storeImages, address, displayName, isClickAndCollectStore,
name, formattedDistance, description, openingHours, geoPoint, storeId
```

**Stok alanı yok.** Endpoint konuma göre mağaza listeliyor, stoğa göre filtrelemiyor.

**Karar:** DESIGN.md §1.9 bölgesel plasebo testi bu kaynakla yapılamaz. Plandan çıkarılsın.
Bu bir kayıp değil — inşa edilmeden önce öğrenildi.

---

## §7.10 — `reviewDisplayStatus` ✅ ÇÖZÜLDÜ

254 yorumda dağılım:

| Değer | Sayı |
|---|---|
| `true` | 147 |
| `false` | 107 |

Her zaman `true` değil. Ama §7.4'te görüldüğü gibi `false` olması neredeyse tamamen
`pct = 0` ile örtüşüyor (%94).

**Yorum:** Bu bir moderasyon bayrağı değil, "kalıp değerlendirmesi verilmiş mi" bayrağı.

**İki sonuç:**
- İyi haber: gizlenmiş yorum yok, yani görmediğimiz bir seçilim katmanı yok.
  DESIGN.md §5.10 endişesi kapandı.
- Faydalı: eksikliği kodlamak için ikinci, bağımsız bir gösterge elde edildi. Ayrıştırıcı
  ikisinin çeliştiği %6'lık kısmı işaretlesin.

---

## ⚠️ YENİ BULGU 1 — Eksik cevap oranı hücreye göre değişiyor

Bu testler sırasında planda olmayan bir tehdit çıktı.

`pct = 0` (yani kalıp sorusunun cevaplanmaması) oranı, cinsiyet ve kategoriye göre
sistematik olarak değişiyor:

| Cinsiyet / Kategori | Sıfır | Toplam | **Eksik oranı** |
|---|---|---|---|
| Erkek / Gömlek | 12 | 15 | **%80** |
| Erkek / Tişört | 30 | 54 | **%56** |
| Kadın / Jean | 31 | 80 | **%39** |
| Kadın / Tişört | 31 | 95 | **%33** |
| Kadın / Gömlek | 3 | 10 | **%30** |

**Erkekler kalıp sorusunu kadınlardan çok daha az cevaplıyor** — ve oran kategoriye göre de
oynuyor.

### Neden ciddi

DESIGN.md §1.3'teki fark-içinde-fark tahmin edicisi, yorum yazma seçiliminin *kategoriler
arasında cinsiyet içinde simetrik* olduğu varsayımına dayanıyordu. Bu tablo o varsayımın
ihlal edildiğini gösteriyor: erkek gömlekte %80, erkek tişörtte %56 — kategori içinde 24
puanlık fark.

Dahası bu eksikliğin kendisi bilgi taşıyor olabilir: kalıbı sorunsuz bulan biri soruyu
atlıyor olabilir, ki bu durumda eksiklik rastgele değil sonuçla ilişkili.

### Yapılması gerekenler

1. Eksikliği ayrı bir sonuç değişkeni olarak modelle — "kalıp sorusunu cevaplama olasılığı"
   kendisi cinsiyet × kategori DiD'i olarak tahmin edilsin.
2. Ana tahmin ediciye ters olasılık ağırlıklandırması (IPW) veya bir seçilim modeli ekle.
3. Duyarlılık analizi: eksiklerin hepsi "ideal" varsayılırsa ve hepsi "geniş" varsayılırsa
   sonuç ne olur — sınırları raporla.
4. `PREREGISTRATION.md`'de bunu açıkça yaz.

**Not:** Örneklem küçük (5 hücre, 254 yorum). Tam katalogda tekrar hesaplanmalı.
Ama yön ve büyüklük göz ardı edilemeyecek kadar belirgin.

---

## ⚠️ YENİ BULGU 2 — Hacim tahmini hedefin altında

Örneklemden kaba bir tahmin:

| Ölçüm | Değer | Kaynak |
|---|---|---|
| Toplam renk varyantı | 5.629 | sitemap |
| Yetişkin + hedef kategori oranı | 26/60 = %43 | 60 ürünlük örneklem |
| Tahmini hedef ürün | ~2.420 | çarpım |
| Hedef üründe ortalama yorum | 12,7 | 254 yorum / 20 ürün |
| **Tahmini toplam yorum** | **~30.700** | çarpım |
| Kalıp sorusu cevaplanma oranı | ~%55 | 147/254 |
| **Tahmini kullanılabilir gözlem** | **~17.000** | çarpım |

DESIGN.md §5.2'deki hedef ~40-50 bin kullanılabilir gözlemdi. Tahmin bunun **yaklaşık
üçte biri.**

### Uyarılar

- Örneklem küçük ve yorum sayısı çok çarpık — ortalama 12,7 ama medyan çok daha düşük,
  birkaç ürün toplamı domine ediyor. Gerçek sayı bu tahminden sapabilir.
- Renk varyantları model düzeyinde toplanınca ürün sayısı düşer ama yorum sayısı düşmez.

### Sonucu

Bu rakam doğrulanırsa iki seçenek var: kategori kapsamını genişletmek (Sweatshirt, Bluz,
Pantolon, Şort eklemek — üst/alt ayrımı korunarak) veya ikinci markayı Faz 5'ten Faz 2'ye
çekmek. **Karar, tam sayımdan sonra ve güç analizine bakarak verilmeli**
(§7.3).

---

## Yan bulgular

**Site bir beden önerisi hesaplıyor.** Mağaza modalında şu metin çıktı:
*"Müşteri geri bildirimlerine göre, kendi bedeninizi almanızı öneriyoruz."*
Bu, kalıp verisinden türetilmiş ürün düzeyinde bir özet. Ham HTML'de bulunamadı — istemci
tarafında hesaplanıyor. Kovalamaya değmez, çünkü altındaki sinyal zaten topladığımız kalıp
puanları. Ama markanın bu veriyi bizimle aynı şekilde okuduğunu gösteriyor.

**Yorum metni oranı örneklemde daha yüksek çıktı.** Pilot üründe 4/163 idi; 254 yorumluk
karışık örneklemde 57/254 = %22. Yine de metin madenciliği için yetersiz, ama pilot ürün
kadar kötü değil. §5.6 "tamamen yok" yerine "seyrek" olarak yumuşatılabilir.

**Hız sınırı sorunu yaşanmadı.** Yaklaşık 180 istek, saniyede ~2-4, hiç engelleme yok.
Yine de üretimde 1 istek/saniye ile başlanmalı.

---

## DESIGN.md'ye işlenecek değişiklikler

| Bölüm | Değişiklik |
|---|---|
| §1.9 | **Sil** — bölgesel test yapılamıyor (§7.9) |
| §3.2 | `averageSizeRating` alanının hiç dolmadığını not et |
| §3.5 | Beden tablosu yok; üç yedek yolu yaz (§7.7) |
| §5.3 | Etiket şişmesi düzeltmesini manken ölçüleri üzerine yeniden kur |
| §5.4 | **Genişlet** — farklı eksik oranı artık ölçülmüş bir tehdit, hipotetik değil |
| §5.6 | "Neredeyse yok" → "seyrek, ~%22" |
| §5.8 | Tavan doğrulandı, 60 üründe maksimum 6 |
| §5.10 | **Kapat** — moderasyon bayrağı değil |
| §7.1, §7.2, §7.4, §7.5, §7.6, §7.7, §7.9, §7.10 | Tamamlandı olarak işaretle |
| §7 | **Yeni madde:** manken ölçüleri alanının kapsamı |
| §7 | **Yeni madde:** eksiklik modeli ve duyarlılık analizi |
| §3 | Ürün meta verisi bloğunu tam alan eşlemesiyle ekle |

---

## Devredilecek işler

1. **§7.3 — Tam hacim sayımı ve güç analizi.** 5.629 ürün için `pageSize=1` sondası,
   cinsiyet × kategori toplamı, ardından minimum saptanabilir etki hesabı.
2. **§7.5 teyidi** — daha geniş örneklemde stok tavanı.
3. **§7.8** — hız sınırı testi.
4. **Yeni** — manken ölçüleri alanının kapsam testi.
5. **Yeni** — eksik cevap oranının tam katalogda hesaplanması.
6. Şema ve ayrıştırıcıların yazımı.
