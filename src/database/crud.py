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
    EstadoSolicitud,
    EstadoRFQ,
    EstadoOrdenCompra,
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


# Instancias globales de CRUD
solicitud = CRUDSolicitud(Solicitud)
proveedor = CRUDProveedor(Proveedor)
rfq = CRUDRFQ(RFQ)
cotizacion = CRUDCotizacion(Cotizacion)
orden_compra = CRUDOrdenCompra(OrdenCompra)
