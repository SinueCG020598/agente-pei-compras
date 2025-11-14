#!/usr/bin/env python3
"""
Script para actualizar registros con urgencia=None a urgencia="normal"
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.database.session import get_db
from src.database.models import Solicitud

def fix_urgencia_none():
    """Actualiza registros con urgencia=None a urgencia='normal'"""

    print("=" * 70)
    print("FIX: Actualizando registros con urgencia=None")
    print("=" * 70)

    db = next(get_db())

    try:
        # Contar registros con urgencia=None
        count_none = db.query(Solicitud).filter(Solicitud.urgencia == None).count()

        if count_none == 0:
            print("\n✅ No hay registros con urgencia=None")
            return True

        print(f"\n📊 Registros con urgencia=None: {count_none}")

        # Actualizar registros
        db.query(Solicitud).filter(Solicitud.urgencia == None).update(
            {"urgencia": "normal"},
            synchronize_session=False
        )

        db.commit()

        # Verificar
        count_after = db.query(Solicitud).filter(Solicitud.urgencia == None).count()
        count_normal = db.query(Solicitud).filter(Solicitud.urgencia == "normal").count()

        print(f"✅ Registros actualizados: {count_none - count_after}")
        print(f"✅ Registros con urgencia='normal': {count_normal}")

        print("\n" + "=" * 70)
        print("✅ ACTUALIZACIÓN EXITOSA")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False


if __name__ == "__main__":
    print("\n" + "🔧" * 35)
    print("   FIX: URGENCIA=NONE → URGENCIA='NORMAL'")
    print("🔧" * 35 + "\n")

    exito = fix_urgencia_none()

    if exito:
        print("\n💡 El frontend ahora debería funcionar sin errores.")
        sys.exit(0)
    else:
        sys.exit(1)
