import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(__file__))

from notifier import Notifier

# Mail ayarları
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "kullanacaginiz.mail.com"
SMTP_PASSWORD = ""  # Kendi uygulama şifreniz
ALERT_EMAILS = ["kullanacaginiz.mail.com"]

# Notifier'ı başlat
notifier = Notifier(SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD)

print("=" * 50)
print("SSL Manager - Mail Test")
print("=" * 50)

# Test 1: Uyarı maili (15 gün)
print("\n1. Uyarı maili gönderiliyor (15 gün)...")
test_warning = {
    'domain': 'intetra.com.tr',
    'days_left': 15,
    'status': 'warning',
    'not_after': datetime.now() + timedelta(days=15),
    'issuer': 'Sectigo Public Server'
}
notifier.send_alert(test_warning, ALERT_EMAILS)
print("   ✅ Uyarı maili gönderildi!")

# Test 2: Kritik mail (3 gün)
print("\n2. Kritik maili gönderiliyor (3 gün)...")
test_critical = {
    'domain': 'intetra.com.tr',
    'days_left': 3,
    'status': 'critical',
    'not_after': datetime.now() + timedelta(days=3),
    'issuer': 'Sectigo Public Server'
}
notifier.send_alert(test_critical, ALERT_EMAILS)
print("   ✅ Kritik maili gönderildi!")

# Test 3: Yenileme raporu (başarılı)
print("\n3. Başarılı yenileme raporu gönderiliyor...")
notifier.send_renewal_report('intetra.com.tr', True, ALERT_EMAILS)
print("   ✅ Başarılı yenileme raporu gönderildi!")

# Test 4: Yenileme raporu (başarısız)
print("\n4. Başarısız yenileme raporu gönderiliyor...")
notifier.send_renewal_report('intetra.com.tr', False, ALERT_EMAILS)
print("   ✅ Başarısız yenileme raporu gönderildi!")

print("\n" + "=" * 50)
print("📬 Tüm test mailleri gönderildi! Emailinizi kontrol edin.")
print("   Spam klasörünü de kontrol etmeyi unutmayın.")
print("=" * 50)
