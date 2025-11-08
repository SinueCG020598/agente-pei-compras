# Quick Start Guide - PEI Compras AI

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
source venv/bin/activate  # Ya existe

# Instalar dependencias
make install-dev
```

### 2. Configurar Variables de Entorno

Edita el archivo `.env` (ya existe, necesita ser completado):

```bash
nano .env
```

**Mínimo requerido para testing**:
```env
OPENAI_API_KEY=sk-proj-tu-api-key-aqui
EVOLUTION_API_KEY=cualquier-string-aqui
GMAIL_USER=tu-email@gmail.com
GMAIL_APP_PASSWORD=tu-app-password-aqui
```

### 3. Verificar Setup

```bash
# Verificar estructura y configuración
python scripts/test_setup.py
```

### 4. Ejecutar Tests

```bash
# Tests unitarios
make test

# O con pytest directamente
pytest tests/unit/test_setup.py -v
```

## 📁 Estructura del Proyecto

```
50 archivos creados en total
20+ directorios organizados
2,500+ líneas de código base
2,000+ líneas de documentación
```

## 🎯 Próximos Pasos

1. **Ahora**: Completar `.env` y ejecutar `python scripts/test_setup.py`
2. **Siguiente**: Fase 1 - Implementar modelos de base de datos
3. **Después**: Fase 2 - Servicios externos (OpenAI, WhatsApp, Email)

## 📚 Documentación

- `README.md` - Guía principal
- `docs/RESUMEN_FASE_0.md` - Resumen ejecutivo completo
- `docs/fase_0_setup.md` - Detalles técnicos de implementación
- `docs/architecture.md` - Arquitectura del sistema
- `docs/api_docs.md` - Documentación de API
- `docs/deployment.md` - Guía de deployment

## ✅ Todo Listo

✅ Estructura completa del proyecto
✅ Configuración base implementada
✅ Tests iniciales creados
✅ CI/CD configurado
✅ Documentación completa

**FASE 0 COMPLETADA AL 100%**
