"""
Servicio de integración con Email (SMTP/IMAP).

Este servicio proporciona funcionalidades para:
- Enviar emails (RFQs) usando SMTP
- Recibir emails (cotizaciones) usando IMAP
- Parsear emails y extraer información
- Manejo de adjuntos
"""
import email
import imaplib
import logging
import smtplib
from datetime import datetime
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, EmailStr

from config.settings import settings

logger = logging.getLogger(__name__)


class EmailMessage(BaseModel):
    """Modelo para un email."""

    to: EmailStr
    subject: str
    body: str
    body_html: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[str]] = None  # Rutas de archivos


class ReceivedEmail(BaseModel):
    """Modelo para email recibido."""

    message_id: str
    from_address: str
    subject: str
    date: datetime
    body_text: str
    body_html: Optional[str] = None
    attachments: List[Dict[str, Any]] = []


class EmailService:
    """
    Servicio para enviar y recibir emails.

    Usa Gmail SMTP/IMAP por defecto, pero puede configurarse
    para otros proveedores.
    """

    def __init__(
        self,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        imap_host: str = "imap.gmail.com",
        imap_port: int = 993,
        email_user: Optional[str] = None,
        email_password: Optional[str] = None,
    ):
        """
        Inicializa el servicio de email.

        Args:
            smtp_host: Host del servidor SMTP
            smtp_port: Puerto del servidor SMTP (587 para TLS)
            imap_host: Host del servidor IMAP
            imap_port: Puerto del servidor IMAP (993 para SSL)
            email_user: Usuario de email (usa settings si no se proporciona)
            email_password: Contraseña/App Password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.imap_host = imap_host
        self.imap_port = imap_port

        self.email_user = email_user or settings.GMAIL_USER
        self.email_password = email_password or settings.GMAIL_APP_PASSWORD

        logger.info(
            f"Email Service inicializado - Usuario: {self.email_user}, "
            f"SMTP: {smtp_host}:{smtp_port}, IMAP: {imap_host}:{imap_port}"
        )

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """
        Envía un email usando SMTP.

        Args:
            to: Destinatario principal
            subject: Asunto del email
            body: Cuerpo del email en texto plano
            body_html: Cuerpo del email en HTML (opcional)
            cc: Lista de destinatarios en copia
            bcc: Lista de destinatarios en copia oculta
            attachments: Lista de rutas de archivos a adjuntar

        Returns:
            True si se envió exitosamente, False en caso contrario

        Raises:
            smtplib.SMTPException: Si hay error enviando el email
        """
        logger.info(f"Enviando email a {to} - Asunto: {subject}")

        try:
            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["From"] = self.email_user
            msg["To"] = to
            msg["Subject"] = subject

            if cc:
                msg["Cc"] = ", ".join(cc)
            if bcc:
                msg["Bcc"] = ", ".join(bcc)

            # Agregar cuerpo de texto
            msg.attach(MIMEText(body, "plain", "utf-8"))

            # Agregar cuerpo HTML si se proporciona
            if body_html:
                msg.attach(MIMEText(body_html, "html", "utf-8"))

            # Agregar adjuntos
            if attachments:
                for file_path in attachments:
                    try:
                        self._attach_file(msg, file_path)
                    except Exception as e:
                        logger.error(f"Error adjuntando archivo {file_path}: {e}")
                        raise

            # Enviar email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Habilitar TLS
                server.login(self.email_user, self.email_password)

                # Lista completa de destinatarios
                recipients = [to]
                if cc:
                    recipients.extend(cc)
                if bcc:
                    recipients.extend(bcc)

                server.sendmail(self.email_user, recipients, msg.as_string())

            logger.info(f"Email enviado exitosamente a {to}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP enviando email: {e}")
            raise
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            raise

    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> None:
        """
        Adjunta un archivo al mensaje.

        Args:
            msg: Mensaje al que adjuntar el archivo
            file_path: Ruta del archivo a adjuntar

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        filename = os.path.basename(file_path)

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)

        logger.debug(f"Adjunto agregado: {filename}")

    def send_rfq(
        self,
        proveedor_email: str,
        proveedor_nombre: str,
        rfq_text: str,
        solicitud_numero: str,
    ) -> bool:
        """
        Envía un RFQ a un proveedor.

        Args:
            proveedor_email: Email del proveedor
            proveedor_nombre: Nombre del proveedor
            rfq_text: Texto del RFQ generado por IA
            solicitud_numero: Número de la solicitud

        Returns:
            True si se envió exitosamente

        Raises:
            smtplib.SMTPException: Si hay error enviando
        """
        subject = f"Solicitud de Cotización - {solicitud_numero}"

        # Agregar encabezado y pie profesional
        body = f"""Estimado/a equipo de {proveedor_nombre},

{rfq_text}

Esperamos su respuesta a la brevedad.

---
Equipo de Compras
PEI Compras AI
"""

        return self.send_email(to=proveedor_email, subject=subject, body=body)

    def fetch_unread_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
    ) -> List[ReceivedEmail]:
        """
        Obtiene emails no leídos usando IMAP.

        Args:
            folder: Carpeta de email a revisar (INBOX por defecto)
            limit: Máximo número de emails a obtener

        Returns:
            Lista de emails recibidos

        Raises:
            imaplib.IMAP4.error: Si hay error conectando o leyendo
        """
        logger.info(f"Buscando emails no leídos en {folder}")

        try:
            # Conectar a IMAP
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_user, self.email_password)
            mail.select(folder)

            # Buscar emails no leídos
            status, messages = mail.search(None, "UNSEEN")

            if status != "OK":
                logger.warning("No se pudieron obtener emails")
                return []

            email_ids = messages[0].split()
            if not email_ids:
                logger.info("No hay emails no leídos")
                return []

            # Limitar cantidad
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids

            received_emails = []

            for email_id in email_ids:
                try:
                    parsed = self._fetch_and_parse_email(mail, email_id)
                    if parsed:
                        received_emails.append(parsed)
                except Exception as e:
                    logger.error(f"Error parseando email {email_id}: {e}")
                    continue

            mail.close()
            mail.logout()

            logger.info(f"Obtenidos {len(received_emails)} emails")
            return received_emails

        except imaplib.IMAP4.error as e:
            logger.error(f"Error IMAP: {e}")
            raise
        except Exception as e:
            logger.error(f"Error obteniendo emails: {e}")
            raise

    def _fetch_and_parse_email(
        self, mail: imaplib.IMAP4_SSL, email_id: bytes
    ) -> Optional[ReceivedEmail]:
        """
        Obtiene y parsea un email específico.

        Args:
            mail: Conexión IMAP activa
            email_id: ID del email a obtener

        Returns:
            ReceivedEmail parseado o None si hay error
        """
        status, msg_data = mail.fetch(email_id, "(RFC822)")

        if status != "OK":
            return None

        # Parsear email
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)

        # Extraer metadata
        message_id = email_message.get("Message-ID", "")
        from_address = email_message.get("From", "")
        subject = self._decode_header(email_message.get("Subject", ""))
        date_str = email_message.get("Date", "")

        # Parsear fecha
        try:
            date = email.utils.parsedate_to_datetime(date_str)
        except Exception:
            date = datetime.now()

        # Extraer cuerpo
        body_text, body_html = self._extract_body(email_message)

        # Extraer adjuntos
        attachments = self._extract_attachments(email_message)

        return ReceivedEmail(
            message_id=message_id,
            from_address=from_address,
            subject=subject,
            date=date,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
        )

    def _decode_header(self, header: str) -> str:
        """
        Decodifica un header de email.

        Args:
            header: Header codificado

        Returns:
            Header decodificado
        """
        if not header:
            return ""

        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                decoded_parts.append(
                    part.decode(encoding or "utf-8", errors="ignore")
                )
            else:
                decoded_parts.append(part)

        return "".join(decoded_parts)

    def _extract_body(self, email_message: email.message.Message) -> Tuple[str, Optional[str]]:
        """
        Extrae el cuerpo del email (texto y HTML).

        Args:
            email_message: Mensaje de email parseado

        Returns:
            Tupla (texto_plano, html)
        """
        body_text = ""
        body_html = None

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Ignorar adjuntos
                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_text = payload.decode("utf-8", errors="ignore")
                    except Exception as e:
                        logger.error(f"Error decodificando texto: {e}")

                elif content_type == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body_html = payload.decode("utf-8", errors="ignore")
                    except Exception as e:
                        logger.error(f"Error decodificando HTML: {e}")
        else:
            # Email de una sola parte
            try:
                payload = email_message.get_payload(decode=True)
                if payload:
                    body_text = payload.decode("utf-8", errors="ignore")
            except Exception as e:
                logger.error(f"Error decodificando email: {e}")

        return body_text, body_html

    def _extract_attachments(
        self, email_message: email.message.Message
    ) -> List[Dict[str, Any]]:
        """
        Extrae información de los adjuntos.

        Args:
            email_message: Mensaje de email parseado

        Returns:
            Lista de diccionarios con info de adjuntos
        """
        attachments = []

        if not email_message.is_multipart():
            return attachments

        for part in email_message.walk():
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = self._decode_header(filename)

                    attachments.append(
                        {
                            "filename": filename,
                            "content_type": part.get_content_type(),
                            "size": len(part.get_payload(decode=True) or b""),
                        }
                    )

        return attachments

    def mark_as_read(self, message_id: str, folder: str = "INBOX") -> bool:
        """
        Marca un email como leído.

        Args:
            message_id: ID del mensaje a marcar
            folder: Carpeta donde está el email

        Returns:
            True si se marcó exitosamente

        Raises:
            imaplib.IMAP4.error: Si hay error
        """
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
            mail.login(self.email_user, self.email_password)
            mail.select(folder)

            # Buscar por Message-ID
            status, messages = mail.search(None, f'HEADER Message-ID "{message_id}"')

            if status == "OK" and messages[0]:
                email_id = messages[0].split()[0]
                mail.store(email_id, "+FLAGS", "\\Seen")
                logger.info(f"Email {message_id} marcado como leído")
                result = True
            else:
                logger.warning(f"Email {message_id} no encontrado")
                result = False

            mail.close()
            mail.logout()
            return result

        except imaplib.IMAP4.error as e:
            logger.error(f"Error marcando como leído: {e}")
            raise


# Instancia global del servicio
email_service = EmailService()
