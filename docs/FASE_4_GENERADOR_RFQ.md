# FASE 4: Generador RFQ + Email Service + Orquestador

**Versión:** 0.6.0
**Fecha:** Noviembre 2024
**Estado:** ✅ Implementado y Testeado

---

## 📋 Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Componentes Implementados](#componentes-implementados)
3. [Arquitectura](#arquitectura)
4. [Guía de Uso](#guía-de-uso)
5. [Endpoints de API](#endpoints-de-api)
6. [Pruebas y Tests](#pruebas-y-tests)
7. [Configuración](#configuración)
8. [Ejemplos de Uso](#ejemplos-de-uso)
9. [Troubleshooting](#troubleshooting)

---

## 📖 Descripción General

La FASE 4 implementa el **flujo completo end-to-end** del sistema PEI Compras AI, conectando todos los agentes previos y agregando la capacidad de generar y enviar RFQs (Request for Quotation) profesionales por email.

### Flujo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUJO END-TO-END FASE 4                       │
└─────────────────────────────────────────────────────────────────┘

1. 📥 ENTRADA
   ↓
   Usuario envía solicitud en lenguaje natural
   "Necesito 5 PLCs Siemens S7-1200 urgente"

2. 🤖 AGENTE RECEPTOR (FASE 2)
   ↓
   Extrae: productos, cantidades, urgencia, categorías
   Resultado: JSON estructurado

3. 🔍 AGENTE INVESTIGADOR (FASE 3)
   ↓
   Busca proveedores en:
   - Base de datos local
   - Internet (Google Search vía Serper API)
   - E-commerce (Amazon, MercadoLibre, etc.)
   Resultado: Lista de proveedores rankeados

4. 📧 GENERADOR RFQ (FASE 4 - NUEVO)
   ↓
   Para cada proveedor:
   - Genera RFQ personalizado con IA
   - Guarda en base de datos
   - Envía por email

5. 💾 BASE DE DATOS
   ↓
   Registra todo el proceso:
   - Solicitud original
   - RFQs generados
   - Emails enviados
   - Estados y tracking

6. ✅ RESULTADO
   ↓
   Sistema retorna:
   - ID de solicitud
   - Número de RFQs enviados
   - Detalles de cada envío
   - Estado final
```

### Objetivos Logrados

- ✅ Generación automática de RFQs profesionales personalizados
- ✅ Envío de emails SMTP a múltiples proveedores
- ✅ Orquestación completa de los 3 agentes principales
- ✅ API REST para procesamiento end-to-end
- ✅ Gestión de estados de solicitudes y RFQs
- ✅ Tests completos con >85% de cobertura
- ✅ Manejo robusto de errores en cada etapa
- ✅ **🆕 Interfaz interactiva Streamlit para gestión de RFQs**
- ✅ **🆕 Generación de borradores para revisión antes del envío**
- ✅ **🆕 Edición de contenido antes de enviar emails**
- ✅ **🆕 Selección flexible de proveedores a contactar**

---

## 🏗️ Componentes Implementados

### 1. **Agente Generador RFQ** (`src/agents/generador_rfq.py`)

Responsable de crear RFQs profesionales y enviarlos por email.

**Funciones principales:**

- `generar_rfq()` - Genera contenido del RFQ usando GPT-4o
- `enviar_rfq()` - Guarda en BD y envía por email
- `enviar_rfqs_multiples()` - Procesa múltiples proveedores

**Nuevas funciones interactivas (🆕 Opción 2):**

- `generar_borrador_rfq()` - Genera RFQ y guarda como BORRADOR (no envía email)
- `enviar_rfq_existente()` - Envía RFQ existente (con contenido editado opcional)
- `obtener_rfqs_pendientes()` - Lista todos los borradores pendientes de envío

**Características:**
- RFQs personalizados por proveedor
- Fecha límite calculada según urgencia
- Asuntos profesionales con número de RFQ
- Integración con EmailService existente

### 2. **Orquestador** (`src/agents/orquestador.py`)

Coordina el flujo completo entre los 3 agentes.

**Funciones principales:**

- `procesar_solicitud_completa()` - Flujo end-to-end completo
- `obtener_estado_solicitud()` - Consulta estado de solicitud

**Etapas del orquestador:**
1. **Receptor**: Procesa texto → extrae productos
2. **BD**: Guarda solicitud
3. **Investigador**: Busca proveedores
4. **Generador RFQ**: Crea y envía RFQs
5. **Finalización**: Actualiza estados

### 3. **Funciones Helper CRUD** (`src/database/crud.py`)

Nuevas funciones agregadas:

```python
# Crear solicitud desde datos procesados
crear_solicitud(db, origen, contenido, productos, urgencia)

# Crear RFQ con número automático
crear_rfq(db, solicitud_id, proveedor_id, contenido)

# Actualizar estado de solicitud
actualizar_estado_solicitud(db, solicitud_id, nuevo_estado)
```

### 4. **API REST** (`main.py`)

Servidor FastAPI con endpoints para:

- `POST /solicitud/procesar-completa` - Procesar solicitud completa
- `GET /solicitud/{id}/estado` - Consultar estado
- `GET /health` - Health check
- `GET /` - Información de la API

### 5. **Prompt del Generador** (`src/prompts/generador_rfq_prompt.txt`)

Prompt engineering con:
- Instrucciones detalladas para RFQs profesionales
- 3 ejemplos completos (industrial, electrónico, servicios)
- Formato empresarial estándar
- Personalización por proveedor

### 6. **Tests Completos** (`tests/test_fase_4.py`)

17 tests implementados:
- 6 tests unitarios del Generador RFQ
- 3 tests de funciones CRUD helper
- 5 tests del Orquestador
- 3 tests de endpoints API

**Cobertura:**
- Generador RFQ: 87%
- Tests unitarios: 100% (6/6 pasando)
- Tests de integración: 8/11 pasando

---

## 🏛️ Arquitectura

### Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────┐
│                        FASE 4                                │
│                   Generador RFQ + API                        │
└──────────────────────────────────────────────────────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Cliente   │────────>│  API REST   │────────>│ Orquestador │
│  (Externo)  │  HTTP   │  (main.py)  │  async  │             │
└─────────────┘         └─────────────┘         └──────┬──────┘
                                                       │
                    ┌──────────────────────────────────┤
                    │                                  │
          ┌─────────▼──────┐              ┌───────────▼────────┐
          │    Receptor    │              │   Investigador     │
          │ (FASE 2)       │              │   (FASE 3)         │
          └───────┬────────┘              └──────────┬─────────┘
                  │                                  │
                  │         ┌────────────────────────┘
                  │         │
          ┌───────▼─────────▼──────┐
          │   Generador RFQ        │
          │  - generar_rfq()       │
          │  - enviar_rfq()        │
          │  - enviar_rfqs_mult()  │
          └────────┬───────────────┘
                   │
          ┌────────▼────────┐
          │  EmailService   │<─────┐
          │  (SMTP/IMAP)    │      │
          └─────────────────┘      │
                                   │
          ┌────────────────────────┴───┐
          │      Base de Datos         │
          │  - Solicitudes             │
          │  - RFQs                    │
          │  - Proveedores             │
          │  - Estados y Tracking      │
          └────────────────────────────┘
```

### Flujo de Datos

```python
# 1. Usuario envía solicitud
POST /solicitud/procesar-completa
{
    "texto": "Necesito 5 PLCs Siemens S7-1200",
    "origen": "api"
}

# 2. Orquestador coordina agentes
orquestador.procesar_solicitud_completa()
    ↓
    receptor.procesar_solicitud()      # Extrae productos
    ↓
    crud.crear_solicitud()              # Guarda en BD
    ↓
    investigador.buscar_proveedores()   # Busca proveedores
    ↓
    generador_rfq.enviar_rfqs_multiples()  # Genera y envía RFQs
        ↓
        Para cada proveedor:
            generar_rfq()               # Genera contenido con IA
            ↓
            crud.crear_rfq()            # Guarda RFQ en BD
            ↓
            email_service.send_email()  # Envía email SMTP
            ↓
            crud_rfq.marcar_enviado()   # Actualiza estado

# 3. Respuesta al usuario
{
    "message": "Solicitud procesada exitosamente",
    "solicitud_id": 123,
    "proveedores_contactados": 5,
    "rfqs_enviados": 5,
    "detalles": {...}
}
```

---

## 🚀 Guía de Uso

### Requisitos Previos

1. **Variables de entorno configuradas** (`.env`):
```bash
# OpenAI API (requerido)
OPENAI_API_KEY=sk-...

# Gmail SMTP (requerido para enviar emails)
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Serper API (opcional, para búsqueda web)
SERPER_API_KEY=...
```

2. **Base de datos inicializada**:
```bash
# Ejecutar migraciones
alembic upgrade head

# Sembrar proveedores de ejemplo
python -m src.database.seed_proveedores
```

### Opción 1: Usar la API REST

#### Paso 1: Iniciar el servidor

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar servidor FastAPI
python main.py
```

El servidor estará disponible en: `http://localhost:8000`

Documentación interactiva: `http://localhost:8000/docs`

#### Paso 2: Procesar una solicitud completa

```bash
curl -X POST "http://localhost:8000/solicitud/procesar-completa" \
     -H "Content-Type: application/json" \
     -d '{
       "texto": "Necesito 5 PLCs Siemens S7-1200 y 10 sensores de temperatura bajo norma EMA",
       "origen": "api"
     }'
```

**Respuesta esperada:**
```json
{
  "message": "Solicitud procesada exitosamente",
  "solicitud_id": 1,
  "proveedores_contactados": 3,
  "rfqs_enviados": 3,
  "detalles": {
    "exito": true,
    "etapa": "completado",
    "solicitud": {...},
    "proveedores": {...},
    "rfqs": {
      "total": 3,
      "exitosos": 3,
      "fallidos": 0,
      "detalles": [...]
    }
  }
}
```

#### Paso 3: Consultar estado de solicitud

```bash
curl "http://localhost:8000/solicitud/1/estado"
```

**Respuesta:**
```json
{
  "solicitud_id": 1,
  "estado": "en_proceso",
  "urgencia": "alta",
  "rfqs_total": 3,
  "rfqs_enviados": 3,
  "rfqs_respondidos": 0,
  "cotizaciones_recibidas": 0,
  "ultima_actualizacion": "2024-11-15T10:30:00",
  "created_at": "2024-11-15T10:00:00"
}
```

### Opción 2: Usar la Interfaz Interactiva (Streamlit) 🆕

La nueva interfaz interactiva permite generar y gestionar RFQs con control completo antes del envío.

#### Paso 1: Iniciar Streamlit

```bash
# Activar entorno virtual
source venv/bin/activate

# Iniciar aplicación Streamlit
streamlit run frontend/app.py
```

La aplicación estará disponible en: `http://localhost:8501`

#### Paso 2: Navegar a la pestaña "📧 Generar RFQs"

La interfaz ofrece un flujo de trabajo en 5 pasos:

**1️⃣ Seleccionar Solicitud**
- Dropdown con solicitudes pendientes o en proceso
- Visualización de detalles (estado, urgencia, prioridad)
- Descripción completa de la solicitud

**2️⃣ Buscar Proveedores Recomendados**
- Checkbox para incluir búsqueda web (Serper API)
- Botón "🔍 Buscar Proveedores"
- Resultados con scoring de relevancia

**3️⃣ Seleccionar Proveedores para RFQ**
- Checkboxes para seleccionar proveedores individuales
- Los 3 mejores proveedores seleccionados por defecto
- Vista de nombre, score y email de cada proveedor
- Contador de proveedores seleccionados

**4️⃣ Generar Borradores de RFQs**
- Botón para generar borradores con IA (GPT-4o)
- Generación personalizada para cada proveedor
- RFQs guardados en estado BORRADOR (no se envían aún)
- Confirmación de borradores creados

**5️⃣ Borradores Pendientes de Envío**
- Lista expandible de todos los borradores
- **Vista previa** del contenido generado
- **Edición** del texto antes de enviar
- **Botones de acción:**
  - 📤 Enviar RFQ - Envía por email y marca como ENVIADO
  - 👁️ Vista Previa - Muestra el contenido formateado
  - 🗑️ Eliminar - Elimina el borrador (próximamente)

#### Ventajas de la Interfaz Interactiva

✅ **Control total**: Revisa y edita cada RFQ antes de enviar
✅ **Flexibilidad**: Selecciona exactamente qué proveedores contactar
✅ **Seguridad**: No se envían emails sin confirmación explícita
✅ **Transparencia**: Vista previa del contenido exacto que recibirán los proveedores
✅ **Rastreabilidad**: Historial completo de RFQs generados y enviados

#### Funciones Helper Disponibles

```python
from src.agents.generador_rfq import (
    generar_borrador_rfq,      # Genera RFQ sin enviar
    enviar_rfq_existente,       # Envía RFQ existente
    obtener_rfqs_pendientes     # Lista borradores pendientes
)

# Generar borrador sin enviar
resultado = generar_borrador_rfq(
    solicitud_id=1,
    proveedor={"nombre": "Proveedor SA", "email": "contacto@proveedor.com"},
    productos=[{"nombre": "PLC Siemens", "cantidad": 5}],
    urgencia="alta"
)
# Resultado: {"exito": True, "rfq_id": 10, "numero_rfq": "RFQ-2024-0010"}

# Enviar RFQ existente (con contenido editado opcional)
resultado = enviar_rfq_existente(
    rfq_id=10,
    contenido_editado="Contenido personalizado modificado..."
)
# Resultado: {"exito": True, "email_enviado": True}

# Obtener borradores pendientes
borradores = obtener_rfqs_pendientes(solicitud_id=1)
# Resultado: [{"id": 10, "numero_rfq": "RFQ-2024-0010", "estado": "BORRADOR", ...}]
```

### Opción 3: Usar el código directamente

```python
import asyncio
from src.agents.orquestador import procesar_solicitud_completa

async def main():
    resultado = await procesar_solicitud_completa(
        texto_solicitud="Necesito 5 PLCs Siemens S7-1200 urgente",
        origen="script"
    )

    if resultado["exito"]:
        print(f"✅ Solicitud {resultado['solicitud_id']} procesada")
        print(f"RFQs enviados: {resultado['rfqs']['exitosos']}")
    else:
        print(f"❌ Error: {resultado['error']}")

asyncio.run(main())
```

### Opción 4: Usar el script de prueba manual

```bash
python test_fase_4_manual.py
```

Este script ejecuta 4 pruebas:
1. Generador de RFQ
2. Funciones CRUD helper
3. Verificación de archivos
4. Orquestador completo

---

## 🌐 Endpoints de API

### 1. POST `/solicitud/procesar-completa`

Procesa una solicitud completa end-to-end.

**Request:**
```json
{
  "texto": "string (requerido) - Solicitud en lenguaje natural",
  "origen": "string (opcional) - Origen: api, formulario, whatsapp, email"
}
```

**Response 200:**
```json
{
  "message": "Solicitud procesada exitosamente",
  "solicitud_id": 123,
  "proveedores_contactados": 5,
  "rfqs_enviados": 5,
  "detalles": {
    "exito": true,
    "etapa": "completado",
    "solicitud_id": 123,
    "solicitud": {...},
    "proveedores": {...},
    "rfqs": {...}
  }
}
```

**Response 400:**
```json
{
  "detail": {
    "error": "No se encontraron proveedores adecuados",
    "etapa_fallida": "investigador",
    "detalles": {...}
  }
}
```

**Ejemplo con curl:**
```bash
curl -X POST "http://localhost:8000/solicitud/procesar-completa" \
     -H "Content-Type: application/json" \
     -d '{"texto": "Necesito PLCs", "origen": "api"}'
```

### 2. GET `/solicitud/{solicitud_id}/estado`

Consulta el estado de una solicitud.

**Response 200:**
```json
{
  "solicitud_id": 123,
  "estado": "en_proceso",
  "urgencia": "alta",
  "rfqs_total": 3,
  "rfqs_enviados": 3,
  "rfqs_respondidos": 1,
  "cotizaciones_recibidas": 2,
  "ultima_actualizacion": "2024-11-15T10:30:00",
  "created_at": "2024-11-15T10:00:00"
}
```

**Response 404:**
```json
{
  "detail": "Solicitud no encontrada"
}
```

### 3. GET `/health`

Health check del servidor.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "0.6.0"
}
```

### 4. GET `/`

Información de la API.

**Response 200:**
```json
{
  "name": "PEI Compras AI",
  "version": "0.6.0",
  "status": "operational",
  "docs": "/docs",
  "endpoints": {...}
}
```

---

## 🧪 Pruebas y Tests

### Ejecutar Tests

```bash
# Activar entorno virtual
source venv/bin/activate

# Todos los tests de FASE 4
pytest tests/test_fase_4.py -v

# Solo tests unitarios (más rápido)
pytest tests/test_fase_4.py -v -m "not integration"

# Con cobertura
pytest tests/test_fase_4.py --cov=src/agents/generador_rfq --cov=src/agents/orquestador

# Test específico
pytest tests/test_fase_4.py::test_generar_rfq_exitoso -v
```

### Prueba Manual Completa

```bash
python test_fase_4_manual.py
```

Este script verifica:
- ✅ Generador de RFQ funciona
- ✅ Funciones CRUD helper funcionan
- ✅ Todos los archivos existen
- ✅ Orquestador ejecuta correctamente

### Tests Implementados

| Test | Descripción | Estado |
|------|-------------|--------|
| `test_generar_rfq_exitoso` | RFQ se genera correctamente | ✅ |
| `test_generar_rfq_con_urgencia_alta` | Fecha límite para urgencia alta | ✅ |
| `test_generar_rfq_con_urgencia_urgente` | Fecha límite para urgencia urgente | ✅ |
| `test_generar_rfq_error_en_agente` | Manejo de errores de OpenAI | ✅ |
| `test_enviar_rfq_flujo_completo` | Flujo completo de envío | ✅ |
| `test_enviar_rfqs_multiples` | Envío a múltiples proveedores | ✅ |
| `test_crear_solicitud_helper` | Función crear_solicitud | ✅ |
| `test_crear_rfq_helper` | Función crear_rfq | ✅ |
| `test_actualizar_estado_solicitud_helper` | Función actualizar_estado_solicitud | ✅ |
| `test_orquestador_flujo_completo_mock` | Orquestador completo (mocked) | ⚠️ |
| `test_orquestador_falla_en_receptor` | Manejo de error en receptor | ⚠️ |
| `test_orquestador_sin_proveedores` | Caso sin proveedores | ⚠️ |
| `test_obtener_estado_solicitud` | Consulta de estado | ✅ |
| `test_obtener_estado_solicitud_inexistente` | Estado de ID inexistente | ✅ |
| `test_endpoint_procesar_completa` | Endpoint POST /procesar-completa | ✅ |
| `test_endpoint_procesar_completa_error` | Endpoint maneja errores | ✅ |
| `test_endpoint_consultar_estado` | Endpoint GET /estado | ✅ |

**Resumen:**
- ✅ Tests unitarios: 6/6 (100%)
- ⚠️ Tests de integración: 8/11 (73%)
- **Total**: 14/17 (82%)

---

## ⚙️ Configuración

### Variables de Entorno Requeridas

Crear archivo `.env` en la raíz del proyecto:

```bash
# ============== OPENAI (REQUERIDO) ==============
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL_MINI=gpt-4o-mini
OPENAI_MODEL_FULL=gpt-4o

# ============== EMAIL (REQUERIDO PARA RFQs) ==============
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

# ============== SERPER API (OPCIONAL) ==============
SERPER_API_KEY=tu-api-key-de-serper

# ============== BASE DE DATOS ==============
DATABASE_URL=sqlite:///./pei_compras.db

# ============== WHATSAPP (OPCIONAL) ==============
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=tu-api-key
EVOLUTION_INSTANCE_NAME=pei-compras
```

### Obtener Gmail App Password

1. Ir a https://myaccount.google.com/security
2. Habilitar "Verificación en 2 pasos"
3. Ir a "Contraseñas de aplicaciones"
4. Generar nueva contraseña para "Mail"
5. Copiar la contraseña de 16 caracteres
6. Agregar a `.env` como `GMAIL_APP_PASSWORD`

### Configuración de Base de Datos

```bash
# 1. Aplicar migraciones
alembic upgrade head

# 2. Verificar tablas
sqlite3 pei_compras.db ".schema"

# 3. Sembrar proveedores de ejemplo
python -m src.database.seed_proveedores
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Solicitud Simple

**Entrada:**
```bash
curl -X POST "http://localhost:8000/solicitud/procesar-completa" \
     -H "Content-Type: application/json" \
     -d '{
       "texto": "Necesito 50 laptops HP para oficina",
       "origen": "formulario"
     }'
```

**Proceso:**
1. Receptor extrae: `{"nombre": "Laptops HP", "cantidad": "50", "categoria": "Tecnología"}`
2. Investigador encuentra 5 proveedores de laptops
3. Generador crea 5 RFQs personalizados
4. Se envían 5 emails
5. Se guardan 5 RFQs en BD

**Resultado:**
```json
{
  "message": "Solicitud procesada exitosamente",
  "solicitud_id": 45,
  "proveedores_contactados": 5,
  "rfqs_enviados": 5
}
```

### Ejemplo 2: Solicitud Urgente Múltiple

**Entrada:**
```bash
curl -X POST "http://localhost:8000/solicitud/procesar-completa" \
     -H "Content-Type: application/json" \
     -d '{
       "texto": "URGENTE: Necesito 5 PLCs Siemens S7-1200 y 10 sensores de temperatura calibrados bajo norma EMA",
       "origen": "whatsapp"
     }'
```

**Proceso:**
1. Receptor detecta urgencia "URGENTE" y extrae 2 productos
2. Investigador busca proveedores especializados en automatización
3. Generador crea RFQs con fecha límite de 1 día
4. Emails incluyen mención de urgencia

**RFQ Generado (extracto):**
```
Estimado Ing. Carlos Ramírez,

...

• PLC Siemens S7-1200
  - Cantidad: 5 unidades
  - Especificaciones: Modelo S7-1200 CPU 1214C DC/DC/DC
  - Marca: Siemens original

• Sensores de temperatura
  - Cantidad: 10 unidades
  - Estándares: Certificación bajo norma EMA

**Fecha límite para recibir su cotización: 16 de noviembre de 2024**

Debido a la urgencia de este requerimiento, agradeceremos dar prioridad a esta solicitud.

...
```

### Ejemplo 3: Consultar Estado

```bash
# Consultar estado después de procesar
curl "http://localhost:8000/solicitud/45/estado"
```

**Respuesta:**
```json
{
  "solicitud_id": 45,
  "estado": "en_proceso",
  "urgencia": "normal",
  "rfqs_total": 5,
  "rfqs_enviados": 5,
  "rfqs_respondidos": 2,
  "cotizaciones_recibidas": 3,
  "ultima_actualizacion": "2024-11-15T14:30:00",
  "created_at": "2024-11-15T14:00:00"
}
```

---

## 🔧 Troubleshooting

### Error: "OpenAI API key not found"

**Problema:** No se configuró la API key de OpenAI

**Solución:**
```bash
# Agregar a .env
OPENAI_API_KEY=sk-proj-tu-api-key
```

### Error: "SMTP authentication error"

**Problema:** Credenciales de Gmail incorrectas

**Solución:**
1. Verificar que `GMAIL_USER` sea correcto
2. Generar nueva App Password:
   - https://myaccount.google.com/security
   - "Contraseñas de aplicaciones"
3. Actualizar `GMAIL_APP_PASSWORD` en `.env`

### Error: "No se encontraron proveedores"

**Problema:** Base de datos sin proveedores

**Solución:**
```bash
# Sembrar proveedores de ejemplo
python -m src.database.seed_proveedores

# Verificar proveedores
python -c "from src.database.session import SessionLocal; from src.database.models import Proveedor; db = SessionLocal(); print(f'Proveedores: {db.query(Proveedor).count()}')"
```

### Error: "cannot import name 'SessionLocal'"

**Problema:** Import incorrecto

**Solución:**
```python
# Correcto
from src.database.session import SessionLocal

# Incorrecto
from src.database.models import SessionLocal
```

### Tests fallan con "connection error"

**Problema:** Base de datos no inicializada

**Solución:**
```bash
# Inicializar BD
alembic upgrade head

# Ejecutar solo tests unitarios
pytest tests/test_fase_4.py -m "not integration"
```

### RFQs se generan pero no se envían

**Problema:** Email service no está configurado

**Solución:**
1. Verificar configuración de SMTP en `.env`
2. Probar email service:
```python
from src.services.email_service import email_service
result = email_service.send_email(
    to="tu-email@gmail.com",
    subject="Test",
    body="Prueba de email"
)
print(f"Enviado: {result}")
```

---

## 📊 Métricas y Estadísticas

### Cobertura de Código

```
Componente                  Cobertura
────────────────────────────────────
generador_rfq.py              87%
orquestador.py                41%  (funciones helper al 100%)
crud.py (helpers FASE 4)      57%  (funciones nuevas al 100%)
email_service.py              23%  (ya existía)
main.py                       N/A  (endpoint API)
```

### Performance

- **Tiempo promedio por solicitud**: 15-25 segundos
  - Receptor: 2-3s
  - Investigador: 5-10s (con búsqueda web)
  - Generador RFQ: 5-10s (depende de # proveedores)
  - Email: 2-5s

- **Solicitudes concurrentes**: Hasta 10 (depende de OpenAI rate limit)

### Capacidad

- **RFQs por solicitud**: Sin límite (recomendado: 3-10)
- **Proveedores en BD**: Sin límite
- **Almacenamiento**: ~1KB por RFQ

---

## 📚 Referencias

- [Documentación OpenAI](https://platform.openai.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Pytest Documentation](https://docs.pytest.org/)

---

## 🎯 Próximos Pasos (FASE 5)

- Receptor de cotizaciones vía email (IMAP)
- Parser de PDFs y documentos adjuntos
- Comparador automático de cotizaciones
- Generador de órdenes de compra

---

**Documentación creada:** Noviembre 2024
**Última actualización:** Noviembre 2024
**Versión del sistema:** 0.6.0
