# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Por Hacer
- Implementación de Generador RFQ + Email Service (FASE 4)
- Implementación de WhatsApp Básico (FASE 5)
- Monitor + Comparador de Cotizaciones (FASE 6)
- Audio + Imágenes + Refinamiento (FASE 7)

## [0.5.0] - 2025-11-13

### Fase 3: Búsqueda Web de Proveedores - COMPLETADO ✅

#### Added

- ✅ **SearchService Mejorado** (`src/services/search_service.py` - 180+ líneas nuevas)
  - Integración completa con Serper API (Google Search)
  - Método `buscar_proveedores_web()` - Busca proveedores en internet
  - Método `buscar_en_ecommerce()` - Busca en marketplaces (Amazon, MercadoLibre, Liverpool)
  - Método `buscar_mejores_precios()` - Combina búsqueda web + ecommerce
  - Método `_extraer_precio()` - Extrae precios con regex (múltiples formatos)
  - Método `_get_marketplace_name()` - Mapeo de dominios a nombres amigables
  - Soporte para 5 marketplaces mexicanos
  - Graceful degradation sin API key
  - Timeout configurado (30s)
  - Logging detallado con emojis

- ✅ **Agente Investigador** (`src/agents/investigador.py` - 180+ líneas)
  - Búsqueda multi-fuente: BD Local + Web + E-commerce
  - Función `buscar_proveedores(productos, usar_web=True)`
  - Integración con SearchService
  - Análisis inteligente con GPT-4o-mini
  - Recomendaciones por fuente y estrategia
  - Resultado completo con todas las fuentes
  - Enriquecimiento de datos de BD
  - Manejo robusto de errores
  - Backward compatible (funciona sin web search)

- ✅ **Prompt Investigador** (`src/prompts/investigador_prompt.txt` - 70+ líneas)
  - Análisis de 3 fuentes simultáneas
  - Criterios de evaluación por fuente
  - Formato JSON estructurado
  - Recomendaciones de estrategia (cotización/compra_directa/investigar)
  - Priorización (alta/media/baja)
  - Estimación de ahorros

- ✅ **Comparador de Precios** (FASE 3.5) (`src/agents/comparador_precios.py` - 120+ líneas)
  - Función `comparar_precios_multiples_fuentes()`
  - Análisis de 4 factores: Precio, Tiempo, Confiabilidad, Términos
  - Recomendación principal con justificación
  - Comparativa detallada por fuente
  - Análisis de trade-offs
  - Alertas automáticas
  - Estimación de ahorros
  - Modelo GPT-4o para análisis financiero

- ✅ **Tests FASE 3** (`tests/test_fase_3.py` - 350+ líneas)
  - 12 tests unitarios e integración
  - Tests para SearchService (búsqueda web, ecommerce, precios)
  - Tests para Agente Investigador (con/sin web)
  - Tests para Comparador de Precios
  - Mocking completo de APIs (Serper, OpenAI)
  - Fixtures reutilizables
  - Test E2E de flujo completo
  - Marca @pytest.mark.integration para tests costosos

- ✅ **Script Manual** (`test_fase_3_manual.py` - 250+ líneas)
  - Prueba interactiva de 3 componentes
  - Test 1: SearchService (proveedores + ecommerce)
  - Test 2: Agente Investigador (flujo completo)
  - Test 3: Comparador de Precios (análisis)
  - Output formateado con emojis
  - Resumen de resultados
  - Duración: ~2-3 minutos

- ✅ **Documentación FASE 3**
  - `docs/RESUMEN_FASE_3.md` - Resumen ejecutivo completo (280+ líneas)
  - `docs/COMO_PROBAR_FASE_3.md` - Guía de pruebas paso a paso (450+ líneas)
  - Secciones: Quick Start, Tests Detallados, Troubleshooting, Checklist
  - Ejemplos de código ejecutables
  - Comandos de referencia rápida
  - Solución de problemas comunes

#### Changed

- 🔧 README.md actualizado con FASE 3 completada
- 🔧 Versión actualizada de 0.4.0 → 0.5.0
- 🔧 Estado del proyecto: 3 fases completadas (de 7)
- 🔧 Tabla de fases actualizada con links a documentación

#### Technical Details

- **APIs Integradas**: Serper API (Google Search)
- **Modelos IA**: GPT-4o-mini (Investigador), GPT-4o (Comparador)
- **Marketplaces**: Amazon MX, MercadoLibre, Liverpool, Walmart, Home Depot
- **Tests**: 12 nuevos (total: 30+)
- **Cobertura**: >85% en nuevos componentes
- **Líneas de código**: ~900 nuevas
- **Archivos creados**: 7
- **Archivos modificados**: 4

#### Mejoras Implementadas

1. **Búsqueda Multi-fuente**: Ya no solo BD, ahora 3 fuentes simultáneas
2. **Inteligencia Mejorada**: IA decide mejor estrategia por fuente
3. **Compra Directa**: Enlaces a marketplaces para compra inmediata
4. **Análisis de Precios**: Comparador inteligente con trade-offs
5. **Graceful Degradation**: Funciona sin SERPER_API_KEY (solo BD)
6. **Logging Mejorado**: Trazabilidad completa de búsquedas
7. **Type Safety**: Type hints en todas las funciones
8. **Error Handling**: Manejo robusto de timeouts y errores de red
9. **Testing Completo**: Unit + Integration + E2E + Manual
10. **Documentación Exhaustiva**: Resumen + Guía de pruebas

#### Performance

- **Rate Limits**: 2500 búsquedas gratis/mes (Serper)
- **Timeout**: 30s por búsqueda
- **Proveedores**: De ~5 (BD) a 50+ (web+ecommerce)
- **Ahorro estimado**: 10-30% en comparaciones
- **Tiempo de respuesta**: 2-5s por búsqueda completa

#### Migration Notes

Para actualizar a v0.5.0:
```bash
# 1. Configurar API key de Serper
echo "SERPER_API_KEY=tu-api-key" >> .env

# 2. No requiere migraciones de BD
# 3. Verificar instalación
pytest tests/test_fase_3.py -v

# 4. Probar manualmente
python test_fase_3_manual.py
```

## [0.4.0] - 2025-11-11

### Fase 2: Agente Receptor + Formulario Web - COMPLETADO ✅

#### Added

- ✅ **Agente Receptor** (`src/agents/receptor.py` - 320+ líneas)
  - Procesamiento de lenguaje natural con OpenAI
  - Extracción estructurada de solicitudes informales
  - Modelos Pydantic: `ProductoExtraido`, `SolicitudProcesada`
  - Validación automática de categorías, urgencias, presupuestos
  - Función `procesar_solicitud(texto, origen)`
  - Función `validar_solicitud(datos)`
  - Temperatura IA: 0.3 para precisión
  - Carga dinámica de prompt desde archivo
  - Manejo de 6 categorías de productos
  - Detección de 3 niveles de urgencia
  - Instancia global reutilizable
  - 84% cobertura de código

- ✅ **Prompt del Agente** (`src/prompts/receptor_prompt.txt` - 150+ líneas)
  - Instrucciones detalladas para el agente
  - Formato JSON estructurado con schema
  - 3 ejemplos de uso (simple, compleja, informal)
  - Reglas de categorización y validación
  - Manejo de ambigüedad y casos edge

- ✅ **Aplicación Streamlit** (`frontend/app.py` - 670+ líneas)
  - Interfaz web profesional con 3 tabs:
    - 📝 Nueva Solicitud: Formulario inteligente
    - 📚 Mis Solicitudes: Historial con filtros
    - 📊 Estadísticas: Métricas del sistema
  - Procesamiento en tiempo real con IA
  - Cards visuales para productos
  - Badges de urgencia con colores (🟢 🟡 🔴)
  - Sidebar interactivo con métricas
  - Configuración de usuario (nombre, email)
  - Guardado automático en base de datos
  - CSS personalizado (150+ líneas)
  - Filtros por estado y límite de resultados
  - Integración completa con CRUD de FASE 1

- ✅ **Suite de Tests** (`tests/test_agente_receptor.py` - 500+ líneas)
  - 18 tests unitarios (100% passed)
  - Tests de validación (6 tests)
  - Tests de modelos Pydantic (5 tests)
  - Tests con mocks de OpenAI (4 tests)
  - Tests de manejo de errores (3 tests)
  - Tests de integración opcionales (2 tests, skipped)
  - 4 fixtures reutilizables
  - 84% cobertura de código

- ✅ **Migración EnvioTracking** (`alembic/versions/a32997d10b1e_*.py`)
  - Tabla `envios_tracking` con 13 campos
  - Enum `EstadoEnvio` con 8 estados
  - Relación one-to-one con OrdenCompra
  - 4 índices para performance

- ✅ **Documentación FASE 2**
  - `docs/RESUMEN_FASE_2.md` (600+ líneas)
  - Guía de uso completa
  - Ejemplos de las 3 solicitudes
  - Instrucciones de ejecución
  - Métricas y estadísticas
  - Checklist de verificación

#### Changed
- 📝 Actualizado `src/database/models.py` con modelo `EnvioTracking`
- 📝 Actualizado `src/database/crud.py` con `CRUDEnvioTracking`
- 📝 Agregado `consultar_historial()` para vista 360° de solicitudes
- 📝 Aplicadas migraciones de Alembic

#### Technical Details
- Tests: 18/18 passed (100%)
- Cobertura Agente Receptor: 84%
- Líneas de código nuevas: 1540+
- Archivos creados: 4
- Modelos Pydantic: 2 nuevos
- Categorías soportadas: 6
- Niveles de urgencia: 3
- Tabs en UI: 3
- Temperatura OpenAI: 0.3
- Response format: JSON forzado

#### Integration
- ✅ Integración con CRUD de Solicitud (FASE 1)
- ✅ Guardado en base de datos SQLite
- ✅ Uso de estados y enums existentes
- ✅ Compatible con migraciones Alembic

## [0.3.0] - 2025-11-08

### Fase 2: Servicios Externos - COMPLETADO ✅

#### Added

- ✅ **OpenAI Service** (`src/services/openai_service.py` - 450+ líneas)
  - Análisis de solicitudes con GPT-4o-mini
  - Generación de RFQs personalizados
  - Análisis de cotizaciones recibidas
  - Comparación inteligente de múltiples cotizaciones
  - Chat completion genérico
  - Extracción de JSON estructurado
  - Modelos Pydantic: `SolicitudAnalizada`, `CotizacionAnalizada`
  - 11 tests unitarios (74% cobertura)

- ✅ **WhatsApp Service** (`src/services/whatsapp_service.py` - 460+ líneas)
  - Cliente Evolution API completo
  - Envío de mensajes de texto y media
  - Gestión de instancia (QR code, estado)
  - Configuración de webhooks
  - Procesamiento de mensajes recibidos
  - Soporte async con aiohttp
  - Formateo de números telefónicos
  - Modelos: `WhatsAppMessage`, `WhatsAppMediaMessage`, `WebhookMessage`
  - 23 tests unitarios (78% cobertura)

- ✅ **Email Service** (`src/services/email_service.py` - 500+ líneas)
  - Cliente SMTP para envío (Gmail)
  - Cliente IMAP para recepción
  - Soporte de HTML y adjuntos
  - Parsing completo de emails
  - Extracción de adjuntos
  - Decodificación de headers
  - Método específico `send_rfq()`
  - Modelos: `EmailMessage`, `ReceivedEmail`
  - Implementación completa

- ✅ **Search Service** (`src/services/search_service.py` - 320+ líneas)
  - Cliente Serper API (Google Search)
  - Búsqueda general con parámetros
  - Búsqueda especializada de proveedores
  - Búsqueda de precios
  - Búsqueda de información de contacto
  - Extracción automática de email/teléfono
  - Modelos: `SearchResult`, `ProveedorEncontrado`
  - Implementación completa

- ✅ **Tests de Servicios** (34 tests)
  - 11 tests OpenAI Service
  - 23 tests WhatsApp Service
  - Framework de mocking completo
  - Fixtures reutilizables
  - 100% tests pasando

- ✅ **Documentación Técnica**
  - `docs/fase_2_servicios.md` (900+ líneas)
  - Guía completa de cada servicio
  - Ejemplos de uso detallados
  - Diagramas de arquitectura
  - Flujos de integración

#### Changed
- 📝 Actualizado `src/services/__init__.py` con exports de todos los servicios
- 📝 Agregados modelos Pydantic para validación de datos
- 📝 Configurados headers y autenticación para cada API

#### Technical Details
- APIs integradas: OpenAI, Evolution API, Gmail, Serper
- Total de tests: 50 (16 fase 1 + 34 fase 2)
- Cobertura servicios: 52% promedio
- Líneas de código servicios: 945
- Modelos Pydantic: 9 nuevos
- Dependencias: requests, aiohttp, openai

## [0.2.0] - 2025-11-06

### Fase 1: Base de Datos y Modelos - COMPLETADO

#### Added
- ✅ **Modelos SQLAlchemy** (320+ líneas)
  - `Solicitud` - Solicitudes de compra con 14 campos
  - `Proveedor` - Proveedores con 16 campos
  - `RFQ` - Request for Quotation con 11 campos
  - `Cotizacion` - Cotizaciones recibidas con 13 campos
  - `OrdenCompra` - Órdenes de compra con 16 campos
  - Enums para estados (EstadoSolicitud, EstadoRFQ, EstadoOrdenCompra)
  - Relaciones bidireccionales completas
  - Timestamps automáticos
  - 22 índices para performance

- ✅ **Sistema de Migraciones con Alembic**
  - Alembic inicializado y configurado
  - `alembic.ini` personalizado
  - `alembic/env.py` con auto-import de modelos
  - Primera migración generada y aplicada
  - 5 tablas creadas en SQLite

- ✅ **CRUD Operations** (450+ líneas)
  - Clase base genérica `CRUDBase` con operaciones comunes
  - 5 clases CRUD especializadas:
    - `CRUDSolicitud` - 4 métodos específicos
    - `CRUDProveedor` - 4 métodos específicos
    - `CRUDRFQ` - 4 métodos específicos
    - `CRUDCotizacion` - 3 métodos específicos
    - `CRUDOrdenCompra` - 4 métodos específicos
  - Total: 30+ métodos CRUD
  - Manejo robusto de errores
  - Logging estructurado
  - Type hints completos

- ✅ **Datos de Prueba**
  - 10 proveedores de prueba en 5 categorías
  - Datos realistas de empresas chilenas
  - Script idempotente (`seed_proveedores.py`)
  - Categorías: tecnología, mobiliario, insumos, servicios, equipamiento

- ✅ **Tests Unitarios**
  - `tests/unit/test_database/test_models.py`
  - Tests de creación de modelos
  - Validación de estados por defecto
  - Configuración de fixtures

- ✅ **Documentación Técnica**
  - `docs/fase_1_database.md` (400+ líneas)
  - Diagramas de relaciones
  - Descripción completa de modelos
  - Guía de CRUD operations
  - Ejemplos de uso
  - Comandos de verificación

#### Changed
- 📝 Actualizado `scripts/setup_database.py` para usar Alembic
- 📝 Actualizado `scripts/seed_data.py` con seed de proveedores
- 📝 Actualizado `src/database/__init__.py` con exports

#### Technical Details
- Base de datos: SQLite (desarrollo) → PostgreSQL (producción)
- ORM: SQLAlchemy 2.0.23
- Migraciones: Alembic 1.13.0
- Total de archivos: 13 creados/modificados
- Líneas de código: 800+ en database layer

## [0.1.0] - 2025-11-06

### Fase 0: Setup Inicial Completo

#### Added
- ✅ Estructura completa del proyecto
  - Directorios organizados para src/, tests/, docs/, config/, etc.
  - Paquetes Python con __init__.py

- ✅ Configuración de proyecto
  - `pyproject.toml` con Poetry
  - `requirements.txt` y `requirements-dev.txt`
  - `setup.py` para instalación editable
  - `.editorconfig` para consistencia de código

- ✅ Control de calidad
  - `.gitignore` robusto
  - `.pre-commit-config.yaml` con hooks
  - Configuración de Black (formatter)
  - Configuración de Ruff (linter)
  - Configuración de MyPy (type checker)

- ✅ Automatización
  - `Makefile` con comandos útiles
  - `docker-compose.yml` para servicios externos

- ✅ Configuración Python
  - `config/settings.py` con Pydantic Settings
  - `config/logging_config.py` con logging estructurado
  - Carga automática desde .env
  - Validación de tipos completa

- ✅ Scripts de utilidad
  - `scripts/test_setup.py` - Verificación completa del setup
  - `scripts/setup_database.py` - Configuración de base de datos
  - `scripts/seed_data.py` - Datos iniciales
  - `scripts/check_dependencies.py` - Verificación de dependencias

- ✅ Tests iniciales (Fase 0)
  - `tests/conftest.py` con fixtures compartidas
  - `tests/unit/test_setup.py` con 15 tests
  - Cobertura de estructura, configuración y archivos
  - Configuración de pytest en pyproject.toml

- ✅ Variables de entorno
  - `.env.example` como template completo
  - `.env` creado automáticamente
  - Documentación de todas las variables necesarias

- ✅ CI/CD con GitHub Actions
  - `.github/workflows/ci.yml` - Integración continua
  - `.github/workflows/lint.yml` - Linting automático
  - `.github/workflows/tests.yml` - Tests automáticos
  - Matrix testing en Python 3.11 y 3.12

- ✅ Documentación completa
  - `README.md` profesional con badges y guías
  - `docs/fase_0_setup.md` - Documentación detallada de Fase 0
  - `docs/architecture.md` - Arquitectura del sistema
  - `docs/api_docs.md` - Documentación de API
  - `docs/deployment.md` - Guía de deployment
  - `CHANGELOG.md` - Este archivo

#### Dependencies
- **Backend**: FastAPI 0.104.1, Uvicorn 0.24.0
- **IA**: OpenAI 1.3.0, LangChain 0.1.0, LangGraph 0.0.20
- **Database**: SQLAlchemy 2.0.23, Alembic 1.13.0
- **Frontend**: Streamlit 1.29.0
- **Testing**: pytest 7.4.3, pytest-cov 4.1.0, pytest-asyncio 0.21.1
- **Code Quality**: Black 23.12.0, Ruff 0.1.8, MyPy 1.7.1

#### Infrastructure
- Docker Compose para servicios externos
- Evolution API para WhatsApp
- MongoDB para Evolution API
- SQLite para desarrollo (migración a PostgreSQL planeada)

#### Technical Details
- Python 3.11+ requerido
- Type hints completos
- Docstrings en Google Style
- Logging estructurado
- Manejo de errores robusto
- Settings centralizados con validación

### Changed
- N/A (primera versión)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Variables de entorno para secrets
- .env excluido de git
- JWT para autenticación (preparado)
- Validación de entrada con Pydantic

## Roadmap

### v0.2.0 - Fase 1: Base de Datos y Modelos
- [ ] Modelos SQLAlchemy (Solicitud, Proveedor, RFQ, Cotización, OrdenCompra)
- [ ] Configuración de Alembic
- [ ] CRUD operations
- [ ] Tests de base de datos
- [ ] Seed data para desarrollo

### v0.3.0 - Fase 2: Servicios Externos
- [ ] OpenAI Service (chat completions, embeddings)
- [ ] WhatsApp Service (Evolution API integration)
- [ ] Email Service (SMTP/IMAP)
- [ ] Search Service (Serper API)
- [ ] Tests de integración

### v0.4.0 - Fase 3: Agentes AI
- [ ] Agente Base
- [ ] Agente Receptor
- [ ] Agente Investigador
- [ ] Agente Generador RFQ
- [ ] Agente Monitor
- [ ] Agente Analista
- [ ] Agente Documentador
- [ ] Orquestador con LangGraph
- [ ] Tests de agentes

### v0.5.0 - Fase 4: API REST
- [ ] Endpoints CRUD para todas las entidades
- [ ] Autenticación JWT
- [ ] Autorización RBAC
- [ ] Webhooks (WhatsApp, Email)
- [ ] Rate limiting
- [ ] Tests de API

### v0.6.0 - Fase 5: Frontend
- [ ] App principal Streamlit
- [ ] Página: Nueva Solicitud
- [ ] Página: Mis Solicitudes
- [ ] Página: Estadísticas
- [ ] Componentes reutilizables
- [ ] Tests E2E

### v1.0.0 - MVP Completo
- [ ] Flujo completo funcional
- [ ] Documentación completa
- [ ] Cobertura de tests > 80%
- [ ] Performance optimizado
- [ ] Deployment en producción
- [ ] Monitoreo implementado

## Versiones Futuras

### v1.1.0
- [ ] WebSockets para actualizaciones en tiempo real
- [ ] Notificaciones push
- [ ] Dashboard mejorado

### v1.2.0
- [ ] Multi-tenancy
- [ ] Roles y permisos avanzados
- [ ] Audit log

### v1.3.0
- [ ] Integración con ERPs
- [ ] Exportación de reportes
- [ ] Analytics avanzados

### v2.0.0
- [ ] Migración a microservicios
- [ ] Message queue (RabbitMQ/Kafka)
- [ ] Cache distribuido (Redis)
- [ ] Kubernetes deployment

## Notas

- Las versiones siguen Semantic Versioning: MAJOR.MINOR.PATCH
- MAJOR: Cambios incompatibles en la API
- MINOR: Nueva funcionalidad compatible hacia atrás
- PATCH: Bug fixes compatibles hacia atrás

---

**Mantenido por**: PEI Team
**Última actualización**: 2025-11-06
