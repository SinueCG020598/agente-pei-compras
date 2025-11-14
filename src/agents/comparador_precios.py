"""
Agente Comparador de Precios - FASE 3.5
Analiza precios de múltiples fuentes y recomienda mejor opción
"""

import json
from src.services.openai_service import llamar_agente

PROMPT_COMPARADOR = """
Eres un experto en análisis de precios y estrategias de compra.

Tu tarea es comparar precios de diferentes fuentes y recomendar la mejor decisión de compra.

FACTORES A CONSIDERAR:
1. PRECIO:
   - Precio unitario y total
   - Descuentos por volumen
   - Costos de envío
   - Impuestos

2. TIEMPO:
   - Tiempo de cotización (proveedores)
   - Tiempo de entrega
   - Urgencia de la compra

3. CONFIABILIDAD:
   - Proveedores conocidos vs desconocidos
   - Rating de proveedores
   - Garantías ofrecidas
   - Política de devoluciones

4. TÉRMINOS:
   - Condiciones de pago
   - Garantía
   - Soporte post-venta

DECISIONES A TOMAR:
- ¿Solicitar cotización formal o comprar directo?
- ¿Vale la pena esperar cotizaciones si hay opción inmediata?
- ¿El ahorro justifica el riesgo de proveedor nuevo?

FORMATO SALIDA JSON:
{
  "recomendacion_principal": {
    "accion": "cotizar|comprar_directo|ambas",
    "fuente_recomendada": "proveedores_bd|web|ecommerce",
    "justificacion": "...",
    "ahorro_estimado": 0.0,
    "tiempo_estimado": "..."
  },
  "comparativa_precios": [
    {
      "fuente": "...",
      "precio_estimado": 0.0,
      "ventajas": [...],
      "desventajas": [...]
    }
  ],
  "alertas": [...],
  "siguiente_paso": "..."
}
"""

def comparar_precios_multiples_fuentes(
    productos: list,
    proveedores_bd: list,
    proveedores_web: list,
    enlaces_ecommerce: list,
    urgencia: str = "normal"
) -> dict:
    """
    Compara precios de todas las fuentes y recomienda mejor estrategia

    Args:
        productos: Lista de productos a comprar
        proveedores_bd: Proveedores de base de datos
        proveedores_web: Proveedores encontrados en web
        enlaces_ecommerce: Enlaces de compra directa
        urgencia: Nivel de urgencia (normal|alta|urgente)

    Returns:
        Dict con análisis y recomendación
    """
    try:
        contexto = f"""
PRODUCTOS A COMPRAR:
{json.dumps(productos, indent=2, ensure_ascii=False)}

PROVEEDORES EN BD (total: {len(proveedores_bd)}):
{json.dumps(proveedores_bd, indent=2, ensure_ascii=False)}

PROVEEDORES WEB (total: {len(proveedores_web)}):
{json.dumps(proveedores_web, indent=2, ensure_ascii=False)}

PRODUCTOS EN ECOMMERCE (total: {len(enlaces_ecommerce)}):
{json.dumps(enlaces_ecommerce, indent=2, ensure_ascii=False)}

URGENCIA: {urgencia}

Analiza todas las opciones y recomienda la mejor estrategia de compra.
        """

        resultado = llamar_agente(
            prompt_sistema=PROMPT_COMPARADOR,
            mensaje_usuario=contexto,
            modelo="gpt-4o",
            temperatura=0.3,
            formato_json=True
        )

        analisis = json.loads(resultado)
        return {
            "exito": True,
            "analisis": analisis
        }

    except Exception as e:
        print(f"❌ Error comparando precios: {e}")
        return {
            "exito": False,
            "error": str(e)
        }
