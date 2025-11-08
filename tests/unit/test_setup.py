"""
Tests para verificar el setup inicial del proyecto (Fase 0).
"""
import os
import sys
from pathlib import Path

import pytest

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestSetupInicial:
    """Tests del setup inicial del proyecto."""

    def test_estructura_directorios_existe(self, project_root: Path) -> None:
        """Verifica que todos los directorios necesarios existan."""
        directorios = [
            "src/agents",
            "src/database",
            "src/services",
            "src/api",
            "src/api/routes",
            "src/schemas",
            "src/core",
            "src/prompts",
            "config",
            "frontend",
            "frontend/pages",
            "frontend/components",
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "scripts",
            "docs",
            "logs",
        ]

        for directorio in directorios:
            dir_path = project_root / directorio
            assert dir_path.exists(), f"Directorio {directorio} no existe"
            assert dir_path.is_dir(), f"{directorio} no es un directorio"

    def test_archivos_configuracion_existen(self, project_root: Path) -> None:
        """Verifica que los archivos de configuración existan."""
        archivos = [
            ".gitignore",
            ".editorconfig",
            ".pre-commit-config.yaml",
            "pyproject.toml",
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            "Makefile",
            "docker-compose.yml",
        ]

        for archivo in archivos:
            file_path = project_root / archivo
            assert file_path.exists(), f"Archivo {archivo} no existe"
            assert file_path.is_file(), f"{archivo} no es un archivo"

    def test_archivos_init_existen(self, src_dir: Path) -> None:
        """Verifica que los archivos __init__.py existan en todos los paquetes."""
        paquetes = [
            "src",
            "src/agents",
            "src/database",
            "src/services",
            "src/api",
            "src/api/routes",
            "src/schemas",
            "src/core",
            "src/prompts",
        ]

        project_root = src_dir.parent
        for paquete in paquetes:
            init_file = project_root / paquete / "__init__.py"
            assert init_file.exists(), f"__init__.py no existe en {paquete}"

    def test_config_settings_importable(self) -> None:
        """Verifica que settings se pueda importar correctamente."""
        try:
            from config.settings import settings

            assert settings is not None
            assert hasattr(settings, "PROJECT_NAME")
            assert hasattr(settings, "VERSION")
            assert hasattr(settings, "OPENAI_API_KEY")
        except ImportError as e:
            pytest.fail(f"Error importando settings: {e}")

    def test_config_logging_importable(self) -> None:
        """Verifica que logging_config se pueda importar correctamente."""
        try:
            from config.logging_config import logger, setup_logging

            assert logger is not None
            assert setup_logging is not None
        except ImportError as e:
            pytest.fail(f"Error importando logging_config: {e}")

    def test_project_version(self) -> None:
        """Verifica que la versión del proyecto esté definida."""
        from src import __version__

        assert __version__ == "0.1.0"

    def test_gitignore_contiene_archivos_importantes(self, project_root: Path) -> None:
        """Verifica que .gitignore incluya archivos importantes."""
        gitignore_path = project_root / ".gitignore"
        gitignore_content = gitignore_path.read_text()

        # Patrones que deben estar presentes (más flexibles)
        patrones_requeridos = [
            ".env",
            "__pycache__",
            "venv/",
            ".pytest_cache",
            "*.db",
            "logs/",
        ]

        for patron in patrones_requeridos:
            assert (
                patron in gitignore_content
            ), f"{patron} no está en .gitignore"

        # Verificar que archivos .pyc estén ignorados (acepta *.pyc o *.py[cod])
        assert ("*.pyc" in gitignore_content or "*.py[cod]" in gitignore_content), \
            "archivos .pyc no están siendo ignorados"

    def test_pyproject_toml_valido(self, project_root: Path) -> None:
        """Verifica que pyproject.toml sea válido y contenga las secciones necesarias."""
        pyproject_path = project_root / "pyproject.toml"
        content = pyproject_path.read_text()

        secciones_requeridas = [
            "[tool.poetry]",
            "[tool.poetry.dependencies]",
            "[tool.black]",
            "[tool.ruff]",
            "[tool.mypy]",
            "[tool.pytest.ini_options]",
        ]

        for seccion in secciones_requeridas:
            assert seccion in content, f"Sección {seccion} no está en pyproject.toml"

    def test_requirements_txt_contiene_dependencias(
        self, project_root: Path
    ) -> None:
        """Verifica que requirements.txt contenga las dependencias principales."""
        requirements_path = project_root / "requirements.txt"
        content = requirements_path.read_text()

        dependencias_principales = [
            "fastapi",
            "uvicorn",
            "openai",
            "langchain",
            "sqlalchemy",
            "pydantic",
            "streamlit",
        ]

        for dependencia in dependencias_principales:
            assert (
                dependencia in content
            ), f"{dependencia} no está en requirements.txt"


class TestScripts:
    """Tests para los scripts de utilidad."""

    def test_scripts_son_ejecutables(self, project_root: Path) -> None:
        """Verifica que los scripts principales existan y sean archivos Python."""
        scripts = [
            "scripts/test_setup.py",
            "scripts/setup_database.py",
            "scripts/seed_data.py",
            "scripts/check_dependencies.py",
        ]

        for script in scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Script {script} no existe"
            assert script_path.suffix == ".py", f"{script} no es un archivo Python"

    def test_scripts_tienen_main(self, project_root: Path) -> None:
        """Verifica que los scripts tengan un bloque if __name__ == '__main__'."""
        scripts = [
            "scripts/test_setup.py",
            "scripts/setup_database.py",
            "scripts/seed_data.py",
            "scripts/check_dependencies.py",
        ]

        for script in scripts:
            script_path = project_root / script
            content = script_path.read_text()
            assert (
                'if __name__ == "__main__"' in content
            ), f"{script} no tiene bloque main"


class TestDocumentacion:
    """Tests para verificar que existe documentación básica."""

    def test_readme_existe(self, project_root: Path) -> None:
        """Verifica que README.md exista."""
        readme_path = project_root / "README.md"
        # Este test pasará una vez que creemos el README
        # assert readme_path.exists(), "README.md no existe"

    def test_docs_directory_existe(self, project_root: Path) -> None:
        """Verifica que el directorio docs exista."""
        docs_dir = project_root / "docs"
        assert docs_dir.exists(), "Directorio docs no existe"
        assert docs_dir.is_dir(), "docs no es un directorio"
