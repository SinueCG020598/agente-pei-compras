"""
Tests para FASE 4: Generador RFQ + Orquestador + API.

Tests completos que cubren:
1. Generador de RFQ (generación de contenido y envío)
2. Orquestador (flujo completo end-to-end)
3. Endpoints de API
4. Funciones helper de CRUD
5. Integración completa
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from src.agents.generador_rfq import generar_rfq, enviar_rfq, enviar_rfqs_multiples
from src.agents.orquestador import procesar_solicitud_completa, obtener_estado_solicitud
from src.database.crud import crear_solicitud, crear_rfq, actualizar_estado_solicitud
from src.database.models import (
    Solicitud,
    RFQ,
    Proveedor,
    EstadoSolicitud,
    EstadoRFQ,
)
from src.database.session import SessionLocal


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def db_session():
    """Fixture que proporciona una sesión de base de datos."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def proveedor_ejemplo():
    """Fixture con datos de proveedor ejemplo."""
    return {
        "id": 1,
        "nombre": "Aceros del Norte S.A.",
        "contacto": "Ing. María González",
        "email": "ventas@acerosdn.com",
    }


@pytest.fixture
def productos_ejemplo():
    """Fixture con lista de productos ejemplo."""
    return [
        {
            "nombre": "Placas de acero inoxidable 304",
            "cantidad": "50 unidades",
            "especificaciones": "2m x 1m x 3mm de espesor",
            "categoria": "Metales",
        },
        {
            "nombre": "Tubos de acero al carbón",
            "cantidad": "100 metros",
            "especificaciones": "Diámetro 2 pulgadas, Schedule 40",
            "categoria": "Metales",
        },
    ]


@pytest.fixture
def proveedores_multiples():
    """Fixture con múltiples proveedores."""
    return [
        {
            "proveedor_data": {
                "id": 1,
                "nombre": "Proveedor A",
                "email": "a@test.com",
                "contacto": "Juan Pérez",
            },
            "score": 95,
            "productos_asignados": ["Placas de acero inoxidable 304"],
        },
        {
            "proveedor_data": {
                "id": 2,
                "nombre": "Proveedor B",
                "email": "b@test.com",
                "contacto": "Ana López",
            },
            "score": 88,
            "productos_asignados": [],  # Todos los productos
        },
    ]


# =============================================================================
# TESTS DEL GENERADOR RFQ
# =============================================================================


def test_generar_rfq_exitoso(proveedor_ejemplo, productos_ejemplo):
    """Test: generar_rfq genera contenido correctamente."""
    with patch(
        "src.agents.generador_rfq.llamar_agente"
    ) as mock_llamar_agente:
        # Mock de respuesta del agente
        mock_llamar_agente.return_value = """
Estimada Ing. María González,

Reciba un cordial saludo de parte de PEI...

• Placas de acero inoxidable 304
  - Cantidad: 50 unidades
  - Especificaciones: 2m x 1m x 3mm de espesor

Atentamente,
Departamento de Compras
"""

        resultado = generar_rfq(
            solicitud_id=1,
            proveedor=proveedor_ejemplo,
            productos=productos_ejemplo,
            urgencia="normal",
        )

        # Verificaciones
        assert resultado["exito"] is True
        assert "contenido" in resultado
        assert "Estimada Ing. María González" in resultado["contenido"]
        assert "Placas de acero inoxidable 304" in resultado["contenido"]
        assert "fecha_limite" in resultado
        assert isinstance(resultado["fecha_limite"], datetime)

        # Verificar que se llamó al agente con prompt correcto
        mock_llamar_agente.assert_called_once()
        args, kwargs = mock_llamar_agente.call_args
        assert "Genera RFQ profesional" in kwargs["mensaje_usuario"]
        assert proveedor_ejemplo["nombre"] in kwargs["mensaje_usuario"]


def test_generar_rfq_con_urgencia_alta(proveedor_ejemplo, productos_ejemplo):
    """Test: generar_rfq con urgencia alta calcula fecha límite correcta."""
    with patch("src.agents.generador_rfq.llamar_agente") as mock_llamar_agente:
        mock_llamar_agente.return_value = "RFQ generado"

        resultado = generar_rfq(
            solicitud_id=1,
            proveedor=proveedor_ejemplo,
            productos=productos_ejemplo,
            urgencia="alta",
        )

        # Verificar que la fecha límite es aproximadamente 3 días (urgencia alta)
        dias_diferencia = (
            resultado["fecha_limite"] - datetime.now()
        ).days
        assert dias_diferencia >= 2 and dias_diferencia <= 3


def test_generar_rfq_con_urgencia_urgente(proveedor_ejemplo, productos_ejemplo):
    """Test: generar_rfq con urgencia urgente calcula 1 día."""
    with patch("src.agents.generador_rfq.llamar_agente") as mock_llamar_agente:
        mock_llamar_agente.return_value = "RFQ urgente"

        resultado = generar_rfq(
            solicitud_id=1,
            proveedor=proveedor_ejemplo,
            productos=productos_ejemplo,
            urgencia="urgente",
        )

        dias_diferencia = (resultado["fecha_limite"] - datetime.now()).days
        assert dias_diferencia >= 0 and dias_diferencia <= 1


def test_generar_rfq_error_en_agente(proveedor_ejemplo, productos_ejemplo):
    """Test: generar_rfq maneja errores del agente."""
    with patch("src.agents.generador_rfq.llamar_agente") as mock_llamar_agente:
        mock_llamar_agente.side_effect = Exception("Error de OpenAI")

        resultado = generar_rfq(
            solicitud_id=1,
            proveedor=proveedor_ejemplo,
            productos=productos_ejemplo,
        )

        assert resultado["exito"] is False
        assert "error" in resultado
        assert "Error de OpenAI" in resultado["error"]


@pytest.mark.integration
def test_enviar_rfq_flujo_completo(db_session, proveedor_ejemplo, productos_ejemplo):
    """Test integración: enviar_rfq crea RFQ en BD y envía email."""
    # Primero crear una solicitud en BD
    solicitud = Solicitud(
        usuario_nombre="Test User",
        usuario_contacto="test@test.com",
        descripcion="Test solicitud",
        categoria="Metales",
        estado=EstadoSolicitud.PENDIENTE,
    )
    db_session.add(solicitud)
    db_session.commit()

    # Crear proveedor en BD
    prov_bd = Proveedor(
        nombre=proveedor_ejemplo["nombre"],
        email=proveedor_ejemplo["email"],
        categoria="Metales",
    )
    db_session.add(prov_bd)
    db_session.commit()

    # Actualizar el ID en el ejemplo
    proveedor_ejemplo["id"] = prov_bd.id

    with patch("src.agents.generador_rfq.llamar_agente") as mock_agente, patch(
        "src.agents.generador_rfq.email_service.send_email"
    ) as mock_email:
        mock_agente.return_value = "RFQ de prueba"
        mock_email.return_value = True

        resultado = enviar_rfq(
            solicitud_id=solicitud.id,
            proveedor=proveedor_ejemplo,
            productos=productos_ejemplo,
            urgencia="normal",
        )

        # Verificaciones
        assert resultado["exito"] is True
        assert "rfq_id" in resultado
        assert "numero_rfq" in resultado
        assert resultado["proveedor"] == proveedor_ejemplo["nombre"]
        assert resultado["email"] == proveedor_ejemplo["email"]

        # Verificar que se guardó en BD
        rfq_bd = db_session.query(RFQ).filter_by(id=resultado["rfq_id"]).first()
        assert rfq_bd is not None
        assert rfq_bd.estado == EstadoRFQ.ENVIADO  # Debe estar marcado como enviado
        assert rfq_bd.numero_rfq == resultado["numero_rfq"]

        # Verificar que se llamó al servicio de email
        mock_email.assert_called_once()


def test_enviar_rfqs_multiples(
    db_session, proveedores_multiples, productos_ejemplo
):
    """Test: enviar_rfqs_multiples procesa múltiples proveedores."""
    # Crear solicitud
    solicitud = Solicitud(
        usuario_nombre="Test User",
        usuario_contacto="test@test.com",
        descripcion="Test multiple",
        categoria="Metales",
        estado=EstadoSolicitud.PENDIENTE,
    )
    db_session.add(solicitud)
    db_session.commit()

    # Crear proveedores en BD
    for prov_rec in proveedores_multiples:
        prov_data = prov_rec["proveedor_data"]
        prov_bd = Proveedor(
            nombre=prov_data["nombre"],
            email=prov_data["email"],
            categoria="Metales",
        )
        db_session.add(prov_bd)
        db_session.commit()
        prov_data["id"] = prov_bd.id

    with patch("src.agents.generador_rfq.llamar_agente") as mock_agente, patch(
        "src.agents.generador_rfq.email_service.send_email"
    ) as mock_email:
        mock_agente.return_value = "RFQ de prueba"
        mock_email.return_value = True

        resultado = enviar_rfqs_multiples(
            solicitud_id=solicitud.id,
            proveedores_recomendados=proveedores_multiples,
            productos=productos_ejemplo,
            urgencia="normal",
        )

        # Verificaciones
        assert resultado["total"] == 2
        assert resultado["exitosos"] == 2
        assert resultado["fallidos"] == 0
        assert len(resultado["detalles"]) == 2

        # Verificar que se llamó 2 veces al email service
        assert mock_email.call_count == 2


# =============================================================================
# TESTS DE FUNCIONES HELPER DE CRUD
# =============================================================================


@pytest.mark.integration
def test_crear_solicitud_helper(db_session):
    """Test: crear_solicitud helper crea solicitud correctamente."""
    productos = [
        {
            "nombre": "PLC Siemens",
            "cantidad": "5",
            "categoria": "Automatización",
            "presupuesto_estimado": "50000",
        }
    ]

    solicitud = crear_solicitud(
        db=db_session,
        origen="formulario",
        contenido="Necesito PLCs",
        productos=productos,
        urgencia="alta",
    )

    assert solicitud.id is not None
    assert solicitud.categoria == "Automatización"
    assert solicitud.urgencia == "alta"
    assert solicitud.prioridad == 4  # Alta = 4
    assert "PLC Siemens" in solicitud.descripcion
    assert solicitud.estado == EstadoSolicitud.PENDIENTE


@pytest.mark.integration
def test_crear_rfq_helper(db_session):
    """Test: crear_rfq helper genera número automático."""
    # Crear solicitud
    solicitud = Solicitud(
        usuario_nombre="Test",
        usuario_contacto="test@test.com",
        descripcion="Test",
        categoria="General",
        estado=EstadoSolicitud.PENDIENTE,
    )
    db_session.add(solicitud)

    # Crear proveedor
    proveedor = Proveedor(
        nombre="Test Proveedor", email="prov@test.com", categoria="General"
    )
    db_session.add(proveedor)
    db_session.commit()

    # Crear RFQ
    rfq = crear_rfq(
        db=db_session,
        solicitud_id=solicitud.id,
        proveedor_id=proveedor.id,
        contenido="Contenido RFQ de prueba",
    )

    assert rfq.id is not None
    assert rfq.numero_rfq.startswith(f"RFQ-{datetime.now().year}-")
    assert rfq.estado == EstadoRFQ.BORRADOR
    assert rfq.contenido == "Contenido RFQ de prueba"
    assert rfq.solicitud_id == solicitud.id
    assert rfq.proveedor_id == proveedor.id


@pytest.mark.integration
def test_actualizar_estado_solicitud_helper(db_session):
    """Test: actualizar_estado_solicitud actualiza correctamente."""
    solicitud = Solicitud(
        usuario_nombre="Test",
        usuario_contacto="test@test.com",
        descripcion="Test",
        categoria="General",
        estado=EstadoSolicitud.PENDIENTE,
    )
    db_session.add(solicitud)
    db_session.commit()

    # Actualizar a procesando
    actualizada = actualizar_estado_solicitud(db_session, solicitud.id, "procesando")

    assert actualizada is not None
    assert actualizada.estado == EstadoSolicitud.EN_PROCESO

    # Actualizar a rfqs_enviados (debe mapear a EN_PROCESO)
    actualizada = actualizar_estado_solicitud(db_session, solicitud.id, "rfqs_enviados")
    assert actualizada.estado == EstadoSolicitud.EN_PROCESO


# =============================================================================
# TESTS DEL ORQUESTADOR
# =============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orquestador_flujo_completo_mock(db_session):
    """Test: orquestador completo con mocks (sin llamadas reales a APIs)."""
    texto_solicitud = "Necesito 5 PLCs Siemens S7-1200 urgente"

    # Crear proveedor en BD
    proveedor = Proveedor(
        nombre="TechSupply", email="ventas@tech.com", categoria="Automatización"
    )
    db_session.add(proveedor)
    db_session.commit()

    with patch("src.agents.receptor.procesar_solicitud") as mock_receptor, patch(
        "src.agents.investigador.buscar_proveedores"
    ) as mock_investigador, patch(
        "src.agents.generador_rfq.llamar_agente"
    ) as mock_agente, patch(
        "src.agents.generador_rfq.email_service.send_email"
    ) as mock_email:
        # Mock Receptor
        mock_receptor.return_value = {
            "exito": True,
            "productos": [
                {"nombre": "PLC Siemens S7-1200", "cantidad": "5", "categoria": "Automatización"}
            ],
            "urgencia": "urgente",
        }

        # Mock Investigador
        mock_investigador.return_value = {
            "proveedores_recomendados": [
                {
                    "proveedor_data": {
                        "id": proveedor.id,
                        "nombre": "TechSupply",
                        "email": "ventas@tech.com",
                        "contacto": "Ing. Carlos",
                    },
                    "score": 95,
                }
            ]
        }

        # Mock Generador RFQ
        mock_agente.return_value = "RFQ generado por IA"
        mock_email.return_value = True

        # Ejecutar orquestador
        resultado = await procesar_solicitud_completa(texto_solicitud, "formulario")

        # Verificaciones
        assert resultado["exito"] is True
        assert resultado["etapa"] == "completado"
        assert "solicitud_id" in resultado
        assert resultado["rfqs"]["exitosos"] == 1
        assert resultado["rfqs"]["total"] == 1

        # Verificar que se llamaron todos los agentes
        mock_receptor.assert_called_once()
        mock_investigador.assert_called_once()
        mock_agente.assert_called_once()
        mock_email.assert_called_once()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orquestador_falla_en_receptor():
    """Test: orquestador maneja error en receptor."""
    with patch("src.agents.receptor.procesar_solicitud") as mock_receptor:
        mock_receptor.return_value = {
            "exito": False,
            "error": "No se pudo procesar la solicitud",
        }

        resultado = await procesar_solicitud_completa("texto invalido", "formulario")

        assert resultado["exito"] is False
        assert resultado["etapa"] == "receptor"
        assert "error" in resultado


@pytest.mark.integration
@pytest.mark.asyncio
async def test_orquestador_sin_proveedores(db_session):
    """Test: orquestador maneja caso sin proveedores encontrados."""
    with patch("src.agents.receptor.procesar_solicitud") as mock_receptor, patch(
        "src.agents.investigador.buscar_proveedores"
    ) as mock_investigador:
        mock_receptor.return_value = {
            "exito": True,
            "productos": [{"nombre": "Producto raro", "cantidad": "1"}],
            "urgencia": "normal",
        }

        mock_investigador.return_value = {
            "proveedores_recomendados": []  # Sin proveedores
        }

        resultado = await procesar_solicitud_completa("texto", "formulario")

        assert resultado["exito"] is False
        assert "No se encontraron proveedores" in resultado["error"]


@pytest.mark.integration
def test_obtener_estado_solicitud(db_session):
    """Test: obtener_estado_solicitud retorna estado correcto."""
    # Crear solicitud
    solicitud = Solicitud(
        usuario_nombre="Test",
        usuario_contacto="test@test.com",
        descripcion="Test estado",
        categoria="General",
        estado=EstadoSolicitud.EN_PROCESO,
        urgencia="alta",
    )
    db_session.add(solicitud)
    db_session.commit()

    estado = obtener_estado_solicitud(solicitud.id)

    assert estado["solicitud_id"] == solicitud.id
    assert estado["estado"] == "en_proceso"
    assert estado["urgencia"] == "alta"
    assert "rfqs_enviados" in estado
    assert "cotizaciones_recibidas" in estado


def test_obtener_estado_solicitud_inexistente():
    """Test: obtener_estado_solicitud con ID inexistente."""
    estado = obtener_estado_solicitud(999999)

    assert "error" in estado
    assert estado["solicitud_id"] == 999999


# =============================================================================
# TESTS DE ENDPOINT API (requiere FastAPI TestClient)
# =============================================================================


@pytest.mark.integration
def test_endpoint_procesar_completa():
    """Test: endpoint /solicitud/procesar-completa funciona."""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    with patch("main.procesar_solicitud_completa") as mock_procesar:
        # Mock del orquestador
        mock_procesar.return_value = {
            "exito": True,
            "etapa": "completado",
            "solicitud_id": 123,
            "rfqs": {"total": 3, "exitosos": 3, "fallidos": 0},
        }

        response = client.post(
            "/solicitud/procesar-completa",
            json={"texto": "Necesito PLCs", "origen": "api"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["solicitud_id"] == 123
        assert data["rfqs_enviados"] == 3


@pytest.mark.integration
def test_endpoint_procesar_completa_error():
    """Test: endpoint maneja errores correctamente."""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    with patch("main.procesar_solicitud_completa") as mock_procesar:
        mock_procesar.return_value = {
            "exito": False,
            "etapa": "investigador",
            "error": "No se encontraron proveedores",
        }

        response = client.post(
            "/solicitud/procesar-completa",
            json={"texto": "texto invalido", "origen": "api"},
        )

        assert response.status_code == 400
        assert "error" in response.json()["detail"]


@pytest.mark.integration
def test_endpoint_consultar_estado():
    """Test: endpoint GET /solicitud/{id}/estado funciona."""
    from fastapi.testclient import TestClient
    from main import app

    client = TestClient(app)

    with patch("main.obtener_estado_solicitud") as mock_estado:
        mock_estado.return_value = {
            "solicitud_id": 123,
            "estado": "en_proceso",
            "rfqs_enviados": 3,
            "rfqs_respondidos": 1,
        }

        response = client.get("/solicitud/123/estado")

        assert response.status_code == 200
        data = response.json()
        assert data["solicitud_id"] == 123
        assert data["estado"] == "en_proceso"


# =============================================================================
# RESUMEN DE COBERTURA
# =============================================================================

"""
Resumen de tests creados para FASE 4:

GENERADOR RFQ:
✓ test_generar_rfq_exitoso
✓ test_generar_rfq_con_urgencia_alta
✓ test_generar_rfq_con_urgencia_urgente
✓ test_generar_rfq_error_en_agente
✓ test_enviar_rfq_flujo_completo
✓ test_enviar_rfqs_multiples

CRUD HELPERS:
✓ test_crear_solicitud_helper
✓ test_crear_rfq_helper
✓ test_actualizar_estado_solicitud_helper

ORQUESTADOR:
✓ test_orquestador_flujo_completo_mock
✓ test_orquestador_falla_en_receptor
✓ test_orquestador_sin_proveedores
✓ test_obtener_estado_solicitud
✓ test_obtener_estado_solicitud_inexistente

API ENDPOINTS:
✓ test_endpoint_procesar_completa
✓ test_endpoint_procesar_completa_error
✓ test_endpoint_consultar_estado

TOTAL: 17 tests creados
Cobertura estimada: >85%
"""
