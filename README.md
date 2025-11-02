# 🤖 Automomo# automomo



Sistema de sincronización bidireccional para workflows de n8n con GitHub.n8n Flows for automomo - A version-controlled repository for n8n workflow automation.



## 🎯 ¿Qué es Automomo?## Structure



Automomo es un sistema que mantiene sincronizados tus workflows de n8n con un repositorio Git, permitiendo:```

.

- ✅ **Control de versiones** para tus workflows├── workflows/          # All n8n workflow JSON files

- ✅ **Sincronización bidireccional**: Git ↔️ n8n│   └── README.md      # Guide for managing workflows

- ✅ **Trabajo con GitHub Copilot** para crear workflows con IA└── README.md          # This file

- ✅ **Backup automático** de cambios en n8n```

- ✅ **Deploy desde Git** a n8n con un comando

## Quick Start

## 🚀 Quick Start

### Exporting Workflows

### Instalación

1. Open your workflow in n8n

```bash2. Click on the workflow menu (⋮)

cd /home/bigmomo_n8n_cristian/automomo3. Select "Download"

./setup.sh4. Save the JSON file to the `workflows/` directory

```5. Commit and push:

   ```bash

### Uso básico   git add workflows/your-workflow.json

   git commit -m "Add: your workflow description"

```bash   git push

# Ver estado de sincronización   ```

./automomo status

### Importing Workflows

# Descargar workflows desde n8n (Pull)

./automomo pull1. Open n8n

2. Click "Import from File" or use the workflow menu

# Subir workflows a n8n (Push)3. Select a workflow JSON file from the `workflows/` directory

./automomo push4. The workflow will be imported with all nodes and connections



# Sincronización completa (Pull + Push)## Best Practices

./automomo sync

```- **Naming**: Use descriptive names (e.g., `slack-notification.json`, `data-sync.json`)

- **Documentation**: Add comments in workflow descriptions within n8n

## 📖 Documentación- **Credentials**: Never commit credentials - use n8n's credential system

- **Testing**: Test workflows before committing

- **[SETUP.md](SETUP.md)** - Configuración inicial detallada- **Versioning**: Use meaningful commit messages to track changes

- **[WORKFLOW_BACKUP_SETUP.md](WORKFLOW_BACKUP_SETUP.md)** - Configurar backup automático en n8n

## About n8n

## 🔄 Flujo de trabajo

n8n is a fair-code distributed workflow automation tool. Learn more at [n8n.io](https://n8n.io)

### Opción 1: Manual (recomendado para empezar)

1. **Edita workflows en n8n** (interfaz visual)
2. **Descarga cambios**:
   ```bash
   ./automomo pull
   ```
3. **Revisa cambios**:
   ```bash
   git diff
   ```
4. **Commit y push**:
   ```bash
   git add workflows/
   git commit -m "update: descripción de cambios"
   git push
   ```

### Opción 2: Automática

1. Configura el workflow "n8n - backup to git" siguiendo [WORKFLOW_BACKUP_SETUP.md](WORKFLOW_BACKUP_SETUP.md)
2. Los cambios en n8n se sincronizarán automáticamente a Git

### Opción 3: Deploy desde Git

1. **Edita workflows localmente** (archivos JSON)
2. **Prueba antes de subir**:
   ```bash
   ./automomo push --dry-run
   ```
3. **Sube a n8n**:
   ```bash
   ./automomo push
   ```

## 📦 Comandos disponibles

### `./automomo status`
Muestra el estado de sincronización entre Git y n8n.

```bash
# Ver estado básico
./automomo status

# Ver estado con detalles de cambios
./automomo status -v
```

### `./automomo pull`
Descarga workflows desde n8n y los guarda en `workflows/`.

```bash
./automomo pull
```

### `./automomo push`
Sube workflows desde Git a n8n.

```bash
# Subir todos los workflows
./automomo push

# Subir workflows específicos
./automomo push "n8n - error trigger" "asana - create pre environment"

# Ver qué se subiría sin hacer cambios (dry-run)
./automomo push --dry-run

# Forzar actualización aunque no haya cambios
./automomo push --force
```

### `./automomo sync`
Sincronización completa bidireccional (pull + push).

```bash
# Sincronización completa
./automomo sync

# Solo pull (sin push)
./automomo sync --no-push

# Dry-run (ver qué se haría)
./automomo sync --dry-run
```

## 📁 Estructura del proyecto

```
automomo/
├── workflows/              # Workflows en formato JSON
│   ├── n8n-error-trigger.json
│   ├── asana-create-pre-environment.json
│   └── ...
├── scripts/               # Scripts de sincronización
│   ├── automomo.py       # ⭐ Script principal
│   ├── sync_workflows.py # Pull (n8n → Git)
│   ├── deploy_to_n8n.py  # Push (Git → n8n)
│   ├── n8n_client.py     # Cliente API de n8n
│   └── crypto_helper.py  # Encriptación de credenciales
├── config/                # Configuración (no en git)
│   ├── .encryption_key
│   ├── config.json
│   └── config.encrypted
├── automomo              # ⭐ Comando principal
├── setup.sh              # Script de configuración
├── SETUP.md              # Documentación de setup
├── WORKFLOW_BACKUP_SETUP.md  # Setup de backup automático
└── README.md             # Este archivo
```

## 🔐 Seguridad

- ✅ API Keys encriptadas localmente con Fernet
- ✅ Archivos sensibles excluidos de Git (.gitignore)
- ✅ Permisos 600 en archivos de claves

**Archivos NO incluidos en Git:**
- `config/.encryption_key`
- `config/config.json`
- `config/config.encrypted`

## 🎨 Nomenclatura de archivos

Los workflows se guardan en formato **kebab-case**:

| Nombre en n8n | Archivo en Git |
|---------------|----------------|
| `n8n - error trigger` | `n8n-error-trigger.json` |
| `(ai) gmail - triage of labels` | `ai-gmail-triage-of-labels.json` |
| `asana - create pre environment` | `asana-create-pre-environment.json` |

## 🤝 Trabajo con GitHub Copilot

Con todos los workflows en Git, GitHub Copilot puede:

1. **Ver y entender** la estructura de tus workflows
2. **Sugerir mejoras** en nodos y conexiones
3. **Crear nuevos workflows** desde cero
4. **Detectar errores** y patrones problemáticos

**Ejemplo de uso:**

1. Abre un workflow JSON en VS Code
2. Pide a Copilot: "Añade un nodo de error handling a este workflow"
3. Copilot sugerirá el código JSON necesario
4. Guarda y haz push a n8n: `./automomo push`

## 🛠️ Scripts Python individuales

Si prefieres usar los scripts directamente:

```bash
# Pull
python3 scripts/sync_workflows.py

# Push
python3 scripts/deploy_to_n8n.py --dry-run

# Cliente de API
python3 scripts/n8n_client.py list
python3 scripts/n8n_client.py get <workflow_id>
```

## 🔧 Configuración avanzada

### Cambiar frecuencia de backup automático

Si usas el workflow de n8n para backup automático, edita el nodo "Schedule Trigger":

- Cada 5 minutos: `*/5 * * * *`
- Cada hora: `0 * * * *`
- Cada día a las 2 AM: `0 2 * * *`

### Usar cronjob en lugar de workflow n8n

```bash
# Editar crontab
crontab -e

# Añadir línea para sync cada 5 minutos
*/5 * * * * cd /home/bigmomo_n8n_cristian/automomo && ./automomo pull >> logs/sync.log 2>&1
```

## 📊 Ejemplos de uso

### Crear un nuevo workflow desde Git

1. Crea un archivo JSON en `workflows/`:
   ```bash
   cp workflows/n8n-error-trigger.json workflows/mi-nuevo-workflow.json
   ```

2. Edita el JSON (cambia nombre, nodos, etc.)

3. Sube a n8n:
   ```bash
   ./automomo push "mi nuevo workflow"
   ```

### Backup de workflow específico

```bash
# Pull de todo
./automomo pull

# Commit solo un workflow
git add workflows/workflow-importante.json
git commit -m "backup: workflow importante"
git push
```

### Restaurar workflow desde Git

```bash
# Si borraste un workflow en n8n por error
git log workflows/workflow-borrado.json  # Ver historial
git checkout <commit> workflows/workflow-borrado.json  # Restaurar
./automomo push "workflow borrado"  # Subir a n8n
```

## 🐛 Troubleshooting

### Error: "No se encontró configuración"

```bash
./setup.sh  # Reconfigura las credenciales
```

### Los nombres de archivo no coinciden

Ejecuta pull para regenerar con nomenclatura correcta:
```bash
./automomo pull
```

### Push no detecta cambios

```bash
./automomo push --force  # Forzar actualización
```

## 📚 Links útiles

- **n8n**: https://automomo.bigmomo.com
- **GitHub Repo**: https://github.com/zephir1/automomo
- **n8n API Docs**: https://docs.n8n.io/api/

## 🤖 Sobre este proyecto

Creado para mantener workflows de n8n sincronizados con Git y poder trabajar con GitHub Copilot de forma eficiente.

**Autor**: Cristian Alcaraz  
**Organización**: BigMomo  
**Fecha**: Noviembre 2025

---

**¿Preguntas o problemas?** Revisa [SETUP.md](SETUP.md) o consulta la documentación de n8n.
