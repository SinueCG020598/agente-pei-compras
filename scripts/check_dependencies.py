"""
Script para verificar que todas las dependencias estén instaladas correctamente.
"""
import sys
from importlib import import_module


def check_dependencies() -> bool:
    """Verifica que todas las dependencias estén instaladas."""
    print("🔍 Verificando dependencias instaladas...")

    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("openai", "OpenAI"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("requests", "Requests"),
        ("aiohttp", "AIOHTTP"),
        ("streamlit", "Streamlit"),
        ("dotenv", "Python-dotenv"),
    ]

    all_ok = True
    for module_name, display_name in dependencies:
        try:
            import_module(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NO INSTALADO")
            all_ok = False

    if all_ok:
        print("\n✅ Todas las dependencias están instaladas correctamente")
        return True
    else:
        print("\n❌ Faltan dependencias. Ejecuta: make install")
        return False


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
