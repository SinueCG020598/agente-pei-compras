"""
Tests para el Agente Receptor.

Tests unitarios y de integración para validar el procesamiento
de solicitudes de compra mediante IA.
"""
import pytest
from unittest.mock import Mock, patch

from src.agents.receptor import (
    ReceptorAgent,
    procesar_solicitud,
    validar_solicitud,
    SolicitudProcesada,
    ProductoExtraido,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def agente_receptor():
    """Fixture que proporciona una instancia del agente receptor."""
    return ReceptorAgent()


@pytest.fixture
def solicitud_simple():
    """Fixture con una solicitud simple."""
    return "Necesito 5 laptops HP para el equipo de ventas"


@pytest.fixture
def solicitud_compleja():
    """Fixture con una solicitud compleja con múltiples productos."""
    return """Hola! Necesitamos urgente 10 escritorios ejecutivos y 10 sillas
    ergonómicas para la nueva oficina. También 2 impresoras láser multifunción.
    Tenemos un presupuesto de 8 millones. Es para este viernes!"""


@pytest.fixture
def solicitud_informal():
    """Fixture con una solicitud informal."""
    return "oye necesito unas sillas pa la sala de reuniones, como 6 o 7, nada muy caro, pa la prox semana porfa"


# =============================================================================
# TESTS DE VALIDACIÓN
# =============================================================================


def test_validar_solicitud_valida():
    """Test validación de solicitud válida."""
    solicitud = {
        "productos": [
            {
                "nombre": "Laptop HP",
                "cantidad": 5,
                "categoria": "tecnologia",
                "especificaciones": "Para equipo de ventas",
            }
        ],
        "urgencia": "normal",
        "presupuesto_estimado": 5000000.0,
        "notas_adicionales": "Test",
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is True
    assert error == ""


def test_validar_solicitud_sin_productos():
    """Test validación falla cuando no hay productos."""
    solicitud = {
        "productos": [],
        "urgencia": "normal",
        "presupuesto_estimado": None,
        "notas_adicionales": "",
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is False
    assert "al menos un producto" in error.lower()


def test_validar_solicitud_sin_nombre_producto():
    """Test validación falla cuando un producto no tiene nombre."""
    solicitud = {
        "productos": [
            {"nombre": "", "cantidad": 5, "categoria": "tecnologia", "especificaciones": ""}
        ],
        "urgencia": "normal",
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is False
    assert "nombre" in error.lower()


def test_validar_solicitud_cantidad_invalida():
    """Test validación falla con cantidad inválida."""
    solicitud = {
        "productos": [
            {
                "nombre": "Laptop",
                "cantidad": 0,
                "categoria": "tecnologia",
                "especificaciones": "",
            }
        ],
        "urgencia": "normal",
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is False
    assert "cantidad" in error.lower()


def test_validar_solicitud_urgencia_invalida():
    """Test validación falla con urgencia inválida."""
    solicitud = {
        "productos": [
            {
                "nombre": "Laptop",
                "cantidad": 5,
                "categoria": "tecnologia",
                "especificaciones": "",
            }
        ],
        "urgencia": "super_urgente",  # Inválida
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is False
    assert "urgencia" in error.lower()


def test_validar_solicitud_presupuesto_negativo():
    """Test validación falla con presupuesto negativo."""
    solicitud = {
        "productos": [
            {
                "nombre": "Laptop",
                "cantidad": 5,
                "categoria": "tecnologia",
                "especificaciones": "",
            }
        ],
        "urgencia": "normal",
        "presupuesto_estimado": -1000,
    }

    es_valida, error = validar_solicitud(solicitud)

    assert es_valida is False
    assert "presupuesto" in error.lower()


# =============================================================================
# TESTS DE MODELOS PYDANTIC
# =============================================================================


def test_producto_extraido_valido():
    """Test creación de ProductoExtraido válido."""
    producto = ProductoExtraido(
        nombre="Laptop HP",
        cantidad=5,
        categoria="tecnologia",
        especificaciones="16GB RAM, i7",
    )

    assert producto.nombre == "Laptop HP"
    assert producto.cantidad == 5
    assert producto.categoria == "tecnologia"
    assert producto.especificaciones == "16GB RAM, i7"


def test_producto_extraido_categoria_invalida():
    """Test que categoría inválida se convierte a 'otros'."""
    producto = ProductoExtraido(
        nombre="Producto raro",
        cantidad=1,
        categoria="categoria_inexistente",
        especificaciones="",
    )

    assert producto.categoria == "otros"


def test_producto_extraido_cantidad_default():
    """Test que cantidad por defecto es 1."""
    producto = ProductoExtraido(
        nombre="Producto", categoria="tecnologia", especificaciones=""
    )

    assert producto.cantidad == 1


def test_solicitud_procesada_valida():
    """Test creación de SolicitudProcesada válida."""
    solicitud = SolicitudProcesada(
        productos=[
            ProductoExtraido(
                nombre="Laptop", cantidad=5, categoria="tecnologia", especificaciones=""
            )
        ],
        urgencia="alta",
        presupuesto_estimado=5000000.0,
        notas_adicionales="Test",
    )

    assert len(solicitud.productos) == 1
    assert solicitud.urgencia == "alta"
    assert solicitud.presupuesto_estimado == 5000000.0


def test_solicitud_procesada_urgencia_invalida():
    """Test que urgencia inválida se convierte a 'normal'."""
    solicitud = SolicitudProcesada(
        productos=[
            ProductoExtraido(
                nombre="Laptop", cantidad=5, categoria="tecnologia", especificaciones=""
            )
        ],
        urgencia="mega_urgente",  # Inválida
    )

    assert solicitud.urgencia == "normal"


# =============================================================================
# TESTS DE INTEGRACIÓN CON OPENAI (MOCKEADOS)
# =============================================================================


@patch("src.agents.receptor.OpenAI")
def test_procesar_solicitud_simple_mock(mock_openai_class, solicitud_simple):
    """Test procesamiento de solicitud simple (con mock)."""
    # Configurar mock
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    # Crear mock con estructura correcta
    mock_message = Mock()
    mock_message.content = """{
        "productos": [
            {
                "nombre": "Laptop HP para equipo de ventas",
                "cantidad": 5,
                "categoria": "tecnologia",
                "especificaciones": "Marca: HP, para uso de equipo de ventas"
            }
        ],
        "urgencia": "normal",
        "presupuesto_estimado": null,
        "notas_adicionales": "Solicitud para equipo de ventas"
    }"""

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    # Ejecutar
    agente = ReceptorAgent()
    resultado = agente.procesar_solicitud(solicitud_simple)

    # Verificar
    assert "productos" in resultado
    assert len(resultado["productos"]) == 1
    assert resultado["productos"][0]["nombre"] == "Laptop HP para equipo de ventas"
    assert resultado["productos"][0]["cantidad"] == 5
    assert resultado["productos"][0]["categoria"] == "tecnologia"
    assert resultado["urgencia"] == "normal"


@patch("src.agents.receptor.OpenAI")
def test_procesar_solicitud_compleja_mock(mock_openai_class, solicitud_compleja):
    """Test procesamiento de solicitud compleja (con mock)."""
    # Configurar mock
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    # Crear mock con estructura correcta
    mock_message = Mock()
    mock_message.content = """{
        "productos": [
            {
                "nombre": "Escritorio ejecutivo",
                "cantidad": 10,
                "categoria": "mobiliario",
                "especificaciones": "Tipo: Ejecutivo, para nueva oficina"
            },
            {
                "nombre": "Silla ergonómica",
                "cantidad": 10,
                "categoria": "mobiliario",
                "especificaciones": "Tipo: Ergonómica, para nueva oficina"
            },
            {
                "nombre": "Impresora láser multifunción",
                "cantidad": 2,
                "categoria": "tecnologia",
                "especificaciones": "Tipo: Láser multifunción"
            }
        ],
        "urgencia": "urgente",
        "presupuesto_estimado": 8000000.0,
        "notas_adicionales": "Requerido para este viernes, nueva oficina"
    }"""

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    # Ejecutar
    agente = ReceptorAgent()
    resultado = agente.procesar_solicitud(solicitud_compleja)

    # Verificar
    assert len(resultado["productos"]) == 3
    assert resultado["urgencia"] == "urgente"
    assert resultado["presupuesto_estimado"] == 8000000.0


@patch("src.agents.receptor.OpenAI")
def test_procesar_solicitud_informal_mock(mock_openai_class, solicitud_informal):
    """Test procesamiento de solicitud informal (con mock)."""
    # Configurar mock
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    # Crear mock con estructura correcta
    mock_message = Mock()
    mock_message.content = """{
        "productos": [
            {
                "nombre": "Silla para sala de reuniones",
                "cantidad": 7,
                "categoria": "mobiliario",
                "especificaciones": "Para sala de reuniones, rango económico"
            }
        ],
        "urgencia": "alta",
        "presupuesto_estimado": null,
        "notas_adicionales": "Solicitud informal, presupuesto ajustado, requerido para próxima semana"
    }"""

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    # Ejecutar
    agente = ReceptorAgent()
    resultado = agente.procesar_solicitud(solicitud_informal, origen="whatsapp")

    # Verificar
    assert len(resultado["productos"]) == 1
    assert resultado["productos"][0]["cantidad"] == 7
    assert resultado["urgencia"] == "alta"


# =============================================================================
# TESTS DE MANEJO DE ERRORES
# =============================================================================


def test_procesar_solicitud_texto_vacio():
    """Test que falla con texto vacío."""
    agente = ReceptorAgent()

    with pytest.raises(ValueError, match="vacío"):
        agente.procesar_solicitud("")


def test_procesar_solicitud_texto_none():
    """Test que falla con texto None."""
    agente = ReceptorAgent()

    with pytest.raises(ValueError, match="vacío"):
        agente.procesar_solicitud(None)


@patch("src.agents.receptor.OpenAI")
def test_procesar_solicitud_openai_error(mock_openai_class):
    """Test manejo de error de OpenAI."""
    # Configurar mock para lanzar error
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    from openai import OpenAIError

    mock_client.chat.completions.create.side_effect = OpenAIError("API Error")

    # Ejecutar y verificar error
    agente = ReceptorAgent()

    with pytest.raises(OpenAIError):
        agente.procesar_solicitud("Necesito laptops")


@patch("src.agents.receptor.OpenAI")
def test_procesar_solicitud_respuesta_invalida(mock_openai_class):
    """Test manejo de respuesta JSON inválida."""
    # Configurar mock con respuesta no JSON
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    # Crear mock con estructura correcta pero contenido inválido
    mock_message = Mock()
    mock_message.content = "Esto no es JSON válido"

    mock_choice = Mock()
    mock_choice.message = mock_message

    mock_response = Mock()
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    # Ejecutar y verificar error
    agente = ReceptorAgent()

    with pytest.raises(ValueError, match="JSON válido"):
        agente.procesar_solicitud("Necesito laptops")


# =============================================================================
# TESTS DE INTEGRACIÓN COMPLETOS (REQUIEREN API KEY)
# =============================================================================
# Nota: Para ejecutar tests de integración con la API real de OpenAI:
# pytest tests/test_agente_receptor.py -m integration -v
#
# Estos tests están deshabilitados por defecto para evitar consumir créditos
# de la API en cada ejecución de tests.


@pytest.mark.integration
@pytest.mark.skip(reason="Test de integración con OpenAI API - ejecutar manualmente")
def test_procesar_solicitud_simple_integracion(solicitud_simple):
    """
    Test de integración real con OpenAI API.

    Este test requiere una API key válida y consumirá créditos.
    Para ejecutarlo manualmente: pytest -m integration --runxfail
    """
    resultado = procesar_solicitud(solicitud_simple)

    # Verificar estructura
    assert "productos" in resultado
    assert len(resultado["productos"]) > 0

    # Verificar primer producto
    producto = resultado["productos"][0]
    assert "laptop" in producto["nombre"].lower() or "hp" in producto["nombre"].lower()
    assert producto["cantidad"] >= 5
    assert producto["categoria"] in [
        "tecnologia",
        "equipamiento",
        "otros",
    ]


@pytest.mark.integration
@pytest.mark.skip(reason="Test de integración con OpenAI API - ejecutar manualmente")
def test_procesar_solicitud_compleja_integracion(solicitud_compleja):
    """
    Test de integración real con solicitud compleja.

    Este test requiere una API key válida y consumirá créditos.
    Para ejecutarlo manualmente: pytest -m integration --runxfail
    """
    resultado = procesar_solicitud(solicitud_compleja)

    # Verificar múltiples productos
    assert len(resultado["productos"]) >= 3

    # Verificar urgencia detectada
    assert resultado["urgencia"] in ["alta", "urgente"]

    # Verificar presupuesto
    assert resultado["presupuesto_estimado"] is not None
