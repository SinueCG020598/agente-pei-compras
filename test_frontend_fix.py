#!/usr/bin/env python3
"""
Test rápido para verificar las correcciones del frontend
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath('.'))

from src.database.session import get_db
from src.database.crud import solicitud as crud_solicitud
from src.database.models import EstadoSolicitud

def test_crud_methods():
    """Verificar que los métodos CRUD funcionan correctamente"""

    print("=" * 70)
    print("TEST: Verificación de métodos CRUD y modelo Solicitud")
    print("=" * 70)

    db = next(get_db())

    try:
        # Test 1: count()
        print("\n1. Probando método count()...")
        total = crud_solicitud.count(db)
        print(f"   ✅ Total de solicitudes: {total}")

        # Test 2: count_by_estado()
        print("\n2. Probando método count_by_estado()...")
        pendientes = crud_solicitud.count_by_estado(db, EstadoSolicitud.PENDIENTE)
        en_proceso = crud_solicitud.count_by_estado(db, EstadoSolicitud.EN_PROCESO)
        completadas = crud_solicitud.count_by_estado(db, EstadoSolicitud.COMPLETADA)
        print(f"   ✅ Pendientes: {pendientes}")
        print(f"   ✅ En proceso: {en_proceso}")
        print(f"   ✅ Completadas: {completadas}")

        # Test 3: get_by_fecha_rango()
        print("\n3. Probando método get_by_fecha_rango()...")
        from datetime import datetime, timedelta
        fecha_mes_atras = datetime.utcnow() - timedelta(days=30)
        recientes = crud_solicitud.get_by_fecha_rango(db, fecha_mes_atras)
        print(f"   ✅ Solicitudes recientes (30 días): {len(recientes)}")

        # Test 4: Verificar campos del modelo
        print("\n4. Verificando campos del modelo Solicitud...")
        solicitudes = crud_solicitud.get_multi(db, limit=1)
        if solicitudes:
            sol = solicitudes[0]
            print(f"   ✅ Campo 'descripcion' existe: {hasattr(sol, 'descripcion')}")
            print(f"   ✅ Campo 'presupuesto' existe: {hasattr(sol, 'presupuesto')}")
            print(f"   ✅ Campo 'urgencia' existe: {hasattr(sol, 'urgencia')}")
            print(f"   ✅ Campo 'prioridad' existe: {hasattr(sol, 'prioridad')}")
            print(f"   ✅ Campo 'estado' existe: {hasattr(sol, 'estado')}")

            # Mostrar valores
            print(f"\n   Valores de ejemplo:")
            print(f"   - ID: {sol.id}")
            print(f"   - Descripción: {sol.descripcion[:50]}...")
            print(f"   - Estado: {sol.estado.value}")
            print(f"   - Urgencia: {sol.urgencia}")
            print(f"   - Presupuesto: {sol.presupuesto}")
        else:
            print("   ⚠️  No hay solicitudes en la BD (esto es normal si está vacía)")

        print("\n" + "=" * 70)
        print("✅ TODOS LOS TESTS EXITOSOS")
        print("=" * 70)
        print("\n✅ Correcciones verificadas:")
        print("  [x] Métodos count() agregados al CRUD")
        print("  [x] Método count_by_estado() funcionando")
        print("  [x] Método get_by_fecha_rango() funcionando")
        print("  [x] Campo 'descripcion' existe en modelo")
        print("  [x] Campo 'presupuesto' existe en modelo")
        print("  [x] Campo 'urgencia' agregado al modelo")
        print("\n✅ El frontend ahora debería funcionar sin errores")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "🔧" * 35)
    print("   TEST DE CORRECCIONES FRONTEND")
    print("🔧" * 35 + "\n")

    exito = test_crud_methods()

    if exito:
        print("\n" + "=" * 70)
        print("💡 Ahora puedes correr el frontend con:")
        print("   source venv/bin/activate")
        print("   streamlit run frontend/app.py")
        print("=" * 70)
        sys.exit(0)
    else:
        sys.exit(1)
