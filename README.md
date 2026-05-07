# 🔒 SSL Control Manager
SSL Control Manager, birden fazla domaine ait SSL sertifikalarının geçerlilik tarihlerini otomatik olarak izleyen, süresi dolmak üzere olanlara dikkat çeken ve bunu şık bir kullanıcı arayüzü ile sunan modern bir takip sistemidir.
Bu uygulama, manuel takibi tamamen ortadan kaldırarak sertifikalarınızın süresi bitmeden e-posta bildirimleri (SMTP üzerinden) almanızı sağlar.

## ✨ Özellikler
* **Otomatik Denetim:** Sistem, eklenen domainleri (varsayılan olarak her 6 saatte bir) periyodik olarak arka planda kontrol eder.
* **Modern Dashboard (Front-end):** Streamlit ile desteklenen hızlı ve şık bir kontrol paneli.
* **Grafiksel Analizler:** Plotly ile sertifika kalan günlerini, risk düzeylerini ve istatistikleri pasta veya çubuk grafikler ile canlı izleme imkanı.
* **Akıllı Bildirim Sistemi:** 
  * 🔴 **Kritik (<= 7 gün):** Sertifika bitimine çok az kaldığında kritik loglar ve mail alarmı.
  * ⚠️ **Uyarı (<= 30 gün):** 30 günden az süresi kalanlar için bildirim ağı.
* **Dinamik Domain Yönetimi:** Arayüz üzerinden yeni domain ekleyebilir, gereksizleri silebilirsiniz.
* **E-Posta Yönetimi:** Doğrudan kullanıcı arayüzü üzerinden SMTP ayarlarını ve maili alacak kişileri konfigüre edebilme.
* **Docker Desteği:** `docker-compose` ile izole bir şekilde saniyeler içerisinde kurulum ve çalıştırma.
* 
## 🛠️ Kullanılan Teknolojiler
* **Backend:** Python, FastAPI, APScheduler, OpenSSL
* **Frontend:** Python, Streamlit, Pandas, Plotly
* **Altyapı:** Docker, Docker Compose
* 
## 🚀 Kurulum & Çalıştırma
Projeyi sisteminizde çalıştırmanız için Docker'ın bilgisayarınızda yüklü olması yeterlidir.

```bash
git clone https://github.com/havvanamal/ssl-control-manager.git
cd ssl-control-manager
docker-compose up -d --build

Frontend (Arayüz): Tarayıcınızda http://localhost:8502 adresine gidin.
Backend (API): İşlemlerin yürütüldüğü API'ye http://localhost:9000 üzerinden erişebilirsiniz.
