#!/usr/bin/env python3
"""
Script de prueba para OpenAI Service.
Requiere OPENAI_API_KEY configurada en .env
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import openai_service


def test_analizar_solicitud():
    """Prueba el análisis de solicitud."""
    print("\n" + "=" * 60)
    print("🧪 TEST 1: Análisis de Solicitud")
    print("=" * 60)

    descripcion = """
    Necesitamos 50 laptops HP para el equipo de desarrollo.
    Especificaciones:
    - 16GB RAM
    - SSD 512GB
    - Procesador Intel i7
    - Presupuesto: $50.000.000 CLP
    - Urgente para fin de mes
    """

    print(f"\n📝 Solicitud original:\n{descripcion}")

    try:
        resultado = openai_service.analizar_solicitud(
            descripcion=descripcion,
            usuario_nombre="Juan Pérez"
        )

        print("\n✅ Análisis completado:")
        print(f"   Productos: {resultado.productos}")
        print(f"   Categoría: {resultado.categoria}")
        print(f"   Cantidad: {resultado.cantidad_estimada}")
        print(f"   Presupuesto: ${resultado.presupuesto_estimado:,.0f}" if resultado.presupuesto_estimado else "   Presupuesto: No especificado")
        print(f"   Urgencia: {resultado.urgencia}")
        print(f"   Especificaciones: {resultado.especificaciones}")
        print(f"   Keywords: {resultado.keywords}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_generar_rfq():
    """Prueba la generación de RFQ."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Generación de RFQ")
    print("=" * 60)

    try:
        rfq = openai_service.generar_rfq(
            producto="Laptop HP",
            especificaciones=[
                "16GB RAM DDR4",
                "SSD 512GB NVMe",
                "Procesador Intel i7 11va gen",
                "Pantalla 15.6 pulgadas Full HD",
                "Windows 11 Pro"
            ],
            cantidad=50,
            proveedor_nombre="Tech Solutions Chile",
            proveedor_categoria="tecnologia",
            tono="profesional"
        )

        print("\n✅ RFQ generado:")
        print("-" * 60)
        print(rfq)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def test_analizar_cotizacion():
    """Prueba el análisis de cotización."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Análisis de Cotización")
    print("=" * 60)

    email_cotizacion = """
    Estimado cliente,

    Gracias por su solicitud. Adjuntamos nuestra cotización:

    Producto: Laptop HP EliteBook 840 G8
    Cantidad: 50 unidades
    Precio unitario: $900.000 CLP
    Precio total: $45.000.000 CLP (IVA incluido)

    Especificaciones:
    - 16GB RAM DDR4
    - SSD 512GB NVMe
    - Intel Core i7 11va gen
    - Pantalla 15.6" Full HD
    - Windows 11 Pro incluido
    - Garantía: 3 años on-site

    Tiempo de entrega: 15 días hábiles
    Forma de pago: 50% anticipo, 50% contra entrega

    Saludos,
    Tech Solutions Chile
    """

    print(f"\n📧 Email de cotización:\n{email_cotizacion[:200]}...")

    try:
        analisis = openai_service.analizar_cotizacion(
            contenido_email=email_cotizacion,
            proveedor_nombre="Tech Solutions Chile",
            solicitud_descripcion="50 laptops HP con 16GB RAM"
        )

        print("\n✅ Análisis completado:")
        print(f"   Proveedor: {analisis.proveedor}")
        print(f"   Precio total: ${analisis.precio_total:,.0f}")
        print(f"   Tiempo entrega: {analisis.tiempo_entrega_dias} días")
        print(f"   Score calidad: {analisis.calidad_score}/10")
        print(f"   Ventajas: {', '.join(analisis.ventajas)}")
        print(f"   Desventajas: {', '.join(analisis.desventajas)}")
        print(f"   Recomendación: {analisis.recomendacion}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "=" * 60)
    print("🚀 PRUEBAS DE OPENAI SERVICE")
    print("=" * 60)

    # Verificar API key
    if not openai_service.api_key or openai_service.api_key.startswith("sk-proj-xxx"):
        print("\n❌ ERROR: OPENAI_API_KEY no configurada")
        print("\nPasos para configurar:")
        print("1. Ve a https://platform.openai.com/api-keys")
        print("2. Crea una nueva API key")
        print("3. Edita el archivo .env y agrega:")
        print("   OPENAI_API_KEY=sk-proj-tu-key-aqui")
        print("\n4. Vuelve a ejecutar este script")
        return

    print(f"\n✅ API Key configurada: {openai_service.api_key[:20]}...")
    print(f"✅ Modelo mini: {openai_service.model_mini}")
    print(f"✅ Modelo full: {openai_service.model_full}")

    # Ejecutar tests
    resultados = []
    resultados.append(("Análisis de Solicitud", test_analizar_solicitud()))
    resultados.append(("Generación de RFQ", test_generar_rfq()))
    resultados.append(("Análisis de Cotización", test_analizar_cotizacion()))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado} - {nombre}")

    print(f"\nTotal: {exitosos}/{total} pruebas exitosas")

    if exitosos == total:
        print("\n🎉 ¡Todas las pruebas pasaron! OpenAI Service funciona correctamente.")
    else:
        print(f"\n⚠️  {total - exitosos} prueba(s) fallaron. Revisa los errores arriba.")


if __name__ == "__main__":
    main()
