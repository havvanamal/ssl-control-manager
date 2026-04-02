import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    # SMTP Ayarları
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.office365.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    ALERT_EMAILS = os.getenv('ALERT_EMAILS', '').split(',') if os.getenv('ALERT_EMAILS') else []
    
    # Yenileme Ayarları
    RENEW_DAYS_BEFORE = int(os.getenv('RENEW_DAYS_BEFORE', 30))
    CHECK_INTERVAL_HOURS = int(os.getenv('CHECK_INTERVAL_HOURS', 6))
    
    # Dizinler
    DATA_DIR = '/app/data'
    CERTS_DIR = f'{DATA_DIR}/certs'
    CONFIG_FILE = f'{DATA_DIR}/domains.json'
    
    @classmethod
    def load_domains(cls):
        """Domain konfigürasyonlarını JSON'dan yükle"""
        if os.path.exists(cls.CONFIG_FILE):
            with open(cls.CONFIG_FILE, 'r') as f:
                return json.load(f)
        return []
    
    @classmethod
    def save_domains(cls, domains):
        """Domain konfigürasyonlarını JSON'a kaydet"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(domains, f, indent=2)