import os
from dotenv import load_dotenv
import json

load_dotenv()

class Config:
    # Dizinler
    DATA_DIR = '/app/data'
    # Local fallback
    if not os.path.exists('/app') and os.path.exists('./data'):
        DATA_DIR = './data'
        
    CERTS_DIR = f'{DATA_DIR}/certs'
    CONFIG_FILE = f'{DATA_DIR}/domains.json'
    SETTINGS_FILE = f'{DATA_DIR}/settings.json'
    USERS_FILE = f'{DATA_DIR}/users.json'
    
    @classmethod
    def get_settings(cls):
        """Ayarları JSON'dan yükle, yoksa env'den al"""
        settings = {
            "SMTP_SERVER": os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            "SMTP_PORT": int(os.getenv('SMTP_PORT', 587)),
            "SMTP_USER": os.getenv('SMTP_USER', ''),
            "SMTP_PASSWORD": os.getenv('SMTP_PASSWORD', ''),
            "ALERT_EMAILS": os.getenv('ALERT_EMAILS', ''),
            "WARNING_DAYS": int(os.getenv('WARNING_DAYS', 30)),
            "CRITICAL_DAYS": int(os.getenv('CRITICAL_DAYS', 7)),
            "CHECK_INTERVAL_HOURS": int(os.getenv('CHECK_INTERVAL_HOURS', 6))
        }
        
        if os.path.exists(cls.SETTINGS_FILE):
            try:
                with open(cls.SETTINGS_FILE, 'r') as f:
                    file_settings = json.load(f)
                    settings.update(file_settings)
            except Exception as e:
                import logging
                logging.error(f"Settings load error: {e}")
                
        return settings

    @classmethod
    def save_settings(cls, settings_dict):
        """Ayarları JSON'a kaydet"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        current_settings = cls.get_settings()
        current_settings.update(settings_dict)
        with open(cls.SETTINGS_FILE, 'w') as f:
            json.dump(current_settings, f, indent=2)

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

    @classmethod
    def load_users(cls):
        """Kullanıcıları JSON'dan yükle, yoksa default admin oluştur"""
        import hashlib
        if os.path.exists(cls.USERS_FILE):
            try:
                with open(cls.USERS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        default_users = [{
            "username": "admin",
            "password_hash": hashlib.sha256("admin".encode()).hexdigest()
        }]
        cls.save_users(default_users)
        return default_users
        
    @classmethod
    def save_users(cls, users):
        """Kullanıcıları JSON'a kaydet"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        with open(cls.USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
