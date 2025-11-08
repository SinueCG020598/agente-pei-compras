"""
Tests para los modelos de base de datos.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
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


@pytest.fixture
def db_session():
    """Crea una sesión de base de datos de prueba en memoria."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


class TestSolicitudModel:
    """Tests del modelo Solicitud."""

    def test_create_solicitud(self, db_session):
        """Test creación de solicitud con valores por defecto."""
        solicitud = Solicitud(
            usuario_nombre="Juan Pérez",
            usuario_contacto="+56912345678",
            descripcion="Necesito 100 laptops HP",
            categoria="tecnologia",
            presupuesto=150000000,
        )

        db_session.add(solicitud)
        db_session.commit()
        db_session.refresh(solicitud)

        assert solicitud.id is not None
        assert solicitud.usuario_nombre == "Juan Pérez"
        assert solicitud.categoria == "tecnologia"
        assert solicitud.estado == EstadoSolicitud.PENDIENTE
        assert solicitud.created_at is not None
        assert solicitud.updated_at is not None


class TestProveedorModel:
    """Tests del modelo Proveedor."""

    def test_create_proveedor(self, db_session):
        """Test creación de proveedor con valores por defecto."""
        proveedor = Proveedor(
            nombre="Tech Solutions",
            email="ventas@tech.cl",
            categoria="tecnologia",
            pais="Chile",
        )

        db_session.add(proveedor)
        db_session.commit()
        db_session.refresh(proveedor)

        assert proveedor.id is not None
        assert proveedor.nombre == "Tech Solutions"
        assert proveedor.rating == 0.0
        assert proveedor.es_verificado == False
        assert proveedor.created_at is not None


class TestRFQModel:
    """Tests del modelo RFQ."""

    def test_create_rfq(self, db_session):
        """Test creación de RFQ con valores por defecto."""
        # Primero crear solicitud y proveedor
        solicitud = Solicitud(
            usuario_nombre="Juan Pérez",
            usuario_contacto="+56912345678",
            descripcion="Necesito 100 laptops HP",
            categoria="tecnologia",
        )
        proveedor = Proveedor(
            nombre="Tech Solutions",
            email="ventas@tech.cl",
            categoria="tecnologia",
            pais="Chile",
        )

        db_session.add_all([solicitud, proveedor])
        db_session.commit()

        # Ahora crear RFQ
        rfq = RFQ(
            solicitud_id=solicitud.id,
            proveedor_id=proveedor.id,
            numero_rfq="RFQ-2024-001",
            asunto="Solicitud de cotización",
            contenido="Estimado proveedor...",
        )

        db_session.add(rfq)
        db_session.commit()
        db_session.refresh(rfq)

        assert rfq.id is not None
        assert rfq.numero_rfq == "RFQ-2024-001"
        assert rfq.estado == EstadoRFQ.BORRADOR
        assert rfq.created_at is not None
