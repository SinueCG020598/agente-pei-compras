# CÓMO PROBAR FASE 3 - Guía Rápida ⚡

**Versión**: 0.5.0  
**Última actualización**: 2025-11-13

---

## 🎯 ¿Qué se implementó en FASE 3?

✅ **SearchService**: Búsqueda web usando Serper API (Google Search)  
✅ **Agente Investigador**: Búsqueda multi-fuente (BD + Web + Ecommerce)  
✅ **Comparador de Precios**: Análisis de precios y recomendaciones  
✅ **12 Tests**: Suite completa de tests unitarios e integración  
✅ **Script Manual**: Prueba interactiva de las 3 funcionalidades

---

## ⚡ PRUEBA RÁPIDA (5 minutos)

### 1️⃣ Configurar API Key de Serper

```bash
# Obtén tu API key gratis en: https://serper.dev
# 2500 búsquedas gratis al mes

# Agrega a tu archivo .env
echo "SERPER_API_KEY=tu-api-key-aqui" >> .env
```

**⚠️ IMPORTANTE**: Sin SERPER_API_KEY, solo funcionará la búsqueda en BD local.

### 2️⃣ Verificar Instalación

```bash
cd /home/sinuecg/proyects/pei-compras-ai
source venv/bin/activate

# Verificar que los archivos existen
ls src/services/search_service.py
ls src/agents/investigador.py
ls src/agents/comparador_precios.py
ls src/prompts/investigador_prompt.txt
```

### 3️⃣ Ejecutar Tests Unitarios

```bash
pytest tests/test_fase_3.py -v
```

**✅ Resultado esperado**: 
```
test_extraer_precio_formato_pesos PASSED
test_get_marketplace_name PASSED
test_search_service_no_api_key PASSED
test_comparar_precios_exitoso PASSED
...
========== 12 passed in 2.5s ==========
```

### 4️⃣ Ejecutar Script Manual

```bash
python test_fase_3_manual.py
```

**✅ Resultado esperado**:
```
================================================================================
                    PRUEBA MANUAL - FASE 3
               SearchService + Investigador + Comparador
================================================================================

TEST 1: SearchService - Búsqueda de Proveedores Web
✅ SearchService disponible
🔍 Buscando proveedores de 'Mouse inalámbrico'...
📋 Encontrados 3 proveedores:
  1. Amazon México - Mouse Logitech
  ...
✅ Test 1: EXITOSO

TEST 2: Agente Investigador - Búsqueda Multi-fuente
🤖 Ejecutando Agente Investigador...
📊 RESUMEN DE BÚSQUEDA:
   • Proveedores en BD: 0
   • Proveedores Web: 5
   • Enlaces Ecommerce: 15
   • Búsqueda Web: ✅ Activa
✅ Test 2: EXITOSO

TEST 3: Comparador de Precios
💰 RECOMENDACIÓN PRINCIPAL:
   • Acción: COMPRAR_DIRECTO
   • Fuente: ecommerce
   • Ahorro estimado: $500.00
✅ Test 3: EXITOSO

Total: 3/3 tests exitosos
🎉 ¡Todos los tests pasaron! FASE 3 funcionando correctamente.
```

---

## 📋 PRUEBAS DETALLADAS (15 minutos)

### Test 1: SearchService - Búsqueda Web de Proveedores

**Objetivo**: Verificar que SearchService puede buscar proveedores en Google

```bash
# Prueba desde Python interactivo
python3 << 'PYEOF'
from src.services.search_service import search_service

# Verificar disponibilidad
if search_service.is_available():
    print("✅ SearchService disponible")
    
    # Buscar proveedores
    proveedores = search_service.buscar_proveedores_web(
        producto="Laptop HP",
        ubicacion="México",
        num_resultados=5
    )
    
    print(f"\n📋 Encontrados {len(proveedores)} proveedores:")
    for p in proveedores[:3]:
        print(f"  - {p['nombre']}")
        print(f"    URL: {p['url']}")
        print()
else:
    print("⚠️  SERPER_API_KEY no configurada")
PYEOF
```

**✅ Salida esperada**:
```
✅ SearchService disponible

📋 Encontrados 5 proveedores:
  - Distribuidora Tech México - Laptops HP Empresariales
    URL: https://techmexico.com.mx
  
  - HP Store México
    URL: https://www.hp.com/mx-es/shop
  
  - Computadoras al Mayoreo MX
    URL: https://computadorasmayor.com.mx
```

---

### Test 2: SearchService - Búsqueda en E-commerce

**Objetivo**: Verificar búsqueda en marketplaces con extracción de precios

```bash
python3 << 'PYEOF'
from src.services.search_service import search_service

if search_service.is_available():
    # Buscar en marketplaces
    productos = search_service.buscar_en_ecommerce(
        producto="Mouse inalámbrico Logitech",
        marketplaces=["amazon.com.mx", "mercadolibre.com.mx"]
    )
    
    print(f"🛒 Encontrados {len(productos)} productos en ecommerce:\n")
    for p in productos[:5]:
        print(f"  [{p['marketplace']}]")
        print(f"  {p['producto']}")
        print(f"  💰 {p['precio_aprox']}")
        print(f"  🔗 {p['url_compra'][:60]}...")
        print()
else:
    print("⚠️  SERPER_API_KEY no configurada")
PYEOF
```

**✅ Salida esperada**:
```
🛒 Encontrados 10 productos en ecommerce:

  [Amazon México]
  Logitech M510 Mouse Inalámbrico
  💰 $399.00
  🔗 https://www.amazon.com.mx/Logitech-M510-Inal%C3%A1mbr...

  [MercadoLibre]
  Mouse Inalámbrico Logitech M185
  💰 $199.00
  🔗 https://articulo.mercadolibre.com.mx/MLM-123456789...
```

---

### Test 3: Agente Investigador - Flujo Completo

**Objetivo**: Probar búsqueda multi-fuente con recomendaciones IA

```bash
python3 << 'PYEOF'
from src.agents.investigador import buscar_proveedores

productos = [
    {
        "nombre": "Teclado mecánico",
        "cantidad": 10,
        "categoria": "tecnologia",
        "especificaciones": "RGB, switches cherry mx blue"
    }
]

print("🔍 Buscando proveedores para teclados mecánicos...\n")

resultado = buscar_proveedores(productos, usar_web=True)

# Mostrar resumen
resumen = resultado['resumen']
print("📊 RESUMEN:")
print(f"  • Proveedores BD: {resumen['total_proveedores_bd']}")
print(f"  • Proveedores Web: {resumen['total_proveedores_web']}")
print(f"  • Enlaces Ecommerce: {resumen['total_enlaces_ecommerce']}")
print(f"  • Búsqueda Web: {'✅' if resumen['busqueda_web_activa'] else '❌'}\n")

# Mostrar recomendaciones
if 'recomendaciones' in resultado:
    recs = resultado['recomendaciones']['proveedores_recomendados']
    print(f"💡 RECOMENDACIONES ({len(recs)} proveedores):\n")
    
    for i, rec in enumerate(recs[:3], 1):
        print(f"  {i}. {rec['nombre']}")
        print(f"     Fuente: {rec['fuente']}")
        print(f"     Estrategia: {rec['estrategia']}")
        print(f"     Prioridad: {rec['prioridad']}")
        print(f"     {rec['justificacion'][:80]}...")
        print()
PYEOF
```

**✅ Salida esperada**:
```
🔍 Buscando proveedores para teclados mecánicos...
🌐 Buscando proveedores en internet...
  ✓ Encontrados 5 proveedores web para Teclado mecánico
  ✓ Encontrados 12 productos en ecommerce

📊 RESUMEN:
  • Proveedores BD: 1
  • Proveedores Web: 5
  • Enlaces Ecommerce: 12
  • Búsqueda Web: ✅

💡 RECOMENDACIONES (3 proveedores):

  1. Amazon México
     Fuente: ecommerce
     Estrategia: compra_directa
     Prioridad: alta
     Opción más rápida para urgencias, precios competitivos visibles...

  2. MechaKeys México
     Fuente: web
     Estrategia: investigar
     Prioridad: media
     Especialista en teclados mecánicos, posibles mejores precios al mayor...
  
  3. TechSupply SA
     Fuente: base_de_datos
     Estrategia: cotizacion
     Prioridad: alta
     Proveedor conocido con buen rating, relación comercial establecida...
```

---

### Test 4: Comparador de Precios - Análisis

**Objetivo**: Verificar análisis y recomendación de mejor opción

```bash
python3 << 'PYEOF'
from src.agents.comparador_precios import comparar_precios_multiples_fuentes

productos = [
    {"nombre": "Monitor 27 pulgadas", "cantidad": 5, "categoria": "tecnologia"}
]

proveedores_bd = [
    {
        "id": 1,
        "nombre": "Displays Pro MX",
        "rating": 4.8,
        "email": "ventas@displayspro.mx",
        "fuente": "base_de_datos"
    }
]

proveedores_web = [
    {
        "nombre": "Monitores Al Mayoreo",
        "url": "https://monitoresmayor.mx",
        "descripcion": "Distribuidores de monitores LG, Samsung, Dell",
        "fuente": "web_search"
    }
]

enlaces_ecommerce = [
    {
        "marketplace": "Amazon México",
        "producto": "Monitor LG 27\" IPS Full HD",
        "precio_aprox": "$3,299",
        "url_compra": "https://amazon.com.mx/monitor-lg",
        "disponible_compra_directa": True
    }
]

print("💰 Analizando opciones de compra...\n")

resultado = comparar_precios_multiples_fuentes(
    productos=productos,
    proveedores_bd=proveedores_bd,
    proveedores_web=proveedores_web,
    enlaces_ecommerce=enlaces_ecommerce,
    urgencia="normal"
)

if resultado['exito']:
    analisis = resultado['analisis']
    rec = analisis['recomendacion_principal']
    
    print("🎯 RECOMENDACIÓN PRINCIPAL:")
    print(f"  • Acción: {rec['accion'].upper()}")
    print(f"  • Fuente: {rec['fuente_recomendada']}")
    print(f"  • Ahorro estimado: ${rec['ahorro_estimado']:,.2f} MXN")
    print(f"  • Tiempo: {rec['tiempo_estimado']}")
    print(f"\n  📝 {rec['justificacion']}\n")
    
    print("📊 COMPARATIVA:")
    for comp in analisis['comparativa_precios']:
        print(f"\n  {comp['fuente'].upper()}:")
        print(f"    Precio: ${comp['precio_estimado']:,.2f}")
        print(f"    ✅ {', '.join(comp['ventajas'][:2])}")
        print(f"    ⚠️  {', '.join(comp['desventajas'][:2])}")
else:
    print(f"❌ Error: {resultado['error']}")
PYEOF
```

**✅ Salida esperada**:
```
💰 Analizando opciones de compra...

🎯 RECOMENDACIÓN PRINCIPAL:
  • Acción: COTIZAR
  • Fuente: proveedores_bd
  • Ahorro estimado: $2,500.00 MXN
  • Tiempo: 2-3 días hábiles

  📝 Para 5 monitores, es recomendable solicitar cotización formal a
  Displays Pro MX (proveedor conocido) para obtener descuento por volumen.
  Amazon es opción de respaldo si hay urgencia.

📊 COMPARATIVA:

  PROVEEDORES_BD:
    Precio: $14,500.00
    ✅ Proveedor confiable, Descuento por volumen posible
    ⚠️  Requiere esperar cotización, No inmediato

  ECOMMERCE:
    Precio: $16,495.00
    ✅ Disponibilidad inmediata, Precio visible
    ⚠️  Sin descuento por volumen, Precio más alto
```

---

## 🔍 VERIFICAR INTEGRACIÓN

### Verificar que SearchService está disponible

```bash
python3 << 'PYEOF'
from src.services.search_service import search_service

print(f"SearchService disponible: {search_service.is_available()}")
print(f"API Key configurada: {'✅' if search_service.api_key else '❌'}")

if search_service.is_available():
    # Test rápido
    result = search_service.buscar_proveedores_web("test", num_resultados=1)
    print(f"Test de búsqueda: {'✅ OK' if isinstance(result, list) else '❌ ERROR'}")
PYEOF
```

### Verificar que archivos existen

```bash
# Verificar estructura FASE 3
echo "Verificando archivos FASE 3..."

files=(
    "src/services/search_service.py"
    "src/agents/investigador.py"
    "src/agents/comparador_precios.py"
    "src/prompts/investigador_prompt.txt"
    "tests/test_fase_3.py"
    "test_fase_3_manual.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ FALTA: $file"
    fi
done
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ "SERPER_API_KEY no configurada"

**Problema**: SearchService no está disponible

**Solución**:
```bash
# 1. Registrarse en https://serper.dev (gratis)
# 2. Obtener API key
# 3. Agregar al .env
echo "SERPER_API_KEY=tu-api-key-aqui" >> .env

# 4. Verificar
grep SERPER_API_KEY .env
```

### ❌ "ModuleNotFoundError: No module named 'src'"

**Problema**: Python no encuentra los módulos

**Solución**:
```bash
# Asegúrate de estar en el directorio raíz
cd /home/sinuecg/proyects/pei-compras-ai
pwd  # Debería mostrar: /home/sinuecg/proyects/pei-compras-ai

# Activar entorno virtual
source venv/bin/activate
```

### ❌ "Error buscando proveedores web: 401 Unauthorized"

**Problema**: API key inválida

**Solución**:
```bash
# Verificar que la API key es correcta
grep SERPER_API_KEY .env

# Probar API key manualmente
curl -X POST https://google.serper.dev/search \
  -H "X-API-KEY: TU_API_KEY_AQUI" \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'

# Debería retornar JSON, no error 401
```

### ❌ "Error parseando JSON del agente"

**Problema**: OpenAI retorna respuesta inválida

**Solución**:
```bash
# Verificar que OPENAI_API_KEY funciona
python3 << 'PYEOF'
from src.services.openai_service import llamar_agente

try:
    resp = llamar_agente(
        prompt_sistema="Eres un asistente.",
        mensaje_usuario="Di 'hola'",
        modelo="gpt-4o-mini"
    )
    print("✅ OpenAI API funciona")
    print(f"Respuesta: {resp}")
except Exception as e:
    print(f"❌ Error: {e}")
PYEOF
```

### ❌ Tests fallan por timeout

**Problema**: Red lenta o API no responde

**Solución**:
```bash
# Aumentar timeout en SearchService
# Editar src/services/search_service.py línea ~108 y ~415:
# timeout=30  →  timeout=60

# O ejecutar solo tests locales (sin API)
pytest tests/test_fase_3.py -v -k "not integration"
```

---

## 📊 CHECKLIST DE VERIFICACIÓN

**Pre-requisitos**:
- [ ] Python 3.11+ instalado
- [ ] Entorno virtual activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] OPENAI_API_KEY configurada en .env (de FASE 2)
- [ ] SERPER_API_KEY configurada en .env (FASE 3)

**Archivos**:
- [ ] `src/services/search_service.py` existe y tiene métodos FASE 3
- [ ] `src/agents/investigador.py` creado ✅
- [ ] `src/agents/comparador_precios.py` creado ✅
- [ ] `src/prompts/investigador_prompt.txt` creado ✅
- [ ] `tests/test_fase_3.py` creado ✅
- [ ] `test_fase_3_manual.py` creado ✅

**Tests**:
- [ ] Tests unitarios: `pytest tests/test_fase_3.py -v` ✅
- [ ] Tests sin API key funcionan (retornan listas vacías)
- [ ] Test manual: `python test_fase_3_manual.py` ✅
- [ ] SearchService.is_available() retorna True
- [ ] Búsqueda web retorna resultados
- [ ] Búsqueda ecommerce retorna productos con precios
- [ ] Agente Investigador retorna recomendaciones
- [ ] Comparador de Precios retorna análisis

**Integración**:
- [ ] SearchService integrado en Investigador
- [ ] Investigador llama a OpenAI correctamente
- [ ] Comparador recibe datos de Investigador
- [ ] Flujo completo: Investigador → Comparador funciona

---

## 🚀 COMANDOS DE REFERENCIA RÁPIDA

```bash
# Activar entorno
source venv/bin/activate

# Tests unitarios
pytest tests/test_fase_3.py -v

# Tests sin integración (no usa APIs)
pytest tests/test_fase_3.py -v -k "not integration"

# Test manual interactivo
python test_fase_3_manual.py

# Verificar API keys
python3 -c "from src.services.search_service import search_service; print('Serper:', search_service.is_available())"

# Test rápido de búsqueda
python3 -c "from src.services.search_service import search_service; print(len(search_service.buscar_proveedores_web('laptop')))"

# Ver logs detallados
pytest tests/test_fase_3.py -v -s  # -s muestra prints
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- **Resumen Ejecutivo**: [RESUMEN_FASE_3.md](RESUMEN_FASE_3.md)
- **Arquitectura**: [architecture.md](architecture.md)
- **FASE 2**: [COMO_PROBAR_FASE_2.md](COMO_PROBAR_FASE_2.md)
- **Roadmap**: `docs/roadmap-pei-compras.pdf` páginas 26-30

---

## 🎯 SIGUIENTE PASO

Una vez que todas las pruebas pasen:

✅ **FASE 3 COMPLETADA**  
🎯 **Continuar con FASE 4**: Generador RFQ + Email Service

---

## 📞 SOPORTE

Si encuentras problemas:

1. **Revisa**: Esta guía - Sección "Solución de Problemas"
2. **Verifica**: Logs en consola durante ejecución
3. **Consulta**: [RESUMEN_FASE_3.md](RESUMEN_FASE_3.md) - Documentación técnica
4. **Ejecuta**: `python test_fase_3_manual.py` para diagnóstico interactivo

---

**Elaborado por**: Claude Code  
**Fecha**: 2025-11-13  
**Versión**: 1.0
