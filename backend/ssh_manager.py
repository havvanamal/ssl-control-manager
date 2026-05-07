import paramiko
import os
import logging
from config import Config

logger = logging.getLogger(__name__)

class SSHManager:
    def __init__(self):
        self.key_dir = os.path.join(Config.DATA_DIR, 'ssh_keys')
        self.private_key_path = os.path.join(self.key_dir, 'id_rsa')
        self.public_key_path = os.path.join(self.key_dir, 'id_rsa.pub')
        self._ensure_keys_exist()

    def _ensure_keys_exist(self):
        """RSA anahtarı yoksa oluşturur"""
        os.makedirs(self.key_dir, exist_ok=True)
        if not os.path.exists(self.private_key_path):
            logger.info("Yeni SSH Anahtarı üretiliyor...")
            key = paramiko.RSAKey.generate(2048)
            key.write_private_key_file(self.private_key_path)
            with open(self.public_key_path, 'w') as f:
                f.write(f"{key.get_name()} {key.get_base64()} ssl-manager\n")
            # Set restrictive permissions
            os.chmod(self.private_key_path, 0o600)
            logger.info("SSH Anahtarı üretildi.")

    def get_public_key(self):
        """Açık anahtarı okur"""
        if os.path.exists(self.public_key_path):
            with open(self.public_key_path, 'r') as f:
                return f.read().strip()
        return ""

    def run_command(self, host, user, command):
        """Uzak sunucuda güvenli olarak komut çalıştırır"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            ssh.connect(
                hostname=host,
                username=user,
                key_filename=self.private_key_path,
                timeout=15,
                look_for_keys=False,
                allow_agent=False
            )
            
            logger.info(f"SSH Bağlantısı başarılı: {user}@{host} -> {command}")
            stdin, stdout, stderr = ssh.exec_command(command)
            
            exit_status = stdout.channel.recv_exit_status()
            out = stdout.read().decode().strip()
            err = stderr.read().decode().strip()
            
            return {
                "success": exit_status == 0,
                "output": out,
                "error": err,
                "exit_code": exit_status
            }
            
        except Exception as e:
            logger.error(f"SSH Bağlantı Hatası ({host}): {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
        finally:
            ssh.close()

    def renew_certificate(self, domain_config):
        """Domain için uzak sunucuda yenileme komutlarını tetikler"""
        domain = domain_config.get('domain')
        server_ip = domain_config.get('server')
        ssh_user = domain_config.get('ssh_user', 'ssl_admin') # Default to ssl_admin
        service = domain_config.get('service', 'nginx')
        
        if not server_ip:
            return {"success": False, "error": f"{domain} için tanımlı bir sunucu IP adresi yok."}

        # 1. Komut: Certbot renew
        cert_cmd = f"sudo certbot renew --cert-name {domain}"
        cert_result = self.run_command(server_ip, ssh_user, cert_cmd)
        
        if not cert_result['success'] and "not due for renewal" not in cert_result['output']:
            return {"success": False, "error": f"Sertifika yenileme başarısız: {cert_result['error']} - {cert_result['output']}"}

        # 2. Komut: Nginx/Apache reload
        reload_cmd = f"sudo systemctl reload {service}"
        reload_result = self.run_command(server_ip, ssh_user, reload_cmd)
        
        if not reload_result['success']:
            return {"success": False, "error": f"Web sunucusu yeniden başlatılamadı: {reload_result['error']} - {reload_result['output']}"}
            
        out_msg = cert_result['output'] if cert_result['output'] else "Sertifika başarıyla yenilendi."
        return {"success": True, "message": out_msg}
