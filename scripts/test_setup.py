"""
Script de verificación del setup del proyecto.
Verifica que todas las dependencias y servicios estén configurados correctamente.
"""
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))


def verificar_variables_entorno() -> bool:
    """Verifica que todas las variables de entorno necesarias estén configuradas."""
    print("🔍 Verificando variables de entorno...")

    try:
        from config.settings import settings

        variables_requeridas = [
            ("OPENAI_API_KEY", settings.OPENAI_API_KEY),
            ("EVOLUTION_API_KEY", settings.EVOLUTION_API_KEY),
            ("GMAIL_USER", settings.GMAIL_USER),
            ("GMAIL_APP_PASSWORD", settings.GMAIL_APP_PASSWORD),
        ]

        faltantes = []
        for nombre, valor in variables_requeridas:
            if not valor:
                faltantes.append(nombre)

        if faltantes:
            print(f"❌ Variables de entorno faltantes: {', '.join(faltantes)}")
            return False

        print("✅ Variables de entorno configuradas correctamente")
        return True

    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return False


def verificar_openai() -> bool:
    """Verifica conexión con OpenAI API."""
    print("🔍 Verificando conexión con OpenAI...")

    try:
        from openai import OpenAI
        from config.settings import settings

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Di 'Setup correcto'"}],
            max_tokens=10,
        )

        mensaje = response.choices[0].message.content
        print(f"✅ OpenAI API: OK - Respuesta: {mensaje}")
        return True

    except Exception as e:
        print(f"❌ OpenAI API: ERROR - {e}")
        return False


def verificar_evolution_api() -> bool:
    """Verifica conexión con Evolution API."""
    print("🔍 Verificando conexión con Evolution API...")

    try:
        import requests
        from config.settings import settings

        url = f"{settings.EVOLUTION_API_URL}/instance/fetchInstances"
        headers = {"apikey": settings.EVOLUTION_API_KEY}

        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code in [200, 201]:
            print(f"✅ Evolution API: OK (Status {response.status_code})")
            return True
        else:
            print(f"⚠️  Evolution API: Status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠️  Evolution API: No disponible (¿está corriendo el contenedor?)")
        print("   Ejecuta: make docker-up")
        return False
    except Exception as e:
        print(f"❌ Evolution API: ERROR - {e}")
        return False


def verificar_estructura_proyecto() -> bool:
    """Verifica que la estructura de carpetas esté correcta."""
    print("🔍 Verificando estructura del proyecto...")

    directorios_requeridos = [
        "src/agents",
        "src/database",
        "src/services",
        "src/api",
        "src/schemas",
        "src/core",
        "src/prompts",
        "frontend",
        "tests",
        "scripts",
        "docs",
        "logs",
        "config",
    ]

    faltantes = []
    for directorio in directorios_requeridos:
        if not Path(directorio).exists():
            faltantes.append(directorio)

    if faltantes:
        print(f"❌ Directorios faltantes: {', '.join(faltantes)}")
        return False

    print("✅ Estructura del proyecto correcta")
    return True


def verificar_archivos_configuracion() -> bool:
    """Verifica que los archivos de configuración existan."""
    print("🔍 Verificando archivos de configuración...")

    archivos_requeridos = [
        ".env",
        ".gitignore",
        "pyproject.toml",
        "requirements.txt",
        "Makefile",
        "config/settings.py",
        "config/logging_config.py",
    ]

    faltantes = []
    for archivo in archivos_requeridos:
        if not Path(archivo).exists():
            faltantes.append(archivo)

    if faltantes:
        print(f"❌ Archivos faltantes: {', '.join(faltantes)}")
        return False

    print("✅ Archivos de configuración presentes")
    return True


def main() -> int:
    """Ejecuta todas las verificaciones."""
    print("=" * 80)
    print("🚀 VERIFICACIÓN DE SETUP - PEI COMPRAS AI")
    print("=" * 80)
    print()

    resultados = {
        "Estructura del proyecto": verificar_estructura_proyecto(),
        "Archivos de configuración": verificar_archivos_configuracion(),
        "Variables de entorno": verificar_variables_entorno(),
        "OpenAI API": verificar_openai(),
        "Evolution API": verificar_evolution_api(),
    }

    print()
    print("=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)

    for nombre, resultado in resultados.items():
        status = "✅ OK" if resultado else "❌ FALLÓ"
        print(f"{nombre}: {status}")

    total_exitosos = sum(resultados.values())
    total = len(resultados)

    print()
    print(f"✅ {total_exitosos}/{total} verificaciones pasaron")

    if total_exitosos == total:
        print()
        print("🎉 ¡Setup completado exitosamente!")
        return 0
    else:
        print()
        print("⚠️  Algunas verificaciones fallaron. Revisa la configuración.")
        print()
        print("💡 Tips:")
        print("   - Asegúrate de tener un archivo .env con todas las variables")
        print("   - Para Evolution API: ejecuta 'make docker-up'")
        print("   - Verifica que tu API key de OpenAI sea válida")
        return 1


if __name__ == "__main__":
    sys.exit(main())
