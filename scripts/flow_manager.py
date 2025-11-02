#!/usr/bin/env python3
"""
Gestión de flujos: sincronización entre n8n y git
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from n8n_client import N8nClient

class FlowManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.flows_dir = self.base_dir / "flows"
        self.client = N8nClient()
    
    def sanitize_filename(self, name):
        """Convierte el nombre del workflow en un nombre de archivo válido"""
        # Reemplaza caracteres no válidos
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        return name.strip()
    
    def pull_all(self):
        """Descarga todos los workflows de n8n a archivos locales"""
        print("🔄 Descargando workflows desde n8n...")
        
        workflows = self.client.list_workflows()
        count = 0
        
        for wf in workflows.get('data', []):
            workflow_id = wf['id']
            workflow_name = wf['name']
            
            # Obtener el workflow completo
            full_workflow = self.client.get_workflow(workflow_id)
            
            # Crear nombre de archivo
            filename = self.sanitize_filename(workflow_name) + ".json"
            filepath = self.flows_dir / filename
            
            # Guardar
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(full_workflow, f, indent=2, ensure_ascii=False)
            
            status = "✅" if wf.get('active') else "⭕"
            print(f"  {status} {workflow_name} → {filename}")
            count += 1
        
        print(f"\n✅ {count} workflows descargados a {self.flows_dir}")
    
    def push_all(self):
        """Sube todos los workflows locales a n8n"""
        print("🔄 Subiendo workflows a n8n...")
        
        if not self.flows_dir.exists():
            print(f"❌ No existe el directorio {self.flows_dir}")
            return
        
        json_files = list(self.flows_dir.glob("*.json"))
        
        if not json_files:
            print(f"⚠️  No hay archivos JSON en {self.flows_dir}")
            return
        
        for filepath in json_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            workflow_name = workflow_data.get('name', filepath.stem)
            workflow_id = workflow_data.get('id')
            
            try:
                if workflow_id:
                    # Actualizar workflow existente
                    self.client.update_workflow(workflow_id, workflow_data)
                    print(f"  ✅ Actualizado: {workflow_name}")
                else:
                    # Crear nuevo workflow
                    result = self.client.create_workflow(workflow_data)
                    print(f"  ✨ Creado: {workflow_name} (ID: {result['id']})")
                    
                    # Actualizar el archivo con el nuevo ID
                    workflow_data['id'] = result['id']
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(workflow_data, f, indent=2, ensure_ascii=False)
            
            except Exception as e:
                print(f"  ❌ Error con {workflow_name}: {e}")
        
        print(f"\n✅ Sincronización completada")
    
    def list_local(self):
        """Lista los workflows locales"""
        print(f"\n📁 Workflows locales en {self.flows_dir}:\n")
        
        json_files = list(self.flows_dir.glob("*.json"))
        
        if not json_files:
            print("  (vacío)")
            return
        
        for filepath in json_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            workflow_id = workflow_data.get('id', 'sin-id')
            workflow_name = workflow_data.get('name', filepath.stem)
            
            print(f"  [{workflow_id}] {workflow_name}")
            print(f"    └─ {filepath.name}")
    
    def compare(self):
        """Compara workflows locales vs remotos"""
        print("🔍 Comparando workflows locales vs n8n...\n")
        
        # Obtener workflows remotos
        remote_workflows = self.client.list_workflows()
        remote_dict = {wf['id']: wf for wf in remote_workflows.get('data', [])}
        
        # Obtener workflows locales
        local_files = list(self.flows_dir.glob("*.json"))
        local_dict = {}
        
        for filepath in local_files:
            with open(filepath, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            wf_id = workflow_data.get('id')
            if wf_id:
                local_dict[wf_id] = {'data': workflow_data, 'file': filepath}
        
        # Solo en n8n (no descargados)
        only_remote = set(remote_dict.keys()) - set(local_dict.keys())
        if only_remote:
            print("☁️  Solo en n8n (no descargados):")
            for wf_id in only_remote:
                print(f"  - {remote_dict[wf_id]['name']}")
            print()
        
        # Solo en local (no subidos)
        only_local = set(local_dict.keys()) - set(remote_dict.keys())
        if only_local:
            print("💾 Solo en local (no subidos a n8n):")
            for wf_id in only_local:
                print(f"  - {local_dict[wf_id]['data']['name']}")
            print()
        
        # En ambos
        both = set(local_dict.keys()) & set(remote_dict.keys())
        if both:
            print("🔄 En ambos lugares:")
            for wf_id in both:
                print(f"  ✅ {remote_dict[wf_id]['name']}")
            print()
        
        print(f"📊 Resumen: {len(remote_dict)} en n8n, {len(local_dict)} en local")

def main():
    if len(sys.argv) < 2:
        print("""
Uso: python flow_manager.py [comando]

Comandos:
  pull       - Descarga todos los workflows de n8n
  push       - Sube todos los workflows locales a n8n
  list       - Lista workflows locales
  compare    - Compara workflows locales vs n8n
        """)
        sys.exit(1)
    
    try:
        manager = FlowManager()
        command = sys.argv[1]
        
        if command == "pull":
            manager.pull_all()
        elif command == "push":
            manager.push_all()
        elif command == "list":
            manager.list_local()
        elif command == "compare":
            manager.compare()
        else:
            print(f"❌ Comando desconocido: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
