"""
Agente Investigador - FASE 3
Busca proveedores en BD local, web y ecommerce
"""

import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.models import Proveedor
from src.services.openai_service import llamar_agente
from src.services.search_service import search_service
from config.settings import settings

# Leer prompt del archivo
PROMPT_PATH = os.path.join(os.path.dirname(__file__), "../prompts/investigador_prompt.txt")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    PROMPT_INVESTIGADOR = f.read()

# Configurar sesión de BD
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def buscar_proveedores(productos: list, usar_web: bool = True) -> dict:
    """
    Busca proveedores adecuados para lista de productos
    MEJORADO: Ahora busca en BD local Y en internet

    Args:
        productos: Lista de productos con nombre, cantidad, categoría
        usar_web: Si True, también busca en internet (default: True)

    Returns:
        Dict con proveedores de BD, web y enlaces de ecommerce
    """
    db = SessionLocal()

    try:
        # 1. Obtener todos los proveedores de BD LOCAL (verificados preferentemente)
        proveedores_bd = db.query(Proveedor).all()

        if not proveedores_bd:
            proveedores_bd = []

        # Preparar info para el agente
        info_proveedores_bd = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "categoria": p.categoria,
                "rating": p.rating,
                "email": p.email,
                "telefono": p.telefono,
                "notas": p.notas,
                "es_verificado": p.es_verificado,
                "fuente": "base_de_datos"
            }
            for p in proveedores_bd
        ]

        # 2. NUEVO: Buscar en INTERNET si está habilitado
        proveedores_web = []
        enlaces_ecommerce = []

        if usar_web and search_service.is_available():
            print("🌐 Buscando proveedores en internet...")

            for producto in productos:
                nombre_producto = producto.get("nombre", "")

                # Buscar proveedores en web
                try:
                    web_results = search_service.buscar_proveedores_web(
                        nombre_producto,
                        ubicacion="México",
                        num_resultados=5
                    )
                    proveedores_web.extend(web_results)
                    print(f"  ✓ Encontrados {len(web_results)} proveedores web para {nombre_producto}")
                except Exception as e:
                    print(f"  ⚠️  Error buscando proveedores web: {e}")

                # Buscar en marketplaces
                try:
                    ecommerce_results = search_service.buscar_en_ecommerce(nombre_producto)
                    enlaces_ecommerce.extend(ecommerce_results)
                    print(f"  ✓ Encontrados {len(ecommerce_results)} productos en ecommerce")
                except Exception as e:
                    print(f"  ⚠️  Error buscando en ecommerce: {e}")

        # 3. Preparar mensaje para el agente con TODAS las fuentes
        mensaje = f"""
PRODUCTOS A COMPRAR:
{json.dumps(productos, indent=2, ensure_ascii=False)}

PROVEEDORES EN BASE DE DATOS LOCAL ({len(info_proveedores_bd)}):
{json.dumps(info_proveedores_bd, indent=2, ensure_ascii=False)}

PROVEEDORES ENCONTRADOS EN WEB ({len(proveedores_web)}):
{json.dumps(proveedores_web, indent=2, ensure_ascii=False)}

PRODUCTOS EN ECOMMERCE ({len(enlaces_ecommerce)}):
{json.dumps(enlaces_ecommerce, indent=2, ensure_ascii=False)}

INSTRUCCIONES IMPORTANTES:
1. Para cada proveedor recomendado, incluye TODA la información de contacto disponible:
   - Proveedores BD: proveedor_id, email, telefono, ciudad, rating
   - Proveedores Web: nombre completo, URL completa, descripción
   - Ecommerce: marketplace, producto, URL COMPLETA de compra, precio

2. Analiza y recomienda:
   - Qué proveedores de BD contactar (con email y teléfono)
   - Qué proveedores web investigar (con URL completa)
   - Qué productos comprar directo en ecommerce (con URL de compra)
   - Cuál es la estrategia más eficiente (precio vs tiempo)

3. En "como_contactar" describe específicamente cómo proceder con cada proveedor.
        """

        # 4. Llamar agente con contexto completo
        resultado = llamar_agente(
            prompt_sistema=PROMPT_INVESTIGADOR,
            mensaje_usuario=mensaje,
            modelo="gpt-4o-mini",
            temperatura=0.4,
            formato_json=True
        )

        # 5. Parsear resultado
        recomendaciones = json.loads(resultado)

        # 6. Enriquecer con datos completos de proveedores BD
        for rec in recomendaciones.get("proveedores_recomendados", []):
            if rec.get("fuente") == "base_de_datos":
                proveedor = db.query(Proveedor).filter(
                    Proveedor.id == rec["proveedor_id"]
                ).first()

                if proveedor:
                    rec["proveedor_data"] = {
                        "nombre": proveedor.nombre,
                        "email": proveedor.email,
                        "telefono": proveedor.telefono,
                        "ciudad": proveedor.ciudad
                    }

        # 7. Retornar resultado completo con TODAS las fuentes
        return {
            "proveedores_bd": info_proveedores_bd,
            "proveedores_web": proveedores_web,
            "enlaces_ecommerce": enlaces_ecommerce,
            "recomendaciones": recomendaciones,
            "resumen": {
                "total_proveedores_bd": len(info_proveedores_bd),
                "total_proveedores_web": len(proveedores_web),
                "total_enlaces_ecommerce": len(enlaces_ecommerce),
                "busqueda_web_activa": usar_web and search_service.is_available()
            }
        }

    except json.JSONDecodeError as e:
        print(f"Error parseando JSON: {e}")
        return {
            "error": "Error parseando respuesta del agente",
            "proveedores_recomendados": []
        }

    except Exception as e:
        print(f"Error buscando proveedores: {e}")
        return {
            "error": str(e),
            "proveedores_recomendados": []
        }

    finally:
        db.close()
