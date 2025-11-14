# 🚀 EJECUTAR FRONTEND - Guía Visual

## ✅ INSTALACIÓN COMPLETADA

Streamlit ya está instalado y configurado correctamente:

```
✅ Streamlit 1.29.0
✅ OpenAI 2.7.1
✅ Pydantic 2.12.4
✅ SQLAlchemy 2.0.23
✅ Todas las importaciones verificadas
✅ Configuración de Streamlit creada
✅ Script de inicio creado
```

---

## 🎯 OPCIÓN 1: Script de Inicio (RECOMENDADO)

### Paso 1: Abrir terminal

```bash
cd /home/sinuecg/proyects/pei-compras-ai
```

### Paso 2: Ejecutar script

```bash
./iniciar_frontend.sh
```

**Esto hará**:
1. ✅ Verificar entorno virtual
2. ✅ Verificar Streamlit instalado
3. ✅ Verificar configuración (.env)
4. ✅ Verificar base de datos
5. ✅ Iniciar aplicación en http://localhost:8501

---

## 🎯 OPCIÓN 2: Comando Manual

```bash
# Paso 1: Activar entorno
cd /home/sinuecg/proyects/pei-compras-ai
source venv/bin/activate

# Paso 2: Ejecutar Streamlit
streamlit run frontend/app.py
```

---

## 🌐 ACCEDER A LA APLICACIÓN

Una vez ejecutado, verás en la terminal:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.X:8501
```

**La aplicación se abrirá automáticamente en tu navegador**

Si no se abre automáticamente:
1. Abre tu navegador
2. Ve a: `http://localhost:8501`

---

## 🖥️ QUÉ VERÁS

### Página Principal

```
╔════════════════════════════════════════════════════════════╗
║                   🛒 PEI Compras AI                        ║
║            Sistema Inteligente de Compras                  ║
╚════════════════════════════════════════════════════════════╝

Sidebar:                          Tabs:
┌─────────────────┐              ┌──────────────────────────┐
│ 📊 Estadísticas │              │ 📝 Nueva Solicitud       │
│                 │              │ 📚 Mis Solicitudes       │
│ Total: 0        │              │ 📊 Estadísticas          │
│ Pendientes: 0   │              └──────────────────────────┘
│ En Proceso: 0   │
│ Completadas: 0  │
│                 │
│ ⚙️ Configuración│
│ Tu nombre: ____ │
│ Tu email: _____ │
│                 │
│ ℹ️ Sistema      │
│ Versión: 0.4.0  │
└─────────────────┘
```

---

## 🧪 PRUEBA RÁPIDA (30 segundos)

### 1. Ve al tab "📝 Nueva Solicitud"

### 2. Escribe en el text area:

```
Necesito 5 laptops HP para el equipo de ventas
```

### 3. Click en "🚀 Procesar Solicitud"

### 4. Verás:

```
✅ Solicitud procesada y guardada exitosamente (ID: 1)

📋 Información Extraída

Urgencia: 🟢 NORMAL

🛍️ Productos Identificados

┌────────────────────────────────────────────────┐
│ 🔹 Laptop HP para equipo de ventas            │
│ Cantidad: 5 unidades                           │
│ Categoría: Tecnologia                          │
│ Especificaciones: Marca: HP, para ventas      │
└────────────────────────────────────────────────┘
```

---

## 📱 NAVEGACIÓN

### Tab 1: 📝 Nueva Solicitud

**¿Qué hace?**
- Procesa solicitudes en lenguaje natural
- Extrae productos, cantidades y especificaciones
- Guarda automáticamente en la base de datos

**Úsalo para**:
- Crear nuevas solicitudes de compra
- Probar el agente de IA
- Ver productos extraídos

### Tab 2: 📚 Mis Solicitudes

**¿Qué hace?**
- Muestra historial de todas las solicitudes
- Permite filtrar por estado
- Muestra detalles completos

**Úsalo para**:
- Ver solicitudes anteriores
- Revisar detalles de cada solicitud
- Filtrar por estado o cantidad

### Tab 3: 📊 Estadísticas

**¿Qué hace?**
- Muestra métricas del sistema
- Actividad de los últimos 30 días
- Información del sistema

**Úsalo para**:
- Ver resumen general
- Verificar versión
- Revisar configuración

---

## 🛑 DETENER EL SERVIDOR

Para detener Streamlit:

1. En la terminal donde está corriendo
2. Presiona: **`Ctrl + C`**
3. Confirma con: **`Y`** (si pregunta)

---

## 🎨 PERSONALIZACIÓN

### Cambiar Usuario

1. En el **Sidebar**
2. Sección "⚙️ Configuración"
3. Edita "Tu nombre" y "Tu email"
4. Las siguientes solicitudes usarán estos datos

### Cambiar Puerto

Si el puerto 8501 está ocupado:

```bash
streamlit run frontend/app.py --server.port 8502
```

---

## 📊 VERIFICACIÓN DE FUNCIONAMIENTO

### ✅ Checklist

Después de ejecutar, verifica:

- [ ] ✅ Aplicación abre en http://localhost:8501
- [ ] ✅ Sidebar muestra estadísticas
- [ ] ✅ 3 tabs visibles
- [ ] ✅ Puede crear una solicitud
- [ ] ✅ Procesa con IA correctamente
- [ ] ✅ Muestra productos en cards
- [ ] ✅ Guarda en historial
- [ ] ✅ Estadísticas se actualizan

---

## 🐛 PROBLEMAS COMUNES

### 1. Puerto ocupado

```
Error: Address already in use

Solución:
streamlit run frontend/app.py --server.port 8502
```

### 2. No encuentra módulos

```
Error: ModuleNotFoundError: No module named 'src'

Solución:
cd /home/sinuecg/proyects/pei-compras-ai
./iniciar_frontend.sh
```

### 3. OpenAI API Key

```
Error: OpenAI API key not found

Solución:
1. Verifica .env: cat .env | grep OPENAI_API_KEY
2. Si no existe, agrégalo: echo "OPENAI_API_KEY=sk-..." >> .env
```

### 4. Base de datos vacía

```
No hay solicitudes en el historial

Solución:
1. Crea una solicitud en Tab 1
2. O ejecuta: python scripts/setup_database.py
```

---

## 📚 MÁS INFORMACIÓN

- **README Frontend**: [frontend/README.md](frontend/README.md)
- **Instrucciones FASE 2**: [docs/INSTRUCCIONES_FASE_2.md](docs/INSTRUCCIONES_FASE_2.md)
- **Resumen FASE 2**: [docs/RESUMEN_FASE_2.md](docs/RESUMEN_FASE_2.md)

---

## 🎉 ¡LISTO PARA USAR!

```bash
./iniciar_frontend.sh
```

Y comienza a probar el sistema 🚀

---

**Elaborado por**: Claude Code
**Fecha**: 2025-11-11
**Versión**: 1.0
