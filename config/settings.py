"""
Configuración centralizada del proyecto usando Pydantic Settings.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # Configuración del proyecto
    PROJECT_NAME: str = "PEI Compras AI"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL_MINI: str = "gpt-4o-mini"
    OPENAI_MODEL_FULL: str = "gpt-4o"

    # Database
    DATABASE_URL: str = "sqlite:///./pei_compras.db"

    # Evolution API (WhatsApp)
    EVOLUTION_API_URL: str = "http://localhost:8080"
    EVOLUTION_API_KEY: str
    EVOLUTION_INSTANCE_NAME: str = "pei-compras"

    # Gmail
    GMAIL_USER: str
    GMAIL_APP_PASSWORD: str

    # Serper API (opcional para búsqueda web)
    SERPER_API_KEY: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Instancia global de configuración
settings = Settings()
