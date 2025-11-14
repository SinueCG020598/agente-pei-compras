# INSTRUCCIONES DE PRUEBA - FASE 2
# Agente Receptor + Formulario Web

**Versión**: 0.4.0
**Fecha**: 2025-11-11
**Fase**: 2 - Agente Receptor + Formulario Web

---

## 📋 TABLA DE CONTENIDOS

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración Inicial](#configuración-inicial)
3. [Paso 1: Verificar Instalación](#paso-1-verificar-instalación)
4. [Paso 2: Ejecutar Tests del Agente Receptor](#paso-2-ejecutar-tests-del-agente-receptor)
5. [Paso 3: Probar el Agente desde Python](#paso-3-probar-el-agente-desde-python)
6. [Paso 4: Ejecutar Aplicación Streamlit](#paso-4-ejecutar-aplicación-streamlit)
7. [Paso 5: Pruebas Funcionales en la UI](#paso-5-pruebas-funcionales-en-la-ui)
8. [Paso 6: Verificar Integración con Base de Datos](#paso-6-verificar-integración-con-base-de-datos)
9. [Solución de Problemas](#solución-de-problemas)
10. [Checklist de Verificación](#checklist-de-verificación)

---

## REQUISITOS PREVIOS

Antes de comenzar, asegúrate de tener:

- ✅ FASE 1 completada (Base de Datos + Modelos)
- ✅ Python 3.12+ instalado
- ✅ Entorno virtual activado
- ✅ Dependencias instaladas
- ✅ OpenAI API Key configurada en `.env`
- ✅ Base de datos `pei_compras.db` existente

---

## CONFIGURACIÓN INICIAL

### 1. Navegar al directorio del proyecto

```bash
cd /home/sinuecg/proyects/pei-compras-ai
```

### 2. Activar entorno virtual

```bash
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu prompt:
```
(venv) user@host:~/proyects/pei-compras-ai$
```

### 3. Verificar variables de entorno

```bash
# Verificar que existe el archivo .env
ls -la .env

# Verificar que tiene la API key de OpenAI
grep OPENAI_API_KEY .env
```

**Resultado esperado**:
```
OPENAI_API_KEY=sk-proj-...
```

Si no tienes API key, agrégala al archivo `.env`:
```bash
echo "OPENAI_API_KEY=sk-proj-TU_API_KEY_AQUI" >> .env
```

---

## PASO 1: VERIFICAR INSTALACIÓN

### 1.1. Verificar archivos creados

```bash
# Verificar archivos de FASE 2
ls -lh src/prompts/receptor_prompt.txt
ls -lh src/agents/receptor.py
ls -lh frontend/app.py
ls -lh tests/test_agente_receptor.py
```

**Resultado esperado**:
```
-rw-r--r-- 1 user user  10K receptor_prompt.txt
-rw-r--r-- 1 user user  18K receptor.py
-rw-r--r-- 1 user user  25K app.py
-rw-r--r-- 1 user user  16K test_agente_receptor.py
```

### 1.2. Verificar estructura del proyecto

```bash
tree -L 2 src/
```

**Resultado esperado**:
```
src/
├── agents/
│   ├── __init__.py
│   └── receptor.py          ← NUEVO
├── prompts/
│   ├── __init__.py
│   └── receptor_prompt.txt  ← NUEVO
├── database/
│   ├── models.py
│   ├── crud.py
│   └── ...
└── services/
    ├── openai_service.py
    └── ...
```

---

## PASO 2: EJECUTAR TESTS DEL AGENTE RECEPTOR

### 2.1. Ejecutar todos los tests

```bash
pytest tests/test_agente_receptor.py -v
```

**Resultado esperado**:
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.4.2, pluggy-1.6.0
...
tests/test_agente_receptor.py::test_validar_solicitud_valida PASSED      [  5%]
tests/test_agente_receptor.py::test_validar_solicitud_sin_productos PASSED [ 10%]
...
tests/test_agente_receptor.py::test_procesar_solicitud_simple_mock PASSED [ 60%]
...
==================== 18 passed, 2 skipped in 1.06s ====================
```

✅ **Éxito**: 18 tests pasando, 2 skipped (tests de integración)

### 2.2. Ejecutar tests con cobertura

```bash
pytest tests/test_agente_receptor.py -v --cov=src/agents/receptor --cov-report=term-missing
```

**Resultado esperado**:
```
----------- coverage: platform linux, python 3.12.3-final-0 -----------
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/agents/receptor.py      108     17    84%   129-130, 139, ...
-------------------------------------------------------
TOTAL                       108     17    84%
```

✅ **Éxito**: Cobertura ≥ 80%

### 2.3. Ejecutar solo tests de validación

```bash
pytest tests/test_agente_receptor.py -v -k "validar"
```

**Resultado esperado**:
```
test_validar_solicitud_valida PASSED
test_validar_solicitud_sin_productos PASSED
test_validar_solicitud_sin_nombre_producto PASSED
test_validar_solicitud_cantidad_invalida PASSED
test_validar_solicitud_urgencia_invalida PASSED
test_validar_solicitud_presupuesto_negativo PASSED
==================== 6 passed in 0.15s ====================
```

---

## PASO 3: PROBAR EL AGENTE DESDE PYTHON

### 3.1. Crear script de prueba

Crea un archivo `test_agente_manual.py`:

```bash
cat > test_agente_manual.py << 'EOF'
"""
Script de prueba manual del Agente Receptor.
"""
from src.agents.receptor import procesar_solicitud, validar_solicitud

def test_solicitud_simple():
    """Test con solicitud simple."""
    print("\n=== TEST 1: SOLICITUD SIMPLE ===")
    texto = "Necesito 5 laptops HP para el equipo de ventas"
    print(f"Input: {texto}\n")

    resultado = procesar_solicitud(texto, origen="formulario")

    print("Output:")
    print(f"  Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"    {i}. {p['nombre']} (x{p['cantidad']}) - {p['categoria']}")
    print(f"  Urgencia: {resultado['urgencia']}")
    print(f"  Presupuesto: {resultado['presupuesto_estimado']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    print(f"\n  Validación: {'✅ VÁLIDA' if es_valida else f'❌ ERROR: {error}'}")

    return resultado


def test_solicitud_compleja():
    """Test con solicitud compleja."""
    print("\n=== TEST 2: SOLICITUD COMPLEJA ===")
    texto = """
    Hola! Necesitamos urgente 10 escritorios ejecutivos y 10 sillas ergonómicas
    para la nueva oficina. También 2 impresoras láser multifunción.
    Tenemos un presupuesto de 8 millones. Es para este viernes!
    """
    print(f"Input: {texto.strip()}\n")

    resultado = procesar_solicitud(texto, origen="formulario")

    print("Output:")
    print(f"  Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"    {i}. {p['nombre']} (x{p['cantidad']}) - {p['categoria']}")
        print(f"       Specs: {p['especificaciones']}")
    print(f"  Urgencia: {resultado['urgencia']}")
    print(f"  Presupuesto: ${resultado['presupuesto_estimado']:,.0f}" if resultado['presupuesto_estimado'] else "  Presupuesto: No especificado")
    print(f"  Notas: {resultado['notas_adicionales']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    print(f"\n  Validación: {'✅ VÁLIDA' if es_valida else f'❌ ERROR: {error}'}")

    return resultado


def test_solicitud_informal():
    """Test con solicitud informal."""
    print("\n=== TEST 3: SOLICITUD INFORMAL ===")
    texto = "oye necesito unas sillas pa la sala de reuniones, como 6 o 7, nada muy caro, pa la prox semana porfa"
    print(f"Input: {texto}\n")

    resultado = procesar_solicitud(texto, origen="whatsapp")

    print("Output:")
    print(f"  Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"    {i}. {p['nombre']} (x{p['cantidad']}) - {p['categoria']}")
    print(f"  Urgencia: {resultado['urgencia']}")
    print(f"  Notas: {resultado['notas_adicionales']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    print(f"\n  Validación: {'✅ VÁLIDA' if es_valida else f'❌ ERROR: {error}'}")

    return resultado


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PRUEBAS MANUALES DEL AGENTE RECEPTOR")
    print("="*60)

    try:
        # Test 1
        r1 = test_solicitud_simple()

        # Test 2
        r2 = test_solicitud_compleja()

        # Test 3
        r3 = test_solicitud_informal()

        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
EOF
```

### 3.2. Ejecutar script de prueba

```bash
python test_agente_manual.py
```

**Resultado esperado**:
```
============================================================
PRUEBAS MANUALES DEL AGENTE RECEPTOR
============================================================

=== TEST 1: SOLICITUD SIMPLE ===
Input: Necesito 5 laptops HP para el equipo de ventas

Output:
  Productos: 1
    1. Laptop HP para equipo de ventas (x5) - tecnologia
  Urgencia: normal
  Presupuesto: None

  Validación: ✅ VÁLIDA

=== TEST 2: SOLICITUD COMPLEJA ===
Input: Hola! Necesitamos urgente 10 escritorios...

Output:
  Productos: 3
    1. Escritorio ejecutivo (x10) - mobiliario
       Specs: Tipo: Ejecutivo, para nueva oficina
    2. Silla ergonómica (x10) - mobiliario
       Specs: Tipo: Ergonómica, para nueva oficina
    3. Impresora láser multifunción (x2) - tecnologia
       Specs: Tipo: Láser multifunción
  Urgencia: urgente
  Presupuesto: $8,000,000
  Notas: Requerido para este viernes, nueva oficina

  Validación: ✅ VÁLIDA

=== TEST 3: SOLICITUD INFORMAL ===
Input: oye necesito unas sillas pa la sala de reuniones...

Output:
  Productos: 1
    1. Silla para sala de reuniones (x7) - mobiliario
  Urgencia: alta
  Notas: Solicitud informal, presupuesto ajustado...

  Validación: ✅ VÁLIDA

============================================================
✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE
============================================================
```

✅ **Éxito**: El agente procesa correctamente los 3 tipos de solicitudes

---

## PASO 4: EJECUTAR APLICACIÓN STREAMLIT

### 4.1. Iniciar aplicación

```bash
streamlit run frontend/app.py
```

**Resultado esperado**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### 4.2. Verificar que carga correctamente

Deberías ver:

- ✅ Header: "🛒 PEI Compras AI"
- ✅ Subheader: "Sistema Inteligente de Compras"
- ✅ Sidebar con métricas
- ✅ 3 tabs: "📝 Nueva Solicitud", "📚 Mis Solicitudes", "📊 Estadísticas"

### 4.3. Si hay errores al iniciar

```bash
# Ver logs detallados
streamlit run frontend/app.py --logger.level=debug

# O ejecutar con Python directamente para ver traceback
python -c "import sys; sys.path.insert(0, '.'); exec(open('frontend/app.py').read())"
```

---

## PASO 5: PRUEBAS FUNCIONALES EN LA UI

### 5.1. Prueba 1: Solicitud Simple

**Pasos**:

1. Abre la aplicación en `http://localhost:8501`
2. Ve al tab "📝 Nueva Solicitud"
3. En el text area, escribe:
   ```
   Necesito 5 laptops HP para el equipo de ventas
   ```
4. Deja "Urgencia" en "Auto-detectar"
5. Deja "Presupuesto" en 0
6. Click en "🚀 Procesar Solicitud"

**Resultado esperado**:

- ✅ Spinner "🤖 Procesando solicitud con IA..."
- ✅ Mensaje verde: "✅ Solicitud procesada y guardada exitosamente (ID: X)"
- ✅ Sección "📋 Información Extraída" aparece
- ✅ Badge de urgencia: 🟢 NORMAL
- ✅ Card del producto:
  ```
  🔹 Laptop HP para equipo de ventas
  Cantidad: 5 unidades
  Categoría: Tecnologia
  Especificaciones: Marca: HP, para uso de equipo de ventas
  ```

**Captura de pantalla recomendada**: `screenshots/fase2_test1_simple.png`

### 5.2. Prueba 2: Solicitud Compleja

**Pasos**:

1. En el mismo tab "📝 Nueva Solicitud"
2. Refresca el formulario (F5 o recarga la página)
3. En el text area, escribe:
   ```
   Necesitamos urgente 10 escritorios ejecutivos y 10 sillas ergonómicas
   para la nueva oficina. También 2 impresoras láser multifunción.
   Tenemos un presupuesto de 8 millones. Es para este viernes!
   ```
4. Urgencia: "Auto-detectar"
5. Presupuesto: 0 (se detectará automáticamente)
6. Click en "🚀 Procesar Solicitud"

**Resultado esperado**:

- ✅ Badge de urgencia: 🔴 URGENTE
- ✅ Presupuesto: 💰 $8,000,000 CLP
- ✅ 3 productos en cards:
  1. Escritorio ejecutivo (x10) - Mobiliario
  2. Silla ergonómica (x10) - Mobiliario
  3. Impresora láser multifunción (x2) - Tecnologia
- ✅ Notas adicionales: "Requerido para este viernes, nueva oficina"

### 5.3. Prueba 3: Solicitud Informal

**Pasos**:

1. Refresca el formulario
2. En el text area, escribe:
   ```
   oye necesito unas sillas pa la sala de reuniones, como 6 o 7,
   nada muy caro, pa la prox semana porfa
   ```
3. Click en "🚀 Procesar Solicitud"

**Resultado esperado**:

- ✅ Badge de urgencia: 🟡 ALTA
- ✅ 1 producto:
  - Silla para sala de reuniones (x7) - Mobiliario
  - Especificaciones: "Para sala de reuniones, rango económico"
- ✅ Notas: "Solicitud informal, presupuesto ajustado..."

### 5.4. Prueba 4: Urgencia Manual

**Pasos**:

1. Escribe: `Necesito 3 proyectores para las salas de reunión`
2. Urgencia: Selecciona "Urgente" manualmente
3. Presupuesto: Ingresa `2500000`
4. Click en "🚀 Procesar Solicitud"

**Resultado esperado**:

- ✅ Badge: 🔴 URGENTE (forzado manualmente)
- ✅ Presupuesto: 💰 $2,500,000 CLP (especificado manualmente)

### 5.5. Prueba 5: Ver Historial

**Pasos**:

1. Ve al tab "📚 Mis Solicitudes"
2. En "Estado", selecciona "Todos"
3. En "Mostrar", selecciona "10"

**Resultado esperado**:

- ✅ Lista de solicitudes creadas (las 4 pruebas anteriores)
- ✅ Cada solicitud en un expander: "📄 Solicitud #X - Categoria - Estado"
- ✅ Al expandir, se ve:
  - Usuario, Categoría, Estado
  - Fecha, Presupuesto, Fecha Límite
  - Descripción completa
  - Notas internas

**Probar filtros**:

```
Estado: Pendiente → Solo solicitudes pendientes
Mostrar: 25 → Hasta 25 solicitudes
```

### 5.6. Prueba 6: Estadísticas

**Pasos**:

1. Ve al tab "📊 Estadísticas"

**Resultado esperado**:

- ✅ 4 métricas principales:
  - 📝 Total Solicitudes: ≥ 4
  - ⏳ Pendientes: ≥ 4
  - 🔄 En Proceso: 0
  - ✅ Completadas: 0
- ✅ Actividad Reciente (30 días): ≥ 4
- ✅ Información del Sistema:
  - Versión: 0.4.0
  - Modelo IA (Mini): gpt-4o-mini
  - Modelo IA (Full): gpt-4o
  - Base de Datos: SQLite

### 5.7. Prueba 7: Sidebar

**Verificar sidebar** (en cualquier tab):

**Resultado esperado**:

- ✅ Header: "🛒 PEI Compras AI"
- ✅ Subheader: "Sistema Inteligente de Compras"
- ✅ Sección "📊 Estadísticas" con métricas en 2x2:
  - Total, Pendientes
  - En Proceso, Completadas
  - Últimos 30 días
- ✅ Sección "⚙️ Configuración":
  - Input "Tu nombre" (editable)
  - Input "Tu email" (editable)
- ✅ Sección "ℹ️ Sistema":
  - Versión y Modelo IA

**Probar editar configuración**:

1. Cambia "Tu nombre" a "Juan Pérez"
2. Cambia "Tu email" a "juan@empresa.cl"
3. Crea una nueva solicitud
4. Verifica que el usuario guardado sea "Juan Pérez"

---

## PASO 6: VERIFICAR INTEGRACIÓN CON BASE DE DATOS

### 6.1. Ver solicitudes en SQLite

```bash
sqlite3 pei_compras.db
```

Ejecuta estas consultas SQL:

```sql
-- Ver total de solicitudes
SELECT COUNT(*) as total FROM solicitudes;

-- Ver últimas 5 solicitudes
SELECT
    id,
    usuario_nombre,
    categoria,
    estado,
    created_at
FROM solicitudes
ORDER BY created_at DESC
LIMIT 5;

-- Ver detalles de la última solicitud
SELECT
    id,
    usuario_nombre,
    usuario_contacto,
    descripcion,
    categoria,
    presupuesto,
    estado,
    notas_internas
FROM solicitudes
ORDER BY created_at DESC
LIMIT 1;

-- Salir de SQLite
.quit
```

**Resultado esperado**:

```
sqlite> SELECT COUNT(*) as total FROM solicitudes;
4

sqlite> SELECT id, usuario_nombre, categoria, estado FROM solicitudes LIMIT 5;
1|Usuario Web|tecnologia|pendiente
2|Usuario Web|mobiliario|pendiente
3|Usuario Web|mobiliario|pendiente
4|Usuario Web|tecnologia|pendiente
```

### 6.2. Verificar estructura de datos guardados

```bash
# Ver una solicitud completa en formato JSON
sqlite3 pei_compras.db << 'EOF'
.mode json
SELECT * FROM solicitudes ORDER BY created_at DESC LIMIT 1;
EOF
```

**Resultado esperado**:

```json
[
  {
    "id": 4,
    "usuario_id": null,
    "usuario_nombre": "Juan Pérez",
    "usuario_contacto": "juan@empresa.cl",
    "descripcion": "- Proyector (Cantidad: 3, Categoría: tecnologia)",
    "categoria": "tecnologia",
    "presupuesto": 2500000.0,
    "estado": "pendiente",
    "notas_internas": "Origen: Formulario Web\nUrgencia: urgente\nNotas: ...",
    "created_at": "2025-11-11 20:00:00"
  }
]
```

### 6.3. Verificar que NO se guardaron duplicados

```bash
sqlite3 pei_compras.db << 'EOF'
SELECT
    categoria,
    COUNT(*) as cantidad
FROM solicitudes
GROUP BY categoria
ORDER BY cantidad DESC;
EOF
```

**Resultado esperado**:

```
mobiliario|2
tecnologia|2
```

---

## SOLUCIÓN DE PROBLEMAS

### Problema 1: "ModuleNotFoundError: No module named 'src'"

**Solución**:
```bash
# Asegúrate de ejecutar desde el directorio raíz
cd /home/sinuecg/proyects/pei-compras-ai

# Verifica que estás en el lugar correcto
pwd  # Debería mostrar: /home/sinuecg/proyects/pei-compras-ai

# Ejecuta de nuevo
python test_agente_manual.py
```

### Problema 2: "OpenAI API key not found"

**Solución**:
```bash
# Verifica el archivo .env
cat .env | grep OPENAI_API_KEY

# Si no existe, agrégalo
echo "OPENAI_API_KEY=sk-proj-TU_API_KEY_AQUI" >> .env

# Recarga las variables de entorno
source venv/bin/activate
```

### Problema 3: Tests fallan con "Mock object not subscriptable"

**Solución**:
```bash
# Asegúrate de tener la última versión de los tests
git status tests/test_agente_receptor.py

# Si es necesario, actualiza pytest-mock
pip install --upgrade pytest-mock
```

### Problema 4: Streamlit no encuentra módulos

**Solución**:
```bash
# Agrega el directorio actual al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ejecuta Streamlit
streamlit run frontend/app.py
```

### Problema 5: "FileNotFoundError: receptor_prompt.txt"

**Solución**:
```bash
# Verifica que el archivo existe
ls -la src/prompts/receptor_prompt.txt

# Si no existe, vuelve a crearlo desde el repositorio
# o verifica que estás ejecutando desde el directorio correcto
pwd
```

### Problema 6: Streamlit muestra error "Address already in use"

**Solución**:
```bash
# El puerto 8501 está ocupado, usa otro puerto
streamlit run frontend/app.py --server.port 8502

# O mata el proceso anterior
lsof -ti:8501 | xargs kill -9
```

### Problema 7: "OpenAI rate limit exceeded"

**Solución**:
```bash
# Espera 1 minuto y vuelve a intentar
# O usa tests con mocks en lugar de API real:
pytest tests/test_agente_receptor.py -v -k "mock"
```

### Problema 8: Base de datos no tiene solicitudes

**Solución**:
```bash
# Verifica que la migración está aplicada
alembic current

# Debería mostrar: a32997d10b1e (head)

# Si no, aplica las migraciones
source venv/bin/activate
alembic upgrade head
```

---

## CHECKLIST DE VERIFICACIÓN

### ✅ Tests

- [ ] 18/18 tests del agente receptor pasando
- [ ] Cobertura ≥ 80%
- [ ] Tests de validación funcionando
- [ ] Tests de mocks funcionando
- [ ] Tests de errores funcionando

### ✅ Agente Receptor (Python)

- [ ] Script de prueba ejecuta sin errores
- [ ] Test 1 (solicitud simple) funciona
- [ ] Test 2 (solicitud compleja) funciona
- [ ] Test 3 (solicitud informal) funciona
- [ ] Validación detecta errores correctamente

### ✅ Aplicación Streamlit

- [ ] Aplicación inicia en http://localhost:8501
- [ ] Sidebar muestra métricas correctamente
- [ ] Tab "Nueva Solicitud" funciona
- [ ] Tab "Mis Solicitudes" muestra historial
- [ ] Tab "Estadísticas" muestra métricas
- [ ] Procesamiento con IA funciona
- [ ] Cards de productos se muestran correctamente
- [ ] Badges de urgencia tienen colores correctos
- [ ] Filtros en historial funcionan
- [ ] Configuración de usuario se guarda

### ✅ Base de Datos

- [ ] Solicitudes se guardan correctamente
- [ ] No hay duplicados
- [ ] Campos se mapean correctamente
- [ ] Estados son correctos (pendiente)
- [ ] Notas internas contienen origen y urgencia

### ✅ Integración FASE 1 + FASE 2

- [ ] CRUD de solicitud funciona
- [ ] Migraciones aplicadas correctamente
- [ ] Tabla envios_tracking existe
- [ ] Modelos cargan sin errores
- [ ] No hay conflictos de importación

---

## COMANDOS RÁPIDOS DE VERIFICACIÓN

### Verificación Rápida (5 minutos)

```bash
# 1. Tests
pytest tests/test_agente_receptor.py -v

# 2. Script manual
python test_agente_manual.py

# 3. Streamlit (en otra terminal)
streamlit run frontend/app.py

# 4. Base de datos
sqlite3 pei_compras.db "SELECT COUNT(*) FROM solicitudes;"
```

### Verificación Completa (15 minutos)

```bash
# 1. Tests con cobertura
pytest tests/test_agente_receptor.py -v --cov=src/agents/receptor

# 2. Script manual
python test_agente_manual.py

# 3. Streamlit con logs
streamlit run frontend/app.py --logger.level=debug

# 4. Verificar todas las tablas
sqlite3 pei_compras.db << 'EOF'
.tables
SELECT COUNT(*) FROM solicitudes;
SELECT COUNT(*) FROM proveedores;
SELECT COUNT(*) FROM envios_tracking;
.quit
EOF
```

---

## MÉTRICAS DE ÉXITO

Para considerar la FASE 2 como exitosamente probada:

| Métrica | Objetivo | Estado |
|---------|----------|--------|
| Tests pasando | 18/18 | [ ] |
| Cobertura | ≥ 80% | [ ] |
| Script manual | 3/3 tests OK | [ ] |
| Streamlit inicia | Sin errores | [ ] |
| Procesamiento IA | Funciona | [ ] |
| Guardado BD | Correcto | [ ] |
| Historial | Muestra datos | [ ] |
| Estadísticas | Correctas | [ ] |

---

## SIGUIENTE PASO

Una vez que todas las pruebas pasen:

✅ **FASE 2 COMPLETADA Y VERIFICADA**

🚀 **Continuar con FASE 3**: Búsqueda Web de Proveedores

---

## SOPORTE

Si encuentras problemas:

1. **Revisa los logs**:
   ```bash
   # Logs de Streamlit
   tail -f ~/.streamlit/logs/streamlit.log

   # Logs del agente (en consola)
   python test_agente_manual.py
   ```

2. **Verifica configuración**:
   ```bash
   # Variables de entorno
   cat .env

   # Versiones de paquetes
   pip list | grep -E "streamlit|openai|pydantic"
   ```

3. **Limpia y reinicia**:
   ```bash
   # Limpia cache de pytest
   rm -rf .pytest_cache __pycache__

   # Limpia cache de Streamlit
   streamlit cache clear

   # Reinstala dependencias
   pip install -r requirements.txt --upgrade
   ```

---

**Elaborado por**: Claude Code
**Fecha**: 2025-11-11
**Versión**: 1.0
