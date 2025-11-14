#!/bin/bash

# Script para iniciar el frontend de PEI Compras AI
# Uso: ./iniciar_frontend.sh

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}║           🛒 PEI Compras AI - Frontend Streamlit              ║${NC}"
echo -e "${BLUE}║                      Versión 0.4.0                             ║${NC}"
echo -e "${BLUE}║                                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar directorio
if [ ! -f "frontend/app.py" ]; then
    echo -e "${YELLOW}⚠️  Error: No estás en el directorio correcto${NC}"
    echo -e "${YELLOW}   Debes ejecutar este script desde: /home/sinuecg/proyects/pei-compras-ai${NC}"
    echo ""
    exit 1
fi

# Activar entorno virtual
echo -e "${GREEN}1. Activando entorno virtual...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Error: No se encontró el entorno virtual 'venv'${NC}"
    echo -e "${YELLOW}   Ejecuta: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    echo ""
    exit 1
fi

source venv/bin/activate

# Verificar Streamlit
echo -e "${GREEN}2. Verificando Streamlit...${NC}"
if ! python -c "import streamlit" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Streamlit no está instalado. Instalando...${NC}"
    pip install streamlit
fi

# Verificar API key
echo -e "${GREEN}3. Verificando configuración...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: No se encontró archivo .env${NC}"
    echo -e "${YELLOW}   La aplicación puede fallar sin una OpenAI API key${NC}"
    echo ""
fi

# Verificar base de datos
if [ ! -f "pei_compras.db" ]; then
    echo -e "${YELLOW}⚠️  Advertencia: No se encontró la base de datos${NC}"
    echo -e "${YELLOW}   Ejecuta: python scripts/setup_database.py${NC}"
    echo ""
fi

echo -e "${GREEN}4. Iniciando aplicación Streamlit...${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ La aplicación se abrirá en tu navegador${NC}"
echo -e "${GREEN}📍 URL: http://localhost:8501${NC}"
echo ""
echo -e "${YELLOW}💡 Tip: Presiona Ctrl+C para detener el servidor${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Ejecutar Streamlit
streamlit run frontend/app.py
