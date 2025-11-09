"""
Tests para el servicio de OpenAI.
"""
import json
from unittest.mock import Mock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice

from src.services.openai_service import (
    OpenAIService,
    SolicitudAnalizada,
    CotizacionAnalizada,
)


@pytest.fixture
def openai_service():
    """Fixture que retorna una instancia del servicio OpenAI."""
    return OpenAIService(api_key="test-key-123")


@pytest.fixture
def mock_openai_response():
    """Fixture que crea una respuesta mock de OpenAI."""

    def _create_response(content: str) -> ChatCompletion:
        """Crea una respuesta mock con el contenido dado."""
        return ChatCompletion(
            id="test-123",
            object="chat.completion",
            created=1234567890,
            model="gpt-4o-mini",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content=content,
                    ),
                    finish_reason="stop",
                )
            ],
        )

    return _create_response


class TestOpenAIService:
    """Tests para la clase OpenAIService."""

    def test_init(self, openai_service):
        """Test inicialización del servicio."""
        assert openai_service.api_key == "test-key-123"
        assert openai_service.model_mini == "gpt-4o-mini"
        assert openai_service.model_full == "gpt-4o"
        assert openai_service.client is not None

    def test_analizar_solicitud(self, openai_service, mock_openai_response):
        """Test análisis de solicitud."""
        # Preparar respuesta mock
        response_data = {
            "productos": ["Laptop HP", "Mouse"],
            "cantidad_estimada": 50,
            "categoria": "tecnologia",
            "presupuesto_estimado": 50000000.0,
            "urgencia": "alta",
            "especificaciones": ["16GB RAM", "SSD 512GB"],
            "keywords": ["laptop", "hp", "tecnologia"],
        }
        mock_response = mock_openai_response(json.dumps(response_data))

        # Mock del cliente OpenAI
        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            resultado = openai_service.analizar_solicitud(
                descripcion="Necesito 50 laptops HP con 16GB RAM",
                usuario_nombre="Juan Pérez",
            )

        # Verificaciones
        assert isinstance(resultado, SolicitudAnalizada)
        assert resultado.categoria == "tecnologia"
        assert resultado.urgencia == "alta"
        assert len(resultado.productos) == 2
        assert resultado.cantidad_estimada == 50

    def test_generar_rfq(self, openai_service, mock_openai_response):
        """Test generación de RFQ."""
        rfq_text = "Estimado proveedor,\n\nSolicitamos cotización para..."
        mock_response = mock_openai_response(rfq_text)

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            resultado = openai_service.generar_rfq(
                producto="Laptop HP",
                especificaciones=["16GB RAM", "SSD 512GB"],
                cantidad=50,
                proveedor_nombre="Tech Solutions",
                proveedor_categoria="tecnologia",
            )

        assert isinstance(resultado, str)
        assert len(resultado) > 0
        assert "Estimado" in resultado or "estimado" in resultado

    def test_analizar_cotizacion(self, openai_service, mock_openai_response):
        """Test análisis de cotización."""
        response_data = {
            "proveedor": "Tech Solutions",
            "precio_total": 45000000.0,
            "tiempo_entrega_dias": 15,
            "calidad_score": 8.5,
            "ventajas": ["Buen precio", "Entrega rápida"],
            "desventajas": ["Sin garantía extendida"],
            "recomendacion": "Cotización competitiva",
        }
        mock_response = mock_openai_response(json.dumps(response_data))

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            resultado = openai_service.analizar_cotizacion(
                contenido_email="Precio: $45M, entrega en 15 días",
                proveedor_nombre="Tech Solutions",
                solicitud_descripcion="50 laptops HP",
            )

        assert isinstance(resultado, CotizacionAnalizada)
        assert resultado.proveedor == "Tech Solutions"
        assert resultado.precio_total == 45000000.0
        assert resultado.tiempo_entrega_dias == 15
        assert resultado.calidad_score == 8.5

    def test_chat_completion(self, openai_service, mock_openai_response):
        """Test chat completion genérico."""
        mock_response = mock_openai_response("Respuesta del chat")

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            resultado = openai_service.chat_completion(
                messages=[
                    {"role": "system", "content": "Eres un asistente útil"},
                    {"role": "user", "content": "Hola"},
                ],
                temperature=0.7,
            )

        assert isinstance(resultado, str)
        assert resultado == "Respuesta del chat"

    def test_extraer_json(self, openai_service, mock_openai_response):
        """Test extracción de JSON."""
        json_data = {"nombre": "Producto", "precio": 1000}
        mock_response = mock_openai_response(json.dumps(json_data))

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            resultado = openai_service.extraer_json(
                prompt="Extrae el nombre y precio del texto",
                schema_ejemplo={"nombre": "string", "precio": "number"},
            )

        assert isinstance(resultado, dict)
        assert resultado["nombre"] == "Producto"
        assert resultado["precio"] == 1000

    def test_analizar_solicitud_respuesta_vacia(
        self, openai_service, mock_openai_response
    ):
        """Test manejo de respuesta vacía."""
        mock_response = mock_openai_response("")

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            with pytest.raises(ValueError, match="Respuesta vacía"):
                openai_service.analizar_solicitud("Test")

    def test_extraer_json_invalido(self, openai_service, mock_openai_response):
        """Test manejo de JSON inválido."""
        mock_response = mock_openai_response("no es json válido {")

        with patch.object(
            openai_service.client.chat.completions,
            "create",
            return_value=mock_response,
        ):
            with pytest.raises(ValueError, match="no es JSON válido"):
                openai_service.extraer_json("Test")


class TestSolicitudAnalizada:
    """Tests para el modelo SolicitudAnalizada."""

    def test_crear_solicitud_completa(self):
        """Test creación con todos los campos."""
        solicitud = SolicitudAnalizada(
            productos=["Laptop"],
            cantidad_estimada=10,
            categoria="tecnologia",
            presupuesto_estimado=10000.0,
            urgencia="media",
            especificaciones=["16GB RAM"],
            keywords=["laptop"],
        )

        assert solicitud.productos == ["Laptop"]
        assert solicitud.cantidad_estimada == 10
        assert solicitud.categoria == "tecnologia"

    def test_crear_solicitud_minima(self):
        """Test creación con campos mínimos."""
        solicitud = SolicitudAnalizada(
            productos=["Producto"],
            categoria="insumos",
            urgencia="baja",
            especificaciones=[],
            keywords=[],
        )

        assert solicitud.cantidad_estimada is None
        assert solicitud.presupuesto_estimado is None


class TestCotizacionAnalizada:
    """Tests para el modelo CotizacionAnalizada."""

    def test_crear_cotizacion(self):
        """Test creación de cotización."""
        cotizacion = CotizacionAnalizada(
            proveedor="Test Provider",
            precio_total=1000.0,
            tiempo_entrega_dias=10,
            calidad_score=8.0,
            ventajas=["Buena calidad"],
            desventajas=["Precio alto"],
            recomendacion="Aceptable",
        )

        assert cotizacion.proveedor == "Test Provider"
        assert cotizacion.precio_total == 1000.0
        assert cotizacion.calidad_score == 8.0
