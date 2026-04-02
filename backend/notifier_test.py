import smtplib
from email.mime.text import MIMEText

# Mail ayarları
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "kulanacaginiz.mail.com"
SMTP_PASSWORD = "uygulama_sifreniz"  # Uygulama şifreniz
TO_EMAIL = "kullanacaginiz.mail.com"

print("=" * 50)
print("Basit Mail Testi")
print("=" * 50)

try:
    # Basit bir mail oluştur
    msg = MIMEText("Bu bir test mailidir. SSL Manager sisteminden gönderildi.")
    msg['Subject'] = "SSL Manager - Basit Test"
    msg['From'] = SMTP_USER
    msg['To'] = TO_EMAIL
    
    print(f"📧 Mail gönderiliyor...")
    print(f"   Sunucu: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"   Gönderen: {SMTP_USER}")
    print(f"   Alıcı: {TO_EMAIL}")
    
    # Mail gönder
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()
    
    print("✅ Mail başarıyla gönderildi!")
    print("📬 Email kutunuzu kontrol edin (Spam klasörünü de kontrol edin)")
    
except Exception as e:
    print(f"❌ Mail gönderilemedi!")
    print(f"   Hata: {str(e)}")
    
    if "535" in str(e):
        print("\n⚠️  Gmail 535 hatası: Şifre veya uygulama şifresi yanlış")
        print("   Çözüm: https://myaccount.google.com/apppasswords adresinden")
        print("   yeni bir uygulama şifresi alın.")
    
    elif "534" in str(e):
        print("\n⚠️  Gmail 534 hatası: Hesap güvenlik ayarları")
        print("   Çözüm: https://www.google.com/settings/security/lesssecureapps")
        print("   adresinden 'Güvenli olmayan uygulamalara izin ver' seçeneğini açın")

print("=" * 50)
