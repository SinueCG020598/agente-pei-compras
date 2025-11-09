"""
Módulo de servicios externos (OpenAI, WhatsApp, Email, Search).
"""
from src.services.email_service import (
    EmailService,
    EmailMessage,
    ReceivedEmail,
    email_service,
)
from src.services.openai_service import (
    OpenAIService,
    SolicitudAnalizada,
    CotizacionAnalizada,
    openai_service,
)
from src.services.search_service import (
    SearchService,
    SearchResult,
    ProveedorEncontrado,
    search_service,
)
from src.services.whatsapp_service import (
    WhatsAppService,
    WhatsAppMessage,
    WhatsAppMediaMessage,
    WebhookMessage,
    whatsapp_service,
)

__all__ = [
    # OpenAI
    "OpenAIService",
    "SolicitudAnalizada",
    "CotizacionAnalizada",
    "openai_service",
    # WhatsApp
    "WhatsAppService",
    "WhatsAppMessage",
    "WhatsAppMediaMessage",
    "WebhookMessage",
    "whatsapp_service",
    # Email
    "EmailService",
    "EmailMessage",
    "ReceivedEmail",
    "email_service",
    # Search
    "SearchService",
    "SearchResult",
    "ProveedorEncontrado",
    "search_service",
]
