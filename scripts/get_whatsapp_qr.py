#!/usr/bin/env python3
"""
Script para obtener y mostrar el QR code de WhatsApp desde Evolution API
"""

import requests
import time
import json
import base64
import sys
from pathlib import Path

# Configuración
API_URL = "http://localhost:8080"
API_KEY = "e25391171441103e98ada7e0db73744f454d935b3ce70fd8ffe7a240b23f8088"
INSTANCE_NAME = "pei-compras"

headers = {
    "apikey": API_KEY,
    "Content-Type": "application/json"
}

def delete_instance():
    """Elimina la instancia existente"""
    print(f"🗑️  Eliminando instancia existente '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/delete/{INSTANCE_NAME}"
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            print("✅ Instancia eliminada")
        else:
            print(f"⚠️  Instancia no existía o ya fue eliminada")
    except Exception as e:
        print(f"⚠️  Error al eliminar: {e}")
    time.sleep(2)

def create_instance():
    """Crea una nueva instancia"""
    print(f"\n🔧 Creando nueva instancia '{INSTANCE_NAME}'...")
    url = f"{API_URL}/instance/create"
    data = {
        "instanceName": INSTANCE_NAME,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201 or response.status_code == 200:
            result = response.json()
            print(f"✅ Instancia creada: {result.get('instance', {}).get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Error al crear instancia: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def get_qr_code(max_attempts=30):
    """Intenta obtener el QR code con reintentos"""
    print(f"\n🔍 Buscando QR code (intentos: {max_attempts})...")
    url = f"{API_URL}/instance/connect/{INSTANCE_NAME}"

    for attempt in range(max_attempts):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()

                # Verificar si tiene QR
                if "base64" in data:
                    print("\n✅ ¡QR CODE ENCONTRADO!")
                    return data["base64"]

                # Verificar contador
                count = data.get("count", 0)
                if count > 0:
                    print(f"⏳ QR generándose... (count: {count})")
                else:
                    print(f"⏳ Esperando QR... (intento {attempt + 1}/{max_attempts})")

            time.sleep(2)
        except Exception as e:
            print(f"⚠️  Error en intento {attempt + 1}: {e}")
            time.sleep(2)

    print("\n❌ No se pudo obtener el QR code después de todos los intentos")
    return None

def save_qr_image(base64_data):
    """Guarda el QR como imagen PNG"""
    try:
        # Extraer solo la parte base64 (después de "data:image/png;base64,")
        if "base64," in base64_data:
            base64_str = base64_data.split("base64,")[1]
        else:
            base64_str = base64_data

        # Decodificar
        image_data = base64.b64decode(base64_str)

        # Guardar
        output_path = Path.home() / "whatsapp_qr.png"
        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"\n💾 QR guardado en: {output_path}")
        print(f"\n📱 INSTRUCCIONES:")
        print(f"   1. Abre la imagen en: {output_path}")
        print(f"   2. En WhatsApp móvil, ve a: Configuración > Dispositivos vinculados")
        print(f"   3. Toca 'Vincular un dispositivo'")
        print(f"   4. Escanea el QR code")

        return output_path
    except Exception as e:
        print(f"❌ Error al guardar imagen: {e}")
        return None

def check_connection_status():
    """Verifica el estado de conexión"""
    print("\n🔍 Verificando estado de conexión...")
    url = f"{API_URL}/instance/connectionState/{INSTANCE_NAME}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            state = data.get("instance", {}).get("state", "unknown")
            print(f"   Estado: {state}")

            if state == "open":
                print("   ✅ ¡WhatsApp conectado exitosamente!")
                return True
            elif state == "connecting":
                print("   ⏳ Conectando...")
                return False
            else:
                print("   ⚠️  No conectado")
                return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 EVOLUTION API - WHATSAPP QR CODE GENERATOR")
    print("=" * 60)

    # Paso 1: Eliminar instancia existente
    delete_instance()

    # Paso 2: Crear nueva instancia
    if not create_instance():
        print("\n❌ Falló la creación de instancia. Abortando.")
        sys.exit(1)

    # Paso 3: Esperar un poco para que se inicialice
    print("\n⏳ Esperando inicialización (10 segundos)...")
    time.sleep(10)

    # Paso 4: Obtener QR code
    qr_base64 = get_qr_code(max_attempts=30)

    if qr_base64:
        # Guardar imagen
        image_path = save_qr_image(qr_base64)

        if image_path:
            # Esperar a que el usuario escanee
            print("\n⏳ Esperando que escanees el QR...")
            print("   Presiona Ctrl+C cuando hayas escaneado el código\n")

            try:
                for i in range(60):  # Esperar hasta 2 minutos
                    time.sleep(2)
                    if check_connection_status():
                        print("\n🎉 ¡WhatsApp conectado exitosamente!")
                        break
            except KeyboardInterrupt:
                print("\n\n⏸️  Proceso interrumpido por el usuario")
                check_connection_status()
    else:
        print("\n❌ No se pudo obtener el QR code.")
        print("\n🔍 Debugging:")
        print("   1. Verifica que Evolution API esté corriendo: docker ps")
        print("   2. Revisa los logs: docker logs evolution-api --tail 50")
        sys.exit(1)

if __name__ == "__main__":
    main()
