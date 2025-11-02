# Automomo - Configuración

## 🔑 Configurar API Key de n8n

### Paso 1: Obtener tu API Key de n8n

1. Abre tu instancia de n8n en: https://automomo.bigmomo.com
2. Ve a **Settings** → **API**
3. Copia tu API Key

### Paso 2: Guardar la configuración de forma segura

Ejecuta el siguiente comando para configurar tu API key de forma encriptada:

```bash
cd /home/bigmomo_n8n_cristian/automomo
python3 scripts/crypto_helper.py
```

Sigue las instrucciones para introducir:
- **URL de n8n**: https://automomo.bigmomo.com
- **API Key**: [tu API key de n8n]

Esto creará un archivo `config/.env.encrypted` con tus credenciales de forma segura.

### Paso 3: Sincronizar workflows

Una vez configurado, puedes sincronizar tus workflows manualmente:

```bash
python3 scripts/sync_workflows.py
```

Esto descargará todos los workflows activos de n8n y los guardará en `workflows/` con nombres en formato kebab-case.

### Paso 4: Commit y push a GitHub

```bash
git add workflows/
git commit -m "sync: Update workflows from n8n"
git push origin main
```

## 🤖 Automatización con n8n

Para automatizar este proceso, puedes usar el workflow **"n8n - backup to git"** que ya tienes en n8n. Este workflow:

1. Se ejecuta cada minuto (configurable)
2. Obtiene todos los workflows activos
3. Los convierte a formato kebab-case
4. Hace commit automático a GitHub

Solo necesitas activarlo y configurar las credenciales de GitHub OAuth2 en n8n.

---

## 📁 Estructura del proyecto

```
automomo/
├── config/
│   ├── .env.encrypted          # API keys encriptadas (NO en git)
│   └── config.example.json     # Ejemplo de configuración
├── scripts/
│   ├── crypto_helper.py        # Encriptación de credenciales
│   ├── n8n_client.py          # Cliente de API de n8n
│   ├── flow_manager.py        # Gestión de flujos
│   └── sync_workflows.py      # Sincronización con git
├── workflows/
│   ├── n8n-error-trigger.json
│   ├── asana-create-pre-environment.json
│   └── ...                     # Todos tus workflows
└── README.md
```

## 🛠️ Scripts disponibles

### `crypto_helper.py`
Gestión de credenciales encriptadas
```bash
python3 scripts/crypto_helper.py
```

### `n8n_client.py`
Interactuar con la API de n8n
```bash
# Listar workflows
python3 scripts/n8n_client.py list

# Obtener workflow específico
python3 scripts/n8n_client.py get <workflow_id>
```

### `sync_workflows.py`
Sincronizar workflows de n8n a git
```bash
python3 scripts/sync_workflows.py
```

### `flow_manager.py`
Gestión completa de flujos
```bash
python3 scripts/flow_manager.py
```

---

## 🔄 Workflow de trabajo recomendado

1. **Crear/Editar workflows en n8n** (interfaz visual)
2. **Ejecutar sincronización manual** cuando hayas hecho cambios importantes:
   ```bash
   cd /home/bigmomo_n8n_cristian/automomo
   python3 scripts/sync_workflows.py
   git add workflows/
   git commit -m "update: [descripción de cambios]"
   git push
   ```
3. **Activar backup automático** (workflow en n8n) para sincronización continua

---

## 🤝 Integración con GitHub Copilot

Con todos los workflows en git:
- ✅ GitHub Copilot puede ver y entender tus flujos
- ✅ Puedes pedir a Copilot que cree nuevos workflows
- ✅ Control de versiones completo
- ✅ Colaboración en equipo facilitada

---

## 📝 Convenciones de nombres

Los workflows se guardan con formato **kebab-case**:

| Nombre en n8n | Archivo en git |
|---------------|----------------|
| `n8n - error trigger` | `n8n-error-trigger.json` |
| `(ai) gmail - triage of labels` | `ai-gmail-triage-of-labels.json` |
| `asana - create pre environment` | `asana-create-pre-environment.json` |
