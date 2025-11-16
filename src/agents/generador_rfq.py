"""
Agente Generador de RFQ (Request for Quotation).

Este agente es responsable de:
1. Generar solicitudes de cotización profesionales personalizadas
2. Guardar los RFQs en la base de datos
3. Enviar los RFQs por email a los proveedores
4. Gestionar el estado de los RFQs
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from src.database.models import RFQ

from config.logging_config import logger
from src.database.session import SessionLocal
from src.database.crud import crear_rfq, rfq as crud_rfq
from src.services.openai_service import llamar_agente
from src.services.email_service import email_service


# Cargar prompt del generador
PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "prompts", "generador_rfq_prompt.txt"
)
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    PROMPT_GENERADOR = f.read()


def generar_rfq(
    solicitud_id: int,
    proveedor: dict,
    productos: list,
    urgencia: str = "normal",
) -> dict:
    """
    Genera contenido de RFQ personalizado para un proveedor.

    Args:
        solicitud_id: ID de la solicitud de compra
        proveedor: Diccionario con datos del proveedor:
            - id: ID del proveedor
            - nombre: Nombre del proveedor
            - contacto: Nombre del contacto (opcional)
            - email: Email del proveedor
        productos: Lista de productos a cotizar, cada uno con:
            - nombre: Nombre del producto
            - cantidad: Cantidad solicitada
            - especificaciones: Especificaciones técnicas (opcional)
            - marca: Marca preferida (opcional)
        urgencia: Nivel de urgencia ("normal", "alta", "urgente")

    Returns:
        Dict con:
            - exito: bool, True si se generó correctamente
            - contenido: str, Contenido del RFQ generado
            - fecha_limite: datetime, Fecha límite de respuesta
            - proveedor: dict, Datos del proveedor
            - error: str (opcional), Mensaje de error si falló

    Example:
        >>> proveedor = {
        ...     "id": 1,
        ...     "nombre": "Aceros del Norte",
        ...     "contacto": "Ing. María González",
        ...     "email": "ventas@acerosdn.com"
        ... }
        >>> productos = [
        ...     {
        ...         "nombre": "Placas de acero inoxidable 304",
        ...         "cantidad": "50 unidades",
        ...         "especificaciones": "2m x 1m x 3mm"
        ...     }
        ... ]
        >>> resultado = generar_rfq(1, proveedor, productos, "alta")
    """
    try:
        # Calcular fecha límite según urgencia
        dias_respuesta = {"normal": 5, "alta": 3, "urgente": 1}
        fecha_limite = datetime.now() + timedelta(
            days=dias_respuesta.get(urgencia, 5)
        )

        # Formatear fecha en español
        meses = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        fecha_str = f"{fecha_limite.day} de {meses[fecha_limite.month - 1]} de {fecha_limite.year}"

        # Preparar contexto para el agente
        contexto_proveedor = f"""
INFORMACIÓN PROVEEDOR:
- Nombre: {proveedor.get('nombre', 'N/A')}
- Contacto: {proveedor.get('contacto', 'Estimado proveedor')}
"""

        contexto_productos = "PRODUCTOS A COTIZAR:\n"
        for p in productos:
            contexto_productos += f"- {p.get('nombre', 'N/A')}\n"
            contexto_productos += f"  Cantidad: {p.get('cantidad', 'N/A')}\n"
            if p.get('especificaciones'):
                contexto_productos += f"  Especificaciones: {p.get('especificaciones')}\n"
            if p.get('marca'):
                contexto_productos += f"  Marca/modelo: {p.get('marca')}\n"
            contexto_productos += "\n"

        contexto_completo = f"""{contexto_proveedor}

{contexto_productos}

FECHA LÍMITE RESPUESTA: {fecha_str}
URGENCIA: {urgencia.upper()}

DATOS CONTACTO PEI:
- Empresa: PEI (Productos y Servicios)
- Departamento: Compras
- Email: compras@pei.com
- Teléfono: +52-55-1234-5678
"""

        logger.info(
            f"Generando RFQ para proveedor {proveedor.get('nombre')} "
            f"con {len(productos)} producto(s)"
        )

        # Generar RFQ usando el agente
        contenido_rfq = llamar_agente(
            prompt_sistema=PROMPT_GENERADOR,
            mensaje_usuario=f"Genera RFQ profesional con esta información:\n\n{contexto_completo}",
            modelo="gpt-4o",  # Usar modelo más potente para documentos formales
            temperatura=0.7,
        )

        logger.info("RFQ generado exitosamente")

        return {
            "exito": True,
            "contenido": contenido_rfq,
            "fecha_limite": fecha_limite,
            "proveedor": proveedor,
        }

    except Exception as e:
        logger.error(f"Error generando RFQ: {e}")
        return {
            "exito": False,
            "error": str(e),
            "proveedor": proveedor,
        }


def enviar_rfq(
    solicitud_id: int,
    proveedor: dict,
    productos: list,
    urgencia: str = "normal",
) -> dict:
    """
    Genera RFQ, lo guarda en BD y lo envía por email.

    Este es el método principal para crear y enviar un RFQ completo.
    Realiza las siguientes acciones:
    1. Genera el contenido del RFQ personalizado
    2. Guarda el RFQ en la base de datos
    3. Envía el RFQ por email al proveedor
    4. Actualiza el estado del RFQ a "enviado"

    Args:
        solicitud_id: ID de la solicitud de compra
        proveedor: Diccionario con datos del proveedor (id, nombre, email, contacto)
        productos: Lista de productos a cotizar
        urgencia: Nivel de urgencia ("normal", "alta", "urgente")

    Returns:
        Dict con:
            - exito: bool, True si todo el proceso fue exitoso
            - rfq_id: int, ID del RFQ creado (si fue exitoso)
            - proveedor: str, Nombre del proveedor
            - email: str, Email del proveedor
            - fecha_limite: datetime, Fecha límite de respuesta
            - error: str (opcional), Mensaje de error si falló

    Example:
        >>> resultado = enviar_rfq(
        ...     solicitud_id=1,
        ...     proveedor={"id": 5, "nombre": "TechSupply", "email": "ventas@tech.com"},
        ...     productos=[{"nombre": "PLC Siemens", "cantidad": "5"}],
        ...     urgencia="alta"
        ... )
        >>> if resultado["exito"]:
        ...     print(f"RFQ #{resultado['rfq_id']} enviado a {resultado['email']}")
    """
    db = SessionLocal()

    try:
        # Generar contenido del RFQ
        logger.info(
            f"Iniciando proceso de envío de RFQ para solicitud {solicitud_id}, "
            f"proveedor {proveedor.get('nombre')}"
        )
        rfq_data = generar_rfq(solicitud_id, proveedor, productos, urgencia)

        if not rfq_data["exito"]:
            return rfq_data

        # Guardar en BD
        logger.info("Guardando RFQ en base de datos...")
        rfq_obj = crear_rfq(
            db=db,
            solicitud_id=solicitud_id,
            proveedor_id=proveedor["id"],
            contenido=rfq_data["contenido"],
        )

        asunto = f"Solicitud de Cotización - {rfq_obj.numero_rfq}"

        # Enviar email usando el servicio existente
        logger.info(f"Enviando email a {proveedor.get('email')}...")
        email_enviado = email_service.send_email(
            to=proveedor["email"],
            subject=asunto,
            body=rfq_data["contenido"],
        )

        if email_enviado:
            # Marcar RFQ como enviado
            crud_rfq.marcar_enviado(db, rfq_obj.id)
            logger.info(
                f"✓ RFQ {rfq_obj.numero_rfq} enviado exitosamente a "
                f"{proveedor.get('nombre')} ({proveedor.get('email')})"
            )

            return {
                "exito": True,
                "rfq_id": rfq_obj.id,
                "numero_rfq": rfq_obj.numero_rfq,
                "proveedor": proveedor["nombre"],
                "email": proveedor["email"],
                "fecha_limite": rfq_data["fecha_limite"],
            }
        else:
            logger.warning(
                f"RFQ {rfq_obj.numero_rfq} guardado pero el email no se pudo enviar"
            )
            return {
                "exito": False,
                "error": "RFQ guardado pero email no se pudo enviar",
                "rfq_id": rfq_obj.id,
                "numero_rfq": rfq_obj.numero_rfq,
            }

    except Exception as e:
        logger.error(f"Error en proceso RFQ: {e}")
        return {"exito": False, "error": str(e)}

    finally:
        db.close()


def enviar_rfqs_multiples(
    solicitud_id: int,
    proveedores_recomendados: list,
    productos: list,
    urgencia: str = "normal",
) -> dict:
    """
    Envía RFQs a múltiples proveedores de forma eficiente.

    Procesa una lista de proveedores recomendados y envía RFQs personalizados
    a cada uno. Puede asignar productos específicos a cada proveedor o enviar
    todos los productos a todos los proveedores.

    Args:
        solicitud_id: ID de la solicitud de compra
        proveedores_recomendados: Lista de proveedores, cada uno con:
            - proveedor_data: Dict con datos del proveedor (id, nombre, email)
            - productos_asignados: Lista de nombres de productos (opcional)
            - score: Puntuación del proveedor (opcional)
        productos: Lista completa de productos de la solicitud
        urgencia: Nivel de urgencia ("normal", "alta", "urgente")

    Returns:
        Dict con:
            - total: int, Número total de RFQs procesados
            - exitosos: int, Número de RFQs enviados exitosamente
            - fallidos: int, Número de RFQs que fallaron
            - detalles: List[dict], Detalles de cada envío

    Example:
        >>> proveedores = [
        ...     {
        ...         "proveedor_data": {"id": 1, "nombre": "Proveedor A", "email": "a@test.com"},
        ...         "productos_asignados": ["PLC Siemens"],
        ...         "score": 95
        ...     },
        ...     {
        ...         "proveedor_data": {"id": 2, "nombre": "Proveedor B", "email": "b@test.com"},
        ...         "score": 88
        ...     }
        ... ]
        >>> productos = [{"nombre": "PLC Siemens", "cantidad": "5"}]
        >>> resultado = enviar_rfqs_multiples(1, proveedores, productos, "normal")
        >>> print(f"{resultado['exitosos']} de {resultado['total']} RFQs enviados")
    """
    logger.info(
        f"Iniciando envío masivo de RFQs: {len(proveedores_recomendados)} proveedores"
    )

    resultados = []
    exitosos = 0
    fallidos = 0

    for idx, proveedor_rec in enumerate(proveedores_recomendados, 1):
        proveedor = proveedor_rec.get("proveedor_data", {})
        productos_asignados = proveedor_rec.get("productos_asignados", [])

        logger.info(
            f"Procesando proveedor {idx}/{len(proveedores_recomendados)}: "
            f"{proveedor.get('nombre')}"
        )

        # Filtrar productos para este proveedor si hay asignación específica
        if productos_asignados:
            productos_proveedor = [
                p for p in productos if p.get("nombre") in productos_asignados
            ]
            if not productos_proveedor:
                logger.warning(
                    f"No se encontraron productos asignados para {proveedor.get('nombre')}, "
                    f"enviando todos los productos"
                )
                productos_proveedor = productos
        else:
            # Enviar todos si no hay asignación específica
            productos_proveedor = productos

        # Enviar RFQ a este proveedor
        resultado = enviar_rfq(solicitud_id, proveedor, productos_proveedor, urgencia)
        resultados.append(resultado)

        if resultado["exito"]:
            exitosos += 1
        else:
            fallidos += 1

    logger.info(
        f"Envío masivo completado: {exitosos} exitosos, {fallidos} fallidos "
        f"de {len(resultados)} total"
    )

    return {
        "total": len(resultados),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "detalles": resultados,
    }


def generar_borrador_rfq(
    solicitud_id: int,
    proveedor: dict,
    productos: list,
    urgencia: str = "normal",
) -> dict:
    """
    Genera RFQ y lo guarda en BD como BORRADOR sin enviarlo por email.

    Útil para revisar y aprobar RFQs antes de enviarlos.

    Args:
        solicitud_id: ID de la solicitud de compra
        proveedor: Diccionario con datos del proveedor (id, nombre, email, contacto)
        productos: Lista de productos a cotizar
        urgencia: Nivel de urgencia ("normal", "alta", "urgente")

    Returns:
        Dict con:
            - exito: bool
            - rfq_id: int (ID del RFQ en BD)
            - numero_rfq: str (Número único del RFQ)
            - contenido: str (Contenido generado)
            - proveedor: dict
            - fecha_limite: datetime
            - error: str (opcional)

    Example:
        >>> borrador = generar_borrador_rfq(
        ...     solicitud_id=1,
        ...     proveedor={"id": 5, "nombre": "TechSupply", "email": "ventas@tech.com"},
        ...     productos=[{"nombre": "PLC", "cantidad": "5"}],
        ...     urgencia="alta"
        ... )
        >>> print(f"Borrador {borrador['numero_rfq']} creado. Revisa antes de enviar.")
    """
    db = SessionLocal()

    try:
        logger.info(
            f"Generando borrador de RFQ para solicitud {solicitud_id}, "
            f"proveedor {proveedor.get('nombre')}"
        )

        # Generar contenido del RFQ
        rfq_data = generar_rfq(solicitud_id, proveedor, productos, urgencia)

        if not rfq_data["exito"]:
            return rfq_data

        # Guardar en BD como BORRADOR (no marcar como enviado)
        logger.info("Guardando borrador en base de datos...")
        rfq_obj = crear_rfq(
            db=db,
            solicitud_id=solicitud_id,
            proveedor_id=proveedor["id"],
            contenido=rfq_data["contenido"],
        )

        logger.info(
            f"✓ Borrador {rfq_obj.numero_rfq} creado para {proveedor.get('nombre')}"
        )

        return {
            "exito": True,
            "rfq_id": rfq_obj.id,
            "numero_rfq": rfq_obj.numero_rfq,
            "contenido": rfq_data["contenido"],
            "proveedor": proveedor,
            "fecha_limite": rfq_data["fecha_limite"],
            "estado": "borrador",
        }

    except Exception as e:
        logger.error(f"Error generando borrador: {e}")
        return {"exito": False, "error": str(e)}

    finally:
        db.close()


def enviar_rfq_existente(rfq_id: int, contenido_editado: str = None) -> dict:
    """
    Envía un RFQ que ya existe en la BD (típicamente en estado BORRADOR).

    Permite enviar RFQs previamente generados, opcionalmente con contenido editado.

    Args:
        rfq_id: ID del RFQ en la base de datos
        contenido_editado: Contenido del RFQ editado (opcional, usa el original si es None)

    Returns:
        Dict con:
            - exito: bool
            - numero_rfq: str
            - proveedor: str (nombre)
            - email: str
            - error: str (opcional)

    Example:
        >>> # Generar borrador
        >>> borrador = generar_borrador_rfq(...)
        >>> # Revisar y aprobar
        >>> resultado = enviar_rfq_existente(borrador['rfq_id'])
        >>> # O enviar con contenido editado
        >>> resultado = enviar_rfq_existente(borrador['rfq_id'], contenido_editado="...")
    """
    db = SessionLocal()

    try:
        # Obtener RFQ de BD
        rfq_obj = crud_rfq.get(db, rfq_id)

        if not rfq_obj:
            return {
                "exito": False,
                "error": f"RFQ con ID {rfq_id} no encontrado",
            }

        # Usar contenido editado si se proporciona, sino usar el original
        contenido_final = contenido_editado if contenido_editado else rfq_obj.contenido

        # Actualizar contenido si fue editado
        if contenido_editado:
            crud_rfq.update(
                db, db_obj=rfq_obj, obj_in={"contenido": contenido_editado}
            )

        # Obtener datos del proveedor
        proveedor = rfq_obj.proveedor

        logger.info(
            f"Enviando RFQ {rfq_obj.numero_rfq} a {proveedor.nombre} ({proveedor.email})..."
        )

        # Enviar email
        asunto = f"Solicitud de Cotización - {rfq_obj.numero_rfq}"
        email_enviado = email_service.send_email(
            to=proveedor.email,
            subject=asunto,
            body=contenido_final,
        )

        if email_enviado:
            # Marcar como enviado
            crud_rfq.marcar_enviado(db, rfq_id)
            logger.info(
                f"✓ RFQ {rfq_obj.numero_rfq} enviado exitosamente a {proveedor.nombre}"
            )

            return {
                "exito": True,
                "numero_rfq": rfq_obj.numero_rfq,
                "proveedor": proveedor.nombre,
                "email": proveedor.email,
            }
        else:
            logger.warning(f"Error enviando email para RFQ {rfq_obj.numero_rfq}")
            return {
                "exito": False,
                "error": "No se pudo enviar el email",
                "numero_rfq": rfq_obj.numero_rfq,
            }

    except Exception as e:
        logger.error(f"Error enviando RFQ existente: {e}")
        return {"exito": False, "error": str(e)}

    finally:
        db.close()


def obtener_rfqs_pendientes(solicitud_id: int = None) -> List[dict]:
    """
    Obtiene RFQs en estado BORRADOR (pendientes de envío).

    Args:
        solicitud_id: ID de solicitud (opcional, filtra por solicitud)

    Returns:
        Lista de RFQs en formato dict con toda la información

    Example:
        >>> pendientes = obtener_rfqs_pendientes(solicitud_id=1)
        >>> for rfq in pendientes:
        ...     print(f"{rfq['numero_rfq']}: {rfq['proveedor_nombre']}")
    """
    from src.database.models import EstadoRFQ

    db = SessionLocal()

    try:
        if solicitud_id:
            rfqs = db.query(RFQ).filter(
                RFQ.solicitud_id == solicitud_id,
                RFQ.estado == EstadoRFQ.BORRADOR
            ).all()
        else:
            rfqs = crud_rfq.get_by_estado(db, EstadoRFQ.BORRADOR)

        resultado = []
        for rfq_obj in rfqs:
            resultado.append({
                "id": rfq_obj.id,
                "numero_rfq": rfq_obj.numero_rfq,
                "solicitud_id": rfq_obj.solicitud_id,
                "proveedor_id": rfq_obj.proveedor_id,
                "proveedor_nombre": rfq_obj.proveedor.nombre,
                "proveedor_email": rfq_obj.proveedor.email,
                "contenido": rfq_obj.contenido,
                "asunto": rfq_obj.asunto,
                "estado": rfq_obj.estado.value,
                "created_at": rfq_obj.created_at,
            })

        return resultado

    finally:
        db.close()
