import ssl
import socket
from datetime import datetime
import logging
from typing import Dict, List
import OpenSSL.crypto as crypto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSLChecker:
    @staticmethod
    def get_cert_info(domain: str, port: int = 443) -> Dict:
        """Domainin SSL sertifika bilgilerini alır"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    # Sertifikayı al
                    cert_bin = ssock.getpeercert(binary_form=True)
                    cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_bin)
                    
                    # Bilgileri çıkar
                    subject = cert.get_subject()
                    issuer = cert.get_issuer()
                    
                    # Tarihler
                    not_before = datetime.strptime(
                        cert.get_notBefore().decode('ascii'), 
                        '%Y%m%d%H%M%SZ'
                    )
                    not_after = datetime.strptime(
                        cert.get_notAfter().decode('ascii'), 
                        '%Y%m%d%H%M%SZ'
                    )
                    
                    days_left = (not_after - datetime.now()).days
                    
                    # Durum belirle
                    if days_left <= 0:
                        status = 'expired'
                    elif days_left <= 7:
                        status = 'critical'
                    elif days_left <= 30:
                        status = 'warning'
                    else:
                        status = 'valid'

            
                    return {
                        'domain': domain,
                        'issuer': issuer.CN,
                        'subject': subject.CN,
                        'not_before': not_before.strftime('%Y-%m-%d %H:%M:%S'),
                        'not_after': not_after.strftime('%Y-%m-%d %H:%M:%S'),
                        'days_left': days_left,
                        'status': status,
                        'port': port,
                        'error': None
                    }
                    
        except socket.gaierror:
            error = f"Domain çözümlenemedi: {domain}"
            logger.error(error)
            return {'domain': domain, 'error': error, 'status': 'error', 'days_left': 0}
        except socket.timeout:
            error = f"Bağlantı zaman aşımı: {domain}"
            logger.error(error)
            return {'domain': domain, 'error': error, 'status': 'error', 'days_left': 0}
        except Exception as e:
            error = f"Sertifika kontrol hatası: {str(e)}"
            logger.error(f"{domain}: {error}")
            return {'domain': domain, 'error': error, 'status': 'error', 'days_left': 0}
    
    @staticmethod
    def check_all_domains(domains: List[Dict]) -> List[Dict]:
        """Tüm domainleri kontrol eder"""
        results = []
        for domain_config in domains:
            domain = domain_config.get('domain')
            if domain:
                logger.info(f"Kontrol ediliyor: {domain}")
                cert_info = SSLChecker.get_cert_info(domain)
                cert_info['config'] = domain_config
                results.append(cert_info)
        return results