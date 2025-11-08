# API Documentation

## Base URL

```
Development: http://localhost:8000
Production: https://api.pei-compras.com
```

## Versión

Todas las rutas están bajo `/api/v1/`

## Autenticación

La API usa JWT tokens para autenticación.

### Obtener Token

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Usar Token

```http
GET /api/v1/solicitudes
Authorization: Bearer eyJhbGci...
```

## Endpoints

### Solicitudes

#### Crear Solicitud

```http
POST /api/v1/solicitudes
Content-Type: application/json
Authorization: Bearer <token>

{
  "descripcion": "Necesito 100 laptops HP para la oficina",
  "categoria": "tecnologia",
  "presupuesto": 150000,
  "fecha_limite": "2025-12-31"
}
```

**Response:**
```json
{
  "id": 1,
  "usuario_id": 123,
  "descripcion": "Necesito 100 laptops HP para la oficina",
  "categoria": "tecnologia",
  "presupuesto": 150000.0,
  "fecha_limite": "2025-12-31",
  "estado": "pendiente",
  "created_at": "2025-11-06T10:00:00Z",
  "updated_at": "2025-11-06T10:00:00Z"
}
```

#### Listar Solicitudes

```http
GET /api/v1/solicitudes?skip=0&limit=10&estado=pendiente
Authorization: Bearer <token>
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "descripcion": "Necesito 100 laptops HP...",
      "estado": "pendiente",
      ...
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 10
}
```

#### Obtener Solicitud

```http
GET /api/v1/solicitudes/{solicitud_id}
Authorization: Bearer <token>
```

#### Actualizar Solicitud

```http
PUT /api/v1/solicitudes/{solicitud_id}
Content-Type: application/json
Authorization: Bearer <token>

{
  "estado": "en_proceso"
}
```

#### Eliminar Solicitud

```http
DELETE /api/v1/solicitudes/{solicitud_id}
Authorization: Bearer <token>
```

### Proveedores

#### Crear Proveedor

```http
POST /api/v1/proveedores
Content-Type: application/json
Authorization: Bearer <token>

{
  "nombre": "Tech Solutions S.A.",
  "email": "ventas@techsolutions.com",
  "telefono": "+56912345678",
  "categoria": "tecnologia",
  "ubicacion": "Santiago, Chile"
}
```

#### Listar Proveedores

```http
GET /api/v1/proveedores?categoria=tecnologia
Authorization: Bearer <token>
```

#### Buscar Proveedores

```http
POST /api/v1/proveedores/buscar
Content-Type: application/json
Authorization: Bearer <token>

{
  "categoria": "tecnologia",
  "ubicacion": "Santiago",
  "palabras_clave": ["laptops", "HP"]
}
```

**Response:**
```json
{
  "proveedores": [
    {
      "id": 1,
      "nombre": "Tech Solutions S.A.",
      "email": "ventas@techsolutions.com",
      "categoria": "tecnologia",
      "rating": 4.5
    }
  ]
}
```

### RFQs (Request for Quotation)

#### Crear RFQ

```http
POST /api/v1/rfqs
Content-Type: application/json
Authorization: Bearer <token>

{
  "solicitud_id": 1,
  "proveedor_id": 5,
  "contenido": "Estimado proveedor..."
}
```

#### Enviar RFQ

```http
POST /api/v1/rfqs/{rfq_id}/enviar
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "mensaje": "RFQ enviado exitosamente",
  "fecha_envio": "2025-11-06T10:30:00Z"
}
```

#### Listar RFQs

```http
GET /api/v1/rfqs?solicitud_id=1&estado=enviado
Authorization: Bearer <token>
```

### Cotizaciones

#### Registrar Cotización

```http
POST /api/v1/cotizaciones
Content-Type: multipart/form-data
Authorization: Bearer <token>

rfq_id: 10
precio: 145000
tiempo_entrega: 15
condiciones: "Pago al contado"
archivo: <file>
```

#### Listar Cotizaciones

```http
GET /api/v1/cotizaciones?solicitud_id=1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "cotizaciones": [
    {
      "id": 1,
      "rfq_id": 10,
      "proveedor": {
        "nombre": "Tech Solutions S.A.",
        "email": "ventas@techsolutions.com"
      },
      "precio": 145000,
      "tiempo_entrega": 15,
      "condiciones": "Pago al contado",
      "archivo_adjunto": "https://..."
    }
  ]
}
```

#### Comparar Cotizaciones

```http
POST /api/v1/cotizaciones/comparar
Content-Type: application/json
Authorization: Bearer <token>

{
  "solicitud_id": 1,
  "criterios": {
    "peso_precio": 0.5,
    "peso_tiempo": 0.3,
    "peso_calidad": 0.2
  }
}
```

**Response:**
```json
{
  "analisis": {
    "mejor_opcion": {
      "cotizacion_id": 1,
      "proveedor": "Tech Solutions S.A.",
      "score": 0.85,
      "razon": "Mejor balance precio-tiempo"
    },
    "comparativa": [...]
  }
}
```

### Webhooks

#### Webhook WhatsApp

```http
POST /api/v1/webhooks/whatsapp
Content-Type: application/json

{
  "instance": "pei-compras",
  "event": "messages.upsert",
  "data": {
    "key": {
      "remoteJid": "56912345678@s.whatsapp.net"
    },
    "message": {
      "conversation": "Necesito cotización para laptops"
    }
  }
}
```

#### Webhook Email

```http
POST /api/v1/webhooks/email
Content-Type: application/json

{
  "from": "ventas@proveedor.com",
  "subject": "Re: RFQ #123",
  "body": "Estimado...",
  "attachments": [...]
}
```

## Códigos de Estado

| Código | Descripción |
|--------|-------------|
| 200 | OK - Petición exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - No autenticado |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación falló |
| 500 | Internal Server Error - Error del servidor |

## Rate Limiting

- 100 requests por minuto por IP
- 1000 requests por hora por usuario autenticado

**Headers de respuesta:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1636012800
```

## Paginación

Endpoints que retornan listas soportan paginación:

```http
GET /api/v1/solicitudes?skip=0&limit=20
```

**Parámetros:**
- `skip`: Número de items a saltar (default: 0)
- `limit`: Máximo de items a retornar (default: 10, max: 100)

## Filtrado

Muchos endpoints soportan filtros:

```http
GET /api/v1/solicitudes?estado=pendiente&categoria=tecnologia&fecha_desde=2025-01-01
```

## Ordenamiento

```http
GET /api/v1/solicitudes?sort_by=created_at&order=desc
```

## Validación

La API usa Pydantic para validación. Errores de validación retornan:

```json
{
  "detail": [
    {
      "loc": ["body", "presupuesto"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

## Documentación Interactiva

### Swagger UI
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI Schema
```
http://localhost:8000/openapi.json
```

## Ejemplos de Uso

### Python

```python
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "eyJhbGci..."

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Crear solicitud
solicitud = {
    "descripcion": "Necesito 50 sillas de oficina",
    "categoria": "mobiliario",
    "presupuesto": 25000,
    "fecha_limite": "2025-12-31"
}

response = requests.post(
    f"{API_URL}/solicitudes",
    headers=headers,
    json=solicitud
)

print(response.json())
```

### JavaScript

```javascript
const API_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'eyJhbGci...';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Obtener solicitudes
fetch(`${API_URL}/solicitudes`, { headers })
  .then(response => response.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"pass123"}'

# Crear solicitud
curl -X POST http://localhost:8000/api/v1/solicitudes \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Necesito laptops",
    "categoria": "tecnologia",
    "presupuesto": 100000
  }'
```

## WebSockets (Futuro)

### Estado en Tiempo Real

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/solicitud/123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Estado actualizado:', data.estado);
};
```

## Errores Comunes

### 401 Unauthorized

**Causa**: Token inválido o expirado

**Solución**: Obtener nuevo token con `/auth/login`

### 422 Unprocessable Entity

**Causa**: Datos de entrada inválidos

**Solución**: Revisar formato y tipos de datos según schemas

### 429 Too Many Requests

**Causa**: Rate limit excedido

**Solución**: Esperar o implementar backoff exponencial

## Versionado

La API usa versionado semántico en la URL:

- `/api/v1/` - Versión actual estable
- `/api/v2/` - Próxima versión (cuando esté disponible)

Cambios breaking requieren nueva versión major.

## Changelog API

### v1.0.0 (2025-11-06)
- Release inicial
- Endpoints básicos CRUD
- Autenticación JWT
- Webhooks WhatsApp y Email

---

**Última actualización**: 2025-11-06
**Versión API**: 1.0.0
