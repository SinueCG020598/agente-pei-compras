"""
Orquestador Principal del Sistema PEI Compras AI.

Este módulo coordina el flujo completo end-to-end:
1. Receptor: Procesa solicitud en lenguaje natural → extrae productos
2. Investigador: Busca proveedores adecuados (BD + Web)
3. Generador RFQ: Crea y envía RFQs a proveedores seleccionados

El orquestador maneja:
- Gestión del estado de la solicitud en BD
- Logging detallado de cada etapa
- Manejo robusto de errores
- Resultados consolidados
"""
from typing import Dict

from config.logging_config import logger
from src.agents.receptor import procesar_solicitud
from src.agents.investigador import buscar_proveedores
from src.agents.generador_rfq import enviar_rfqs_multiples
from src.database.crud import crear_solicitud, actualizar_estado_solicitud
from src.database.session import SessionLocal


async def procesar_solicitud_completa(
    texto_solicitud: str, origen: str = "formulario"
) -> Dict:
    """
    Flujo completo end-to-end: Solicitud → Proveedores → RFQs.

    Este es el punto de entrada principal para procesar una solicitud completa.
    Orquesta los 3 agentes principales del sistema en secuencia.

    **Flujo de ejecución:**

    1. **Etapa Receptor:**
       - Procesa el texto de la solicitud
       - Extrae productos, cantidades, especificaciones
       - Determina urgencia y categorías

    2. **Etapa Base de Datos:**
       - Crea registro de solicitud en BD
       - Actualiza estado a "procesando"

    3. **Etapa Investigador:**
       - Busca proveedores en BD local
       - Busca proveedores en internet (si está habilitado)
       - Rankea y recomienda mejores proveedores

    4. **Etapa Generador RFQ:**
       - Genera RFQs personalizados para cada proveedor
       - Guarda RFQs en BD
       - Envía RFQs por email
       - Actualiza estado de solicitud

    Args:
        texto_solicitud: Texto en lenguaje natural de la solicitud.
            Ejemplo: "Necesito 5 PLCs Siemens S7-1200 y 10 sensores de temperatura"
        origen: Origen de la solicitud. Valores posibles:
            - "formulario": Formulario web (frontend)
            - "whatsapp": Mensaje de WhatsApp
            - "email": Email recibido
            - "api": Llamada directa a API

    Returns:
        Diccionario con el resultado completo del proceso:
        {
            "exito": bool,  # True si todo el flujo fue exitoso
            "etapa": str,   # Última etapa ejecutada
            "solicitud_id": int,  # ID de la solicitud creada
            "solicitud": dict,    # Datos procesados por Receptor
            "proveedores": dict,  # Proveedores encontrados por Investigador
            "rfqs": dict,         # Resultado de envío de RFQs
            "error": str,         # Mensaje de error si falló (opcional)

            # Detalles de cada etapa:
            "rfqs": {
                "total": int,        # Total de RFQs procesados
                "exitosos": int,     # RFQs enviados exitosamente
                "fallidos": int,     # RFQs que fallaron
                "detalles": [...]    # Lista de resultados individuales
            }
        }

    Raises:
        No lanza excepciones directamente, todos los errores se capturan
        y se retornan en el diccionario de respuesta.

    Examples:
        >>> # Solicitud simple desde formulario
        >>> resultado = await procesar_solicitud_completa(
        ...     "Necesito 5 PLCs Siemens S7-1200",
        ...     origen="formulario"
        ... )
        >>> if resultado["exito"]:
        ...     print(f"Solicitud {resultado['solicitud_id']} procesada")
        ...     print(f"{resultado['rfqs']['exitosos']} RFQs enviados")

        >>> # Solicitud urgente desde WhatsApp
        >>> resultado = await procesar_solicitud_completa(
        ...     "URGENTE: necesito calibración de 3 sensores bajo norma EMA",
        ...     origen="whatsapp"
        ... )

        >>> # Manejo de errores
        >>> resultado = await procesar_solicitud_completa("...")
        >>> if not resultado["exito"]:
        ...     print(f"Error en etapa {resultado['etapa']}: {resultado.get('error')}")
    """
    resultado_final = {
        "etapa": None,
        "exito": False,
        "error": None,
    }

    db = SessionLocal()

    try:
        # ====================================================================
        # ETAPA 1: RECEPTOR - Procesar solicitud
        # ====================================================================
        logger.info("=" * 70)
        logger.info("INICIANDO PROCESAMIENTO COMPLETO DE SOLICITUD")
        logger.info("=" * 70)
        logger.info(f"📥 [1/4] Procesando solicitud (origen: {origen})...")

        resultado_final["etapa"] = "receptor"

        resultado_receptor = procesar_solicitud(texto_solicitud, origen)

        if not resultado_receptor["exito"]:
            resultado_final["error"] = (
                resultado_receptor.get("error", "Error procesando solicitud")
            )
            logger.error(f"❌ Error en Receptor: {resultado_final['error']}")
            return resultado_final

        logger.info(
            f"✓ Receptor completado: {len(resultado_receptor.get('productos', []))} "
            f"producto(s) extraído(s)"
        )
        logger.info(f"  Urgencia detectada: {resultado_receptor.get('urgencia', 'N/A')}")

        # ====================================================================
        # ETAPA 2: BASE DE DATOS - Guardar solicitud
        # ====================================================================
        logger.info(f"💾 [2/4] Guardando solicitud en base de datos...")

        solicitud = crear_solicitud(
            db=db,
            origen=origen,
            contenido=texto_solicitud,
            productos=resultado_receptor["productos"],
            urgencia=resultado_receptor.get("urgencia", "normal"),
        )
        resultado_final["solicitud_id"] = solicitud.id
        resultado_final["solicitud"] = resultado_receptor

        logger.info(
            f"✓ Solicitud guardada con ID={solicitud.id}, Estado={solicitud.estado.value}"
        )

        # ====================================================================
        # ETAPA 3: INVESTIGADOR - Buscar proveedores
        # ====================================================================
        logger.info(f"🔍 [3/4] Buscando proveedores adecuados...")
        resultado_final["etapa"] = "investigador"

        # Actualizar estado a "procesando"
        actualizar_estado_solicitud(db, solicitud.id, "procesando")

        resultado_investigador = buscar_proveedores(
            productos=resultado_receptor["productos"],
            usar_web=True,  # Habilitar búsqueda web
        )

        if "error" in resultado_investigador:
            resultado_final["error"] = resultado_investigador["error"]
            logger.error(f"❌ Error en Investigador: {resultado_final['error']}")
            actualizar_estado_solicitud(db, solicitud.id, "error")
            return resultado_final

        proveedores_recomendados = resultado_investigador.get(
            "proveedores_recomendados", []
        )

        if not proveedores_recomendados:
            resultado_final["error"] = (
                "No se encontraron proveedores adecuados para los productos solicitados"
            )
            logger.warning(f"⚠️  {resultado_final['error']}")
            actualizar_estado_solicitud(db, solicitud.id, "error")
            return resultado_final

        resultado_final["proveedores"] = resultado_investigador

        logger.info(
            f"✓ Investigador completado: {len(proveedores_recomendados)} proveedor(es) "
            f"recomendado(s)"
        )

        for idx, prov in enumerate(proveedores_recomendados[:3], 1):
            prov_data = prov.get("proveedor_data", {})
            score = prov.get("score", "N/A")
            logger.info(
                f"  {idx}. {prov_data.get('nombre', 'N/A')} "
                f"(Score: {score}, Email: {prov_data.get('email', 'N/A')})"
            )

        # ====================================================================
        # ETAPA 4: GENERADOR RFQ - Generar y enviar RFQs
        # ====================================================================
        logger.info(f"📧 [4/4] Generando y enviando RFQs...")
        resultado_final["etapa"] = "generador_rfq"

        resultado_rfqs = enviar_rfqs_multiples(
            solicitud_id=solicitud.id,
            proveedores_recomendados=proveedores_recomendados,
            productos=resultado_receptor["productos"],
            urgencia=resultado_receptor.get("urgencia", "normal"),
        )

        resultado_final["rfqs"] = resultado_rfqs

        # ====================================================================
        # FINALIZACIÓN
        # ====================================================================
        if resultado_rfqs["exitosos"] > 0:
            # Al menos un RFQ fue enviado exitosamente
            actualizar_estado_solicitud(db, solicitud.id, "rfqs_enviados")
            resultado_final["exito"] = True
            resultado_final["etapa"] = "completado"

            logger.info("=" * 70)
            logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
            logger.info("=" * 70)
            logger.info(f"📊 Resumen:")
            logger.info(f"  - Solicitud ID: {solicitud.id}")
            logger.info(f"  - Productos procesados: {len(resultado_receptor['productos'])}")
            logger.info(f"  - Proveedores encontrados: {len(proveedores_recomendados)}")
            logger.info(
                f"  - RFQs enviados: {resultado_rfqs['exitosos']}/{resultado_rfqs['total']}"
            )
            logger.info(f"  - Urgencia: {resultado_receptor.get('urgencia', 'normal')}")
            logger.info("=" * 70)

        else:
            # Ningún RFQ fue enviado
            resultado_final["error"] = (
                f"No se pudo enviar ningún RFQ. "
                f"Fallaron {resultado_rfqs['fallidos']} intentos."
            )
            logger.error(f"❌ {resultado_final['error']}")
            actualizar_estado_solicitud(db, solicitud.id, "error")

        return resultado_final

    except Exception as e:
        # Capturar cualquier error inesperado
        logger.error(f"💥 Error inesperado en orquestador: {e}", exc_info=True)
        resultado_final["error"] = f"Error inesperado: {str(e)}"

        if "solicitud_id" in resultado_final:
            actualizar_estado_solicitud(db, resultado_final["solicitud_id"], "error")

        return resultado_final

    finally:
        db.close()


def obtener_estado_solicitud(solicitud_id: int) -> Dict:
    """
    Obtiene el estado actual de una solicitud procesada.

    Útil para:
    - Monitoreo del progreso
    - Debugging
    - Reportes de estado

    Args:
        solicitud_id: ID de la solicitud a consultar

    Returns:
        Diccionario con:
        {
            "solicitud_id": int,
            "estado": str,
            "rfqs_enviados": int,
            "rfqs_respondidos": int,
            "ultima_actualizacion": str
        }

    Example:
        >>> estado = obtener_estado_solicitud(123)
        >>> print(f"Estado: {estado['estado']}")
    """
    from src.database.crud import consultar_historial

    db = SessionLocal()

    try:
        historial = consultar_historial(db, solicitud_id)

        if not historial:
            return {
                "error": "Solicitud no encontrada",
                "solicitud_id": solicitud_id,
            }

        solicitud_data = historial["solicitud"]
        rfqs = historial.get("rfqs", [])

        # Contar RFQs por estado
        rfqs_enviados = sum(
            1 for rfq in rfqs if rfq.get("estado") in ["enviado", "respondido"]
        )
        rfqs_respondidos = sum(1 for rfq in rfqs if rfq.get("estado") == "respondido")

        return {
            "solicitud_id": solicitud_id,
            "estado": solicitud_data["estado"],
            "urgencia": solicitud_data.get("urgencia", "normal"),
            "rfqs_total": len(rfqs),
            "rfqs_enviados": rfqs_enviados,
            "rfqs_respondidos": rfqs_respondidos,
            "cotizaciones_recibidas": len(historial.get("cotizaciones", [])),
            "ultima_actualizacion": solicitud_data["updated_at"],
            "created_at": solicitud_data["created_at"],
        }

    finally:
        db.close()
