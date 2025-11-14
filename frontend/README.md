# Frontend - PEI Compras AI 🛒

Aplicación web con Streamlit para gestión de solicitudes de compra con procesamiento automático mediante IA.

## 🚀 Inicio Rápido

### Opción 1: Script de inicio (Recomendado)

```bash
# Desde el directorio raíz del proyecto
./iniciar_frontend.sh
```

### Opción 2: Comando directo

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar aplicación
streamlit run frontend/app.py
```

### Opción 3: Makefile (si existe)

```bash
make run-frontend
```

## 📍 Acceso

Una vez iniciada, la aplicación estará disponible en:

- **URL Local**: http://localhost:8501
- **URL Red**: http://192.168.X.X:8501

## 🎨 Características

### Tab 1: 📝 Nueva Solicitud

Formulario inteligente para crear solicitudes de compra:

- **Text Area**: Escribe tu solicitud en lenguaje natural
- **Urgencia**: Auto-detectar, Normal, Alta, Urgente
- **Presupuesto**: Opcional, en CLP
- **Procesamiento IA**: Extracción automática de productos, cantidades y especificaciones
- **Cards Visuales**: Muestra productos extraídos con detalles
- **Guardado Automático**: Se guarda en la base de datos

**Ejemplo de uso**:
```
Necesito 5 laptops HP para el equipo de ventas
```

### Tab 2: 📚 Mis Solicitudes

Historial completo de solicitudes:

- **Filtros**: Por estado (Pendiente, En Proceso, Completada, Cancelada)
- **Límite**: 10, 25, 50, 100 resultados
- **Expandables**: Click para ver detalles completos
- **Información**: Usuario, categoría, presupuesto, fechas, notas

### Tab 3: 📊 Estadísticas

Dashboard con métricas del sistema:

- **Métricas Principales**: Total, Pendientes, En Proceso, Completadas
- **Actividad**: Solicitudes de los últimos 30 días
- **Sistema**: Versión, Modelos IA, Base de datos

### Sidebar

Panel lateral con información en tiempo real:

- **Estadísticas**: Grid 2x2 con métricas
- **Configuración**: Nombre y email del usuario
- **Info Sistema**: Versión y modelos configurados

## 🎨 Diseño

- ✅ CSS Personalizado profesional
- ✅ Badges de urgencia con colores:
  - 🟢 Normal
  - 🟡 Alta
  - 🔴 Urgente
- ✅ Cards con sombras y bordes
- ✅ Diseño responsive
- ✅ Efectos hover en botones

## 🧪 Ejemplos de Solicitudes

### 1. Solicitud Simple

```
Necesito 5 laptops HP para el equipo de ventas
```

**Resultado**:
- 1 producto: Laptop HP (x5)
- Categoría: tecnologia
- Urgencia: 🟢 normal

### 2. Solicitud Compleja

```
Necesitamos urgente 10 escritorios ejecutivos y 10 sillas ergonómicas
para la nueva oficina. También 2 impresoras láser multifunción.
Tenemos un presupuesto de 8 millones. Es para este viernes!
```

**Resultado**:
- 3 productos: Escritorio (x10), Silla (x10), Impresora (x2)
- Urgencia: 🔴 urgente
- Presupuesto: $8,000,000 CLP

### 3. Solicitud Informal

```
oye necesito unas sillas pa la sala de reuniones, como 6 o 7,
nada muy caro, pa la prox semana porfa
```

**Resultado**:
- 1 producto: Silla para reuniones (x7)
- Urgencia: 🟡 alta
- Categoría: mobiliario

## 🔧 Configuración

### Variables de Entorno Requeridas

En el archivo `.env` del proyecto:

```env
# OpenAI (Obligatorio)
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL_MINI=gpt-4o-mini

# Base de Datos
DATABASE_URL=sqlite:///./pei_compras.db

# Proyecto
PROJECT_NAME="PEI Compras AI"
VERSION="0.4.0"
```

### Configuración de Streamlit

Archivo: `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"

[server]
port = 8501
```

## 📦 Dependencias

```
streamlit >= 1.29.0
openai >= 2.7.0
pydantic >= 2.12.0
sqlalchemy >= 2.0.0
```

Todas las dependencias se instalan con:

```bash
pip install -r requirements.txt
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'src'"

```bash
# Asegúrate de ejecutar desde el directorio raíz
cd /home/sinuecg/proyects/pei-compras-ai
```

### Error: "OpenAI API key not found"

```bash
# Verifica el archivo .env
cat .env | grep OPENAI_API_KEY

# Si no existe, agrégalo
echo "OPENAI_API_KEY=sk-proj-xxxxx" >> .env
```

### Error: "Address already in use"

```bash
# El puerto 8501 está ocupado, usa otro
streamlit run frontend/app.py --server.port 8502
```

### Error: Base de datos no existe

```bash
# Crea la base de datos
python scripts/setup_database.py

# O ejecuta las migraciones
alembic upgrade head
```

## 📊 Estado de Desarrollo

| Componente | Estado | Cobertura |
|------------|--------|-----------|
| **Interfaz Principal** | ✅ Completado | - |
| **Tab Nueva Solicitud** | ✅ Completado | - |
| **Tab Mis Solicitudes** | ✅ Completado | - |
| **Tab Estadísticas** | ✅ Completado | - |
| **Sidebar** | ✅ Completado | - |
| **Agente Receptor** | ✅ Completado | 84% |
| **Integración BD** | ✅ Completado | - |
| **CSS Personalizado** | ✅ Completado | - |

## 🔜 Próximas Mejoras

- [ ] Gráficos con matplotlib/plotly
- [ ] Exportación a CSV/Excel
- [ ] Notificaciones por email
- [ ] Autenticación de usuarios
- [ ] Dashboard con métricas avanzadas
- [ ] Historial de cambios de estado
- [ ] Búsqueda y filtros avanzados

## 📚 Documentación

- [Resumen FASE 2](../docs/RESUMEN_FASE_2.md)
- [Instrucciones FASE 2](../docs/INSTRUCCIONES_FASE_2.md)
- [Cómo Probar FASE 2](../COMO_PROBAR_FASE_2.md)

## 🤝 Contribución

Ver [README principal](../README.md) para guía de contribución.

## 📝 Versión

**Versión actual**: 0.4.0

Ver [CHANGELOG](../CHANGELOG.md) para historial completo.

---

**Elaborado por**: Claude Code
**Fecha**: 2025-11-11
