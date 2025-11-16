"""
API Principal del Sistema PEI Compras AI.

Este módulo proporciona los endpoints REST para:
- Procesar solicitudes completas (end-to-end)
- Consultar estado de solicitudes
- Gestionar proveedores, RFQs y cotizaciones
"""
from typing import Dict

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config.settings import settings
from src.database.session import get_db
from src.agents.orquestador import procesar_solicitud_completa, obtener_estado_solicitud
from config.logging_config import logger


# ============================================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de Compras Inteligente con IA Multi-Agente",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELOS DE REQUEST/RESPONSE
# ============================================================================


class SolicitudRequest(BaseModel):
    """Modelo para crear una solicitud."""

    texto: str
    origen: str = "api"

    class Config:
        json_schema_extra = {
            "example": {
                "texto": "Necesito 5 PLCs Siemens S7-1200 y 10 sensores de temperatura bajo norma EMA",
                "origen": "api",
            }
        }


class SolicitudResponse(BaseModel):
    """Modelo de respuesta para solicitud procesada."""

    message: str
    solicitud_id: int
    proveedores_contactados: int
    rfqs_enviados: int
    detalles: Dict

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Solicitud procesada exitosamente",
                "solicitud_id": 123,
                "proveedores_contactados": 5,
                "rfqs_enviados": 5,
                "detalles": {
                    "exito": True,
                    "etapa": "completado",
                    "solicitud": {"urgencia": "normal", "productos": []},
                    "proveedores": {"proveedores_recomendados": []},
                    "rfqs": {"total": 5, "exitosos": 5, "fallidos": 0},
                },
            }
        }


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """Endpoint raíz con información de la API."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "procesar_solicitud_completa": "POST /solicitud/procesar-completa",
            "consultar_estado": "GET /solicitud/{solicitud_id}/estado",
            "health_check": "GET /health",
        },
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoreo."""
    return {"status": "healthy", "version": settings.VERSION}


@app.post("/solicitud/procesar-completa", response_model=SolicitudResponse)
async def procesar_completa(
    data: SolicitudRequest, db: Session = Depends(get_db)
) -> SolicitudResponse:
    """
    Procesa una solicitud end-to-end: Receptor → Investigador → RFQs.

    **Flujo completo:**
    1. Procesa el texto de la solicitud (extrae productos, urgencia, etc.)
    2. Busca proveedores adecuados en BD y web
    3. Genera RFQs personalizados
    4. Envía RFQs por email a los proveedores
    5. Retorna resultado consolidado

    **Args:**
    - texto: Texto de la solicitud en lenguaje natural
    - origen: Origen de la solicitud (api, formulario, whatsapp, email)

    **Returns:**
    - Resultado completo del procesamiento con detalles de cada etapa

    **Raises:**
    - HTTPException 400: Si hubo error procesando la solicitud

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/solicitud/procesar-completa" \\
         -H "Content-Type: application/json" \\
         -d '{
           "texto": "Necesito 5 PLCs Siemens S7-1200",
           "origen": "api"
         }'
    ```
    """
    logger.info(
        f"📨 Nueva solicitud recibida vía API (origen: {data.origen}, "
        f"texto: {data.texto[:50]}...)"
    )

    try:
        # Procesar solicitud completa usando el orquestador
        resultado = await procesar_solicitud_completa(
            texto_solicitud=data.texto, origen=data.origen
        )

        # Verificar si fue exitoso
        if not resultado.get("exito"):
            error_msg = resultado.get("error", "Error desconocido")
            etapa_fallida = resultado.get("etapa", "desconocida")

            logger.error(
                f"❌ Solicitud fallida en etapa '{etapa_fallida}': {error_msg}"
            )

            raise HTTPException(
                status_code=400,
                detail={
                    "error": error_msg,
                    "etapa_fallida": etapa_fallida,
                    "detalles": resultado,
                },
            )

        # Preparar respuesta exitosa
        rfqs_data = resultado.get("rfqs", {})
        respuesta = SolicitudResponse(
            message="Solicitud procesada exitosamente",
            solicitud_id=resultado["solicitud_id"],
            proveedores_contactados=rfqs_data.get("total", 0),
            rfqs_enviados=rfqs_data.get("exitosos", 0),
            detalles=resultado,
        )

        logger.info(
            f"✅ Solicitud {resultado['solicitud_id']} procesada exitosamente. "
            f"RFQs enviados: {rfqs_data.get('exitosos', 0)}/{rfqs_data.get('total', 0)}"
        )

        return respuesta

    except HTTPException:
        # Re-lanzar HTTPException tal cual
        raise

    except Exception as e:
        # Capturar cualquier otro error inesperado
        logger.error(f"💥 Error inesperado en endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/solicitud/{solicitud_id}/estado")
async def consultar_estado(solicitud_id: int, db: Session = Depends(get_db)):
    """
    Consulta el estado actual de una solicitud.

    **Args:**
    - solicitud_id: ID de la solicitud a consultar

    **Returns:**
    - Estado actual de la solicitud con:
        - estado: Estado de la solicitud (pendiente, en_proceso, etc.)
        - rfqs_enviados: Número de RFQs enviados
        - rfqs_respondidos: Número de RFQs con respuesta
        - cotizaciones_recibidas: Número de cotizaciones recibidas

    **Raises:**
    - HTTPException 404: Si la solicitud no existe

    **Example:**
    ```bash
    curl "http://localhost:8000/solicitud/123/estado"
    ```
    """
    logger.info(f"📊 Consultando estado de solicitud {solicitud_id}")

    try:
        estado = obtener_estado_solicitud(solicitud_id)

        if "error" in estado:
            logger.warning(f"⚠️  Solicitud {solicitud_id} no encontrada")
            raise HTTPException(status_code=404, detail=estado["error"])

        return estado

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error consultando estado: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error consultando estado: {str(e)}"
        )


# ============================================================================
# INICIALIZACIÓN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"📚 Documentación disponible en http://localhost:8000/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
