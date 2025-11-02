#!/usr/bin/env python3
"""
Bidirectional sync manager for n8n workflows
Handles both pull (n8n → Git) and push (Git → n8n) operations
"""

import sys
import argparse
from pathlib import Path

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def cmd_pull(args):
    """Pull workflows from n8n to Git"""
    from sync_workflows import sync_workflows_to_git
    
    print_header("📥 PULL: n8n → Git")
    synced, skipped = sync_workflows_to_git()
    
    if synced > 0:
        print("\n💡 Tip: Revisa los cambios con 'git diff' y haz commit si es necesario")
    
    return synced > 0

def cmd_push(args):
    """Push workflows from Git to n8n"""
    from deploy_to_n8n import WorkflowDeployer
    
    print_header("📤 PUSH: Git → n8n")
    
    deployer = WorkflowDeployer()
    deployer.deploy_all(
        workflow_names=args.workflows if args.workflows else None,
        force=args.force,
        dry_run=args.dry_run
    )

def cmd_status(args):
    """Show sync status"""
    from sync_workflows import name_to_kebab_case
    from n8n_client import N8nClient
    import json
    
    print_header("📊 Estado de Sincronización")
    
    # Get local workflows
    workflows_dir = Path(__file__).parent.parent / 'workflows'
    local_files = {f.stem: f for f in workflows_dir.glob('*.json') 
                   if f.name not in ['.gitkeep', 'README.md']}
    
    # Get remote workflows
    client = N8nClient()
    response = client.list_workflows()
    remote_workflows = {name_to_kebab_case(wf['name']): wf 
                       for wf in response.get('data', [])
                       if not wf.get('isArchived', False)}
    
    print(f"📁 Local:  {len(local_files)} workflows")
    print(f"☁️  Remote: {len(remote_workflows)} workflows (activos)\n")
    
    # Find differences
    local_only = set(local_files.keys()) - set(remote_workflows.keys())
    remote_only = set(remote_workflows.keys()) - set(local_files.keys())
    both = set(local_files.keys()) & set(remote_workflows.keys())
    
    if local_only:
        print("📦 Solo en Git (listo para push):")
        for name in sorted(local_only):
            print(f"   + {name}")
        print()
    
    if remote_only:
        print("☁️  Solo en n8n (listo para pull):")
        for name in sorted(remote_only):
            print(f"   + {name}")
        print()
    
    if not local_only and not remote_only:
        print("✅ Todo sincronizado!\n")
    
    # Check for modified workflows
    if args.verbose and both:
        print("🔍 Verificando cambios en workflows existentes...")
        modified = []
        
        for name in both:
            local_file = local_files[name]
            remote_wf = remote_workflows[name]
            
            with open(local_file, 'r') as f:
                local_data = json.load(f)
            
            remote_full = client.get_workflow(remote_wf['id'])
            
            # Simple comparison (could be more sophisticated)
            local_nodes = json.dumps(local_data.get('nodes', []), sort_keys=True)
            remote_nodes = json.dumps(remote_full.get('nodes', []), sort_keys=True)
            
            if local_nodes != remote_nodes:
                modified.append(name)
        
        if modified:
            print(f"\n🔄 Workflows con cambios detectados ({len(modified)}):")
            for name in modified:
                print(f"   ~ {name}")
        print()

def cmd_sync(args):
    """Full bidirectional sync"""
    print_header("🔄 Sincronización Bidireccional")
    
    # First pull from n8n
    print("Paso 1/2: Descargando cambios de n8n...\n")
    from sync_workflows import sync_workflows_to_git
    synced, skipped = sync_workflows_to_git()
    
    if not args.no_push:
        print("\n\nPaso 2/2: Subiendo cambios a n8n...\n")
        from deploy_to_n8n import WorkflowDeployer
        deployer = WorkflowDeployer()
        deployer.deploy_all(force=args.force, dry_run=args.dry_run)
    else:
        print("\n⏭️  Push omitido (--no-push)")
    
    print_header("✅ Sincronización Completa")

def main():
    parser = argparse.ArgumentParser(
        description='Bidirectional sync for n8n workflows',
        epilog="""
Ejemplos:
  %(prog)s pull                    # Descargar workflows de n8n
  %(prog)s push                    # Subir workflows a n8n
  %(prog)s push workflow1 workflow2  # Subir workflows específicos
  %(prog)s push --dry-run          # Ver qué se subiría sin hacer cambios
  %(prog)s status                  # Ver estado de sincronización
  %(prog)s status -v               # Ver estado con detalles de cambios
  %(prog)s sync                    # Sincronización completa (pull + push)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Pull command
    parser_pull = subparsers.add_parser('pull', help='Descargar workflows de n8n a Git')
    
    # Push command
    parser_push = subparsers.add_parser('push', help='Subir workflows de Git a n8n')
    parser_push.add_argument('workflows', nargs='*', 
                            help='Nombres de workflows específicos (todos si no se especifica)')
    parser_push.add_argument('--force', '-f', action='store_true',
                            help='Forzar actualización aunque no haya cambios')
    parser_push.add_argument('--dry-run', '-n', action='store_true',
                            help='Mostrar lo que se haría sin hacer cambios')
    
    # Status command
    parser_status = subparsers.add_parser('status', help='Ver estado de sincronización')
    parser_status.add_argument('--verbose', '-v', action='store_true',
                              help='Mostrar detalles de cambios')
    
    # Sync command
    parser_sync = subparsers.add_parser('sync', help='Sincronización bidireccional completa')
    parser_sync.add_argument('--force', '-f', action='store_true',
                            help='Forzar actualización en push')
    parser_sync.add_argument('--dry-run', '-n', action='store_true',
                            help='Modo de prueba sin hacer cambios')
    parser_sync.add_argument('--no-push', action='store_true',
                            help='Solo hacer pull, no push')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'pull':
            cmd_pull(args)
        elif args.command == 'push':
            cmd_push(args)
        elif args.command == 'status':
            cmd_status(args)
        elif args.command == 'sync':
            cmd_sync(args)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
