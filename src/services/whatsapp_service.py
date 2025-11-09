"""
Servicio de integración con Evolution API para WhatsApp.

Este servicio proporciona funcionalidades para:
- Enviar y recibir mensajes de WhatsApp
- Gestionar instancia de WhatsApp
- Manejo de webhooks
- Envío de media (imágenes, documentos)
"""
import logging
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


class WhatsAppMessage(BaseModel):
    """Modelo para mensaje de WhatsApp."""

    phone: str  # Número con código de país (ej: 56912345678)
    message: str
    quoted_message_id: Optional[str] = None


class WhatsAppMediaMessage(BaseModel):
    """Modelo para mensaje con media."""

    phone: str
    media_url: str
    caption: Optional[str] = None
    media_type: str = "image"  # image, document, video, audio


class WebhookMessage(BaseModel):
    """Modelo para mensaje recibido por webhook."""

    instance: str
    from_number: str
    message_id: str
    message_type: str  # text, image, document, etc
    body: Optional[str] = None
    media_url: Optional[str] = None
    timestamp: int


class WhatsAppService:
    """
    Servicio para interactuar con Evolution API (WhatsApp).

    Evolution API: https://github.com/EvolutionAPI/evolution-api
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_name: Optional[str] = None,
    ):
        """
        Inicializa el servicio de WhatsApp.

        Args:
            api_url: URL de Evolution API (usa settings si no se proporciona)
            api_key: API key para autenticación
            instance_name: Nombre de la instancia de WhatsApp
        """
        self.api_url = (api_url or settings.EVOLUTION_API_URL).rstrip("/")
        self.api_key = api_key or settings.EVOLUTION_API_KEY
        self.instance_name = instance_name or settings.EVOLUTION_INSTANCE_NAME

        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json",
        }

        logger.info(
            f"WhatsApp Service inicializado - Instance: {self.instance_name}, "
            f"URL: {self.api_url}"
        )

    def _get_url(self, endpoint: str) -> str:
        """
        Construye la URL completa para un endpoint.

        Args:
            endpoint: Endpoint de la API (ej: /message/sendText)

        Returns:
            URL completa
        """
        endpoint = endpoint.lstrip("/")
        return f"{self.api_url}/{endpoint}/{self.instance_name}"

    def send_text(
        self,
        phone: str,
        message: str,
        quoted_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto por WhatsApp.

        Args:
            phone: Número de teléfono con código de país (ej: 56912345678)
            message: Texto del mensaje
            quoted_message_id: ID del mensaje a citar (responder)

        Returns:
            Respuesta de la API con el mensaje enviado

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
        """
        logger.info(f"Enviando mensaje a {phone}: {message[:50]}...")

        payload = {
            "number": phone,
            "text": message,
        }

        if quoted_message_id:
            payload["quoted"] = {"key": {"id": quoted_message_id}}

        try:
            response = requests.post(
                self._get_url("/message/sendText"),
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Mensaje enviado exitosamente a {phone}")
            return data

        except requests.HTTPError as e:
            logger.error(f"Error enviando mensaje: {e}")
            logger.error(f"Response: {e.response.text if e.response else 'No response'}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión con Evolution API: {e}")
            raise

    def send_media(
        self,
        phone: str,
        media_url: str,
        caption: Optional[str] = None,
        media_type: str = "image",
    ) -> Dict[str, Any]:
        """
        Envía un archivo multimedia por WhatsApp.

        Args:
            phone: Número de teléfono con código de país
            media_url: URL del archivo multimedia
            caption: Texto que acompaña el archivo
            media_type: Tipo de media (image, document, video, audio)

        Returns:
            Respuesta de la API

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
        """
        logger.info(f"Enviando {media_type} a {phone}")

        # Mapear tipo de media a endpoint
        endpoint_map = {
            "image": "/message/sendMedia",
            "document": "/message/sendMedia",
            "video": "/message/sendMedia",
            "audio": "/message/sendWhatsAppAudio",
        }

        endpoint = endpoint_map.get(media_type, "/message/sendMedia")

        payload = {
            "number": phone,
            "mediatype": media_type,
            "media": media_url,
        }

        if caption:
            payload["caption"] = caption

        try:
            response = requests.post(
                self._get_url(endpoint),
                json=payload,
                headers=self.headers,
                timeout=60,  # Media puede tardar más
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Media enviado exitosamente a {phone}")
            return data

        except requests.HTTPError as e:
            logger.error(f"Error enviando media: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def get_instance_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la instancia de WhatsApp.

        Returns:
            Dict con información de la instancia (conectada, QR, etc.)

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
        """
        logger.debug(f"Consultando estado de instancia {self.instance_name}")

        try:
            response = requests.get(
                self._get_url("/instance/connectionState"),
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            state = data.get("state", "unknown")
            logger.info(f"Estado de instancia: {state}")
            return data

        except requests.HTTPError as e:
            logger.error(f"Error consultando estado: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def is_connected(self) -> bool:
        """
        Verifica si la instancia está conectada.

        Returns:
            True si está conectada, False en caso contrario
        """
        try:
            status = self.get_instance_status()
            state = status.get("state", "").lower()
            return state == "open" or state == "connected"
        except Exception as e:
            logger.warning(f"No se pudo verificar conexión: {e}")
            return False

    def get_qr_code(self) -> Optional[str]:
        """
        Obtiene el código QR para conectar WhatsApp.

        Returns:
            URL o base64 del código QR, o None si ya está conectado

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
        """
        logger.info("Solicitando código QR")

        try:
            response = requests.get(
                self._get_url("/instance/qrcode"),
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            qr_code = data.get("qrcode") or data.get("code")

            if qr_code:
                logger.info("Código QR obtenido")
            else:
                logger.info("No hay código QR disponible (probablemente conectado)")

            return qr_code

        except requests.HTTPError as e:
            if e.response and e.response.status_code == 404:
                logger.info("Instancia ya conectada, no necesita QR")
                return None
            logger.error(f"Error obteniendo QR: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def set_webhook(self, webhook_url: str, events: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Configura el webhook para recibir mensajes.

        Args:
            webhook_url: URL donde se recibirán los webhooks
            events: Lista de eventos a escuchar (messages_upsert por defecto)

        Returns:
            Respuesta de la API

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
        """
        logger.info(f"Configurando webhook: {webhook_url}")

        if not events:
            events = ["messages_upsert"]  # Evento de mensajes nuevos

        payload = {
            "url": webhook_url,
            "events": events,
            "webhook_by_events": True,
        }

        try:
            response = requests.post(
                self._get_url("/webhook/set"),
                json=payload,
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()

            data = response.json()
            logger.info("Webhook configurado exitosamente")
            return data

        except requests.HTTPError as e:
            logger.error(f"Error configurando webhook: {e}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def process_webhook(self, webhook_data: Dict[str, Any]) -> Optional[WebhookMessage]:
        """
        Procesa un webhook recibido de Evolution API.

        Args:
            webhook_data: Datos del webhook

        Returns:
            WebhookMessage parseado o None si no es un mensaje válido
        """
        try:
            # Estructura típica de webhook de Evolution API
            event = webhook_data.get("event")
            instance = webhook_data.get("instance")
            data = webhook_data.get("data", {})

            if event != "messages.upsert":
                logger.debug(f"Evento ignorado: {event}")
                return None

            # Extraer información del mensaje
            message_data = data.get("message", {})
            key = data.get("key", {})

            from_number = key.get("remoteJid", "").split("@")[0]
            message_id = key.get("id", "")
            message_type = list(message_data.keys())[0] if message_data else "unknown"

            # Extraer contenido según tipo
            body = None
            media_url = None

            if message_type == "conversation":
                body = message_data.get("conversation")
            elif message_type == "extendedTextMessage":
                body = message_data.get("extendedTextMessage", {}).get("text")
            elif message_type in ["imageMessage", "documentMessage", "videoMessage"]:
                media_info = message_data.get(message_type, {})
                media_url = media_info.get("url")
                body = media_info.get("caption")

            webhook_msg = WebhookMessage(
                instance=instance,
                from_number=from_number,
                message_id=message_id,
                message_type=message_type,
                body=body,
                media_url=media_url,
                timestamp=data.get("messageTimestamp", 0),
            )

            logger.info(
                f"Mensaje procesado de {from_number}: "
                f"{body[:50] if body else f'[{message_type}]'}..."
            )
            return webhook_msg

        except Exception as e:
            logger.error(f"Error procesando webhook: {e}")
            logger.debug(f"Webhook data: {webhook_data}")
            return None

    async def send_text_async(
        self,
        phone: str,
        message: str,
        quoted_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envía un mensaje de texto de forma asíncrona.

        Args:
            phone: Número de teléfono con código de país
            message: Texto del mensaje
            quoted_message_id: ID del mensaje a citar

        Returns:
            Respuesta de la API

        Raises:
            aiohttp.ClientError: Si hay error en la llamada a la API
        """
        logger.info(f"[Async] Enviando mensaje a {phone}")

        payload = {
            "number": phone,
            "text": message,
        }

        if quoted_message_id:
            payload["quoted"] = {"key": {"id": quoted_message_id}}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._get_url("/message/sendText"),
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    logger.info(f"[Async] Mensaje enviado a {phone}")
                    return data

        except aiohttp.ClientError as e:
            logger.error(f"[Async] Error enviando mensaje: {e}")
            raise

    def format_phone_number(self, phone: str) -> str:
        """
        Formatea un número de teléfono para WhatsApp.

        Elimina caracteres especiales y asegura formato correcto.

        Args:
            phone: Número de teléfono (puede tener +, -, espacios)

        Returns:
            Número formateado (solo dígitos)

        Example:
            "+56 9 1234 5678" -> "56912345678"
        """
        # Eliminar caracteres no numéricos
        digits = "".join(filter(str.isdigit, phone))

        # Asegurar que tiene código de país
        if len(digits) == 9 and digits.startswith("9"):
            # Asume Chile si es un celular de 9 dígitos que empieza con 9
            digits = "56" + digits
            logger.debug(f"Agregando código de país Chile: 56{phone}")

        return digits


# Instancia global del servicio
whatsapp_service = WhatsAppService()
