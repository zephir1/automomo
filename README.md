# automomo

n8n Flows for automomo - A version-controlled repository for n8n workflow automation.

## Structure

```
.
├── workflows/          # All n8n workflow JSON files
│   └── README.md      # Guide for managing workflows
└── README.md          # This file
```

## Quick Start

### Exporting Workflows

1. Open your workflow in n8n
2. Click on the workflow menu (⋮)
3. Select "Download"
4. Save the JSON file to the `workflows/` directory
5. Commit and push:
   ```bash
   git add workflows/your-workflow.json
   git commit -m "Add: your workflow description"
   git push
   ```

### Importing Workflows

1. Open n8n
2. Click "Import from File" or use the workflow menu
3. Select a workflow JSON file from the `workflows/` directory
4. The workflow will be imported with all nodes and connections

## Best Practices

- **Naming**: Use descriptive names (e.g., `slack-notification.json`, `data-sync.json`)
- **Documentation**: Add comments in workflow descriptions within n8n
- **Credentials**: Never commit credentials - use n8n's credential system
- **Testing**: Test workflows before committing
- **Versioning**: Use meaningful commit messages to track changes

## About n8n

n8n is a fair-code distributed workflow automation tool. Learn more at [n8n.io](https://n8n.io)
