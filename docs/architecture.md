# Arquitectura del Sistema PEI Compras AI

## Visión General

PEI Compras AI es un sistema multi-agente basado en IA que automatiza el proceso completo de compras empresariales, desde la recepción de solicitudes hasta la generación de órdenes de compra.

## Principios de Diseño

1. **Modularidad**: Componentes desacoplados y reutilizables
2. **Escalabilidad**: Preparado para crecer en funcionalidad y usuarios
3. **Mantenibilidad**: Código limpio, documentado y testeado
4. **Observabilidad**: Logging estructurado y monitoreo
5. **Resiliencia**: Manejo robusto de errores

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────┐
│                        CANALES DE ENTRADA                    │
├───────────────────┬─────────────────────┬──────────────────┤
│   WhatsApp        │   Formulario Web    │   Email          │
│  (Evolution API)  │   (Streamlit)       │   (IMAP)         │
└────────┬──────────┴──────────┬──────────┴──────────┬───────┘
         │                      │                      │
         └──────────────────────┴──────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   API REST (FastAPI)│
                    │   /api/v1/*         │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┴─────────────────────┐
         │                                            │
    ┌────▼────────────────────────────────────────┐  │
    │         SISTEMA DE AGENTES AI               │  │
    │         (LangChain + LangGraph)             │  │
    ├─────────────────────────────────────────────┤  │
    │  ┌──────────────────────────────────────┐  │  │
    │  │   Orquestador (StateGraph)           │  │  │
    │  │   - Coordina flujo completo          │  │  │
    │  │   - Maneja estado compartido         │  │  │
    │  └───────────────┬──────────────────────┘  │  │
    │                  │                          │  │
    │  ┌───────────────▼──────────────────────┐  │  │
    │  │  Agentes Especializados              │  │  │
    │  ├──────────────────────────────────────┤  │  │
    │  │ 1. Receptor        (Procesar input)  │  │  │
    │  │ 2. Investigador    (Buscar proveed.) │  │  │
    │  │ 3. Generador RFQ   (Crear RFQs)      │  │  │
    │  │ 4. Monitor         (Rastrear resp.)  │  │  │
    │  │ 5. Analista        (Comparar cot.)   │  │  │
    │  │ 6. Documentador    (Gen. OC)         │  │  │
    │  └──────────────────────────────────────┘  │  │
    └─────────────────────────────────────────────┘  │
                               │                      │
         ┌─────────────────────┴──────────────────────┘
         │                      │
    ┌────▼─────┐          ┌────▼─────────┐
    │  Base de │          │  Servicios   │
    │  Datos   │          │  Externos    │
    ├──────────┤          ├──────────────┤
    │ SQLite/  │          │ - OpenAI API │
    │ Postgres │          │ - Gmail      │
    │          │          │ - WhatsApp   │
    │ Modelos: │          │ - Serper     │
    │ - Solici │          └──────────────┘
    │ - Provee │
    │ - RFQ    │
    │ - Cotiza │
    │ - OC     │
    └──────────┘
```

## Componentes Principales

### 1. Capa de Presentación

#### 1.1 Frontend Streamlit (`frontend/`)

- **Aplicación Multipágina**
  - Nueva Solicitud: Formulario para crear solicitudes
  - Mis Solicitudes: Ver estado y seguimiento
  - Estadísticas: Dashboard con métricas

- **Componentes Reutilizables**
  - Sidebar: Navegación y filtros
  - Forms: Formularios de entrada
  - Tables: Tablas de datos
  - Charts: Visualizaciones

#### 1.2 API REST (`src/api/`)

- **Framework**: FastAPI
- **Versión**: v1 (`/api/v1/`)
- **Endpoints**:
  - `/solicitudes`: CRUD de solicitudes
  - `/proveedores`: Gestión de proveedores
  - `/rfqs`: Gestión de RFQs
  - `/cotizaciones`: Gestión de cotizaciones
  - `/webhooks`: Webhooks de servicios externos

### 2. Capa de Negocio

#### 2.1 Sistema de Agentes AI (`src/agents/`)

**Agente Base** (`base.py`):
- Clase abstracta con métodos comunes
- Conexión a OpenAI
- Logging estructurado
- Manejo de errores

**Agentes Especializados**:

1. **Receptor** (`receptor.py`):
   - Procesa solicitudes iniciales
   - Extrae información estructurada
   - Valida completitud

2. **Investigador** (`investigador.py`):
   - Busca proveedores en base de datos
   - Busca proveedores en web (Serper API)
   - Filtra por categoría y ubicación

3. **Generador RFQ** (`generador_rfq.py`):
   - Genera RFQs personalizados
   - Formatea según proveedor
   - Envía por email

4. **Monitor** (`monitor.py`):
   - Monitorea emails entrantes
   - Detecta respuestas de proveedores
   - Extrae cotizaciones

5. **Analista** (`analista.py`):
   - Compara cotizaciones
   - Analiza costo, tiempo, calidad
   - Genera recomendación

6. **Documentador** (`documentador.py`):
   - Genera orden de compra
   - Formatea documento
   - Envía para aprobación

**Orquestador** (`orquestador.py`):
- Usa LangGraph StateGraph
- Coordina flujo entre agentes
- Maneja estado compartido
- Implementa lógica condicional

#### 2.2 Servicios Externos (`src/services/`)

1. **OpenAI Service** (`openai_service.py`):
   - Cliente OpenAI wrapper
   - Chat completions
   - Function calling
   - Embeddings

2. **WhatsApp Service** (`whatsapp.py`):
   - Cliente Evolution API
   - Enviar/recibir mensajes
   - Gestión de instancias
   - Webhooks

3. **Email Service** (`email_service.py`):
   - SMTP para envío
   - IMAP para recepción
   - Parser de emails
   - Extracción de adjuntos

4. **Search Service** (`search_service.py`):
   - Cliente Serper API
   - Búsqueda web de proveedores
   - Extracción de info de contacto

### 3. Capa de Datos

#### 3.1 Base de Datos (`src/database/`)

**Modelos SQLAlchemy** (`models.py`):

```python
Solicitud:
  - id
  - usuario_id
  - descripcion
  - categoria
  - presupuesto
  - fecha_limite
  - estado (pendiente, en_proceso, completada)
  - created_at, updated_at

Proveedor:
  - id
  - nombre
  - email
  - telefono
  - categoria
  - ubicacion
  - rating
  - created_at, updated_at

RFQ:
  - id
  - solicitud_id
  - proveedor_id
  - contenido
  - estado (enviado, respondido, ignorado)
  - fecha_envio
  - created_at, updated_at

Cotizacion:
  - id
  - rfq_id
  - precio
  - tiempo_entrega
  - condiciones
  - archivo_adjunto
  - created_at, updated_at

OrdenCompra:
  - id
  - solicitud_id
  - cotizacion_id
  - numero_orden
  - estado (borrador, enviada, aprobada, rechazada)
  - archivo
  - created_at, updated_at
```

**CRUD Operations** (`crud.py`):
- Operaciones genéricas
- Filtros y paginación
- Transacciones

#### 3.2 Migraciones

- Alembic para gestión de cambios de esquema
- Versionado automático
- Rollback support

### 4. Capa de Configuración

#### 4.1 Settings (`config/settings.py`)

- Pydantic Settings
- Validación de tipos
- Carga desde .env
- Type hints completos

#### 4.2 Logging (`config/logging_config.py`)

- Logging estructurado
- Niveles configurables
- Múltiples handlers (consola, archivo)
- Formato consistente

### 5. Capa de Utilidades

#### 5.1 Core (`src/core/`)

- **Exceptions** (`exceptions.py`): Excepciones personalizadas
- **Security** (`security.py`): JWT, hashing, validación
- **Utils** (`utils.py`): Funciones auxiliares

#### 5.2 Schemas (`src/schemas/`)

- Pydantic models para validación
- Request/Response schemas
- Serialización automática

## Flujo de Datos

### Flujo Completo de una Solicitud

```
1. ENTRADA
   Usuario → WhatsApp/Web → API REST

2. PROCESAMIENTO
   API → Agente Receptor → Extrae info estructurada

3. BÚSQUEDA
   Agente Investigador → DB + Serper → Lista proveedores

4. RFQ
   Agente Generador → Crea RFQs → Email Service → Proveedores

5. MONITOREO
   Email Service → Agente Monitor → Detecta respuestas

6. ANÁLISIS
   Agente Analista → Compara cotizaciones → Genera recomendación

7. DOCUMENTACIÓN
   Agente Documentador → Genera OC → Envía para aprobación

8. NOTIFICACIÓN
   WhatsApp/Email → Usuario → Resultado final
```

### Estado Compartido (LangGraph)

```python
class AgentState(TypedDict):
    solicitud: Dict
    proveedores: List[Dict]
    rfqs: List[Dict]
    cotizaciones: List[Dict]
    analisis: Dict
    orden_compra: Optional[Dict]
    errores: List[str]
```

## Patrones de Diseño

### 1. Repository Pattern
- CRUD operations encapsuladas
- Abstracción de base de datos
- Facilita testing

### 2. Service Layer Pattern
- Lógica de negocio separada
- Servicios reutilizables
- Dependency injection

### 3. Agent Pattern
- Agentes autónomos especializados
- Comunicación asíncrona
- Estado compartido

### 4. Strategy Pattern
- Diferentes estrategias de envío (email, WhatsApp)
- Diferentes proveedores de IA
- Diferentes formatos de RFQ

## Seguridad

### 1. Autenticación
- JWT tokens
- API keys para servicios externos
- Rate limiting

### 2. Autorización
- Role-based access control (RBAC)
- Permisos granulares

### 3. Datos Sensibles
- Encriptación en tránsito (HTTPS)
- Secrets en variables de entorno
- No logs de información sensible

### 4. Validación
- Pydantic para validación de entrada
- Sanitización de datos
- SQL injection prevention (SQLAlchemy ORM)

## Escalabilidad

### Fase 1 (Actual): Monolito
- Todos los componentes en un proceso
- SQLite para desarrollo
- Adecuado para pruebas y MVP

### Fase 2: Servicios Separados
- API en contenedor separado
- Frontend en contenedor separado
- PostgreSQL en contenedor separado
- Redis para cache

### Fase 3: Microservicios
- Cada agente como servicio independiente
- Message queue (RabbitMQ/Kafka)
- Kubernetes para orquestación

### Fase 4: Serverless
- Functions as a Service (AWS Lambda, Cloud Functions)
- Event-driven architecture
- Auto-scaling

## Monitoreo y Observabilidad

### Logs
- Logging estructurado con contexto
- Niveles: DEBUG, INFO, WARNING, ERROR
- Rotación automática

### Métricas
- Tiempo de respuesta de agentes
- Tasa de éxito/error
- Uso de tokens OpenAI
- Costo por solicitud

### Alertas
- Errores críticos
- Uso excesivo de API
- Tiempos de respuesta altos

## Testing

### Pirámide de Testing

```
       ┌─────────┐
       │   E2E   │  ← Pocos, críticos
       ├─────────┤
       │  Integ. │  ← Moderados
       ├─────────┤
       │  Unit   │  ← Muchos, rápidos
       └─────────┘
```

### Estrategia

1. **Unit Tests**:
   - Cada función/método
   - Mocks de servicios externos
   - Coverage > 80%

2. **Integration Tests**:
   - Interacción entre componentes
   - Base de datos real (SQLite test)
   - APIs mockeadas

3. **E2E Tests**:
   - Flujos completos
   - Todos los servicios reales
   - Datos de prueba

## Deployment

### Desarrollo
```bash
# Local
make run-api        # API en localhost:8000
make run-frontend   # Frontend en localhost:8501
make docker-up      # Evolution API
```

### Staging
- Docker Compose
- Todos los servicios en contenedores
- Base de datos PostgreSQL
- Variables de entorno staging

### Producción
- Kubernetes cluster
- Load balancer
- Auto-scaling
- Backups automáticos
- Monitoring (Prometheus + Grafana)

## Tecnologías y Dependencias

### Backend
- **FastAPI**: API REST moderna y rápida
- **Pydantic**: Validación de datos
- **SQLAlchemy**: ORM
- **Alembic**: Migraciones

### IA
- **OpenAI API**: LLMs (GPT-4o, GPT-4o-mini)
- **LangChain**: Framework para aplicaciones LLM
- **LangGraph**: Orquestación de agentes

### Comunicación
- **Evolution API**: WhatsApp Business
- **SMTP/IMAP**: Email
- **Serper API**: Búsqueda web

### Frontend
- **Streamlit**: UI interactiva

### DevOps
- **Docker**: Contenedores
- **GitHub Actions**: CI/CD
- **pytest**: Testing
- **Black/Ruff**: Code quality

## Limitaciones y Consideraciones

### Actuales
1. SQLite no es adecuado para producción
2. Procesamiento secuencial (no paralelo)
3. Sin cache de resultados
4. Sin queue para trabajos largos

### Futuras Mejoras
1. Migrar a PostgreSQL
2. Implementar procesamiento paralelo
3. Agregar Redis cache
4. Implementar Celery para tareas async
5. Agregar webhooks para notificaciones
6. Implementar retry logic robusto

## Referencias

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [SQLAlchemy Patterns](https://docs.sqlalchemy.org/en/20/)

---

**Última actualización**: 2025-11-06
**Versión**: 1.0
**Autor**: PEI Team
