# Pasos Siguientes - Setup Completo

## Estado Actual ✅

- [x] Estructura del proyecto creada
- [x] Archivos de configuración presentes
- [x] .env configurado con tus API keys
- [ ] Dependencias Python instaladas
- [ ] Docker services corriendo
- [ ] Verificación completa

## 🚀 Próximos Pasos (En Orden)

### Paso 1: Activar Entorno Virtual

```bash
# Activar el entorno virtual
source venv/bin/activate

# Deberías ver (venv) al inicio de tu prompt
```

### Paso 2: Instalar Dependencias de Python

```bash
# Opción A: Instalar solo producción (más rápido)
make install

# Opción B: Instalar con herramientas de desarrollo (recomendado)
make install-dev
```

Esto instalará:
- FastAPI, Uvicorn
- OpenAI, LangChain, LangGraph
- SQLAlchemy, Alembic
- Streamlit
- pytest, black, ruff, mypy (si usas install-dev)

**Tiempo estimado**: 2-3 minutos

### Paso 3: Verificar Instalación

```bash
# Verificar que las dependencias se instalaron
python3 scripts/check_dependencies.py
```

Deberías ver:
```
✅ FastAPI
✅ Uvicorn
✅ Pydantic
✅ OpenAI
✅ LangChain
...
✅ Todas las dependencias están instaladas correctamente
```

### Paso 4: Levantar Servicios Docker (Opcional pero Recomendado)

```bash
# Levantar Evolution API (WhatsApp) + MongoDB
make docker-up

# Verificar que están corriendo
docker ps
```

Deberías ver:
```
CONTAINER ID   IMAGE                              STATUS
xxxxx          atendai/evolution-api:latest       Up
xxxxx          mongo:latest                       Up
```

**Nota**: Si no tienes Docker instalado, puedes saltarte este paso por ahora. Los tests básicos funcionarán sin Docker.

### Paso 5: Ejecutar Verificación Completa

```bash
# Verificar todo el setup
python3 scripts/test_setup.py
```

**Resultado esperado**:
```
================================================================================
🚀 VERIFICACIÓN DE SETUP - PEI COMPRAS AI
================================================================================

🔍 Verificando estructura del proyecto...
✅ Estructura del proyecto correcta

🔍 Verificando archivos de configuración...
✅ Archivos de configuración presentes

🔍 Verificando variables de entorno...
✅ Variables de entorno configuradas correctamente

🔍 Verificando conexión con OpenAI...
✅ OpenAI API: OK - Respuesta: Setup correcto

🔍 Verificando conexión con Evolution API...
✅ Evolution API: OK (Status 200)
   O
⚠️  Evolution API: No disponible (si no levantaste Docker)

================================================================================
📊 RESUMEN
================================================================================
✅ 5/5 verificaciones pasaron (o 4/5 si no usaste Docker)

🎉 ¡Setup completado exitosamente!
```

### Paso 6: Ejecutar Tests

```bash
# Tests unitarios
make test

# O con más detalle
pytest tests/unit/test_setup.py -v
```

**Resultado esperado**:
```
tests/unit/test_setup.py::TestSetupInicial::test_estructura_directorios_existe PASSED
tests/unit/test_setup.py::TestSetupInicial::test_archivos_configuracion_existen PASSED
...
========== 15 passed in 2.34s ==========
```

### Paso 7: Verificar Cobertura (Opcional)

```bash
# Tests con reporte de cobertura
make test-cov

# Abrir reporte HTML
xdg-open htmlcov/index.html  # Linux
# o
open htmlcov/index.html      # Mac
```

## 🔧 Solución de Problemas

### Error: `No module named 'pydantic_settings'`

**Causa**: Dependencias no instaladas

**Solución**:
```bash
source venv/bin/activate
make install-dev
```

### Error: `docker compose: command not found`

**Causa**: Docker no instalado o versión antigua

**Solución**:
```bash
# Instalar Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# O actualizar a Docker Compose v2
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

### Error: OpenAI API Invalid API Key

**Causa**: API key incorrecta o sin créditos

**Solución**:
1. Verificar que la key en `.env` sea correcta
2. Verificar en https://platform.openai.com/account/usage que tengas créditos
3. Generar nueva API key si es necesario

### Error: Gmail Authentication Failed

**Causa**: No es un App Password

**Solución**:
1. Ve a https://myaccount.google.com/apppasswords
2. Genera un nuevo App Password
3. Copia el password de 16 caracteres a `.env`
4. **NO** uses tu contraseña normal de Gmail

## 📋 Checklist Final

Antes de continuar con la Fase 1, verifica:

- [ ] Entorno virtual activado (`(venv)` en tu prompt)
- [ ] Dependencias instaladas (`python3 scripts/check_dependencies.py` ✅)
- [ ] Variables .env configuradas
- [ ] OpenAI API funcionando
- [ ] Tests pasando (15/15)
- [ ] Docker corriendo (opcional)

## 🎯 ¿Todo Listo?

Si todos los checks anteriores están ✅, estás listo para:

### Siguiente: Fase 1 - Base de Datos y Modelos

1. Definir modelos SQLAlchemy
2. Configurar Alembic
3. Implementar CRUD operations
4. Crear datos de prueba

## 📞 ¿Necesitas Ayuda?

Si algo no funciona:

1. Revisa los logs: `cat logs/pei_compras.log`
2. Revisa la documentación: `docs/fase_0_setup.md`
3. Ejecuta diagnóstico: `python3 scripts/test_setup.py`

## 🎉 ¡Éxito!

Cuando veas:
```
🎉 ¡Setup completado exitosamente!
```

Significa que la **Fase 0 está 100% completa** y puedes proceder con confianza a la Fase 1.

---

**Última actualización**: 2025-11-06
**Siguiente**: Fase 1 - Base de Datos y Modelos
