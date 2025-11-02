#!/usr/bin/env python3
"""
Cliente para interactuar con la API de n8n
"""
import requests
import json
from pathlib import Path
from crypto_helper import CryptoHelper

class N8nClient:
    def __init__(self):
        self.crypto = CryptoHelper()
        self.config = self.crypto.get_config()
        
        if not self.config:
            raise Exception("No se pudo cargar la configuración")
        
        self.base_url = self.config['n8n']['url']
        self.api_key = self.config['n8n']['api_key']
        self.headers = {
            'X-N8N-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def list_workflows(self):
        """Lista todos los workflows"""
        url = f"{self.base_url}/api/v1/workflows"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_workflow(self, workflow_id):
        """Obtiene un workflow específico"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_workflow(self, workflow_data):
        """Crea un nuevo workflow"""
        url = f"{self.base_url}/api/v1/workflows"
        response = requests.post(url, headers=self.headers, json=workflow_data)
        response.raise_for_status()
        return response.json()
    
    def update_workflow(self, workflow_id, workflow_data):
        """Actualiza un workflow existente"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.put(url, headers=self.headers, json=workflow_data)
        response.raise_for_status()
        return response.json()
    
    def delete_workflow(self, workflow_id):
        """Elimina un workflow"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True
    
    def activate_workflow(self, workflow_id):
        """Activa un workflow"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/activate"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def deactivate_workflow(self, workflow_id):
        """Desactiva un workflow"""
        url = f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate"
        response = requests.post(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

def main():
    import sys
    
    try:
        client = N8nClient()
        
        if len(sys.argv) < 2:
            print("Uso: python n8n_client.py [list|get|create|update|delete] [args...]")
            sys.exit(1)
        
        command = sys.argv[1]
        
        if command == "list":
            workflows = client.list_workflows()
            print(f"\n📋 Total workflows: {len(workflows.get('data', []))}\n")
            for wf in workflows.get('data', []):
                status = "✅" if wf.get('active') else "⭕"
                print(f"{status} [{wf['id']}] {wf['name']}")
        
        elif command == "get":
            if len(sys.argv) < 3:
                print("❌ Especifica el ID del workflow")
                sys.exit(1)
            workflow = client.get_workflow(sys.argv[2])
            print(json.dumps(workflow, indent=2))
        
        else:
            print(f"❌ Comando no implementado: {command}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
