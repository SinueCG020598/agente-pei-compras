"""
Tests para el servicio de WhatsApp (Evolution API).
"""
from unittest.mock import Mock, patch

import pytest
import requests

from src.services.whatsapp_service import (
    WhatsAppService,
    WhatsAppMessage,
    WhatsAppMediaMessage,
    WebhookMessage,
)


@pytest.fixture
def whatsapp_service():
    """Fixture que retorna una instancia del servicio WhatsApp."""
    return WhatsAppService(
        api_url="http://test-api:8080",
        api_key="test-key-123",
        instance_name="test-instance",
    )


@pytest.fixture
def mock_response():
    """Fixture para crear respuestas mock."""

    def _create_response(status_code=200, json_data=None):
        """Crea una respuesta mock."""
        mock_resp = Mock()
        mock_resp.status_code = status_code
        mock_resp.json.return_value = json_data or {"success": True}
        mock_resp.raise_for_status = Mock()

        if status_code >= 400:
            mock_resp.raise_for_status.side_effect = requests.HTTPError(
                response=mock_resp
            )
            mock_resp.text = str(json_data)

        return mock_resp

    return _create_response


class TestWhatsAppService:
    """Tests para la clase WhatsAppService."""

    def test_init(self, whatsapp_service):
        """Test inicialización del servicio."""
        assert whatsapp_service.api_url == "http://test-api:8080"
        assert whatsapp_service.api_key == "test-key-123"
        assert whatsapp_service.instance_name == "test-instance"
        assert whatsapp_service.headers["apikey"] == "test-key-123"

    def test_get_url(self, whatsapp_service):
        """Test construcción de URLs."""
        url = whatsapp_service._get_url("/message/sendText")
        assert url == "http://test-api:8080/message/sendText/test-instance"

        # Test con barra inicial
        url = whatsapp_service._get_url("instance/status")
        assert url == "http://test-api:8080/instance/status/test-instance"

    def test_send_text(self, whatsapp_service, mock_response):
        """Test envío de mensaje de texto."""
        mock_resp = mock_response(200, {"messageId": "msg-123"})

        with patch("requests.post", return_value=mock_resp) as mock_post:
            resultado = whatsapp_service.send_text(
                phone="56912345678", message="Hola, este es un test"
            )

        assert resultado["messageId"] == "msg-123"
        mock_post.assert_called_once()

        # Verificar payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]
        assert payload["number"] == "56912345678"
        assert payload["text"] == "Hola, este es un test"

    def test_send_text_quoted(self, whatsapp_service, mock_response):
        """Test envío de mensaje citando otro."""
        mock_resp = mock_response(200, {"messageId": "msg-124"})

        with patch("requests.post", return_value=mock_resp) as mock_post:
            resultado = whatsapp_service.send_text(
                phone="56912345678",
                message="Respuesta",
                quoted_message_id="original-msg-123",
            )

        assert resultado["messageId"] == "msg-124"

        # Verificar que incluye quoted
        payload = mock_post.call_args[1]["json"]
        assert "quoted" in payload
        assert payload["quoted"]["key"]["id"] == "original-msg-123"

    def test_send_text_error(self, whatsapp_service, mock_response):
        """Test manejo de error al enviar mensaje."""
        mock_resp = mock_response(500, {"error": "Internal server error"})

        with patch("requests.post", return_value=mock_resp):
            with pytest.raises(requests.HTTPError):
                whatsapp_service.send_text("56912345678", "Test")

    def test_send_media_image(self, whatsapp_service, mock_response):
        """Test envío de imagen."""
        mock_resp = mock_response(200, {"messageId": "img-123"})

        with patch("requests.post", return_value=mock_resp) as mock_post:
            resultado = whatsapp_service.send_media(
                phone="56912345678",
                media_url="https://example.com/image.jpg",
                caption="Mira esta imagen",
                media_type="image",
            )

        assert resultado["messageId"] == "img-123"

        payload = mock_post.call_args[1]["json"]
        assert payload["number"] == "56912345678"
        assert payload["media"] == "https://example.com/image.jpg"
        assert payload["caption"] == "Mira esta imagen"
        assert payload["mediatype"] == "image"

    def test_send_media_document(self, whatsapp_service, mock_response):
        """Test envío de documento."""
        mock_resp = mock_response(200, {"messageId": "doc-123"})

        with patch("requests.post", return_value=mock_resp):
            resultado = whatsapp_service.send_media(
                phone="56912345678",
                media_url="https://example.com/doc.pdf",
                media_type="document",
            )

        assert resultado["messageId"] == "doc-123"

    def test_get_instance_status(self, whatsapp_service, mock_response):
        """Test obtención de estado de instancia."""
        mock_resp = mock_response(200, {"state": "open", "connected": True})

        with patch("requests.get", return_value=mock_resp) as mock_get:
            resultado = whatsapp_service.get_instance_status()

        assert resultado["state"] == "open"
        assert resultado["connected"] is True
        mock_get.assert_called_once()

    def test_is_connected_true(self, whatsapp_service, mock_response):
        """Test verificación de conexión (conectado)."""
        mock_resp = mock_response(200, {"state": "open"})

        with patch("requests.get", return_value=mock_resp):
            assert whatsapp_service.is_connected() is True

    def test_is_connected_false(self, whatsapp_service, mock_response):
        """Test verificación de conexión (desconectado)."""
        mock_resp = mock_response(200, {"state": "close"})

        with patch("requests.get", return_value=mock_resp):
            assert whatsapp_service.is_connected() is False

    def test_is_connected_error(self, whatsapp_service):
        """Test verificación de conexión con error."""
        with patch("requests.get", side_effect=requests.RequestException("Error")):
            assert whatsapp_service.is_connected() is False

    def test_get_qr_code(self, whatsapp_service, mock_response):
        """Test obtención de código QR."""
        mock_resp = mock_response(200, {"qrcode": "data:image/png;base64,iVBOR..."})

        with patch("requests.get", return_value=mock_resp):
            qr = whatsapp_service.get_qr_code()

        assert qr.startswith("data:image/png;base64")

    def test_get_qr_code_already_connected(self, whatsapp_service, mock_response):
        """Test QR cuando ya está conectado."""
        mock_resp = mock_response(404)

        with patch("requests.get", return_value=mock_resp):
            qr = whatsapp_service.get_qr_code()

        assert qr is None

    def test_set_webhook(self, whatsapp_service, mock_response):
        """Test configuración de webhook."""
        mock_resp = mock_response(200, {"webhook": {"url": "https://example.com"}})

        with patch("requests.post", return_value=mock_resp) as mock_post:
            resultado = whatsapp_service.set_webhook("https://example.com/webhook")

        assert "webhook" in resultado
        mock_post.assert_called_once()

        payload = mock_post.call_args[1]["json"]
        assert payload["url"] == "https://example.com/webhook"
        assert "messages_upsert" in payload["events"]

    def test_process_webhook_text(self, whatsapp_service):
        """Test procesamiento de webhook con mensaje de texto."""
        webhook_data = {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "56912345678@s.whatsapp.net",
                    "id": "msg-abc-123",
                },
                "message": {"conversation": "Hola, necesito una cotización"},
                "messageTimestamp": 1234567890,
            },
        }

        resultado = whatsapp_service.process_webhook(webhook_data)

        assert resultado is not None
        assert isinstance(resultado, WebhookMessage)
        assert resultado.from_number == "56912345678"
        assert resultado.message_id == "msg-abc-123"
        assert resultado.body == "Hola, necesito una cotización"
        assert resultado.message_type == "conversation"

    def test_process_webhook_extended_text(self, whatsapp_service):
        """Test procesamiento de webhook con mensaje extendido."""
        webhook_data = {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "56912345678@s.whatsapp.net",
                    "id": "msg-xyz-456",
                },
                "message": {
                    "extendedTextMessage": {"text": "Mensaje con formato o links"}
                },
                "messageTimestamp": 1234567890,
            },
        }

        resultado = whatsapp_service.process_webhook(webhook_data)

        assert resultado is not None
        assert resultado.body == "Mensaje con formato o links"
        assert resultado.message_type == "extendedTextMessage"

    def test_process_webhook_image(self, whatsapp_service):
        """Test procesamiento de webhook con imagen."""
        webhook_data = {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "56912345678@s.whatsapp.net",
                    "id": "msg-img-789",
                },
                "message": {
                    "imageMessage": {
                        "url": "https://example.com/image.jpg",
                        "caption": "Mira esta foto",
                    }
                },
                "messageTimestamp": 1234567890,
            },
        }

        resultado = whatsapp_service.process_webhook(webhook_data)

        assert resultado is not None
        assert resultado.message_type == "imageMessage"
        assert resultado.media_url == "https://example.com/image.jpg"
        assert resultado.body == "Mira esta foto"

    def test_process_webhook_ignored_event(self, whatsapp_service):
        """Test que eventos no relevantes sean ignorados."""
        webhook_data = {
            "event": "status.update",  # Evento diferente
            "instance": "test-instance",
            "data": {},
        }

        resultado = whatsapp_service.process_webhook(webhook_data)
        assert resultado is None

    def test_format_phone_number(self, whatsapp_service):
        """Test formateo de números de teléfono."""
        # Con código de país
        assert whatsapp_service.format_phone_number("+56 9 1234 5678") == "56912345678"
        assert whatsapp_service.format_phone_number("56-9-1234-5678") == "56912345678"

        # Sin código de país (asume Chile)
        assert whatsapp_service.format_phone_number("912345678") == "56912345678"

        # Ya formateado
        assert whatsapp_service.format_phone_number("56912345678") == "56912345678"


class TestWhatsAppMessage:
    """Tests para el modelo WhatsAppMessage."""

    def test_crear_mensaje_simple(self):
        """Test creación de mensaje simple."""
        msg = WhatsAppMessage(phone="56912345678", message="Hola")

        assert msg.phone == "56912345678"
        assert msg.message == "Hola"
        assert msg.quoted_message_id is None

    def test_crear_mensaje_quoted(self):
        """Test creación de mensaje citando otro."""
        msg = WhatsAppMessage(
            phone="56912345678", message="Respuesta", quoted_message_id="msg-123"
        )

        assert msg.quoted_message_id == "msg-123"


class TestWhatsAppMediaMessage:
    """Tests para el modelo WhatsAppMediaMessage."""

    def test_crear_media_image(self):
        """Test creación de mensaje con imagen."""
        msg = WhatsAppMediaMessage(
            phone="56912345678",
            media_url="https://example.com/image.jpg",
            caption="Foto",
            media_type="image",
        )

        assert msg.media_type == "image"
        assert msg.caption == "Foto"

    def test_crear_media_document(self):
        """Test creación de mensaje con documento."""
        msg = WhatsAppMediaMessage(
            phone="56912345678",
            media_url="https://example.com/doc.pdf",
            media_type="document",
        )

        assert msg.media_type == "document"
        assert msg.caption is None
