#!/bin/bash
# Setup script para Automomo

echo "🤖 Automomo - Setup"
echo "===================="
echo ""

# Check Python dependencies
echo "📦 Verificando dependencias..."
python3 -c "import cryptography" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Instalando dependencias Python..."
    pip3 install -r requirements.txt
fi
echo ""

# Check if config exists
if [ -f "config/.env.encrypted" ]; then
    echo "✅ Configuración ya existe"
    echo ""
    read -p "¿Quieres reconfigurar? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Saliendo..."
        exit 0
    fi
fi

echo "📝 Configurando credenciales..."
echo ""
echo "Por favor, introduce la siguiente información:"
echo ""

# Get n8n URL
read -p "URL de n8n [https://automomo.bigmomo.com]: " N8N_URL
N8N_URL=${N8N_URL:-https://automomo.bigmomo.com}

# Get API Key
echo ""
echo "Para obtener tu API Key:"
echo "1. Abre $N8N_URL"
echo "2. Ve a Settings → API"
echo "3. Copia tu API Key"
echo ""
read -p "API Key de n8n: " N8N_API_KEY

# Create config file
echo ""
echo "💾 Guardando configuración..."

cat > config/config.json << EOF
{
  "n8n": {
    "url": "$N8N_URL",
    "api_key": "$N8N_API_KEY"
  }
}
EOF

# Encrypt config
echo "🔐 Encriptando configuración..."
python3 scripts/crypto_helper.py encrypt

# Test connection
echo ""
echo "🔌 Probando conexión con n8n..."
python3 scripts/n8n_client.py list

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Configuración completada exitosamente!"
    echo ""
    echo "Ahora puedes:"
    echo "  - Sincronizar workflows: python3 scripts/sync_workflows.py"
    echo "  - Listar workflows: python3 scripts/n8n_client.py list"
else
    echo ""
    echo "❌ Error al conectar con n8n"
    echo "Por favor, verifica tu API Key e intenta de nuevo"
    exit 1
fi
