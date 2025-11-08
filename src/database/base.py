"""
Base declarativa para SQLAlchemy.
Importa todos los modelos para que Alembic pueda detectarlos.
"""
from sqlalchemy.orm import declarative_base

# Base declarativa para todos los modelos
Base = declarative_base()

# Metadata para Alembic
metadata = Base.metadata
