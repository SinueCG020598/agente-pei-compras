# PEI Compras AI 🤖

Sistema inteligente de automatización de compras usando agentes AI para PEI.

[![CI](https://github.com/pei/pei-compras-ai/workflows/CI/badge.svg)](https://github.com/pei/pei-compras-ai/actions)
[![Tests](https://github.com/pei/pei-compras-ai/workflows/Tests/badge.svg)](https://github.com/pei/pei-compras-ai/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Descripción

PEI Compras AI es un sistema multi-agente que automatiza el proceso completo de compras empresariales, desde la recepción de solicitudes hasta la generación de órdenes de compra.

### Características Principales

- **Recepción Multi-canal**: Solicitudes desde WhatsApp (Evolution API) y formularios web
- **Procesamiento Inteligente**: Análisis automático de solicitudes usando OpenAI GPT-4
- **Búsqueda de Proveedores**: Identificación automática de proveedores adecuados
- **Generación de RFQs**: Creación y envío automático de solicitudes de cotización por email
- **Análisis de Cotizaciones**: Comparación inteligente de ofertas
- **Generación de Documentos**: Órdenes de compra automáticas
- **Dashboard Interactivo**: Interfaz Streamlit para seguimiento en tiempo real

## Stack Tecnológico

- **Backend**: Python 3.11+, FastAPI
- **IA**: OpenAI API (GPT-4o, GPT-4o-mini), LangChain, LangGraph
- **Base de Datos**: SQLite (desarrollo) → PostgreSQL (producción)
- **WhatsApp**: Evolution API
- **Email**: SMTP/IMAP (Gmail)
- **Frontend**: Streamlit
- **Testing**: pytest, pytest-cov
- **CI/CD**: GitHub Actions
- **Code Quality**: Black, Ruff, MyPy

## Requisitos Previos

- Python 3.11 o superior
- Docker y Docker Compose (para Evolution API)
- Cuenta OpenAI con API key
- Cuenta Gmail con App Password
- Git

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/pei/pei-compras-ai.git
cd pei-compras-ai
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
# Producción
make install

# Desarrollo (incluye tools de testing y linting)
make install-dev
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y completa con tus credenciales:

```bash
cp .env.example .env
nano .env  # o usa tu editor favorito
```

Variables críticas a configurar:

```env
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxx

# Evolution API (WhatsApp)
EVOLUTION_API_KEY=tu-api-key-aqui
EVOLUTION_API_URL=http://localhost:8080

# Gmail
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

### 5. Levantar servicios Docker

```bash
# Inicia Evolution API y MongoDB
make docker-up
```

### 6. Configurar base de datos

```bash
make setup
```

### 7. Verificar instalación

```bash
# Ejecuta el script de verificación
python scripts/test_setup.py

# O ejecuta los tests
make test
```

## Uso

### Iniciar API Backend

```bash
make run-api
```

La API estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

### Iniciar Frontend

```bash
make run-frontend
```

El frontend estará disponible en: `http://localhost:8501`

### Ejecutar Tests

```bash
# Todos los tests
make test

# Con reporte de cobertura
make test-cov

# Solo tests unitarios
pytest tests/unit/ -v

# Solo tests de integración
pytest tests/integration/ -v
```

### Formatear y Lint

```bash
# Formatear código con Black y Ruff
make format

# Ejecutar linters
make lint
```

## Estructura del Proyecto

```
pei-compras-ai/
├── .github/              # CI/CD workflows
├── config/               # Configuración centralizada
│   ├── settings.py       # Settings con Pydantic
│   └── logging_config.py # Configuración de logs
├── src/                  # Código fuente
│   ├── agents/           # Agentes AI
│   ├── database/         # Modelos y ORM
│   ├── services/         # Servicios externos
│   ├── api/              # API REST (FastAPI)
│   ├── schemas/          # Pydantic schemas
│   ├── core/             # Excepciones, seguridad
│   └── prompts/          # Prompts para agentes
├── frontend/             # Interfaz Streamlit
├── tests/                # Suite de tests
│   ├── unit/             # Tests unitarios
│   ├── integration/      # Tests de integración
│   └── e2e/              # Tests end-to-end
├── scripts/              # Scripts de utilidad
├── docs/                 # Documentación
└── logs/                 # Logs de la aplicación
```

## Flujo de Trabajo

1. **Recepción**: Usuario envía solicitud por WhatsApp o formulario web
2. **Procesamiento**: Agente Receptor analiza y estructura la solicitud
3. **Búsqueda**: Agente Investigador identifica proveedores potenciales
4. **RFQ**: Agente Generador crea y envía solicitudes de cotización
5. **Monitoreo**: Agente Monitor rastrea respuestas de proveedores
6. **Análisis**: Agente Analista compara cotizaciones
7. **Documentación**: Agente Documentador genera orden de compra

## Comandos Útiles

```bash
make help           # Ver todos los comandos disponibles
make install        # Instalar dependencias
make install-dev    # Instalar deps de desarrollo
make setup          # Setup completo del proyecto
make test           # Ejecutar tests
make test-cov       # Tests con cobertura
make lint           # Ejecutar linters
make format         # Formatear código
make clean          # Limpiar archivos temporales
make run-api        # Correr API FastAPI
make run-frontend   # Correr frontend Streamlit
make docker-up      # Levantar servicios Docker
make docker-down    # Detener servicios Docker
```

## Desarrollo

### Pre-commit Hooks

El proyecto usa pre-commit hooks para mantener calidad del código:

```bash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files
```

### Guía de Contribución

1. Crea un branch desde `develop`:
   ```bash
   git checkout -b feature/mi-feature
   ```

2. Escribe código con type hints y docstrings

3. Agrega tests para nuevas funcionalidades

4. Asegúrate que los tests pasen:
   ```bash
   make test
   ```

5. Formatea el código:
   ```bash
   make format
   ```

6. Crea un Pull Request a `develop`

### Estándares de Código

- **Style Guide**: PEP 8
- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type Checker**: MyPy
- **Docstrings**: Google Style
- **Coverage Mínima**: 80%

## Testing

### Estrategia de Testing

- **Unit Tests**: Funciones y clases individuales
- **Integration Tests**: Interacciones entre módulos
- **E2E Tests**: Flujos completos del sistema

### Ejecutar Tests Específicos

```bash
# Un archivo
pytest tests/unit/test_setup.py -v

# Un test específico
pytest tests/unit/test_setup.py::TestSetupInicial::test_estructura_directorios_existe -v

# Con coverage
pytest tests/ --cov=src --cov-report=html

# Ver reporte HTML
open htmlcov/index.html
```

## Configuración Avanzada

### Evolution API (WhatsApp)

1. Accede a la API: `http://localhost:8080`
2. Crea una instancia de WhatsApp
3. Escanea el QR code con WhatsApp
4. Actualiza `EVOLUTION_INSTANCE_NAME` en `.env`

### Gmail App Password

1. Ve a tu cuenta Google: https://myaccount.google.com/security
2. Habilita verificación en 2 pasos
3. Genera App Password: https://myaccount.google.com/apppasswords
4. Copia el password a `GMAIL_APP_PASSWORD` en `.env`

### PostgreSQL (Producción)

Para migrar de SQLite a PostgreSQL:

1. Descomenta el servicio `postgres` en `docker-compose.yml`
2. Actualiza `DATABASE_URL` en `.env`:
   ```env
   DATABASE_URL=postgresql://pei_user:pei_password@localhost:5432/pei_compras
   ```
3. Ejecuta migraciones:
   ```bash
   alembic upgrade head
   ```

## Documentación

- [Arquitectura del Sistema](docs/architecture.md)
- [Documentación API](docs/api_docs.md)
- [Guía de Deployment](docs/deployment.md)
- [Setup Fase 0](docs/fase_0_setup.md)

## Roadmap

Ver [ROADMAP.md](ROADMAP.md) para el plan completo de desarrollo.

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para historial de cambios.

## Troubleshooting

### Error: OpenAI API Key inválida

Verifica que tu API key esté correcta en `.env` y tenga créditos disponibles.

### Error: Evolution API no responde

Asegúrate que Docker esté corriendo:
```bash
docker ps
make docker-up
```

### Error: Tests fallan por falta de .env

Copia `.env.example` a `.env` con credenciales válidas.

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## Soporte

Para reportar bugs o solicitar features:
- Abre un issue en GitHub
- Contacta al equipo de desarrollo

## Autores

**PEI Team** - Desarrollo inicial

---

Hecho con ❤️ por el equipo de PEI
