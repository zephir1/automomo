#!/usr/bin/env python3
"""
Sync workflows from n8n to Git repository
Converts workflow names to kebab-case for file naming
"""

import json
import re
import os
from pathlib import Path

def name_to_kebab_case(name: str) -> str:
    """
    Convert workflow name to kebab-case filename
    Examples:
        'n8n - error trigger' -> 'n8n-error-trigger'
        '(ai) gmail - triage of labels' -> 'ai-gmail-triage-of-labels'
    """
    # Remove parentheses
    name = re.sub(r'[()]', '', name)
    # Replace multiple spaces/underscores with single space
    name = re.sub(r'[\s_]+', ' ', name)
    # Convert to lowercase and replace spaces with hyphens
    name = name.strip().lower().replace(' ', '-')
    # Replace multiple consecutive hyphens with single hyphen
    name = re.sub(r'-+', '-', name)
    # Remove any remaining special characters except hyphens
    name = re.sub(r'[^a-z0-9-]', '', name)
    return name

def sync_workflows_to_git():
    """Fetch all workflows from n8n and save to git repository"""
    
    # Import here to avoid circular dependencies
    from n8n_client import N8nClient
    
    # Initialize n8n client
    client = N8nClient()
    
    # Get workflows directory
    workflows_dir = Path(__file__).parent.parent / 'workflows'
    workflows_dir.mkdir(exist_ok=True)
    
    # Fetch all workflows
    print("🔄 Fetching workflows from n8n...")
    workflows_response = client.list_workflows()
    workflows = workflows_response.get('data', [])
    
    synced = 0
    skipped = 0
    
    for workflow in workflows:
        workflow_name = workflow.get('name', 'unnamed')
        
        # Skip archived workflows
        if workflow.get('isArchived', False):
            print(f"⏭️  Skipping archived: {workflow_name}")
            skipped += 1
            continue
        
        # Convert name to kebab-case filename
        filename = name_to_kebab_case(workflow_name) + '.json'
        filepath = workflows_dir / filename
        
        # Get full workflow details
        workflow_id = workflow['id']
        full_workflow = client.get_workflow(workflow_id)
        
        # Clean up nested metadata that causes unnecessary diffs
        # Remove the nested 'project' object from shared array if present
        if 'shared' in full_workflow and isinstance(full_workflow['shared'], list):
            for shared_item in full_workflow['shared']:
                if 'project' in shared_item:
                    # Keep only essential fields from shared
                    project_id = shared_item.get('projectId')
                    shared_item.pop('project', None)
        
        # Remove versionCounter (changes on every edit, not meaningful for version control)
        full_workflow.pop('versionCounter', None)
        
        # Clean up staticData - remove runtime state that changes on every execution
        if 'staticData' in full_workflow and isinstance(full_workflow['staticData'], dict):
            for node_key, node_data in full_workflow['staticData'].items():
                if isinstance(node_data, dict):
                    # Remove from direct node level (e.g., Calendar nodes)
                    node_data.pop('lastTimeChecked', None)
                    node_data.pop('possibleDuplicates', None)
                    
                    # Remove from nested trigger level (e.g., Gmail Trigger)
                    for trigger_key, trigger_data in node_data.items():
                        if isinstance(trigger_data, dict):
                            trigger_data.pop('lastTimeChecked', None)
                            trigger_data.pop('possibleDuplicates', None)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(full_workflow, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved: {workflow_name} → {filename}")
        synced += 1
    
    print(f"\n📊 Summary: {synced} synced, {skipped} skipped")
    return synced, skipped

if __name__ == '__main__':
    try:
        sync_workflows_to_git()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
