import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Notifier:
    def __init__(self, smtp_server, smtp_port, smtp_user, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
    
    def send_email(self, to_emails, subject, body):
        """E-posta gönderir"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Bildirim gönderildi: {to_emails}")
            return True
        except Exception as e:
            logger.error(f"E-posta gönderme hatası: {str(e)}")
            return False
    
    def send_alert(self, cert_info, to_emails):
        """Sertifika durumu hakkında uyarı gönderir"""
        domain = cert_info['domain']
        days_left = cert_info.get('days_left', 0)
        status = cert_info['status']
        
        if status == 'critical':
            subject = f"⚠️ KRİTİK: {domain} SSL sertifikası {days_left} gün sonra sona eriyor!"
            color = 'red'
        elif status == 'warning':
            subject = f"⚠️ UYARI: {domain} SSL sertifikası {days_left} gün sonra sona erecek"
            color = 'orange'
        else:
            return
        
        not_after = cert_info.get('not_after', 'N/A')
        if hasattr(not_after, 'strftime'):
            not_after = not_after.strftime('%Y-%m-%d %H:%M:%S')
        
        body = f"""
        <html>
        <body>
            <h2 style="color: {color};">SSL Sertifika Uyarısı</h2>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>Durum:</strong> {status.upper()}</p>
            <p><strong>Kalan Gün:</strong> {days_left}</p>
            <p><strong>Son Kullanma Tarihi:</strong> {not_after}</p>
            <p><strong>Issuer:</strong> {cert_info.get('issuer', 'N/A')}</p>
            <hr>
            <p>Sertifika otomatik olarak yenilenecektir.</p>
            <p>Bu mesaj SSL Yönetim Sistemi tarafından gönderilmiştir.</p>
        </body>
        </html>
        """
        
        self.send_email(to_emails, subject, body)
    
    def send_renewal_report(self, domain, success, to_emails):
        """Sertifika yenileme raporu gönderir"""
        subject = f"{'✅' if success else '❌'} SSL Yenileme: {domain}"
        color = 'green' if success else 'red'
        
        body = f"""
        <html>
        <body>
            <h2 style="color: {color};">SSL Sertifika Yenileme {'Başarılı' if success else 'Başarısız'}</h2>
            <p><strong>Domain:</strong> {domain}</p>
            <p><strong>Tarih:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Sonuç:</strong> {'Başarıyla yenilendi' if success else 'Yenileme başarısız - manuel müdahale gerekli'}</p>
            <hr>
            <p>SSL Yönetim Sistemi</p>
        </body>
        </html>
        """
        
        self.send_email(to_emails, subject, body)