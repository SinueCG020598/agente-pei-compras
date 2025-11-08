"""
Configuración de fixtures compartidas para pytest.
"""
import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Retorna la ruta raíz del proyecto."""
    return Path(__file__).parent.parent


@pytest.fixture
def config_dir(project_root: Path) -> Path:
    """Retorna la ruta del directorio de configuración."""
    return project_root / "config"


@pytest.fixture
def src_dir(project_root: Path) -> Path:
    """Retorna la ruta del directorio src."""
    return project_root / "src"
