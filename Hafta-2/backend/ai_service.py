import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API anahtarı .env dosyasından okunur
API_KEY = os.getenv("GEMINI_API_KEY")

if API_KEY and API_KEY != "BURAYA_API_ANAHTARINIZI_YAZIN":
    genai.configure(api_key=API_KEY)
    # Güncel pro modelini seçiyoruz
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
else:
    model = None

def get_admin_assistant_reply(message: str, stats: dict) -> str:
    """
    Sistemin mevcut durumunu (stats) Gemini modeline kontekst olarak sağlar,
    ardından yöneticinin sorduğu soruya (message) yanıt üretir.
    """
    if not model:
        return "⚠️ Gemini API bağlamı ayarlanmamış. Lütfen .env dosyasını oluşturup 'GEMINI_API_KEY' anahtarını girin."
    
    prompt = f"""Sen otobüs seferlerini optimize eden 'Anlık Sefer Optimizasyonu Karar Destek Sistemi'nin akıllı yönetici asistanısın.
Görev: Sistem yöneticisine kibar, profesyonel ve kısa bir dille Türkçe yanıt vermek.

Sistemin mevcut anlık istatistikleri (Veritabanı Görünümü):
- Sistemdeki Toplam Hat Sayısı: {stats.get('total_routes', 0)}
- Sistemdeki Toplam Durak Sayısı: {stats.get('total_stops', 0)}
- Şu Anda Duraklarda Bekleyen Toplam Yolcu: {stats.get('total_waiting', 0)}
- Sefere Çıkan Ek Otobüs Sayısı: {stats.get('extra_dispatch_count', 0)}

Yönetici (Kullanıcı) sana şu soruyu/mesajı gönderdi:
"{message}"

Lütfen yöneticinin mesajına yukarıdaki istatistikleri ve genel yapay zeka bilgilerini birleştirerek yanıt ver. Sadece sistemle ve bu verilerle ilgili konuş.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Yapay zeka ile iletişim kurulurken bir hata oluştu: {str(e)}"
