#!/usr/bin/env python3
"""
Helper para encriptar/desencriptar configuración sensible
"""
import os
import json
import base64
from cryptography.fernet import Fernet
from pathlib import Path

class CryptoHelper:
    def __init__(self, key_file=None):
        self.base_dir = Path(__file__).parent.parent
        self.key_file = key_file or self.base_dir / "config" / ".encryption_key"
        self.config_file = self.base_dir / "config" / "config.json"
        self.encrypted_file = self.base_dir / "config" / "config.encrypted"
        
    def generate_key(self):
        """Genera una nueva clave de encriptación"""
        key = Fernet.generate_key()
        with open(self.key_file, 'wb') as f:
            f.write(key)
        os.chmod(self.key_file, 0o600)  # Solo lectura/escritura para el propietario
        print(f"✅ Clave generada en: {self.key_file}")
        print("⚠️  IMPORTANTE: Guarda esta clave en un lugar seguro!")
        return key
    
    def get_key(self):
        """Obtiene la clave de encriptación"""
        if not self.key_file.exists():
            print("⚠️  No existe clave de encriptación. Generando una nueva...")
            return self.generate_key()
        
        with open(self.key_file, 'rb') as f:
            return f.read()
    
    def encrypt_config(self):
        """Encripta el archivo de configuración"""
        if not self.config_file.exists():
            print(f"❌ No existe el archivo {self.config_file}")
            print("💡 Copia config.example.json a config.json y configúralo primero")
            return False
        
        with open(self.config_file, 'r') as f:
            config_data = f.read()
        
        key = self.get_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(config_data.encode())
        
        with open(self.encrypted_file, 'wb') as f:
            f.write(encrypted_data)
        
        print(f"✅ Configuración encriptada en: {self.encrypted_file}")
        return True
    
    def decrypt_config(self):
        """Desencripta y devuelve la configuración"""
        if not self.encrypted_file.exists():
            print(f"❌ No existe el archivo encriptado {self.encrypted_file}")
            return None
        
        key = self.get_key()
        fernet = Fernet(key)
        
        with open(self.encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = fernet.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"❌ Error al desencriptar: {e}")
            return None
    
    def get_config(self):
        """Obtiene la configuración (encriptada o sin encriptar)"""
        # Primero intenta leer el archivo encriptado
        if self.encrypted_file.exists():
            return self.decrypt_config()
        
        # Si no, lee el archivo sin encriptar
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        print("❌ No se encontró ningún archivo de configuración")
        print("💡 Copia config.example.json a config.json y configúralo")
        return None

def main():
    import sys
    crypto = CryptoHelper()
    
    if len(sys.argv) < 2:
        print("Uso: python crypto_helper.py [encrypt|decrypt|generate-key|show]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate-key":
        crypto.generate_key()
    elif command == "encrypt":
        crypto.encrypt_config()
    elif command == "decrypt":
        config = crypto.decrypt_config()
        if config:
            print(json.dumps(config, indent=2))
    elif command == "show":
        config = crypto.get_config()
        if config:
            # Ocultar el API key en la salida
            if 'n8n' in config and 'api_key' in config['n8n']:
                config['n8n']['api_key'] = "***HIDDEN***"
            print(json.dumps(config, indent=2))
    else:
        print(f"❌ Comando desconocido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
