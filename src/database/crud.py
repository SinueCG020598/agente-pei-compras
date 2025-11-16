"""
Operaciones CRUD (Create, Read, Update, Delete) para todos los modelos.

Este módulo proporciona funciones para interactuar con la base de datos
de manera consistente y segura.
"""
from datetime import datetime
from typing import List, Optional, Type, TypeVar, Generic

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from src.database.models import (
    Solicitud,
    Proveedor,
    RFQ,
    Cotizacion,
    OrdenCompra,
    EnvioTracking,
    EstadoSolicitud,
    EstadoRFQ,
    EstadoOrdenCompra,
    EstadoEnvio,
)
from config.logging_config import logger

# Type variable para operaciones genéricas
ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """
    Clase base para operaciones CRUD genéricas.

    Proporciona operaciones comunes para todos los modelos.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Inicializa CRUD con el modelo especificado.

        Args:
            model: Clase del modelo SQLAlchemy
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Obtiene un registro por ID.

        Args:
            db: Sesión de base de datos
            id: ID del registro

        Returns:
            Registro encontrado o None
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Obtiene múltiples registros con paginación.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar

        Returns:
            Lista de registros
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: dict) -> ModelType:
        """
        Crea un nuevo registro.

        Args:
            db: Sesión de base de datos
            obj_in: Diccionario con datos del objeto

        Returns:
            Objeto creado

        Raises:
            Exception: Si hay error al crear
        """
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Creado {self.model.__name__} con ID {db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error creando {self.model.__name__}: {e}")
            db.rollback()
            raise

    def update(self, db: Session, *, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        Actualiza un registro existente.

        Args:
            db: Sesión de base de datos
            db_obj: Objeto existente en BD
            obj_in: Diccionario con datos a actualizar

        Returns:
            Objeto actualizado

        Raises:
            Exception: Si hay error al actualizar
        """
        try:
            for field, value in obj_in.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Actualizado {self.model.__name__} con ID {db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error actualizando {self.model.__name__}: {e}")
            db.rollback()
            raise

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Elimina un registro por ID.

        Args:
            db: Sesión de base de datos
            id: ID del registro a eliminar

        Returns:
            Objeto eliminado o None si no existe

        Raises:
            Exception: Si hay error al eliminar
        """
        try:
            obj = db.query(self.model).get(id)
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"Eliminado {self.model.__name__} con ID {id}")
            return obj
        except Exception as e:
            logger.error(f"Error eliminando {self.model.__name__}: {e}")
            db.rollback()
            raise


class CRUDSolicitud(CRUDBase[Solicitud]):
    """Operaciones CRUD específicas para Solicitud."""

    def get_by_estado(
        self, db: Session, estado: EstadoSolicitud, skip: int = 0, limit: int = 100
    ) -> List[Solicitud]:
        """
        Obtiene solicitudes por estado.

        Args:
            db: Sesión de base de datos
            estado: Estado de la solicitud
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de solicitudes
        """
        return (
            db.query(Solicitud)
            .filter(Solicitud.estado == estado)
            .order_by(desc(Solicitud.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_usuario(
        self, db: Session, usuario_id: str, skip: int = 0, limit: int = 100
    ) -> List[Solicitud]:
        """
        Obtiene solicitudes de un usuario específico.

        Args:
            db: Sesión de base de datos
            usuario_id: ID del usuario
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de solicitudes del usuario
        """
        return (
            db.query(Solicitud)
            .filter(Solicitud.usuario_id == usuario_id)
            .order_by(desc(Solicitud.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_categoria(
        self, db: Session, categoria: str, skip: int = 0, limit: int = 100
    ) -> List[Solicitud]:
        """
        Obtiene solicitudes por categoría.

        Args:
            db: Sesión de base de datos
            categoria: Categoría a filtrar
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de solicitudes
        """
        return (
            db.query(Solicitud)
            .filter(Solicitud.categoria == categoria)
            .order_by(desc(Solicitud.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def cambiar_estado(
        self, db: Session, solicitud_id: int, nuevo_estado: EstadoSolicitud
    ) -> Optional[Solicitud]:
        """
        Cambia el estado de una solicitud.

        Args:
            db: Sesión de base de datos
            solicitud_id: ID de la solicitud
            nuevo_estado: Nuevo estado

        Returns:
            Solicitud actualizada o None
        """
        solicitud = self.get(db, solicitud_id)
        if solicitud:
            return self.update(db, db_obj=solicitud, obj_in={"estado": nuevo_estado})
        return None

    def count(self, db: Session) -> int:
        """
        Cuenta el total de solicitudes.

        Args:
            db: Sesión de base de datos

        Returns:
            Número total de solicitudes
        """
        return db.query(Solicitud).count()

    def count_by_estado(self, db: Session, estado: EstadoSolicitud) -> int:
        """
        Cuenta solicitudes por estado.

        Args:
            db: Sesión de base de datos
            estado: Estado a filtrar

        Returns:
            Número de solicitudes en ese estado
        """
        return db.query(Solicitud).filter(Solicitud.estado == estado).count()

    def get_by_fecha_rango(
        self, db: Session, fecha_desde: datetime, fecha_hasta: datetime = None
    ) -> List[Solicitud]:
        """
        Obtiene solicitudes en un rango de fechas.

        Args:
            db: Sesión de base de datos
            fecha_desde: Fecha inicial
            fecha_hasta: Fecha final (opcional, por defecto ahora)

        Returns:
            Lista de solicitudes en el rango
        """
        from datetime import datetime

        if fecha_hasta is None:
            fecha_hasta = datetime.utcnow()

        return (
            db.query(Solicitud)
            .filter(Solicitud.created_at >= fecha_desde)
            .filter(Solicitud.created_at <= fecha_hasta)
            .order_by(desc(Solicitud.created_at))
            .all()
        )


class CRUDProveedor(CRUDBase[Proveedor]):
    """Operaciones CRUD específicas para Proveedor."""

    def get_by_email(self, db: Session, email: str) -> Optional[Proveedor]:
        """
        Obtiene proveedor por email.

        Args:
            db: Sesión de base de datos
            email: Email del proveedor

        Returns:
            Proveedor encontrado o None
        """
        return db.query(Proveedor).filter(Proveedor.email == email).first()

    def get_by_categoria(
        self, db: Session, categoria: str, skip: int = 0, limit: int = 100
    ) -> List[Proveedor]:
        """
        Obtiene proveedores por categoría.

        Args:
            db: Sesión de base de datos
            categoria: Categoría a filtrar
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de proveedores
        """
        return (
            db.query(Proveedor)
            .filter(Proveedor.categoria == categoria)
            .order_by(desc(Proveedor.rating))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_verificados(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Proveedor]:
        """
        Obtiene proveedores verificados.

        Args:
            db: Sesión de base de datos
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de proveedores verificados
        """
        return (
            db.query(Proveedor)
            .filter(Proveedor.es_verificado == True)
            .order_by(desc(Proveedor.rating))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def actualizar_rating(
        self, db: Session, proveedor_id: int, nuevo_rating: float
    ) -> Optional[Proveedor]:
        """
        Actualiza el rating de un proveedor.

        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor
            nuevo_rating: Nuevo rating (0-5)

        Returns:
            Proveedor actualizado o None
        """
        proveedor = self.get(db, proveedor_id)
        if proveedor:
            return self.update(db, db_obj=proveedor, obj_in={"rating": nuevo_rating})
        return None


class CRUDRFQ(CRUDBase[RFQ]):
    """Operaciones CRUD específicas para RFQ."""

    def get_by_solicitud(
        self, db: Session, solicitud_id: int
    ) -> List[RFQ]:
        """
        Obtiene RFQs de una solicitud.

        Args:
            db: Sesión de base de datos
            solicitud_id: ID de la solicitud

        Returns:
            Lista de RFQs
        """
        return (
            db.query(RFQ)
            .filter(RFQ.solicitud_id == solicitud_id)
            .order_by(desc(RFQ.created_at))
            .all()
        )

    def get_by_proveedor(
        self, db: Session, proveedor_id: int
    ) -> List[RFQ]:
        """
        Obtiene RFQs enviados a un proveedor.

        Args:
            db: Sesión de base de datos
            proveedor_id: ID del proveedor

        Returns:
            Lista de RFQs
        """
        return (
            db.query(RFQ)
            .filter(RFQ.proveedor_id == proveedor_id)
            .order_by(desc(RFQ.created_at))
            .all()
        )

    def get_by_estado(
        self, db: Session, estado: EstadoRFQ, skip: int = 0, limit: int = 100
    ) -> List[RFQ]:
        """
        Obtiene RFQs por estado.

        Args:
            db: Sesión de base de datos
            estado: Estado del RFQ
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de RFQs
        """
        return (
            db.query(RFQ)
            .filter(RFQ.estado == estado)
            .order_by(desc(RFQ.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def marcar_enviado(
        self, db: Session, rfq_id: int
    ) -> Optional[RFQ]:
        """
        Marca un RFQ como enviado.

        Args:
            db: Sesión de base de datos
            rfq_id: ID del RFQ

        Returns:
            RFQ actualizado o None
        """
        rfq = self.get(db, rfq_id)
        if rfq:
            return self.update(
                db,
                db_obj=rfq,
                obj_in={
                    "estado": EstadoRFQ.ENVIADO,
                    "fecha_envio": datetime.utcnow(),
                },
            )
        return None


class CRUDCotizacion(CRUDBase[Cotizacion]):
    """Operaciones CRUD específicas para Cotización."""

    def get_by_rfq(self, db: Session, rfq_id: int) -> List[Cotizacion]:
        """
        Obtiene cotizaciones de un RFQ.

        Args:
            db: Sesión de base de datos
            rfq_id: ID del RFQ

        Returns:
            Lista de cotizaciones
        """
        return (
            db.query(Cotizacion)
            .filter(Cotizacion.rfq_id == rfq_id)
            .order_by(asc(Cotizacion.precio_total))
            .all()
        )

    def get_mejor_precio(self, db: Session, rfq_id: int) -> Optional[Cotizacion]:
        """
        Obtiene la cotización con mejor precio de un RFQ.

        Args:
            db: Sesión de base de datos
            rfq_id: ID del RFQ

        Returns:
            Cotización con mejor precio o None
        """
        return (
            db.query(Cotizacion)
            .filter(Cotizacion.rfq_id == rfq_id)
            .filter(Cotizacion.es_valida == True)
            .order_by(asc(Cotizacion.precio_total))
            .first()
        )

    def get_mejor_puntaje(self, db: Session, rfq_id: int) -> Optional[Cotizacion]:
        """
        Obtiene la cotización con mejor puntaje IA de un RFQ.

        Args:
            db: Sesión de base de datos
            rfq_id: ID del RFQ

        Returns:
            Cotización con mejor puntaje o None
        """
        return (
            db.query(Cotizacion)
            .filter(Cotizacion.rfq_id == rfq_id)
            .filter(Cotizacion.es_valida == True)
            .filter(Cotizacion.puntaje_ia.isnot(None))
            .order_by(desc(Cotizacion.puntaje_ia))
            .first()
        )


class CRUDOrdenCompra(CRUDBase[OrdenCompra]):
    """Operaciones CRUD específicas para Orden de Compra."""

    def get_by_numero(self, db: Session, numero_orden: str) -> Optional[OrdenCompra]:
        """
        Obtiene orden de compra por número.

        Args:
            db: Sesión de base de datos
            numero_orden: Número de la orden

        Returns:
            Orden encontrada o None
        """
        return (
            db.query(OrdenCompra)
            .filter(OrdenCompra.numero_orden == numero_orden)
            .first()
        )

    def get_by_solicitud(self, db: Session, solicitud_id: int) -> List[OrdenCompra]:
        """
        Obtiene órdenes de compra de una solicitud.

        Args:
            db: Sesión de base de datos
            solicitud_id: ID de la solicitud

        Returns:
            Lista de órdenes de compra
        """
        return (
            db.query(OrdenCompra)
            .filter(OrdenCompra.solicitud_id == solicitud_id)
            .order_by(desc(OrdenCompra.created_at))
            .all()
        )

    def get_by_estado(
        self, db: Session, estado: EstadoOrdenCompra, skip: int = 0, limit: int = 100
    ) -> List[OrdenCompra]:
        """
        Obtiene órdenes por estado.

        Args:
            db: Sesión de base de datos
            estado: Estado de la orden
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de órdenes
        """
        return (
            db.query(OrdenCompra)
            .filter(OrdenCompra.estado == estado)
            .order_by(desc(OrdenCompra.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def aprobar(
        self, db: Session, orden_id: int, aprobado_por: str
    ) -> Optional[OrdenCompra]:
        """
        Aprueba una orden de compra.

        Args:
            db: Sesión de base de datos
            orden_id: ID de la orden
            aprobado_por: Nombre de quien aprueba

        Returns:
            Orden aprobada o None
        """
        orden = self.get(db, orden_id)
        if orden:
            return self.update(
                db,
                db_obj=orden,
                obj_in={
                    "estado": EstadoOrdenCompra.CONFIRMADA,
                    "aprobado_por": aprobado_por,
                    "fecha_aprobacion": datetime.utcnow(),
                },
            )
        return None


class CRUDEnvioTracking(CRUDBase[EnvioTracking]):
    """Operaciones CRUD específicas para Envío Tracking."""

    def get_by_orden_compra(
        self, db: Session, orden_compra_id: int
    ) -> Optional[EnvioTracking]:
        """
        Obtiene el tracking de una orden de compra.

        Args:
            db: Sesión de base de datos
            orden_compra_id: ID de la orden de compra

        Returns:
            EnvioTracking encontrado o None
        """
        return (
            db.query(EnvioTracking)
            .filter(EnvioTracking.orden_compra_id == orden_compra_id)
            .first()
        )

    def get_by_tracking_number(
        self, db: Session, tracking_number: str
    ) -> Optional[EnvioTracking]:
        """
        Obtiene envío por número de tracking.

        Args:
            db: Sesión de base de datos
            tracking_number: Número de tracking

        Returns:
            EnvioTracking encontrado o None
        """
        return (
            db.query(EnvioTracking)
            .filter(EnvioTracking.tracking_number == tracking_number)
            .first()
        )

    def get_by_estado(
        self, db: Session, estado: EstadoEnvio, skip: int = 0, limit: int = 100
    ) -> List[EnvioTracking]:
        """
        Obtiene envíos por estado.

        Args:
            db: Sesión de base de datos
            estado: Estado del envío
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de envíos
        """
        return (
            db.query(EnvioTracking)
            .filter(EnvioTracking.estado == estado)
            .order_by(desc(EnvioTracking.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pendientes(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[EnvioTracking]:
        """
        Obtiene envíos pendientes (no entregados).

        Args:
            db: Sesión de base de datos
            skip: Registros a saltar
            limit: Límite de registros

        Returns:
            Lista de envíos pendientes
        """
        estados_pendientes = [
            EstadoEnvio.PENDIENTE,
            EstadoEnvio.EN_TRANSITO,
            EstadoEnvio.EN_ADUANA,
            EstadoEnvio.EN_DISTRIBUCION,
            EstadoEnvio.EN_ENTREGA,
        ]
        return (
            db.query(EnvioTracking)
            .filter(EnvioTracking.estado.in_(estados_pendientes))
            .order_by(asc(EnvioTracking.fecha_entrega_estimada))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def actualizar_estado(
        self, db: Session, envio_id: int, nuevo_estado: EstadoEnvio, ubicacion: str = None
    ) -> Optional[EnvioTracking]:
        """
        Actualiza el estado de un envío.

        Args:
            db: Sesión de base de datos
            envio_id: ID del envío
            nuevo_estado: Nuevo estado
            ubicacion: Nueva ubicación (opcional)

        Returns:
            EnvioTracking actualizado o None
        """
        envio = self.get(db, envio_id)
        if envio:
            datos_actualizar = {"estado": nuevo_estado}

            if ubicacion:
                datos_actualizar["ubicacion_actual"] = ubicacion

            # Si se marca como entregado, registrar fecha
            if nuevo_estado == EstadoEnvio.ENTREGADO and not envio.fecha_entrega_real:
                datos_actualizar["fecha_entrega_real"] = datetime.utcnow()

            return self.update(db, db_obj=envio, obj_in=datos_actualizar)
        return None

    def agregar_evento(
        self, db: Session, envio_id: int, evento: dict
    ) -> Optional[EnvioTracking]:
        """
        Agrega un evento al historial de tracking.

        Args:
            db: Sesión de base de datos
            envio_id: ID del envío
            evento: Diccionario con info del evento (timestamp, ubicacion, descripcion)

        Returns:
            EnvioTracking actualizado o None
        """
        envio = self.get(db, envio_id)
        if envio:
            eventos = envio.eventos or []
            eventos.append({
                **evento,
                "timestamp": evento.get("timestamp", datetime.utcnow().isoformat())
            })
            return self.update(db, db_obj=envio, obj_in={"eventos": eventos})
        return None


def consultar_historial(db: Session, solicitud_id: int) -> dict:
    """
    Obtiene el historial completo de una solicitud con todas sus relaciones.

    Devuelve una vista completa del ciclo de vida de una solicitud:
    - Solicitud original
    - RFQs enviados a proveedores
    - Cotizaciones recibidas
    - Orden de compra generada (si existe)
    - Tracking de envío (si existe)

    Args:
        db: Sesión de base de datos
        solicitud_id: ID de la solicitud

    Returns:
        Diccionario con todo el historial o None si no existe

    Example:
        >>> historial = consultar_historial(db, solicitud_id=123)
        >>> print(historial["solicitud"]["estado"])
        >>> print(historial["rfqs"][0]["proveedor"]["nombre"])
        >>> print(historial["orden_compra"]["tracking"]["estado"])
    """
    # Obtener solicitud con todas las relaciones
    solicitud_obj = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()

    if not solicitud_obj:
        return None

    # Construir respuesta estructurada
    resultado = {
        "solicitud": {
            "id": solicitud_obj.id,
            "usuario_nombre": solicitud_obj.usuario_nombre,
            "usuario_contacto": solicitud_obj.usuario_contacto,
            "descripcion": solicitud_obj.descripcion,
            "categoria": solicitud_obj.categoria,
            "cantidad": solicitud_obj.cantidad,
            "presupuesto": solicitud_obj.presupuesto,
            "fecha_limite": solicitud_obj.fecha_limite.isoformat() if solicitud_obj.fecha_limite else None,
            "prioridad": solicitud_obj.prioridad,
            "estado": solicitud_obj.estado.value,
            "notas_internas": solicitud_obj.notas_internas,
            "created_at": solicitud_obj.created_at.isoformat(),
            "updated_at": solicitud_obj.updated_at.isoformat(),
        },
        "rfqs": [],
        "cotizaciones": [],
        "orden_compra": None,
        "tracking": None,
    }

    # Procesar RFQs y sus cotizaciones
    for rfq_obj in solicitud_obj.rfqs:
        rfq_data = {
            "id": rfq_obj.id,
            "numero_rfq": rfq_obj.numero_rfq,
            "asunto": rfq_obj.asunto,
            "contenido": rfq_obj.contenido,
            "estado": rfq_obj.estado.value,
            "fecha_envio": rfq_obj.fecha_envio.isoformat() if rfq_obj.fecha_envio else None,
            "fecha_respuesta": rfq_obj.fecha_respuesta.isoformat() if rfq_obj.fecha_respuesta else None,
            "proveedor": {
                "id": rfq_obj.proveedor.id,
                "nombre": rfq_obj.proveedor.nombre,
                "email": rfq_obj.proveedor.email,
                "telefono": rfq_obj.proveedor.telefono,
                "categoria": rfq_obj.proveedor.categoria,
                "rating": rfq_obj.proveedor.rating,
            },
            "cotizaciones": [],
        }

        # Cotizaciones de este RFQ
        for cot_obj in rfq_obj.cotizaciones:
            cot_data = {
                "id": cot_obj.id,
                "precio_total": cot_obj.precio_total,
                "precio_unitario": cot_obj.precio_unitario,
                "moneda": cot_obj.moneda,
                "tiempo_entrega": cot_obj.tiempo_entrega,
                "condiciones_pago": cot_obj.condiciones_pago,
                "garantia": cot_obj.garantia,
                "observaciones": cot_obj.observaciones,
                "es_valida": cot_obj.es_valida,
                "puntaje_ia": cot_obj.puntaje_ia,
                "created_at": cot_obj.created_at.isoformat(),
            }
            rfq_data["cotizaciones"].append(cot_data)
            resultado["cotizaciones"].append(cot_data)

        resultado["rfqs"].append(rfq_data)

    # Procesar Orden de Compra (si existe)
    if solicitud_obj.ordenes_compra:
        oc_obj = solicitud_obj.ordenes_compra[0]  # Normalmente hay solo una
        resultado["orden_compra"] = {
            "id": oc_obj.id,
            "numero_orden": oc_obj.numero_orden,
            "estado": oc_obj.estado.value,
            "monto_total": oc_obj.monto_total,
            "moneda": oc_obj.moneda,
            "fecha_emision": oc_obj.fecha_emision.isoformat() if oc_obj.fecha_emision else None,
            "fecha_entrega_esperada": oc_obj.fecha_entrega_esperada.isoformat() if oc_obj.fecha_entrega_esperada else None,
            "fecha_entrega_real": oc_obj.fecha_entrega_real.isoformat() if oc_obj.fecha_entrega_real else None,
            "aprobado_por": oc_obj.aprobado_por,
            "fecha_aprobacion": oc_obj.fecha_aprobacion.isoformat() if oc_obj.fecha_aprobacion else None,
            "created_at": oc_obj.created_at.isoformat(),
        }

        # Procesar Tracking (si existe)
        if oc_obj.envio_tracking:
            tracking_obj = oc_obj.envio_tracking
            resultado["tracking"] = {
                "id": tracking_obj.id,
                "estado": tracking_obj.estado.value,
                "tracking_number": tracking_obj.tracking_number,
                "proveedor_envio": tracking_obj.proveedor_envio,
                "fecha_envio": tracking_obj.fecha_envio.isoformat() if tracking_obj.fecha_envio else None,
                "fecha_entrega_estimada": tracking_obj.fecha_entrega_estimada.isoformat() if tracking_obj.fecha_entrega_estimada else None,
                "fecha_entrega_real": tracking_obj.fecha_entrega_real.isoformat() if tracking_obj.fecha_entrega_real else None,
                "ubicacion_actual": tracking_obj.ubicacion_actual,
                "ciudad_origen": tracking_obj.ciudad_origen,
                "ciudad_destino": tracking_obj.ciudad_destino,
                "notas": tracking_obj.notas,
                "eventos": tracking_obj.eventos,
                "updated_at": tracking_obj.updated_at.isoformat(),
            }

    return resultado


# ============================================================================
# FUNCIONES HELPER PARA FASE 4
# ============================================================================


def crear_solicitud(
    db: Session,
    origen: str,
    contenido: str,
    productos: List[dict],
    urgencia: str = "normal",
    usuario_nombre: str = "Sistema",
    usuario_contacto: str = "sistema@pei.com",
) -> Solicitud:
    """
    Crea una nueva solicitud a partir de datos procesados.

    Args:
        db: Sesión de base de datos
        origen: Origen de la solicitud (whatsapp, formulario, email, etc.)
        contenido: Contenido original de la solicitud
        productos: Lista de productos extraídos
        urgencia: Nivel de urgencia (normal, alta, urgente)
        usuario_nombre: Nombre del usuario solicitante
        usuario_contacto: Email o teléfono del usuario

    Returns:
        Solicitud creada

    Example:
        >>> productos = [{"nombre": "PLC Siemens", "cantidad": "5", "categoria": "Automatización"}]
        >>> solicitud = crear_solicitud(db, "formulario", "Necesito PLCs", productos, "alta")
    """
    # Determinar categoría principal de los productos
    categoria = productos[0].get("categoria", "General") if productos else "General"

    # Calcular presupuesto total estimado si viene en productos
    presupuesto_total = sum(
        float(p.get("presupuesto_estimado", 0)) for p in productos if p.get("presupuesto_estimado")
    )

    # Crear descripción detallada
    descripcion_productos = "\n".join([
        f"- {p.get('nombre', 'N/A')} (Cant: {p.get('cantidad', 'N/A')})"
        for p in productos
    ])
    descripcion_completa = f"{contenido}\n\nProductos:\n{descripcion_productos}"

    # Mapear urgencia a prioridad numérica
    urgencia_a_prioridad = {
        "normal": 3,
        "alta": 4,
        "urgente": 5,
    }
    prioridad = urgencia_a_prioridad.get(urgencia, 3)

    # Crear solicitud
    solicitud_data = {
        "usuario_nombre": usuario_nombre,
        "usuario_contacto": usuario_contacto,
        "descripcion": descripcion_completa,
        "categoria": categoria,
        "presupuesto": presupuesto_total if presupuesto_total > 0 else None,
        "prioridad": prioridad,
        "urgencia": urgencia,
        "estado": EstadoSolicitud.PENDIENTE,
        "notas_internas": f"Origen: {origen}. Productos detectados: {len(productos)}",
    }

    nueva_solicitud = solicitud.create(db, obj_in=solicitud_data)
    logger.info(f"Solicitud creada: ID={nueva_solicitud.id}, Productos={len(productos)}")

    return nueva_solicitud


def crear_rfq(
    db: Session,
    solicitud_id: int,
    proveedor_id: int,
    contenido: str,
    asunto: str = None,
) -> RFQ:
    """
    Crea un nuevo RFQ con número automático.

    Args:
        db: Sesión de base de datos
        solicitud_id: ID de la solicitud asociada
        proveedor_id: ID del proveedor destinatario
        contenido: Contenido del RFQ generado
        asunto: Asunto del email (opcional, se genera automáticamente)

    Returns:
        RFQ creado

    Example:
        >>> rfq = crear_rfq(db, solicitud_id=1, proveedor_id=5, contenido="Estimado proveedor...")
    """
    # Generar número de RFQ único
    from datetime import datetime

    year = datetime.now().year
    # Contar RFQs de este año
    count = db.query(RFQ).filter(
        RFQ.numero_rfq.like(f"RFQ-{year}-%")
    ).count()
    numero_rfq = f"RFQ-{year}-{count + 1:04d}"

    # Generar asunto si no se proporciona
    if not asunto:
        asunto = f"Solicitud de Cotización - {numero_rfq}"

    # Crear RFQ
    rfq_data = {
        "solicitud_id": solicitud_id,
        "proveedor_id": proveedor_id,
        "numero_rfq": numero_rfq,
        "asunto": asunto,
        "contenido": contenido,
        "estado": EstadoRFQ.BORRADOR,
    }

    nuevo_rfq = rfq.create(db, obj_in=rfq_data)
    logger.info(f"RFQ creado: {numero_rfq}, Proveedor ID={proveedor_id}")

    return nuevo_rfq


def actualizar_estado_solicitud(
    db: Session,
    solicitud_id: int,
    nuevo_estado: str,
) -> Optional[Solicitud]:
    """
    Actualiza el estado de una solicitud.

    Wrapper conveniente para cambiar_estado que acepta strings.

    Args:
        db: Sesión de base de datos
        solicitud_id: ID de la solicitud
        nuevo_estado: Nuevo estado (string: "pendiente", "procesando", "rfqs_enviados", etc.)

    Returns:
        Solicitud actualizada o None si no existe

    Example:
        >>> actualizar_estado_solicitud(db, 1, "procesando")
        >>> actualizar_estado_solicitud(db, 1, "rfqs_enviados")
    """
    # Mapear string a EstadoSolicitud (aceptar variantes)
    estado_map = {
        "pendiente": EstadoSolicitud.PENDIENTE,
        "procesando": EstadoSolicitud.EN_PROCESO,
        "en_proceso": EstadoSolicitud.EN_PROCESO,
        "rfqs_enviados": EstadoSolicitud.EN_PROCESO,  # Mantener como EN_PROCESO
        "cotizaciones_recibidas": EstadoSolicitud.COTIZACIONES_RECIBIDAS,
        "aprobada": EstadoSolicitud.APROBADA,
        "completada": EstadoSolicitud.COMPLETADA,
        "cancelada": EstadoSolicitud.CANCELADA,
        "error": EstadoSolicitud.CANCELADA,  # Mapear error a cancelada
    }

    estado_enum = estado_map.get(nuevo_estado.lower())
    if not estado_enum:
        logger.warning(f"Estado desconocido: {nuevo_estado}, usando PENDIENTE por defecto")
        estado_enum = EstadoSolicitud.PENDIENTE

    return solicitud.cambiar_estado(db, solicitud_id, estado_enum)


# Instancias globales de CRUD
solicitud = CRUDSolicitud(Solicitud)
proveedor = CRUDProveedor(Proveedor)
rfq = CRUDRFQ(RFQ)
cotizacion = CRUDCotizacion(Cotizacion)
orden_compra = CRUDOrdenCompra(OrdenCompra)
envio_tracking = CRUDEnvioTracking(EnvioTracking)
