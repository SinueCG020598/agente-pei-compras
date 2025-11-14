# CÓMO PROBAR FASE 2 - Guía Rápida ⚡

**Versión**: 0.4.0
**Última actualización**: 2025-11-11

---

## 🎯 ¿Qué se implementó en FASE 2?

✅ **Agente Receptor**: Procesa solicitudes en lenguaje natural usando OpenAI
✅ **Formulario Web**: Aplicación Streamlit profesional con 3 tabs
✅ **18 Tests**: 100% pasando con 84% de cobertura
✅ **Integración BD**: Guarda solicitudes automáticamente

---

## ⚡ PRUEBA RÁPIDA (5 minutos)

### 1️⃣ Ejecutar Tests

```bash
cd /home/sinuecg/proyects/pei-compras-ai
source venv/bin/activate
pytest tests/test_agente_receptor.py -v
```

**✅ Resultado esperado**: `18 passed, 2 skipped in 1.06s`

### 2️⃣ Probar Agente desde Python

```bash
python test_agente_manual.py
```

**✅ Resultado esperado**: 3 tests exitosos (simple, compleja, informal)

### 3️⃣ Ejecutar Aplicación Streamlit

```bash
streamlit run frontend/app.py
```

**✅ Resultado esperado**: Se abre http://localhost:8501

### 4️⃣ Crear una Solicitud en la UI

1. Ve al tab **"📝 Nueva Solicitud"**
2. Escribe: `Necesito 5 laptops HP para el equipo de ventas`
3. Click en **"🚀 Procesar Solicitud"**

**✅ Resultado esperado**:
- Mensaje verde: "✅ Solicitud procesada y guardada exitosamente"
- Card del producto con nombre, cantidad, categoría
- Badge de urgencia: 🟢 NORMAL

---

## 📋 PRUEBAS DETALLADAS (15 minutos)

### Test 1: Solicitud Simple

**Input**:
```
Necesito 5 laptops HP para el equipo de ventas
```

**Output esperado**:
- 1 producto: Laptop HP (x5) - tecnologia
- Urgencia: 🟢 normal
- Presupuesto: No especificado

### Test 2: Solicitud Compleja

**Input**:
```
Necesitamos urgente 10 escritorios ejecutivos y 10 sillas ergonómicas
para la nueva oficina. También 2 impresoras láser multifunción.
Tenemos un presupuesto de 8 millones. Es para este viernes!
```

**Output esperado**:
- 3 productos: Escritorio (x10), Silla (x10), Impresora (x2)
- Urgencia: 🔴 urgente
- Presupuesto: $8,000,000 CLP

### Test 3: Solicitud Informal

**Input**:
```
oye necesito unas sillas pa la sala de reuniones, como 6 o 7,
nada muy caro, pa la prox semana porfa
```

**Output esperado**:
- 1 producto: Silla para reuniones (x7) - mobiliario
- Urgencia: 🟡 alta
- Notas: "Solicitud informal, presupuesto ajustado..."

### Test 4: Verificar Historial

1. Ve al tab **"📚 Mis Solicitudes"**
2. Deberías ver las 3 solicitudes creadas
3. Expande una para ver detalles completos

### Test 5: Ver Estadísticas

1. Ve al tab **"📊 Estadísticas"**
2. Deberías ver:
   - Total Solicitudes: ≥ 3
   - Pendientes: ≥ 3
   - Versión: 0.4.0

---

## 🔍 VERIFICAR BASE DE DATOS

```bash
# Ver solicitudes guardadas
sqlite3 pei_compras.db "SELECT id, categoria, estado FROM solicitudes ORDER BY created_at DESC LIMIT 5;"

# Contar total
sqlite3 pei_compras.db "SELECT COUNT(*) FROM solicitudes;"
```

**✅ Resultado esperado**: Ver las solicitudes creadas desde la UI

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ "ModuleNotFoundError: No module named 'src'"

```bash
# Asegúrate de estar en el directorio raíz
cd /home/sinuecg/proyects/pei-compras-ai
pwd  # Debería mostrar: /home/sinuecg/proyects/pei-compras-ai
```

### ❌ "OpenAI API key not found"

```bash
# Verifica el archivo .env
grep OPENAI_API_KEY .env

# Si no existe, agrégalo
echo "OPENAI_API_KEY=sk-proj-TU_API_KEY_AQUI" >> .env
```

### ❌ Tests fallan

```bash
# Reinstala dependencias
pip install -r requirements.txt --upgrade

# Limpia cache
rm -rf .pytest_cache __pycache__
```

### ❌ Streamlit no inicia

```bash
# Usa otro puerto si 8501 está ocupado
streamlit run frontend/app.py --server.port 8502
```

---

## 📊 CHECKLIST DE VERIFICACIÓN

- [ ] Tests: 18/18 pasando ✅
- [ ] Cobertura: ≥ 80% ✅
- [ ] Script manual: 3/3 tests OK ✅
- [ ] Streamlit: Inicia sin errores ✅
- [ ] UI Tab 1: Nueva solicitud funciona ✅
- [ ] UI Tab 2: Historial muestra datos ✅
- [ ] UI Tab 3: Estadísticas correctas ✅
- [ ] Base de datos: Solicitudes guardadas ✅

---

## 📚 DOCUMENTACIÓN COMPLETA

Para instrucciones detalladas paso a paso con todos los comandos:

📖 **[INSTRUCCIONES_FASE_2.md](docs/INSTRUCCIONES_FASE_2.md)** - Guía completa (30+ páginas)

Incluye:
- ✅ Verificación de instalación
- ✅ Ejecución de tests con cobertura
- ✅ Pruebas funcionales en la UI
- ✅ Verificación de integración con BD
- ✅ Solución de problemas detallada
- ✅ Comandos de verificación rápida

---

## 🚀 SIGUIENTE PASO

Una vez que todas las pruebas pasen:

✅ **FASE 2 COMPLETADA**
🎯 **Continuar con FASE 3**: Búsqueda Web de Proveedores

---

## 📞 SOPORTE

Si encuentras problemas:

1. **Revisa**: [INSTRUCCIONES_FASE_2.md](docs/INSTRUCCIONES_FASE_2.md) - Sección "Solución de Problemas"
2. **Verifica**: Logs en consola durante ejecución
3. **Consulta**: [RESUMEN_FASE_2.md](docs/RESUMEN_FASE_2.md) - Documentación técnica

---

**Elaborado por**: Claude Code
**Fecha**: 2025-11-11
