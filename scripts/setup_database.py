"""
Script para configurar la base de datos inicial.
Crea las tablas necesarias usando Alembic.
"""
import sys
import subprocess
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_database() -> int:
    """
    Configura la base de datos y ejecuta migraciones.

    Returns:
        0 si exitoso, 1 si hay error
    """
    print("🔧 Configurando base de datos...")

    try:
        from sqlalchemy import create_engine, text
        from config.settings import settings
        from config.logging_config import logger

        # Crear engine
        engine = create_engine(settings.DATABASE_URL)

        # Probar conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexión a la base de datos exitosa")

        # Ejecutar migraciones con Alembic
        print("\n🔄 Ejecutando migraciones de base de datos...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print("✅ Migraciones aplicadas correctamente")
            print(result.stdout)
        else:
            print("⚠️  Migraciones ya aplicadas o sin cambios")
            if result.stderr:
                print(result.stderr)

        print("\n✅ Base de datos configurada correctamente")
        return 0

    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(setup_database())
