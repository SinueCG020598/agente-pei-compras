

# Fase 1: Base de Datos y Modelos - Documentación Completa

**Fecha**: 2025-11-06
**Versión**: 0.2.0
**Estado**: ✅ COMPLETADO

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Objetivos Alcanzados](#objetivos-alcanzados)
3. [Arquitectura de Base de Datos](#arquitectura-de-base-de-datos)
4. [Modelos Implementados](#modelos-implementados)
5. [CRUD Operations](#crud-operations)
6. [Migraciones con Alembic](#migraciones-con-alembic)
7. [Datos de Prueba](#datos-de-prueba)
8. [Tests](#tests)
9. [Uso y Ejemplos](#uso-y-ejemplos)
10. [Próximos Pasos](#próximos-pasos)

---

## Resumen Ejecutivo

Se ha implementado exitosamente la **Fase 1** del proyecto, estableciendo una capa robusta de persistencia de datos con SQLAlchemy, migraciones con Alembic, operaciones CRUD completas y datos de prueba.

### Logros Principales

- ✅ 5 modelos SQLAlchemy completos con relaciones
- ✅ Sistema de migraciones con Alembic configurado
- ✅ CRUD operations genéricas y específicas
- ✅ 10 proveedores de prueba con datos realistas
- ✅ Tests unitarios para validación
- ✅ Documentación completa

---

## Objetivos Alcanzados

### 1. Modelos SQLAlchemy ✅

**Archivos creados**:
- `src/database/base.py` - Base declarativa
- `src/database/models.py` - 5 modelos completos (320+ líneas)
- `src/database/session.py` - Gestión de sesiones
- `src/database/__init__.py` - Exports centralizados

**Modelos implementados**:
1. **Solicitud** - Solicitudes de compra
2. **Proveedor** - Proveedores y sus datos
3. **RFQ** - Request for Quotation
4. **Cotización** - Cotizaciones recibidas
5. **OrdenCompra** - Órdenes de compra generadas

### 2. Configuración de Alembic ✅

- ✅ Alembic inicializado
- ✅ `alembic.ini` configurado
- ✅ `alembic/env.py` personalizado
- ✅ Primera migración generada y aplicada
- ✅ Todas las tablas creadas en SQLite

### 3. CRUD Operations ✅

- ✅ Clase base genérica `CRUDBase` con operaciones comunes
- ✅ 5 clases CRUD especializadas
- ✅ 30+ métodos CRUD implementados
- ✅ Manejo de errores y logging
- ✅ Type hints completos

### 4. Seed Data ✅

- ✅ 10 proveedores de prueba en 5 categorías
- ✅ Datos realistas de empresas chilenas
- ✅ Script idempotente (puede ejecutarse múltiples veces)

### 5. Tests ✅

- ✅ Tests de modelos
- ✅ Tests de creación de instancias
- ✅ Validación de estados por defecto

---

## Arquitectura de Base de Datos

### Diagrama de Relaciones

```
┌─────────────────┐
│   Solicitud     │
│  (solicitudes)  │
├─────────────────┤
│ id (PK)         │───┐
│ usuario_id      │   │
│ descripcion     │   │
│ categoria       │   │
│ presupuesto     │   │
│ estado          │   │
│ created_at      │   │
└─────────────────┘   │
                      │
                      │ 1:N
                      │
              ┌───────▼────────┐              ┌──────────────────┐
              │      RFQ       │              │   Proveedor      │
              │    (rfqs)      │              │  (proveedores)   │
              ├────────────────┤              ├──────────────────┤
              │ id (PK)        │              │ id (PK)          │
              │ solicitud_id(FK)│─────────────│ nombre           │
              │ proveedor_id(FK)│────────────▶│ email            │
              │ numero_rfq     │              │ categoria        │
              │ contenido      │              │ rating           │
              │ estado         │              │ es_verificado    │
              └────────┬───────┘              └──────────────────┘
                       │
                       │ 1:N
                       │
              ┌────────▼─────────┐
              │   Cotizacion     │
              │ (cotizaciones)   │
              ├──────────────────┤
              │ id (PK)          │
              │ rfq_id (FK)      │───┐
              │ precio_total     │   │
              │ tiempo_entrega   │   │
              │ puntaje_ia       │   │
              └──────────────────┘   │
                                     │ 1:N
                                     │
                          ┌──────────▼──────────┐
                          │   OrdenCompra       │
                          │ (ordenes_compra)    │
                          ├─────────────────────┤
                          │ id (PK)             │
                          │ solicitud_id (FK)   │
                          │ cotizacion_id (FK)  │
                          │ numero_orden        │
                          │ monto_total         │
                          │ estado              │
                          └─────────────────────┘
```

### Tablas Creadas

| Tabla | Columnas | Relaciones | Indices |
|-------|----------|------------|---------|
| **solicitudes** | 14 | → rfqs, ordenes_compra | 4 |
| **proveedores** | 16 | → rfqs | 6 |
| **rfqs** | 11 | ← solicitud, proveedor<br>→ cotizaciones | 5 |
| **cotizaciones** | 13 | ← rfq<br>→ ordenes_compra | 2 |
| **ordenes_compra** | 16 | ← solicitud, cotizacion | 5 |

**Total**: 5 tablas, 70 columnas, 22 índices

---

## Modelos Implementados

### 1. Solicitud

Representa una solicitud de compra.

**Campos principales**:
```python
id: int                           # PK
usuario_id: str                   # ID del usuario
usuario_nombre: str               # Nombre del usuario
usuario_contacto: str             # Email o teléfono
descripcion: Text                 # Descripción detallada
categoria: str                    # Categoría del producto
cantidad: str (opcional)          # Cantidad solicitada
presupuesto: float (opcional)     # Presupuesto máximo
fecha_limite: DateTime (opcional) # Fecha límite
prioridad: int                    # 1-5 (default: 3)
estado: EstadoSolicitud           # Estado actual
created_at: DateTime              # Auto
updated_at: DateTime              # Auto
```

**Estados posibles**:
- `PENDIENTE` (default)
- `EN_PROCESO`
- `COTIZACIONES_RECIBIDAS`
- `APROBADA`
- `COMPLETADA`
- `CANCELADA`

**Relaciones**:
- `rfqs` → List[RFQ]
- `ordenes_compra` → List[OrdenCompra]

### 2. Proveedor

Representa un proveedor de productos/servicios.

**Campos principales**:
```python
id: int                     # PK
nombre: str                 # Nombre del proveedor
razon_social: str (opcional)# Razón social legal
rut: str (opcional, unique) # RUT/NIT
email: str                  # Email principal
telefono: str (opcional)    # Teléfono
direccion: str (opcional)   # Dirección física
ciudad: str (opcional)      # Ciudad
pais: str                   # País (default: "Chile")
sitio_web: str (opcional)   # URL
categoria: str              # Categoría principal
subcategorias: Text (opcional) # JSON de subcategorías
rating: float               # 0-5 (default: 0.0)
es_verificado: bool         # Verificado (default: False)
created_at: DateTime        # Auto
updated_at: DateTime        # Auto
```

**Relaciones**:
- `rfqs` → List[RFQ]

### 3. RFQ (Request for Quotation)

Representa una solicitud de cotización a un proveedor.

**Campos principales**:
```python
id: int                    # PK
solicitud_id: int (FK)     # → solicitudes.id
proveedor_id: int (FK)     # → proveedores.id
numero_rfq: str (unique)   # Ej: "RFQ-2024-001"
asunto: str                # Asunto del email
contenido: Text            # Contenido del RFQ
estado: EstadoRFQ          # Estado actual
fecha_envio: DateTime (opcional)      # Fecha de envío
fecha_respuesta: DateTime (opcional)  # Fecha de respuesta
created_at: DateTime       # Auto
updated_at: DateTime       # Auto
```

**Estados posibles**:
- `BORRADOR` (default)
- `ENVIADO`
- `RESPONDIDO`
- `IGNORADO`
- `EXPIRADO`

**Relaciones**:
- `solicitud` ← Solicitud
- `proveedor` ← Proveedor
- `cotizaciones` → List[Cotizacion]

### 4. Cotizacion

Representa una cotización recibida de un proveedor.

**Campos principales**:
```python
id: int                    # PK
rfq_id: int (FK)           # → rfqs.id
precio_total: float        # Precio total
precio_unitario: float (opcional)  # Precio unitario
moneda: str                # Moneda (default: "CLP")
tiempo_entrega: int (opcional)     # Días
condiciones_pago: str (opcional)   # Condiciones
garantia: str (opcional)           # Información garantía
observaciones: Text (opcional)     # Observaciones
archivo_adjunto: str (opcional)    # URL/path archivo
archivo_nombre: str (opcional)     # Nombre archivo
es_valida: bool            # Válida (default: True)
puntaje_ia: float (opcional)       # Score 0-100
created_at: DateTime       # Auto
updated_at: DateTime       # Auto
```

**Relaciones**:
- `rfq` ← RFQ
- `ordenes_compra` → List[OrdenCompra]

### 5. OrdenCompra

Representa una orden de compra generada.

**Campos principales**:
```python
id: int                    # PK
solicitud_id: int (FK)     # → solicitudes.id
cotizacion_id: int (FK)    # → cotizaciones.id
numero_orden: str (unique) # Ej: "OC-2024-001"
estado: EstadoOrdenCompra  # Estado actual
monto_total: float         # Monto total
moneda: str                # Moneda (default: "CLP")
fecha_emision: DateTime (opcional)         # Fecha emisión
fecha_entrega_esperada: DateTime (opcional) # Entrega esperada
fecha_entrega_real: DateTime (opcional)    # Entrega real
condiciones: Text (opcional)               # Condiciones
observaciones: Text (opcional)             # Observaciones
archivo_oc: str (opcional)                 # PDF de la OC
aprobado_por: str (opcional)               # Quien aprobó
fecha_aprobacion: DateTime (opcional)      # Fecha aprobación
created_at: DateTime       # Auto
updated_at: DateTime       # Auto
```

**Estados posibles**:
- `BORRADOR` (default)
- `ENVIADA`
- `CONFIRMADA`
- `EN_PROCESO`
- `COMPLETADA`
- `CANCELADA`

**Relaciones**:
- `solicitud` ← Solicitud
- `cotizacion` ← Cotizacion

---

## CRUD Operations

### Arquitectura CRUD

**Clase Base Genérica**:
```python
class CRUDBase(Generic[ModelType]):
    def get(db, id) → ModelType
    def get_multi(db, skip, limit) → List[ModelType]
    def create(db, obj_in) → ModelType
    def update(db, db_obj, obj_in) → ModelType
    def delete(db, id) → ModelType
```

### CRUD Específicos Implementados

#### 1. CRUDSolicitud
```python
# Métodos adicionales
get_by_estado(db, estado)
get_by_usuario(db, usuario_id)
get_by_categoria(db, categoria)
cambiar_estado(db, solicitud_id, nuevo_estado)
```

#### 2. CRUDProveedor
```python
# Métodos adicionales
get_by_email(db, email)
get_by_categoria(db, categoria)
get_verificados(db)
actualizar_rating(db, proveedor_id, nuevo_rating)
```

#### 3. CRUDRFQ
```python
# Métodos adicionales
get_by_solicitud(db, solicitud_id)
get_by_proveedor(db, proveedor_id)
get_by_estado(db, estado)
marcar_enviado(db, rfq_id)
```

#### 4. CRUDCotizacion
```python
# Métodos adicionales
get_by_rfq(db, rfq_id)
get_mejor_precio(db, rfq_id)
get_mejor_puntaje(db, rfq_id)
```

#### 5. CRUDOrdenCompra
```python
# Métodos adicionales
get_by_numero(db, numero_orden)
get_by_solicitud(db, solicitud_id)
get_by_estado(db, estado)
aprobar(db, orden_id, aprobado_por)
```

### Uso de CRUD

```python
from src.database import crud
from src.database.session import get_db

# Crear proveedor
db = next(get_db())
proveedor = crud.proveedor.create(db, obj_in={
    "nombre": "Tech Solutions",
    "email": "ventas@tech.cl",
    "categoria": "tecnologia",
})

# Obtener proveedores por categoría
proveedores_tech = crud.proveedor.get_by_categoria(db, "tecnologia")

# Actualizar rating
crud.proveedor.actualizar_rating(db, proveedor.id, 4.5)
```

---

## Migraciones con Alembic

### Configuración

**Archivos configurados**:
- `alembic.ini` - Configuración base
- `alembic/env.py` - Importa modelos y settings
- `alembic/versions/` - Directorio de migraciones

### Comandos Principales

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Ver historial
alembic history

# Revertir última migración
alembic downgrade -1

# Ver estado actual
alembic current
```

### Migración Inicial

**Archivo**: `alembic/versions/fef61ec919d5_initial_migration_create_all_tables.py`

**Tablas creadas**:
- proveedores (6 índices)
- solicitudes (4 índices)
- rfqs (5 índices)
- cotizaciones (2 índices)
- ordenes_compra (5 índices)

---

## Datos de Prueba

### Proveedores de Prueba

Se crearon **10 proveedores** en **5 categorías**:

**Tecnología** (3 proveedores):
- Tech Solutions Chile
- Digitech Store
- Infotech Ltda

**Mobiliario** (2 proveedores):
- Muebles Corporativos SA
- Oficina Total

**Insumos** (2 proveedores):
- Suministros Empresariales Chile
- Papelería Nacional

**Servicios** (2 proveedores):
- Servicios Integrales Empresariales
- Aseo Industrial Pro

**Equipamiento** (1 proveedor):
- Equipos y Maquinaria Chile

### Cargar Datos

```bash
# Ejecutar seed
python3 scripts/seed_data.py

# O usando make
make setup
```

**Resultado esperado**:
```
🌱 SEED DE DATOS - PEI COMPRAS AI
✅ Creado proveedor: Tech Solutions Chile
✅ Creado proveedor: Digitech Store
...
📊 Resumen del seed:
   - Proveedores creados: 10
   - Total en base de datos: 10
✅ Seed de datos completado exitosamente
```

---

## Tests

### Tests Implementados

**Archivo**: `tests/unit/test_database/test_models.py`

**Cobertura**:
- ✅ Creación de Solicitud
- ✅ Estados por defecto
- ✅ Creación de Proveedor
- ✅ Creación de RFQ

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/

# Solo tests de database
pytest tests/unit/test_database/ -v

# Con coverage
pytest tests/unit/test_database/ --cov=src.database
```

---

## Uso y Ejemplos

### Ejemplo 1: Crear Solicitud

```python
from src.database import crud
from src.database.session import SessionLocal

db = SessionLocal()

# Crear solicitud
solicitud = crud.solicitud.create(db, obj_in={
    "usuario_nombre": "Juan Pérez",
    "usuario_contacto": "+56912345678",
    "descripcion": "Necesito 100 laptops HP EliteBook",
    "categoria": "tecnologia",
    "presupuesto": 150000000,
    "prioridad": 4,
})

print(f"Solicitud creada: {solicitud.id}")
```

### Ejemplo 2: Buscar Proveedores

```python
# Proveedores de tecnología verificados
proveedores = crud.proveedor.get_verificados(db)
proveedores_tech = [p for p in proveedores if p.categoria == "tecnologia"]

for proveedor in proveedores_tech:
    print(f"{proveedor.nombre} - Rating: {proveedor.rating}")
```

### Ejemplo 3: Crear RFQ

```python
# Crear RFQ para una solicitud
rfq = crud.rfq.create(db, obj_in={
    "solicitud_id": solicitud.id,
    "proveedor_id": proveedores_tech[0].id,
    "numero_rfq": "RFQ-2024-001",
    "asunto": "Solicitud de Cotización - Laptops HP",
    "contenido": "Estimado proveedor...",
})

# Marcar como enviado
crud.rfq.marcar_enviado(db, rfq.id)
```

### Ejemplo 4: Registrar Cotización

```python
# Registrar cotización recibida
cotizacion = crud.cotizacion.create(db, obj_in={
    "rfq_id": rfq.id,
    "precio_total": 145000000,
    "precio_unitario": 1450000,
    "tiempo_entrega": 15,
    "condiciones_pago": "30 días",
    "garantia": "1 año",
})

# Obtener mejor cotización
mejor = crud.cotizacion.get_mejor_precio(db, rfq.id)
```

---

## Próximos Pasos

### Fase 2: Servicios Externos

**Por implementar**:
1. **OpenAI Service** (`src/services/openai_service.py`)
   - Cliente para GPT-4/GPT-4o-mini
   - Funciones para análisis de solicitudes
   - Generación de contenido de RFQs

2. **WhatsApp Service** (`src/services/whatsapp.py`)
   - Cliente Evolution API
   - Envío/recepción de mensajes
   - Webhooks

3. **Email Service** (`src/services/email_service.py`)
   - SMTP para envío
   - IMAP para recepción
   - Parser de emails

4. **Search Service** (`src/services/search_service.py`)
   - Cliente Serper API
   - Búsqueda web de proveedores

### Testing Pendiente

- Tests de CRUD operations completos
- Tests de relaciones entre modelos
- Tests de integridad referencial
- Tests de performance (bulk inserts)

### Optimizaciones

- Índices adicionales basados en queries frecuentes
- Eager loading para relaciones
- Connection pooling optimizado
- Caché de queries frecuentes

---

## Comandos de Verificación

```bash
# Verificar estructura de BD
sqlite3 pei_compras.db ".schema"

# Ver proveedores en BD
sqlite3 pei_compras.db "SELECT nombre, categoria FROM proveedores;"

# Ver tablas creadas
sqlite3 pei_compras.db ".tables"

# Ejecutar tests
pytest tests/unit/test_database/ -v

# Generar nueva migración
alembic revision --autogenerate -m "Descripción"

# Aplicar migraciones
alembic upgrade head
```

---

## Archivos Creados en Fase 1

### Base de Datos (5 archivos)
1. `src/database/base.py` - Base declarativa
2. `src/database/models.py` - 5 modelos (320+ líneas)
3. `src/database/session.py` - Gestión de sesiones
4. `src/database/crud.py` - CRUD operations (450+ líneas)
5. `src/database/seed_proveedores.py` - Datos de prueba

### Migraciones (3 archivos)
1. `alembic.ini` - Configuración
2. `alembic/env.py` - Environment
3. `alembic/versions/fef61ec919d5_*.py` - Migración inicial

### Scripts (2 actualizados)
1. `scripts/setup_database.py` - Actualizado con Alembic
2. `scripts/seed_data.py` - Actualizado con seed de proveedores

### Tests (2 archivos)
1. `tests/unit/test_database/__init__.py`
2. `tests/unit/test_database/test_models.py`

### Documentación (1 archivo)
1. `docs/fase_1_database.md` - Este documento

**Total**: 13 archivos creados/modificados

---

## Métricas de Fase 1

| Métrica | Valor |
|---------|-------|
| Modelos implementados | 5 |
| Líneas de código (models) | 320+ |
| Líneas de código (crud) | 450+ |
| CRUD operations | 30+ |
| Proveedores de prueba | 10 |
| Tablas en BD | 5 |
| Índices creados | 22 |
| Tests implementados | 3 |
| Archivos creados/modificados | 13 |

---

## Estado Final - Fase 1

**✅ COMPLETADA AL 100%**

Todos los objetivos de la Fase 1 han sido alcanzados:
- ✅ Modelos SQLAlchemy completos
- ✅ Alembic configurado y funcionando
- ✅ CRUD operations implementadas
- ✅ Datos de prueba cargados
- ✅ Tests básicos creados
- ✅ Documentación completa

**Próximo**: Fase 2 - Servicios Externos

---

**Documentado por**: Claude Code
**Fecha**: 2025-11-06
**Versión**: 1.0
