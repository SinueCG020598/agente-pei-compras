"""
Modelos de base de datos para el sistema PEI Compras AI.

Este módulo define todos los modelos SQLAlchemy que representan
las entidades principales del sistema de compras.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Enum,
    ForeignKey,
    Boolean,
    JSON,
)
from sqlalchemy.orm import relationship
import enum

from src.database.base import Base


class EstadoSolicitud(str, enum.Enum):
    """Estados posibles de una solicitud de compra."""

    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COTIZACIONES_RECIBIDAS = "cotizaciones_recibidas"
    APROBADA = "aprobada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class EstadoRFQ(str, enum.Enum):
    """Estados posibles de un RFQ (Request for Quotation)."""

    BORRADOR = "borrador"
    ENVIADO = "enviado"
    RESPONDIDO = "respondido"
    IGNORADO = "ignorado"
    EXPIRADO = "expirado"


class EstadoOrdenCompra(str, enum.Enum):
    """Estados posibles de una orden de compra."""

    BORRADOR = "borrador"
    ENVIADA = "enviada"
    CONFIRMADA = "confirmada"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class EstadoEnvio(str, enum.Enum):
    """Estados posibles de un envío."""

    PENDIENTE = "pendiente"
    EN_TRANSITO = "en_transito"
    EN_ADUANA = "en_aduana"
    EN_DISTRIBUCION = "en_distribucion"
    EN_ENTREGA = "en_entrega"
    ENTREGADO = "entregado"
    DEVUELTO = "devuelto"
    CANCELADO = "cancelado"


class Solicitud(Base):
    """
    Modelo de Solicitud de Compra.

    Representa una solicitud de compra iniciada por un usuario,
    ya sea desde WhatsApp o el formulario web.

    Attributes:
        id: Identificador único
        usuario_id: ID del usuario que hace la solicitud
        usuario_nombre: Nombre del usuario
        usuario_contacto: Email o teléfono del usuario
        descripcion: Descripción detallada de lo que se necesita
        categoria: Categoría del producto/servicio
        cantidad: Cantidad solicitada (opcional)
        presupuesto: Presupuesto máximo disponible
        fecha_limite: Fecha límite para recibir el producto
        prioridad: Nivel de prioridad (1=baja, 5=alta)
        estado: Estado actual de la solicitud
        notas_internas: Notas adicionales del sistema
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "solicitudes"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(String(100), nullable=True, index=True)
    usuario_nombre = Column(String(200), nullable=False)
    usuario_contacto = Column(String(200), nullable=False)  # Email o teléfono

    # Detalles de la solicitud
    descripcion = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False, index=True)
    cantidad = Column(String(100), nullable=True)  # Ej: "100 unidades", "5 cajas"
    presupuesto = Column(Float, nullable=True)
    fecha_limite = Column(DateTime, nullable=True)
    prioridad = Column(Integer, default=3)  # 1-5
    urgencia = Column(String(20), default="normal")  # normal, alta, urgente

    # Estado y tracking
    estado = Column(
        Enum(EstadoSolicitud),
        default=EstadoSolicitud.PENDIENTE,
        nullable=False,
        index=True,
    )
    notas_internas = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    rfqs = relationship("RFQ", back_populates="solicitud", cascade="all, delete-orphan")
    ordenes_compra = relationship(
        "OrdenCompra", back_populates="solicitud", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<Solicitud(id={self.id}, categoria={self.categoria}, estado={self.estado})>"


class Proveedor(Base):
    """
    Modelo de Proveedor.

    Representa un proveedor que puede cotizar productos/servicios.

    Attributes:
        id: Identificador único
        nombre: Nombre del proveedor
        razon_social: Razón social legal
        rut: RUT/NIT del proveedor
        email: Email principal de contacto
        telefono: Teléfono de contacto
        direccion: Dirección física
        ciudad: Ciudad
        pais: País
        sitio_web: URL del sitio web
        categoria: Categoría principal de productos/servicios
        subcategorias: Subcategorías adicionales (JSON)
        rating: Calificación promedio (0-5)
        es_verificado: Si el proveedor está verificado
        notas: Notas adicionales sobre el proveedor
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "proveedores"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    razon_social = Column(String(200), nullable=True)
    rut = Column(String(50), nullable=True, unique=True, index=True)

    # Contacto
    email = Column(String(200), nullable=False, index=True)
    telefono = Column(String(50), nullable=True)
    direccion = Column(String(300), nullable=True)
    ciudad = Column(String(100), nullable=True, index=True)
    pais = Column(String(100), default="Chile", nullable=False)
    sitio_web = Column(String(300), nullable=True)

    # Categorización
    categoria = Column(String(100), nullable=False, index=True)
    subcategorias = Column(Text, nullable=True)  # JSON array de subcategorías

    # Calificación y verificación
    rating = Column(Float, default=0.0, nullable=False)
    es_verificado = Column(Boolean, default=False, nullable=False)
    notas = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    rfqs = relationship("RFQ", back_populates="proveedor", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<Proveedor(id={self.id}, nombre={self.nombre}, categoria={self.categoria})>"


class RFQ(Base):
    """
    Modelo de RFQ (Request for Quotation).

    Representa una solicitud de cotización enviada a un proveedor.

    Attributes:
        id: Identificador único
        solicitud_id: ID de la solicitud relacionada
        proveedor_id: ID del proveedor al que se envía
        contenido: Contenido del RFQ generado por IA
        asunto: Asunto del email
        estado: Estado actual del RFQ
        fecha_envio: Fecha en que se envió
        fecha_respuesta: Fecha de respuesta del proveedor
        numero_rfq: Número único de RFQ (ej: RFQ-2024-001)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "rfqs"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False, index=True)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"), nullable=False, index=True)

    # Contenido del RFQ
    numero_rfq = Column(String(50), unique=True, nullable=False, index=True)
    asunto = Column(String(300), nullable=False)
    contenido = Column(Text, nullable=False)

    # Estado y tracking
    estado = Column(
        Enum(EstadoRFQ), default=EstadoRFQ.BORRADOR, nullable=False, index=True
    )
    fecha_envio = Column(DateTime, nullable=True)
    fecha_respuesta = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="rfqs")
    proveedor = relationship("Proveedor", back_populates="rfqs")
    cotizaciones = relationship(
        "Cotizacion", back_populates="rfq", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<RFQ(id={self.id}, numero={self.numero_rfq}, estado={self.estado})>"


class Cotizacion(Base):
    """
    Modelo de Cotización.

    Representa una cotización recibida de un proveedor en respuesta a un RFQ.

    Attributes:
        id: Identificador único
        rfq_id: ID del RFQ relacionado
        precio_total: Precio total cotizado
        precio_unitario: Precio por unidad (opcional)
        moneda: Moneda de la cotización
        tiempo_entrega: Tiempo de entrega en días
        condiciones_pago: Condiciones de pago
        garantia: Información sobre garantía
        observaciones: Observaciones adicionales del proveedor
        archivo_adjunto: URL o path del archivo adjunto
        archivo_nombre: Nombre original del archivo
        es_valida: Si la cotización es válida
        puntaje_ia: Puntaje asignado por IA (0-100)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "cotizaciones"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"), nullable=False, index=True)

    # Información de precios
    precio_total = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=True)
    moneda = Column(String(10), default="CLP", nullable=False)

    # Condiciones
    tiempo_entrega = Column(Integer, nullable=True)  # En días
    condiciones_pago = Column(String(300), nullable=True)
    garantia = Column(String(300), nullable=True)
    observaciones = Column(Text, nullable=True)

    # Archivo adjunto
    archivo_adjunto = Column(String(500), nullable=True)
    archivo_nombre = Column(String(200), nullable=True)

    # Validación y scoring
    es_valida = Column(Boolean, default=True, nullable=False)
    puntaje_ia = Column(Float, nullable=True)  # 0-100

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    rfq = relationship("RFQ", back_populates="cotizaciones")
    ordenes_compra = relationship(
        "OrdenCompra", back_populates="cotizacion", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<Cotizacion(id={self.id}, rfq_id={self.rfq_id}, precio={self.precio_total})>"


class OrdenCompra(Base):
    """
    Modelo de Orden de Compra.

    Representa una orden de compra generada después de seleccionar
    la mejor cotización.

    Attributes:
        id: Identificador único
        solicitud_id: ID de la solicitud original
        cotizacion_id: ID de la cotización seleccionada
        numero_orden: Número único de la orden (ej: OC-2024-001)
        estado: Estado actual de la orden
        monto_total: Monto total de la orden
        moneda: Moneda de la orden
        fecha_emision: Fecha de emisión de la orden
        fecha_entrega_esperada: Fecha esperada de entrega
        fecha_entrega_real: Fecha real de entrega
        condiciones: Condiciones de la orden
        observaciones: Observaciones adicionales
        archivo_oc: URL o path del PDF de la OC
        aprobado_por: Nombre de quien aprobó la orden
        fecha_aprobacion: Fecha de aprobación
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "ordenes_compra"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    solicitud_id = Column(Integer, ForeignKey("solicitudes.id"), nullable=False, index=True)
    cotizacion_id = Column(
        Integer, ForeignKey("cotizaciones.id"), nullable=False, index=True
    )

    # Identificación
    numero_orden = Column(String(50), unique=True, nullable=False, index=True)

    # Estado y montos
    estado = Column(
        Enum(EstadoOrdenCompra),
        default=EstadoOrdenCompra.BORRADOR,
        nullable=False,
        index=True,
    )
    monto_total = Column(Float, nullable=False)
    moneda = Column(String(10), default="CLP", nullable=False)

    # Fechas
    fecha_emision = Column(DateTime, nullable=True)
    fecha_entrega_esperada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)

    # Detalles
    condiciones = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)

    # Archivo de la orden
    archivo_oc = Column(String(500), nullable=True)

    # Aprobación
    aprobado_por = Column(String(200), nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relaciones
    solicitud = relationship("Solicitud", back_populates="ordenes_compra")
    cotizacion = relationship("Cotizacion", back_populates="ordenes_compra")
    envio_tracking = relationship(
        "EnvioTracking", back_populates="orden_compra", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<OrdenCompra(id={self.id}, numero={self.numero_orden}, estado={self.estado})>"


class EnvioTracking(Base):
    """
    Modelo de Tracking de Envío.

    Representa el seguimiento de un envío asociado a una orden de compra.

    Attributes:
        id: Identificador único
        orden_compra_id: ID de la orden de compra relacionada
        estado: Estado actual del envío
        tracking_number: Número de seguimiento del paquete
        proveedor_envio: Nombre del proveedor de envío (DHL, FedEx, etc.)
        fecha_envio: Fecha en que se envió el paquete
        fecha_entrega_estimada: Fecha estimada de entrega
        fecha_entrega_real: Fecha real de entrega
        ubicacion_actual: Ubicación actual del paquete
        ciudad_origen: Ciudad de origen del envío
        ciudad_destino: Ciudad de destino del envío
        notas: Notas adicionales sobre el envío
        eventos: JSON con historial de eventos de tracking
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
    """

    __tablename__ = "envios_tracking"

    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    orden_compra_id = Column(
        Integer, ForeignKey("ordenes_compra.id"), nullable=False, unique=True, index=True
    )

    # Información del envío
    estado = Column(
        Enum(EstadoEnvio),
        default=EstadoEnvio.PENDIENTE,
        nullable=False,
        index=True,
    )
    tracking_number = Column(String(100), nullable=True, index=True)
    proveedor_envio = Column(String(100), nullable=True)  # DHL, FedEx, Estafeta, etc.

    # Fechas
    fecha_envio = Column(DateTime, nullable=True)
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)

    # Ubicación
    ubicacion_actual = Column(String(300), nullable=True)
    ciudad_origen = Column(String(100), nullable=True)
    ciudad_destino = Column(String(100), nullable=True)

    # Información adicional
    notas = Column(Text, nullable=True)
    eventos = Column(JSON, nullable=True)  # Historial de eventos de tracking

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relación
    orden_compra = relationship("OrdenCompra", back_populates="envio_tracking")

    def __repr__(self) -> str:
        """Representación en string del modelo."""
        return f"<EnvioTracking(id={self.id}, orden_id={self.orden_compra_id}, estado={self.estado})>"
