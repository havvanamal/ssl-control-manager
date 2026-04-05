from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from contextlib import asynccontextmanager
import logging
from typing import List, Dict
import json
import os

from config import Config
from ssl_checker import SSLChecker
from notifier import Notifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()
ssl_checker = SSLChecker()
scheduler = BackgroundScheduler()

def check_and_renew():
    """SSL kontrollerini yap"""
    logger.info("SSL kontrolleri başlıyor...")
    domains = config.load_domains()
    settings = config.get_settings()
    
    if not domains:
        logger.warning("Domain listesi boş!")
        return
    
    results = ssl_checker.check_all_domains(domains)
    
    notifier = Notifier(
        smtp_server=settings.get("SMTP_SERVER"),
        smtp_port=settings.get("SMTP_PORT"),
        smtp_user=settings.get("SMTP_USER"),
        smtp_password=settings.get("SMTP_PASSWORD")
    )
    
    alert_emails = settings.get("ALERT_EMAILS", "").split(",") if settings.get("ALERT_EMAILS") else []
    alert_emails = [e.strip() for e in alert_emails if e.strip()]
    
    # Kritik durumları logla ve e-posta at
    for cert in results:
        if cert.get('status') in ['critical', 'warning']:
            logger.warning(f"{cert['domain']}: {cert['status']} - {cert.get('days_left', 0)} gün kaldı")
            if alert_emails and settings.get("SMTP_SERVER"):
                # send_alert try/except is handled internally in Notifier, wait, send_alert has no return false directly but sends email
                # actually send_alert returns None implicitly, but send_email returns True/False
                notifier.send_alert(cert, alert_emails)
        elif cert.get('error'):
            logger.error(f"{cert['domain']}: {cert['error']}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    logger.info("SSL Manager API başlatılıyor...")
    

    settings = config.get_settings()
    interval = settings.get('CHECK_INTERVAL_HOURS', 6)
    scheduler.add_job(check_and_renew, 'interval', hours=interval)
    scheduler.start()
    logger.info(f"Zamanlayıcı başlatıldı (her {interval} saat)")
    

    check_and_renew()
    
    yield
    

    scheduler.shutdown()
    logger.info("SSL Manager API kapatılıyor")

app = FastAPI(title="SSL Manager API", version="1.0.0", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "SSL Manager API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/api/certificates", "/api/domains", "/api/check"]
    }

@app.get("/api/certificates")
async def get_certificates():
    """Tüm sertifikaların durumunu getir"""
    domains = config.load_domains()
    if not domains:
        return []
    return ssl_checker.check_all_domains(domains)

@app.get("/api/domains")
async def get_domains():
    """Domain listesini getir"""
    return config.load_domains()

@app.post("/api/domains")
async def add_domain(domain_config: dict):
    """Yeni domain ekle"""
    domains = config.load_domains()
    domains.append(domain_config)
    config.save_domains(domains)
    return {"message": "Domain eklendi", "domain": domain_config}

@app.delete("/api/domains/{domain}")
async def remove_domain(domain: str):
    """Domain sil"""
    domains = config.load_domains()
    domains = [d for d in domains if d.get('domain') != domain]
    config.save_domains(domains)
    return {"message": f"Domain silindi: {domain}"}

@app.post("/api/check")
async def check_now():
    """Manuel kontrol başlat"""
    check_and_renew()
    return {"message": "Kontrol başlatıldı"}

@app.get("/health")
async def health_check():
    """Sağlık kontrolü"""
    return {"status": "healthy", "domains_count": len(config.load_domains())}

@app.get("/api/settings")
async def get_settings():
    """Ayarları getir"""
    return config.get_settings()

@app.post("/api/settings")
async def save_settings(settings: dict):
    """Ayarları kaydet"""
    config.save_settings(settings)
    return {"message": "Ayarlar kaydedildi"}

@app.get("/api/test/warning")
async def send_test_warning():
    """Test uyarısı gönder (Sahte data ile)"""
    settings = config.get_settings()
    notifier = Notifier(
        smtp_server=settings.get("SMTP_SERVER"),
        smtp_port=settings.get("SMTP_PORT"),
        smtp_user=settings.get("SMTP_USER"),
        smtp_password=settings.get("SMTP_PASSWORD")
    )
    alert_emails = settings.get("ALERT_EMAILS", "").split(",") if settings.get("ALERT_EMAILS") else []
    alert_emails = [e.strip() for e in alert_emails if e.strip()]
    
    if not alert_emails or not settings.get("SMTP_SERVER"):
        return {"error": "SMTP veya Alert Emails eksik."}
    
    dummy_cert = {
        'domain': 'test.example.com',
        'status': 'critical',
        'days_left': 5,
        'not_after': '2030-01-01 00:00:00',
        'issuer': 'Test Issuer'
    }
    # send_alert doesn't throw, calls send_email which catches exceptions
    notifier.send_alert(dummy_cert, alert_emails)
    return {"message": "Gönderim talebi işlendi (Logları kontrol edin)"}

@app.post("/api/renew/{domain}")
async def mock_renew_domain(domain: str):
    """MOCK: Sertifikayı yenileme simülasyonu"""
    logger.info(f"{domain} için sahte yenileme işlemi başlatıldı.")
    return {"message": f"{domain} yenileme simülasyonu başarılı. Gerçek bir SSH işlemi yapılmadı."}
