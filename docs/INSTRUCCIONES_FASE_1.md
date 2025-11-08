# Instrucciones para Probar la Fase 1

**Fase**: 1 - Base de Datos y Modelos
**Estado**: ✅ COMPLETADA
**Fecha**: 2025-11-06

---

## 🚀 Pasos para Probar la Implementación

### Paso 1: Verificar que las Migraciones se Aplicaron

```bash
# Verificar estado de Alembic
alembic current

# Deberías ver:
# fef61ec919d5 (head)
```

### Paso 2: Cargar Datos de Prueba

```bash
# Ejecutar script de seed
python3 scripts/seed_data.py
```

**Resultado esperado**:
```
================================================================================
🌱 SEED DE DATOS - PEI COMPRAS AI
================================================================================
🌱 Iniciando seed de proveedores...
✅ Creado proveedor: Tech Solutions Chile
✅ Creado proveedor: Digitech Store
✅ Creado proveedor: Infotech Ltda
✅ Creado proveedor: Muebles Corporativos SA
✅ Creado proveedor: Oficina Total
✅ Creado proveedor: Suministros Empresariales Chile
✅ Creado proveedor: Papelería Nacional
✅ Creado proveedor: Servicios Integrales Empresariales
✅ Creado proveedor: Aseo Industrial Pro
✅ Creado proveedor: Equipos y Maquinaria Chile

📊 Resumen del seed:
   - Proveedores creados: 10
   - Total en base de datos: 10
✅ Seed de proveedores completado exitosamente
```

### Paso 3: Verificar Datos en la Base de Datos

```bash
# Ver tablas creadas
sqlite3 pei_compras.db ".tables"

# Deberías ver:
# alembic_version  cotizaciones  ordenes_compra  proveedores  rfqs  solicitudes
```

```bash
# Ver proveedores cargados
sqlite3 pei_compras.db "SELECT nombre, categoria, rating FROM proveedores;"
```

**Resultado esperado**:
```
Tech Solutions Chile|tecnologia|4.5
Digitech Store|tecnologia|4.2
Infotech Ltda|tecnologia|3.8
Muebles Corporativos SA|mobiliario|4.7
Oficina Total|mobiliario|4.3
...
```

### Paso 4: Ejecutar Tests

```bash
# Tests de modelos
pytest tests/unit/test_database/test_models.py -v
```

**Resultado esperado**:
```
tests/unit/test_database/test_models.py::TestSolicitudModel::test_create_solicitud PASSED
tests/unit/test_database/test_models.py::TestProveedorModel::test_create_proveedor PASSED
tests/unit/test_database/test_models.py::TestRFQModel::test_create_rfq PASSED

========== 3 passed in 0.12s ==========
```

### Paso 5: Probar CRUD Operations en Python

Crea un archivo `test_crud.py`:

```python
#!/usr/bin/env python3
"""
Script de prueba para CRUD operations.
"""
from src.database import crud
from src.database.session import SessionLocal
from src.database.models import EstadoSolicitud

def main():
    db = SessionLocal()

    print("=" * 80)
    print("🧪 PRUEBA DE CRUD OPERATIONS")
    print("=" * 80)

    # 1. Listar proveedores
    print("\n1. Proveedores en base de datos:")
    proveedores = crud.proveedor.get_multi(db, limit=5)
    for p in proveedores:
        print(f"   - {p.nombre} ({p.categoria}) - Rating: {p.rating}")

    # 2. Crear solicitud
    print("\n2. Creando solicitud de prueba...")
    solicitud = crud.solicitud.create(db, obj_in={
        "usuario_nombre": "Juan Pérez",
        "usuario_contacto": "+56912345678",
        "descripcion": "Necesito 100 laptops HP EliteBook para la oficina",
        "categoria": "tecnologia",
        "presupuesto": 150000000,
        "prioridad": 4,
    })
    print(f"   ✅ Solicitud creada con ID: {solicitud.id}")

    # 3. Buscar proveedores de tecnología
    print("\n3. Proveedores de tecnología:")
    proveedores_tech = crud.proveedor.get_by_categoria(db, "tecnologia")
    for p in proveedores_tech:
        print(f"   - {p.nombre} - {p.email}")

    # 4. Crear RFQ
    if proveedores_tech:
        print("\n4. Creando RFQ...")
        rfq = crud.rfq.create(db, obj_in={
            "solicitud_id": solicitud.id,
            "proveedor_id": proveedores_tech[0].id,
            "numero_rfq": f"RFQ-2024-{solicitud.id:03d}",
            "asunto": "Solicitud de Cotización - Laptops HP",
            "contenido": "Estimado proveedor, necesitamos cotización...",
        })
        print(f"   ✅ RFQ creado con número: {rfq.numero_rfq}")

        # 5. Marcar RFQ como enviado
        print("\n5. Marcando RFQ como enviado...")
        rfq_enviado = crud.rfq.marcar_enviado(db, rfq.id)
        print(f"   ✅ RFQ {rfq_enviado.numero_rfq} - Estado: {rfq_enviado.estado}")

    # 6. Cambiar estado de solicitud
    print("\n6. Cambiando estado de solicitud...")
    solicitud_actualizada = crud.solicitud.cambiar_estado(
        db, solicitud.id, EstadoSolicitud.EN_PROCESO
    )
    print(f"   ✅ Solicitud {solicitud_actualizada.id} - Estado: {solicitud_actualizada.estado}")

    print("\n" + "=" * 80)
    print("✅ Todas las pruebas completadas exitosamente")
    print("=" * 80)

    db.close()

if __name__ == "__main__":
    main()
```

**Ejecutar**:
```bash
chmod +x test_crud.py
python3 test_crud.py
```

**Resultado esperado**:
```
================================================================================
🧪 PRUEBA DE CRUD OPERATIONS
================================================================================

1. Proveedores en base de datos:
   - Tech Solutions Chile (tecnologia) - Rating: 4.5
   - Digitech Store (tecnologia) - Rating: 4.2
   - Infotech Ltda (tecnologia) - Rating: 3.8
   - Muebles Corporativos SA (mobiliario) - Rating: 4.7
   - Oficina Total (mobiliario) - Rating: 4.3

2. Creando solicitud de prueba...
   ✅ Solicitud creada con ID: 1

3. Proveedores de tecnología:
   - Tech Solutions Chile - ventas@techsolutions.cl
   - Digitech Store - contacto@digitech.cl
   - Infotech Ltda - ventas@infotech.cl

4. Creando RFQ...
   ✅ RFQ creado con número: RFQ-2024-001

5. Marcando RFQ como enviado...
   ✅ RFQ RFQ-2024-001 - Estado: EstadoRFQ.ENVIADO

6. Cambiando estado de solicitud...
   ✅ Solicitud 1 - Estado: EstadoSolicitud.EN_PROCESO

================================================================================
✅ Todas las pruebas completadas exitosamente
================================================================================
```

---

## 📋 Checklist de Verificación

- [ ] Las migraciones se aplicaron correctamente
- [ ] Se cargaron 10 proveedores de prueba
- [ ] Las 5 tablas existen en la base de datos
- [ ] Los tests unitarios pasan (3/3)
- [ ] Se puede crear una solicitud
- [ ] Se puede crear un RFQ
- [ ] Se pueden cambiar estados
- [ ] CRUD operations funcionan correctamente

---

## 🔧 Comandos Útiles

### Ver Estructura de Base de Datos

```bash
# Schema completo
sqlite3 pei_compras.db ".schema"

# Solo tabla solicitudes
sqlite3 pei_compras.db ".schema solicitudes"
```

### Consultas SQL Directas

```bash
# Contar proveedores por categoría
sqlite3 pei_compras.db "
SELECT categoria, COUNT(*) as total
FROM proveedores
GROUP BY categoria;
"

# Ver solicitudes y sus estados
sqlite3 pei_compras.db "
SELECT id, usuario_nombre, categoria, estado
FROM solicitudes;
"

# Ver RFQs con proveedor
sqlite3 pei_compras.db "
SELECT r.numero_rfq, r.estado, p.nombre
FROM rfqs r
JOIN proveedores p ON r.proveedor_id = p.id;
"
```

### Migraciones

```bash
# Ver historial de migraciones
alembic history

# Ver migración actual
alembic current

# Generar nueva migración (si haces cambios)
alembic revision --autogenerate -m "Descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1
```

---

## 🐛 Solución de Problemas

### Error: "No such table"

**Solución**:
```bash
# Aplicar migraciones
alembic upgrade head
```

### Error: "No module named 'src'"

**Solución**:
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /home/sinuecg/proyects/pei-compras-ai

# Y de tener el entorno virtual activado
source venv/bin/activate
```

### Quiero resetear la base de datos

```bash
# PRECAUCIÓN: Esto eliminará todos los datos

# 1. Eliminar base de datos
rm pei_compras.db

# 2. Aplicar migraciones
alembic upgrade head

# 3. Cargar datos nuevamente
python3 scripts/seed_data.py
```

---

## 📚 Documentación Adicional

- **Documentación completa**: `docs/fase_1_database.md`
- **Modelos**: Ver `src/database/models.py`
- **CRUD**: Ver `src/database/crud.py`
- **Changelog**: Ver `CHANGELOG.md` sección [0.2.0]

---

## ✅ Fase 1 Completada

Si todos los pasos anteriores funcionaron correctamente, **¡la Fase 1 está completamente funcional!**

### Próximos Pasos

**Fase 2: Servicios Externos**
- OpenAI Service
- WhatsApp Service (Evolution API)
- Email Service (SMTP/IMAP)
- Search Service (Serper API)

Para comenzar la Fase 2, consulta el roadmap en `CHANGELOG.md`.

---

**Última actualización**: 2025-11-06
**Versión**: 1.0
