# AI Agent Instructions for Automomo

This document provides comprehensive guidance for AI agents working with this n8n workflows repository. **Read this carefully before making changes to workflows or deployment scripts.**

## Repository Purpose

This repository (`automomo`) maintains bidirectional synchronization between n8n workflows and GitHub, enabling:
- Version control for n8n workflows
- Collaborative workflow development with AI assistance
- Automated backup from n8n to Git
- Deployment from Git to n8n

## Critical Project Context

### Location
- **Project Path**: `/home/bigmomo_n8n_cristian/automomo`
- **n8n Instance**: `https://automomo.bigmomo.com`
- **GitHub Repo**: `https://github.com/zephir1/automomo` (branch: `main`)

### File Structure

```
automomo/
├── workflows/              # n8n workflow JSON files (kebab-case naming)
├── scripts/
│   ├── automomo.py        # Main CLI wrapper
│   ├── sync_workflows.py  # Pull workflows from n8n (n8n → Git)
│   ├── deploy_to_n8n.py   # Push workflows to n8n (Git → n8n)
│   ├── n8n_client.py      # n8n API client
│   └── crypto_helper.py   # Config encryption
├── config/                 # Encrypted credentials (NOT in Git)
├── automomo               # Main executable wrapper
├── setup.sh               # Interactive setup
└── README.md, AGENTS.md, SETUP.md
```

## Working with Workflows

### Adding New Workflows

When creating a new workflow:

1. **Create JSON in `workflows/` directory**
   - Use **kebab-case** naming: `service-action-description.json`
   - Example: `gmail-cpanel-disk-quota-alert.json`

2. **Minimal Required Structure**:
   ```json
   {
     "name": "workflow name",
     "nodes": [...],
     "connections": {...},
     "settings": {
       "executionOrder": "v1"
     }
   }
   ```
   **Do NOT include**: `active`, `id`, `createdAt`, `updatedAt`, `versionId`, `triggerCount`, `shared`, `isArchived`, `versionCounter`, `pinData`, `tags` when creating new workflows.

3. **Deploy to n8n**:
   ```bash
   ./automomo push "workflow name"
   ```

4. **Credentials**: Never commit credentials. Reference existing credential IDs from other workflows:
   - Gmail: `81fW20A5QWw8eLph` (gmail - cristian bigmomo)
   - Google Service: `KsbkO5Zn2sEeZIHn` (google service - cristian automomo)
   - Asana: `vNnjWz0xBzSlIfUG` (asana - bigmomo)

### Modifying Workflows

When modifying existing workflows:
1. Preserve the workflow structure and required fields (`name`, `nodes`, `connections`)
2. Maintain node IDs and connection references
3. Update the workflow `name` field if the purpose changes
4. Keep the JSON formatted for readability

### ⚠️ CRITICAL: n8n API Field Restrictions

**When deploying workflows to n8n via API** (update operations), the API is **very strict** about which fields it accepts.

#### ✅ ALLOWED Fields (for updates):
- `name` - Workflow display name
- `nodes` - Array of workflow nodes
- `connections` - Object defining node connections
- `settings` - Workflow settings object
- `staticData` - Only if not null

#### ❌ REJECTED Fields (cause 400 Bad Request):
- `active` - Read-only (set via activate endpoint)
- `id` - Provided in URL, not body
- `createdAt`, `updatedAt` - Server-managed
- `versionId`, `versionCounter` - Server-managed
- `triggerCount` - Server-managed
- `shared` - Server-managed
- `isArchived` - Server-managed
- `pinData` - Not accepted in updates
- `tags` - Not accepted in updates
- `meta` - Not accepted in updates

**The deploy script (`scripts/deploy_to_n8n.py`) automatically filters these fields.**

#### Workflow Files from n8n (via pull)
Files downloaded from n8n will contain ALL fields (including metadata). This is normal and expected. The deploy script filters them out before sending to the API.

### JSON Formatting: Indented vs Minified

**Current Standard: Indented (2 spaces)**

- Local workflows (`sync_workflows.py`): saved with `indent=2` for readability
- n8n backup workflow: configured to use `JSON.stringify(item, null, 2)` for consistent formatting
- Git diffs are readable and show exactly which nodes/fields changed

**Why Indented?**
- ✅ Human-readable
- ✅ Better Git diffs
- ✅ Easier to review code in Code nodes
- ✅ AI can parse and modify more accurately

**Backup Workflow Configuration**:
The `n8n - backup to git` workflow has a Code node that generates:
```javascript
item.formattedJson = JSON.stringify(item, null, 2);
```
This ensures automated backups use the same format as manual pulls.

### Node Structure

Each node must have:
- `parameters` - Node-specific configuration
- `id` - Unique node identifier (UUID format)
- `name` - Node display name
- `type` - Node type (e.g., `n8n-nodes-base.webhook`, `n8n-nodes-base.gmail`)
- `typeVersion` - Node type version (usually `1`, `2`, or `2.1`)
- `position` - `[x, y]` coordinates for visual layout in n8n canvas

## Best Practices for AI Agents

1. **Validate JSON**: Always ensure workflow JSON is syntactically valid
2. **Preserve IDs**: Don't modify existing node or workflow IDs unless necessary
3. **Test Workflows**: When possible, note if workflows should be tested after changes
4. **Documentation**: Add clear commit messages describing workflow changes
5. **Security**: Never commit credentials, API keys, or sensitive data
6. **Minimal Changes**: When updating workflows, make surgical changes to specific nodes
7. **Consistency**: Follow existing naming conventions and file organization

## Common Tasks

### Creating a Simple Webhook Workflow

```json
{
  "name": "Workflow Name",
  "nodes": [
    {
      "parameters": {
        "path": "your-webhook-path",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [250, 300]
    }
  ],
  "connections": {},
  "active": false,
  "settings": {}
}
```

### Adding a New Node to Existing Workflow

1. Add node object to `nodes` array
2. Update `connections` object to link the new node
3. Ensure unique node ID and name
4. Set appropriate position coordinates

## 🐛 Troubleshooting & Lessons Learned

### Issue: 400 Bad Request on Workflow Update

**Symptom**: `./automomo push` fails with `400 Client Error: Bad Request`

**Common Causes**:
1. **Extra fields in request body**
   - Error: `"request/body must NOT have additional properties"`
   - Solution: Ensure `deploy_to_n8n.py` only sends: `name`, `nodes`, `connections`, `settings`, `staticData` (if not null)

2. **Read-only field included**
   - Error: `"request/body/active is read-only"`
   - Solution: Remove `active` from request body

3. **Invalid node operation**
   - Error: Operation doesn't exist (e.g., `markAsRead` doesn't exist in Gmail node)
   - Solution: Use correct operation names:
     - Mark email as read: `operation: "removeLabels"` with `labelIds: "UNREAD"`
     - Mark as unread: `operation: "addLabels"` with `labelIds: "UNREAD"`

### Issue: `--force` Flag Not Working

**Symptom**: Deploy script says "Sin cambios" even with `--force`

**Solution**: Check that `deploy_workflow()` function respects the `force` parameter:
```python
if not force:
    # Only compare if not forcing
    if local_nodes == remote_nodes and local_connections == remote_connections:
        print(f"⏭️  Sin cambios: {workflow_name}")
        return False
```

### Issue: Workflow Names Don't Match Files

**Symptom**: File is `workflow-name.json` but n8n shows "Workflow Name"

**Expected Behavior**: This is normal! 
- Git files: kebab-case (`asana-create-pre-environment.json`)
- n8n UI: Original name (`asana - create pre environment`)
- Conversion: `scripts/sync_workflows.py` → `name_to_kebab_case()` function

### Issue: Credentials Not Found After Deploy

**Symptom**: Workflow deploys but credentials are missing/invalid

**Solution**: 
1. Credentials are stored by ID in n8n, not in workflow JSON
2. When creating workflows, reference existing credential IDs
3. Check credential IDs match those in working workflows
4. User must configure credentials manually in n8n UI if creating new credential types

## Naming Conventions

### File Naming (kebab-case)
- Format: `service-action-description.json`
- Examples:
  - `gmail-cpanel-disk-quota-alert.json`
  - `asana-create-pre-environment.json`
  - `n8n-backup-to-git.json`
  - `ai-gmail-triage-of-labels.json` (prefix with `ai-` for AI-powered workflows)

### Workflow Naming in n8n
- Format: `service - action description`
- Examples:
  - `gmail - cpanel disk quota alert`
  - `asana - create pre environment`
  - `n8n - backup to git`
  - `(ai) gmail - triage of labels` (use `(ai)` prefix for AI workflows)

### Conversion Function
Located in `scripts/sync_workflows.py`:
```python
def name_to_kebab_case(name: str) -> str:
    result = name.replace(/[()]/g, '')           # Remove parentheses
    result = result.replace(/[\s_]+/g, ' ')      # Normalize whitespace
    result = result.trim().toLowerCase().replace(/ /g, '-')  # Convert to kebab
    result = result.replace(/-+/g, '-')          # Collapse multiple hyphens
    result = result.replace(/[^a-z0-9-]/g, '')   # Remove special chars
    return result
```

## Common Gmail Node Operations

| Task | Operation | Parameters |
|------|-----------|------------|
| Mark as read | `removeLabels` | `labelIds: "UNREAD"` |
| Mark as unread | `addLabels` | `labelIds: "UNREAD"` |
| Add custom label | `addLabels` | `labelIds: "Label_XXX"` |
| Delete email | `delete` | `messageId: "={{ $json.id }}"` |
| Get email | `get` | `messageId: "={{ $json.id }}"` |
| Search emails | `getAll` | `filters: { sender: "...", readStatus: "unread" }` |

## Google Chat Space IDs (Common Channels)

| Channel | Space ID |
|---------|----------|
| developers-automomo | `spaces/AAQAs5SDuMQ` |
| (other channels) | Find in Google Chat URL when you open the space |

## Error Prevention Checklist

Before committing/deploying:
- [ ] JSON syntax is valid (`python3 -m json.tool file.json`)
- [ ] No credentials or API keys in files
- [ ] Node IDs are unique within workflow
- [ ] Connections reference existing node names
- [ ] File uses kebab-case naming
- [ ] Workflow name in JSON matches intended n8n name
- [ ] No disallowed fields if creating new workflow (`active`, `id`, etc.)
- [ ] Tested with `--dry-run` before actual deploy

## Testing Workflow Changes

1. **Local validation**:
   ```bash
   python3 -m json.tool workflows/your-workflow.json > /dev/null && echo "✅ Valid JSON"
   ```

2. **Dry-run deploy**:
   ```bash
   ./automomo push --dry-run "your workflow"
   ```

3. **Deploy and verify**:
   ```bash
   ./automomo push "your workflow"
   # Check n8n UI to ensure workflow imported correctly
   ```

4. **Pull back to confirm**:
   ```bash
   ./automomo pull
   git diff  # Should show minimal changes (only metadata)
   ```

## Security Best Practices

- ✅ **Never commit** `config/.encryption_key`, `config/config.json`, or `config/config.encrypted`
- ✅ API keys stored in `config/config.encrypted` (Fernet symmetric encryption)
- ✅ Credentials referenced by ID in workflows, stored securely in n8n database
- ✅ `.gitignore` properly configured to exclude sensitive files
- ✅ File permissions: `chmod 600` on encryption key

## Questions or Issues?

1. Check this document first (AGENTS.md)
2. Review [README.md](README.md) for user-facing documentation
3. Check [SETUP.md](SETUP.md) for configuration details
4. Consult n8n API docs: [docs.n8n.io/api](https://docs.n8n.io/api/)
5. Review `scripts/deploy_to_n8n.py` for latest API field filtering logic
