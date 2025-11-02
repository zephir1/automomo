# AI Agent Instructions

This document provides guidance for AI agents working with this n8n workflows repository.

## Repository Purpose

This repository stores n8n workflow automation files in JSON format for version control and collaboration.

## File Structure

- `workflows/` - Contains all n8n workflow JSON files
- Each workflow is stored as a separate `.json` file
- Workflow files follow n8n's export format

## Working with Workflows

### Adding New Workflows

When adding a new workflow:
1. Place the JSON file in the `workflows/` directory
2. Use descriptive, kebab-case filenames (e.g., `github-to-slack-notification.json`)
3. Ensure the workflow JSON is valid and properly formatted
4. Do not include sensitive credentials - these should be managed in n8n's credential system

### Modifying Workflows

When modifying existing workflows:
1. Preserve the workflow structure and required fields (`name`, `nodes`, `connections`)
2. Maintain node IDs and connection references
3. Update the workflow `name` field if the purpose changes
4. Keep the JSON formatted for readability

### Required JSON Fields

n8n workflows must contain:
- `name` - Workflow display name
- `nodes` - Array of workflow nodes
- `connections` - Object defining node connections
- `active` - Boolean indicating if workflow should be active
- `settings` - Workflow settings object
- `id` - Unique workflow identifier (optional for import)

### Node Structure

Each node must have:
- `parameters` - Node-specific configuration
- `id` - Unique node identifier
- `name` - Node display name
- `type` - Node type (e.g., `n8n-nodes-base.webhook`)
- `typeVersion` - Node type version
- `position` - [x, y] coordinates for visual layout

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

## Error Prevention

- **Do not** remove the `workflows/` directory
- **Do not** commit files with `.env` or credential information
- **Do not** break JSON syntax
- **Do not** duplicate node IDs within a workflow
- **Always** validate connections reference existing nodes

## Questions?

Refer to the main [README.md](README.md) for user-facing documentation or the n8n documentation at [docs.n8n.io](https://docs.n8n.io).
