#!/usr/bin/env python3
"""
Deploy workflows from Git to n8n
Supports creating new workflows or updating existing ones
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional
from n8n_client import N8nClient

class WorkflowDeployer:
    def __init__(self):
        self.client = N8nClient()
        self.workflows_dir = Path(__file__).parent.parent / 'workflows'
        
    def get_local_workflows(self) -> List[Dict]:
        """Get all workflow files from local repository"""
        workflows = []
        for file_path in self.workflows_dir.glob('*.json'):
            if file_path.name in ['.gitkeep', 'README.md']:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    workflow = json.load(f)
                    workflow['_file_path'] = file_path
                    workflows.append(workflow)
            except Exception as e:
                print(f"⚠️  Error leyendo {file_path.name}: {e}")
        
        return workflows
    
    def get_remote_workflows(self) -> Dict[str, Dict]:
        """Get all workflows from n8n, indexed by name"""
        response = self.client.list_workflows()
        workflows = response.get('data', [])
        return {wf['name']: wf for wf in workflows}
    
    def deploy_workflow(self, local_workflow: Dict, remote_workflows: Dict[str, Dict], 
                       force: bool = False, dry_run: bool = False) -> bool:
        """Deploy a single workflow to n8n"""
        workflow_name = local_workflow.get('name', 'unnamed')
        file_path = local_workflow.get('_file_path')
        
        # Remove metadata before deploying
        deploy_data = {k: v for k, v in local_workflow.items() 
                      if not k.startswith('_')}
        
        # Check if workflow exists in n8n
        existing = remote_workflows.get(workflow_name)
        
        if existing:
            workflow_id = existing['id']
            
            # Check if there are changes
            remote_full = self.client.get_workflow(workflow_id)
            
            # Compare key fields (ignore metadata like updatedAt, versionId, etc.)
            local_nodes = json.dumps(deploy_data.get('nodes', []), sort_keys=True)
            remote_nodes = json.dumps(remote_full.get('nodes', []), sort_keys=True)
            local_connections = json.dumps(deploy_data.get('connections', {}), sort_keys=True)
            remote_connections = json.dumps(remote_full.get('connections', {}), sort_keys=True)
            
            if local_nodes == remote_nodes and local_connections == remote_connections:
                print(f"⏭️  Sin cambios: {workflow_name}")
                return False
            
            if dry_run:
                print(f"🔄 [DRY-RUN] Actualizaría: {workflow_name} (ID: {workflow_id})")
                return True
            
            # Update existing workflow
            try:
                # Keep the same ID and some metadata
                deploy_data['id'] = workflow_id
                self.client.update_workflow(workflow_id, deploy_data)
                print(f"✅ Actualizado: {workflow_name} (ID: {workflow_id})")
                return True
            except Exception as e:
                print(f"❌ Error actualizando {workflow_name}: {e}")
                return False
        else:
            if dry_run:
                print(f"✨ [DRY-RUN] Crearía nuevo: {workflow_name}")
                return True
            
            # Create new workflow
            try:
                # Remove id if present (n8n will assign new one)
                deploy_data.pop('id', None)
                result = self.client.create_workflow(deploy_data)
                new_id = result.get('id', 'unknown')
                print(f"✨ Creado: {workflow_name} (ID: {new_id})")
                return True
            except Exception as e:
                print(f"❌ Error creando {workflow_name}: {e}")
                return False
    
    def deploy_all(self, workflow_names: Optional[List[str]] = None, 
                   force: bool = False, dry_run: bool = False):
        """Deploy all workflows or specific ones"""
        
        print("🔄 Obteniendo workflows locales...")
        local_workflows = self.get_local_workflows()
        
        if not local_workflows:
            print("❌ No se encontraron workflows locales")
            return
        
        print(f"📦 Encontrados {len(local_workflows)} workflows locales\n")
        
        print("🔍 Obteniendo workflows de n8n...")
        remote_workflows = self.get_remote_workflows()
        print(f"📡 Encontrados {len(remote_workflows)} workflows en n8n\n")
        
        if dry_run:
            print("🧪 MODO DRY-RUN: No se realizarán cambios\n")
        
        deployed = 0
        skipped = 0
        errors = 0
        
        for workflow in local_workflows:
            workflow_name = workflow.get('name', 'unnamed')
            
            # Filter by workflow names if specified
            if workflow_names and workflow_name not in workflow_names:
                continue
            
            success = self.deploy_workflow(workflow, remote_workflows, force, dry_run)
            if success:
                deployed += 1
            elif success is False:
                skipped += 1
            else:
                errors += 1
        
        print(f"\n📊 Resumen: {deployed} desplegados, {skipped} sin cambios, {errors} errores")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy workflows from Git to n8n')
    parser.add_argument('workflows', nargs='*', help='Workflow names to deploy (all if not specified)')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Force update even if no changes detected')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Show what would be deployed without making changes')
    
    args = parser.parse_args()
    
    try:
        deployer = WorkflowDeployer()
        deployer.deploy_all(
            workflow_names=args.workflows if args.workflows else None,
            force=args.force,
            dry_run=args.dry_run
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
