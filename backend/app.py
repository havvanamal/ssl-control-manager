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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()
ssl_checker = SSLChecker()
scheduler = BackgroundScheduler()

def check_and_renew():
    """SSL kontrollerini yap"""
    logger.info("SSL kontrolleri başlıyor...")
    domains = config.load_domains()
    
    if not domains:
        logger.warning("Domain listesi boş!")
        return
    
    results = ssl_checker.check_all_domains(domains)
    
    # Kritik durumları logla
    for cert in results:
        if cert.get('status') in ['critical', 'warning']:
            logger.warning(f"{cert['domain']}: {cert['status']} - {cert.get('days_left', 0)} gün kaldı")
        elif cert.get('error'):
            logger.error(f"{cert['domain']}: {cert['error']}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlangıç
    logger.info("SSL Manager API başlatılıyor...")
    
    # Zamanlayıcıyı başlat
    scheduler.add_job(check_and_renew, 'interval', hours=config.CHECK_INTERVAL_HOURS)
    scheduler.start()
    logger.info(f"Zamanlayıcı başlatıldı (her {config.CHECK_INTERVAL_HOURS} saat)")
    
    # İlk kontrolü yap
    check_and_renew()
    
    yield
    
    # Kapanış
    scheduler.shutdown()
    logger.info("SSL Manager API kapatılıyor")

app = FastAPI(title="SSL Manager API", version="1.0.0", lifespan=lifespan)

# CORS
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