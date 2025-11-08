"""
Gestión de sesiones de base de datos.

Este módulo maneja la creación y gestión de sesiones de SQLAlchemy,
incluyendo el engine y SessionLocal.
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from config.settings import settings
from config.logging_config import logger

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries en modo debug
    pool_pre_ping=True,  # Verificar conexión antes de usar
    pool_recycle=3600,  # Reciclar conexiones cada hora
)

# Crear SessionLocal
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener sesión de base de datos.

    Uso en FastAPI:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        ```python
        from src.database.session import get_db

        def mi_funcion():
            db = next(get_db())
            try:
                # Usar db
                items = db.query(Item).all()
            finally:
                db.close()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables() -> None:
    """
    Crea todas las tablas en la base de datos.

    Esta función debe ejecutarse al inicializar la aplicación
    o usar Alembic para migraciones en producción.

    Example:
        ```python
        from src.database.session import create_tables

        # Al iniciar la aplicación
        create_tables()
        ```
    """
    from src.database.base import Base

    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas exitosamente")


def drop_tables() -> None:
    """
    Elimina todas las tablas de la base de datos.

    ⚠️ PRECAUCIÓN: Esta función elimina TODOS los datos.
    Solo usar en desarrollo o testing.

    Example:
        ```python
        from src.database.session import drop_tables

        # Solo en testing
        drop_tables()
        ```
    """
    from src.database.base import Base

    logger.warning("⚠️  Eliminando todas las tablas de la base de datos...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Tablas eliminadas")
