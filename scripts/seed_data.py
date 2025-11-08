"""
Script para poblar la base de datos con datos iniciales de prueba.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.seed_proveedores import seed_proveedores
from config.logging_config import logger, setup_logging


def main() -> int:
    """
    Ejecuta el seed de datos en la base de datos.

    Returns:
        0 si exitoso, 1 si hay error
    """
    setup_logging()

    try:
        logger.info("=" * 80)
        logger.info("🌱 SEED DE DATOS - PEI COMPRAS AI")
        logger.info("=" * 80)

        # Seed de proveedores
        seed_proveedores()

        logger.info("\n" + "=" * 80)
        logger.info("✅ Seed de datos completado exitosamente")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"\n❌ Error en seed de datos: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
