# WHM - Proactive Disk Space Monitor

## 📋 Descripción

Workflow de n8n que monitoriza proactivamente el espacio en disco de todas las cuentas cPanel/WHM (solo usuarios de root, excluyendo resellers) en el servidor de producción. Identifica problemas potenciales y realiza limpieza automática de archivos seguros antes de que se conviertan en alertas críticas.

## 🎯 Funcionalidades

### Filtrado Inteligente de Usuarios
- **Solo usuarios del owner root**: Excluye automáticamente usuarios de resellers como "marficom"
- **Filtra cuentas del sistema**: Excluye root, nobody, mysql, cpanel, admin

### Análisis Automático
- **Lista todos los usuarios cPanel** del servidor WHM (filtrados por owner)
- **Analiza el espacio usado** por cada cuenta
- **Detecta problemas comunes**:
  - 🗑️ Logs grandes (>100MB) → **Se vacían automáticamente**
  - 💿 Dumps SQL grandes (>100MB) → **Se eliminan automáticamente**
  - 💾 Backups redundantes o antiguos (>30 días) → **Se eliminan automáticamente**
  - 📦 Archivos individuales muy grandes (>500MB) → Requieren revisión manual
  - 📁 Uploads de WordPress/Drupal grandes (>5GB) → Advertencia
  - 📝 Access logs excesivos (>1GB) → Advertencia
  - 📧 Buzones de correo grandes (>2GB) → Advertencia

### Limpieza Automática
El workflow realiza limpieza automática de forma segura:
1. **Vacía logs grandes** (trunca archivos sin eliminarlos)
2. **Elimina dumps SQL >100MB** (considerar que son backups de BD)
3. **Elimina backups antiguos** (>30 días) o **redundantes** (mantiene solo el más reciente)

### Notificaciones Inteligentes
- **Notificación individual** por cada limpieza automática realizada
- **Reporte final consolidado** con:
  - Resumen de usuarios analizados
  - Limpiezas automáticas realizadas
  - Problemas que requieren atención manual
  - Recomendaciones específicas
- **Solo notifica si hay actividad** (limpiezas o problemas detectados)

## ⚙️ Configuración

### Trigger: Schedule
Por defecto configurado para ejecutarse **cada lunes a las 9:00 AM**.

Puedes modificar la frecuencia en el nodo "Schedule Trigger":
- **Diaria**: `0 9 * * *` (cada día a las 9:00)
- **Semanal**: `0 9 * * 1` (cada lunes a las 9:00)
- **Quincenal**: `0 9 1,15 * *` (día 1 y 15 de cada mes)

### Credenciales Requeridas
- **SSH**: Acceso root al servidor WHM vía clave privada
  - Credencial: `ssh - bigmomo-1 production - root caution`
- **Google Chat**: Bot "automomo" (cristian automomo)
  - Credencial: `google service - cristian automomo`
  - Space ID: `spaces/AAQAs5SDuMQ`

### Umbrales Configurables

Puedes ajustar los umbrales de detección editando el nodo "Process Disk Analysis":

```javascript
// Cuenta muy grande
if (totalGB > 20) {  // Cambiar 20 por el límite deseado
  issues.push(`⚠️ Cuenta muy grande: ${totalSize}`);
}

// Logs grandes a vaciar
find . -type f ... -size +100M  // Cambiar 100M por el tamaño deseado

// Dumps SQL a eliminar (todos >100MB se eliminan automáticamente)
find . -type f \\( -name "*.sql" ... \\) -size +100M

// Archivos grandes (solo advertencia)
find . -type f -size +500M  // Cambiar 500M por el tamaño deseado

// WordPress uploads
if (wpBytes > 5 * 1024 * 1024 * 1024) {  // 5GB, ajustar según necesidad
```

### Lógica de Limpieza de Backups

El workflow aplica las siguientes reglas para backups:
- Si hay **múltiples backups**: Elimina todos excepto el más reciente
- Si hay **un solo backup** y es antiguo (>30 días): Lo elimina
- Esto evita acumular backups obsoletos que ocupan espacio

### Excluir Usuarios del Análisis

Los usuarios de resellers (como "marficom") ya están excluidos automáticamente.

Si quieres excluir usuarios adicionales del sistema, edita el nodo "Parse Users List":

```javascript
const systemUsers = ['root', 'nobody', 'mysql', 'cpanel', 'admin', 'test', 'demo'];
```

## 🔍 ¿Qué Analiza?

Para cada usuario cPanel (solo usuarios con OWNER=root), el workflow ejecuta los siguientes análisis:

1. **Tamaño total de la cuenta**
2. **Top 10 directorios más grandes**
3. **Logs grandes** (archivos .log, error_log, access_log >100MB) → **Se vacían**
4. **Archivos individuales muy grandes** (>500MB) → Solo advertencia
5. **WordPress uploads** (si existe wp-content/uploads)
6. **Drupal files** (si existe sites/default/files)
7. **Directorios de backups** con fecha de modificación
8. **Dumps de bases de datos** (archivos .sql, .sql.gz, .sql.bz2 >100MB) → **Se eliminan**
9. **Logs de acceso** (directorio access-logs)
10. **Buzones de correo** (directorio mail)

## 🧹 Limpieza Automática

El workflow realiza las siguientes acciones **automáticamente y de forma segura**:

### 1. Vaciar Logs Grandes (>100MB)
- **Acción**: `> archivo.log` (trunca el archivo sin eliminarlo)
- **Seguro**: Mantiene el archivo para que las aplicaciones no tengan errores
- **Aplica a**: `*.log`, `error_log`, `*_log`, `access_log`

### 2. Eliminar Dumps SQL (>100MB)
- **Acción**: `rm -f dump.sql`
- **Razón**: Los dumps SQL son copias de seguridad de bases de datos que suelen ser obsoletas
- **Umbral**: Solo dumps >100MB (los pequeños se conservan)

### 3. Eliminar Backups Redundantes/Antiguos
- **Si hay múltiples backups**: Elimina todos excepto el más reciente
- **Si hay un solo backup antiguo** (>30 días): Lo elimina
- **Acción**: `rm -rf directorio_backup/`

### ⚠️ Archivos que NO se eliminan automáticamente
- Archivos grandes individuales (>500MB): Requieren revisión manual
- WordPress/Drupal uploads: Solo advertencia, no se tocan
- Bases de datos activas: Solo se eliminan dumps, nunca archivos de BD en uso

## 📊 Ejemplo de Reporte

### Notificación Individual (Durante Limpieza)
```
🧹 Limpieza Automática - bigmomo

🗑️ 3 log(s) vaciado(s)
💿 2 dump(s) SQL eliminado(s)
💾 1 backup(s) eliminado(s)

💾 Tamaño total cuenta: 28G
```

### Reporte Final Consolidado
```
🔍 Monitorización de Espacio en Disco - WHM

📊 Resumen:
• Total de usuarios analizados: 42
• Usuarios con problemas/warnings: 8
• Usuarios con limpieza automática: 5
• Espacio total usado: 234.56 GB
• Fecha: 13/11/2025, 9:00:00

🧹 Limpiezas Automáticas Realizadas:
1. bigmomo: 🗑️ 3 log(s) vaciado(s), 💿 2 dump(s) SQL eliminado(s)
2. nargesa: 💾 2 backup(s) eliminado(s)
3. windsor: 🗑️ 1 log(s) vaciado(s)
...

⚠️ Usuarios que requieren atención:

1. bigmomo (26G)
   ✅ 🗑️ 3 log(s) vaciado(s), 💿 2 dump(s) SQL eliminado(s)
   📦 2 archivo(s) muy grande(s) (>500MB) - revisar manualmente
   📁 WordPress uploads grande: 12G
   📦 Archivos grandes (revisar): 2.1G, 850M

2. nargesa (15G)
   ✅ 💾 2 backup(s) eliminado(s)
   📁 Drupal files grande: 6G

...

---
💡 Recomendaciones:
• ✅ Logs grandes y dumps SQL: limpiados automáticamente
• ✅ Backups redundantes: eliminados automáticamente
• ⚠️ Archivos grandes: revisar manualmente si son necesarios
• ⚠️ Uploads de WordPress/Drupal grandes: optimizar si es necesario
```

## 🚀 Uso

### Desplegar el Workflow

1. El workflow ya está en el repositorio: `whm-proactive-disk-space-monitor.json`

2. Despliega a n8n usando automomo:
   ```bash
   cd /home/bigmomo_n8n_cristian/automomo
   ./automomo push
   ```

3. En n8n, abre el workflow "WHM - Proactive Disk Space Monitor"

4. Verifica las credenciales:
   - Nodos SSH → Credencial `ssh - bigmomo-1 production - root caution`
   - Nodos Google Chat → Credencial `google service - cristian automomo`

5. **Activa el workflow**

### Ejecución Manual

Para probar sin esperar al schedule:
1. Abre el workflow en n8n
2. Click en "Execute Workflow"
3. Observa:
   - Notificaciones individuales de limpieza (si hay archivos a limpiar)
   - Reporte final en Google Chat (si hay actividad)

### Flujo de Ejecución

```
Schedule Trigger (Lunes 9:00 AM)
  ↓
Obtener usuarios cPanel (solo OWNER=root)
  ↓
Para cada usuario:
  ↓
  Analizar uso de disco
  ↓
  ¿Necesita limpieza? (logs/dumps/backups grandes)
  ↓ Sí
  Realizar limpieza automática
  ↓
  ¿Se limpió algo?
  ↓ Sí
  Notificar limpieza individual en Google Chat
  ↓
Siguiente usuario...
  ↓
Agregrar resultados de todos los usuarios
  ↓
Formatear reporte final
  ↓
¿Hay actividad para reportar?
  ↓ Sí
Enviar reporte final a Google Chat
```

## 🔧 Mantenimiento

### Modificar Destino de Notificaciones

Si quieres cambiar el canal de Google Chat:

1. Ve a los nodos de Google Chat:
   - "Notify Cleanup (Individual)"
   - "Send Final Report to Chat"
2. Actualiza el `spaceId` con tu espacio de Chat
3. Guarda el workflow

### Excluir Usuarios del Análisis

Si hay usuarios que quieres excluir (ej: cuentas de prueba), edita el nodo "Parse Users List":

```javascript
const systemUsers = ['root', 'nobody', 'mysql', 'cpanel', 'admin', 'test', 'demo'];
```

Los usuarios de resellers (OWNER != root) ya están automáticamente excluidos en la obtención de usuarios.

### Personalizar Umbrales de Limpieza

En el nodo "SSH: Analyze User Disk", busca estas líneas:

- `size +100M` → Umbral de logs grandes a vaciar
- `size +100M` (en DB_DUMPS) → Umbral de dumps SQL a eliminar
- `size +500M` → Umbral de archivos grandes (solo advertencia)

En el nodo "Process Disk Analysis":

- Backups antiguos: Busca `thirtyDaysAgo` para cambiar los días
- Otras advertencias: Ajusta los valores de bytes según necesidad

### Deshabilitar Limpieza Automática

Si solo quieres el análisis sin limpieza automática:

1. Desconecta el nodo "SSH: Auto Cleanup"
2. Conecta "Filter: Needs Cleanup" (salida "false") directamente a "Loop Back to Next User"
3. El workflow solo reportará problemas sin limpiar

### Agregar Nuevos Análisis

Para agregar nuevas verificaciones:

1. Modifica el comando SSH en "SSH: Analyze User Disk"
2. Agrega secciones de análisis (ej: `CUSTOM_CHECK:`)
3. Actualiza el parser en "Process Disk Analysis"
4. Agrega lógica de issues/warnings según necesidad
5. Opcionalmente, agrega lógica de limpieza en "SSH: Auto Cleanup"

## 📝 Notas

- **Impacto en el servidor**: El análisis usa comandos `du` y `find` que pueden consumir recursos. El workflow procesa usuarios secuencialmente para minimizar impacto.
- **Tiempo de ejecución**: Depende del número de usuarios y tamaño de las cuentas. Estimado: 1-3 minutos por usuario.
- **Permisos**: Requiere acceso root SSH ya que necesita leer directorios de todos los usuarios.
- **Notificaciones duales**: 
  - Notificaciones individuales durante cada limpieza (inmediatas)
  - Reporte final consolidado al terminar el análisis completo
- **Seguridad de limpieza**:
  - Los logs se **vacían** (no se eliminan) para evitar errores en aplicaciones
  - Solo se eliminan dumps SQL y backups redundantes/antiguos
  - Archivos grandes requieren revisión manual
- **Filtrado de usuarios**: Solo analiza usuarios con OWNER=root, excluye resellers automáticamente

## 🐛 Troubleshooting

### No recibo notificaciones

1. Verifica que el workflow esté activo
2. Ejecuta manualmente y revisa los logs
3. Verifica que haya usuarios con problemas detectados o limpiezas realizadas
4. Comprueba las credenciales de Google Chat

### Error "Home directory not found"

- Usuario puede haber sido eliminado pero sigue en `/var/cpanel/users/`
- El script lo maneja con `continueOnFail: true`

### Timeout en SSH

- Reduce el número de usuarios procesados dividiendo en grupos
- Aumenta umbrales para archivos/logs
- Considera ejecutar en horarios de menor carga

### Usuarios de reseller aparecen en el análisis

- Verifica el comando en "SSH: Get cPanel Users (Root Only)"
- Debe filtrar por `OWNER=root` correctamente
- Revisa los logs del nodo para ver qué usuarios se obtienen

### Limpieza automática no funciona

1. Verifica que el nodo "Filter: Needs Cleanup" esté detectando archivos
2. Revisa los logs del nodo "SSH: Auto Cleanup"
3. Verifica permisos en los directorios de usuario
4. Comprueba que los paths de archivos sean correctos

### Demasiadas notificaciones individuales

- Puedes desactivar el nodo "Notify Cleanup (Individual)"
- Solo recibirás el reporte final consolidado
- Útil si prefieres menos interrupciones

## 🔄 Integración con Otros Workflows

Este workflow complementa:
- **gmail-cpanel-disk-quota-alert.json**: Responde a alertas reactivas de cPanel
- **n8n-backup-to-git.json**: Mantiene el workflow versionado

## 📚 Referencias

- [n8n SSH Node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.ssh/)
- [n8n Schedule Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/)
- [Google Chat Webhooks](https://developers.google.com/chat/how-tos/webhooks)
