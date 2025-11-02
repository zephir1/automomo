# Workflows

This directory contains all n8n workflow files exported as JSON.

## Organization

- Each workflow should be saved as a `.json` file
- Use descriptive names for workflow files (e.g., `slack-notification.json`, `github-backup.json`)
- You can create subdirectories to organize workflows by category if needed

## Exporting Workflows from n8n

1. Open your workflow in n8n
2. Click on the workflow menu (three dots)
3. Select "Download"
4. Save the JSON file to this directory
5. Commit and push to this repository

## Importing Workflows to n8n

1. Open n8n
2. Click "Import from File" or "Import from URL"
3. Select the workflow JSON file from this directory
4. The workflow will be imported with all nodes and connections
