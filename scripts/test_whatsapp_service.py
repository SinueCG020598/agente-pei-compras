#!/usr/bin/env python3
"""
Script de prueba para WhatsApp Service.
NO requiere Evolution API corriendo (solo prueba funciones básicas).
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import whatsapp_service


def test_format_phone():
    """Prueba el formateo de números telefónicos."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Formateo de Números Telefónicos")
    print("=" * 60)

    numeros = [
        "+56 9 1234 5678",
        "56-9-1234-5678",
        "912345678",
        "56912345678",
        "+1 (555) 123-4567",
    ]

    print("\nProbando formateo:")
    for num in numeros:
        formateado = whatsapp_service.format_phone_number(num)
        print(f"  {num:20s} → {formateado}")

    return True


def test_process_webhook():
    """Prueba el procesamiento de webhooks."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Procesamiento de Webhooks")
    print("=" * 60)

    # Webhook de mensaje de texto
    webhook_data = {
        "event": "messages.upsert",
        "instance": "pei-compras",
        "data": {
            "key": {
                "remoteJid": "56912345678@s.whatsapp.net",
                "id": "msg-abc-123",
            },
            "message": {
                "conversation": "Hola, necesito una cotización para laptops"
            },
            "messageTimestamp": 1234567890,
        },
    }

    print("\n📥 Webhook recibido (simulado):")
    print(f"   Evento: {webhook_data['event']}")
    print(f"   Instancia: {webhook_data['instance']}")

    mensaje = whatsapp_service.process_webhook(webhook_data)

    if mensaje:
        print("\n✅ Mensaje procesado:")
        print(f"   De: {mensaje.from_number}")
        print(f"   ID: {mensaje.message_id}")
        print(f"   Tipo: {mensaje.message_type}")
        print(f"   Contenido: {mensaje.body}")
        return True
    else:
        print("\n❌ No se pudo procesar el webhook")
        return False


def test_instance_info():
    """Muestra información de configuración."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Información de Configuración")
    print("=" * 60)

    print(f"\n✅ Configuración:")
    print(f"   API URL: {whatsapp_service.api_url}")
    print(f"   Instancia: {whatsapp_service.instance_name}")
    print(f"   API Key: {whatsapp_service.api_key[:20]}..." if whatsapp_service.api_key else "   API Key: No configurada")

    print(f"\n📝 Nota: Para probar envío de mensajes reales:")
    print(f"   1. Instala Evolution API con Docker:")
    print(f"      docker compose up -d")
    print(f"   2. Configura EVOLUTION_API_KEY en .env")
    print(f"   3. Conecta WhatsApp escaneando el QR code")

    return True


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "=" * 60)
    print("🚀 PRUEBAS DE WHATSAPP SERVICE")
    print("=" * 60)

    print("\n⚠️  Nota: Estas son pruebas SIN conexión a Evolution API")
    print("   Solo prueban funciones de formateo y procesamiento")

    # Ejecutar tests
    resultados = []
    resultados.append(("Formateo de Números", test_format_phone()))
    resultados.append(("Procesamiento Webhooks", test_process_webhook()))
    resultados.append(("Configuración", test_instance_info()))

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
        print("\n🎉 ¡Todas las pruebas básicas pasaron!")
        print("\n📌 Próximos pasos para pruebas completas:")
        print("   1. Instalar Evolution API: make docker-up")
        print("   2. Conectar WhatsApp (escanear QR)")
        print("   3. Probar envío de mensajes reales")


if __name__ == "__main__":
    main()
