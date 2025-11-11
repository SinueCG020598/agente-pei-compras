#!/usr/bin/env python3
"""
Script maestro para probar todos los servicios de Fase 2.
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import (
    openai_service,
    whatsapp_service,
    email_service,
    search_service,
)


def verificar_configuracion():
    """Verifica qué servicios están configurados."""
    print("\n" + "=" * 70)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 70)

    servicios = {
        "OpenAI": {
            "configurado": bool(openai_service.api_key and not openai_service.api_key.startswith("sk-proj-xxx")),
            "necesario": "OBLIGATORIO para pruebas",
            "url": "https://platform.openai.com/api-keys"
        },
        "WhatsApp": {
            "configurado": bool(whatsapp_service.api_key and whatsapp_service.api_key != "tu-api-key-super-secreta-aqui"),
            "necesario": "Opcional (requiere Docker)",
            "url": "docker compose up -d"
        },
        "Email": {
            "configurado": bool(email_service.email_user and email_service.email_user != "tu-email@gmail.com"),
            "necesario": "Opcional",
            "url": "https://myaccount.google.com/apppasswords"
        },
        "Search": {
            "configurado": search_service.is_available(),
            "necesario": "Opcional",
            "url": "https://serper.dev"
        }
    }

    print("\nEstado de servicios:\n")

    for nombre, info in servicios.items():
        estado = "✅ Configurado" if info["configurado"] else "❌ No configurado"
        print(f"{nombre:15s} {estado:20s} ({info['necesario']})")

        if not info["configurado"]:
            print(f"{'':15s} 📝 Configurar en: {info['url']}")

    print("\n" + "-" * 70)

    # Verificar si al menos OpenAI está configurado
    if not servicios["OpenAI"]["configurado"]:
        print("\n⚠️  ADVERTENCIA: OpenAI NO está configurado")
        print("   Es NECESARIO para las pruebas principales\n")
        print("Pasos:")
        print("1. Edita el archivo .env")
        print("2. Agrega: OPENAI_API_KEY=sk-proj-tu-key-aqui")
        print("3. Guarda y vuelve a ejecutar\n")
        return False

    return True


def probar_flujo_completo():
    """Prueba un flujo completo de compra."""
    print("\n" + "=" * 70)
    print("🎯 FLUJO COMPLETO: Solicitud → Análisis → RFQ")
    print("=" * 70)

    # 1. Solicitud original
    solicitud_texto = """
    Necesitamos comprar 20 sillas ergonómicas para la oficina nueva.
    Requisitos:
    - Respaldo ajustable
    - Soporte lumbar
    - Brazos regulables
    - Base con ruedas
    - Presupuesto: máximo $10.000.000 CLP
    - Necesitamos para el 15 de diciembre
    """

    print(f"\n1️⃣  SOLICITUD ORIGINAL:")
    print("-" * 70)
    print(solicitud_texto)

    # 2. Análisis con IA
    print(f"\n2️⃣  ANÁLISIS CON IA...")

    try:
        analisis = openai_service.analizar_solicitud(solicitud_texto)

        print("✅ Solicitud analizada:")
        print(f"   • Productos: {', '.join(analisis.productos)}")
        print(f"   • Categoría: {analisis.categoria}")
        print(f"   • Cantidad: {analisis.cantidad_estimada}")
        print(f"   • Urgencia: {analisis.urgencia}")
        print(f"   • Especificaciones: {', '.join(analisis.especificaciones[:3])}...")

    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False

    # 3. Generación de RFQ
    print(f"\n3️⃣  GENERACIÓN DE RFQ...")

    try:
        rfq = openai_service.generar_rfq(
            producto=analisis.productos[0],
            especificaciones=analisis.especificaciones,
            cantidad=analisis.cantidad_estimada or 20,
            proveedor_nombre="Muebles Corporativos SA",
            proveedor_categoria=analisis.categoria
        )

        print("✅ RFQ generado:")
        print("-" * 70)
        print(rfq[:400] + "..." if len(rfq) > 400 else rfq)
        print("-" * 70)

    except Exception as e:
        print(f"❌ Error generando RFQ: {e}")
        return False

    # 4. Simular cotización
    print(f"\n4️⃣  ANÁLISIS DE COTIZACIÓN (simulada)...")

    cotizacion_simulada = """
    Estimado cliente,

    Adjuntamos cotización para sillas ergonómicas:

    Producto: Silla Ergonómica Ejecutiva Pro
    Cantidad: 20 unidades
    Precio unitario: $450.000 CLP
    Precio total: $9.000.000 CLP

    Características:
    - Respaldo mesh ergonómico ajustable
    - Soporte lumbar premium
    - Brazos 4D regulables
    - Base cromada con ruedas
    - Garantía: 5 años

    Entrega: 10 días hábiles
    Pago: 30% anticipo, 70% contra entrega

    Saludos,
    Muebles Corporativos SA
    """

    try:
        analisis_cot = openai_service.analizar_cotizacion(
            contenido_email=cotizacion_simulada,
            proveedor_nombre="Muebles Corporativos SA",
            solicitud_descripcion="20 sillas ergonómicas"
        )

        print("✅ Cotización analizada:")
        print(f"   • Precio: ${analisis_cot.precio_total:,.0f}")
        print(f"   • Entrega: {analisis_cot.tiempo_entrega_dias} días")
        print(f"   • Calidad: {analisis_cot.calidad_score}/10")
        print(f"   • Recomendación: {analisis_cot.recomendacion}")

    except Exception as e:
        print(f"❌ Error analizando cotización: {e}")
        return False

    print("\n✅ Flujo completo ejecutado exitosamente!")
    return True


def main():
    """Función principal."""
    print("\n" + "=" * 70)
    print("🚀 PRUEBA INTEGRAL DE SERVICIOS - FASE 2")
    print("=" * 70)

    # 1. Verificar configuración
    if not verificar_configuracion():
        print("\n❌ Configuración incompleta. Configura OpenAI primero.\n")
        return

    # 2. Probar flujo completo
    print("\n" + "=" * 70)
    print("Ejecutando prueba de flujo completo...")
    print("=" * 70)

    if probar_flujo_completo():
        print("\n" + "=" * 70)
        print("🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("=" * 70)
        print("\n✅ Los servicios de Fase 2 funcionan correctamente")
        print("\n📌 Próximos pasos:")
        print("   1. Configura servicios opcionales (WhatsApp, Email, Search)")
        print("   2. Prueba con datos reales")
        print("   3. Continúa con Fase 3: Agentes AI")
        print()
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.\n")


if __name__ == "__main__":
    main()
