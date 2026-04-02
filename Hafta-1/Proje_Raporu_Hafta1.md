# ANLIK SEFER OPTİMİZASYONU KARAR DESTEK SİSTEMİ 
## 1. Hafta Proje Geliştirme Raporu

**Tarih:** 10-17 Mart (1. Hafta Tamamlandı)

### 1. Proje Özeti ve Amacı
Bu proje, duraklardaki yolcu yoğunluğunu ve kart okutma (doğrulama) verilerini gerçek zamanlı olarak izleyerek, sabit hat seferlerine ek olarak "talebe dayalı ek seferler" üreten bir **Karar Destek Sistemi** olmayı hedeflemektedir. Bekleyen yolcu sayısı, sistemde belirlenen eşik değerleri aştığında otomatik olarak anlık sefer tanımlanır.

### 2. Yapılan Çalışmalar (1. Hafta)

#### 2.1. Altyapı ve Konteynerizasyon (Docker Kurulumu)
Projenin bağımsız ortamlarda çalışabilirliğini sağlamak amacıyla ilk adımda Docker altyapısı kurulmuştur.
- Tüm veritabanı sistemi `docker-compose.yml` kullanılarak izole bir Docker konteyneri olarak ayağa kaldırılmış ve projenin ihtiyacı olan **PostgreSQL (Sürüm 15)** veritabanı sisteme entegre edilmiştir.

#### 2.2. Veritabanı Mimarisi ve Tablolar
Python tabanlı REST API framework'ü olan **FastAPI** ve **SQLAlchemy ORM** mimarisi entegre edilerek, projenin üzerinde koşacağı 4 temel veri tabanı modeli (tablosu) kodlanmıştır:

1. **Route (Hatlar):** Şehir içi güzergahları ve o hatta ek sefer atanması için gerekli olan eşik sınır (threshold) sayısını tutar.
2. **Stop (Duraklar):** Hatlara bağlı otobüs/metro duraklarını ve bulundukları konumu tutar.
3. **PassengerDemand (Yolcu Talepleri):** Kullanıcıların duraklarda kart okuttukları anı (timestamp) ve mevcut durumlarını (bekliyor / araca bindi) kayıt altına alır.
4. **Dispatch (Seferler):** Sistem tarafından alınan yolcu talepleri karar destek testinden geçtikten sonra üretilen "Planlı" veya "Ek" sefer komutlarını kaydeder.

#### 2.3. Sonuç ve Test Bağlantıları
Backend iskeleti kurulmuş, FastAPI ile veritabanı arasında köprü vazifesi gören bağlantı kodları (`database.py` ve `database_setup.py`) başarıyla test edilecek şekilde hazırlanmıştır. Ortam, diğer haftalardaki yapay zeka ve WebSocket eklemelerine hazır hale getirilmiştir.

---
*Bu rapor, proje takvimindeki "1. Hafta: Proje raporunun hazırlanması, Docker kurulması, veritabanı tablolarının ayarlanması" hedeflerinin %100 oranında tamamlandığını belgeler.*
