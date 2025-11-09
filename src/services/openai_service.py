"""
Servicio de integración con OpenAI para procesamiento de lenguaje natural.

Este servicio proporciona funcionalidades para:
- Análisis de solicitudes de compra
- Generación de RFQs personalizados
- Análisis y comparación de cotizaciones
- Chat genérico con GPT
"""
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI, OpenAIError
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


class SolicitudAnalizada(BaseModel):
    """Modelo para solicitud analizada por IA."""

    productos: List[str]
    cantidad_estimada: Optional[int] = None
    categoria: str
    presupuesto_estimado: Optional[float] = None
    urgencia: str  # baja, media, alta
    especificaciones: List[str]
    keywords: List[str]


class CotizacionAnalizada(BaseModel):
    """Modelo para cotización analizada por IA."""

    proveedor: str
    precio_total: float
    tiempo_entrega_dias: int
    calidad_score: float  # 0-10
    ventajas: List[str]
    desventajas: List[str]
    recomendacion: str


class OpenAIService:
    """
    Servicio para interactuar con la API de OpenAI.

    Proporciona métodos de alto nivel para las tareas específicas
    del sistema de compras, así como métodos genéricos para chat.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_mini: Optional[str] = None,
        model_full: Optional[str] = None,
    ):
        """
        Inicializa el servicio de OpenAI.

        Args:
            api_key: API key de OpenAI (usa settings si no se proporciona)
            model_mini: Modelo mini a usar (gpt-4o-mini por defecto)
            model_full: Modelo completo a usar (gpt-4o por defecto)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_mini = model_mini or settings.OPENAI_MODEL_MINI
        self.model_full = model_full or settings.OPENAI_MODEL_FULL

        self.client = OpenAI(api_key=self.api_key)
        logger.info(
            f"OpenAI Service inicializado - Mini: {self.model_mini}, "
            f"Full: {self.model_full}"
        )

    def analizar_solicitud(
        self,
        descripcion: str,
        usuario_nombre: Optional[str] = None,
    ) -> SolicitudAnalizada:
        """
        Analiza una solicitud de compra usando IA.

        Extrae información estructurada de una descripción en lenguaje natural.

        Args:
            descripcion: Descripción de la solicitud en lenguaje natural
            usuario_nombre: Nombre del usuario que hace la solicitud

        Returns:
            SolicitudAnalizada con la información extraída

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
            ValueError: Si la respuesta no se puede parsear
        """
        logger.info(f"Analizando solicitud: {descripcion[:100]}...")

        system_prompt = """Eres un asistente experto en análisis de solicitudes de compra.
Extrae información estructurada de la descripción del usuario.

Categorías válidas: tecnologia, mobiliario, insumos, servicios, equipamiento
Niveles de urgencia: baja, media, alta

Responde SOLO con un JSON válido siguiendo este formato exacto:
{
    "productos": ["lista de productos mencionados"],
    "cantidad_estimada": 100,
    "categoria": "tecnologia",
    "presupuesto_estimado": 1000000.0,
    "urgencia": "media",
    "especificaciones": ["lista de especificaciones técnicas"],
    "keywords": ["palabras clave para búsqueda"]
}"""

        user_prompt = f"Descripción de la solicitud: {descripcion}"
        if usuario_nombre:
            user_prompt = f"Usuario: {usuario_nombre}\n{user_prompt}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_mini,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Más determinístico para extracción
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Respuesta vacía de OpenAI")

            data = json.loads(content)
            resultado = SolicitudAnalizada(**data)

            logger.info(
                f"Solicitud analizada - Categoría: {resultado.categoria}, "
                f"Productos: {len(resultado.productos)}"
            )
            return resultado

        except OpenAIError as e:
            logger.error(f"Error en OpenAI API: {e}")
            raise
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parseando respuesta: {e}")
            raise ValueError(f"No se pudo parsear la respuesta de IA: {e}")

    def generar_rfq(
        self,
        producto: str,
        especificaciones: List[str],
        cantidad: int,
        proveedor_nombre: str,
        proveedor_categoria: str,
        tono: str = "profesional",
    ) -> str:
        """
        Genera un RFQ (Request for Quotation) personalizado.

        Args:
            producto: Nombre del producto o servicio
            especificaciones: Lista de especificaciones técnicas
            cantidad: Cantidad solicitada
            proveedor_nombre: Nombre del proveedor
            proveedor_categoria: Categoría del proveedor
            tono: Tono del mensaje (profesional, amigable, formal)

        Returns:
            Texto del RFQ generado

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
        """
        logger.info(f"Generando RFQ para {producto} - Proveedor: {proveedor_nombre}")

        specs_text = "\n".join([f"- {spec}" for spec in especificaciones])

        system_prompt = f"""Eres un asistente experto en redacción de RFQs (Request for Quotation).
Genera un email profesional solicitando cotización a un proveedor.

Características del email:
- Tono: {tono}
- Claro y conciso
- Incluye toda la información técnica
- Solicita precio, tiempo de entrega y condiciones
- Formato profesional de email

NO uses placeholders como [Tu Nombre] o [Tu Empresa]. Usa "Equipo de Compras PEI"."""

        user_prompt = f"""Genera un RFQ para:

Proveedor: {proveedor_nombre}
Categoría: {proveedor_categoria}
Producto/Servicio: {producto}
Cantidad: {cantidad}

Especificaciones técnicas:
{specs_text}

Información a solicitar:
- Precio unitario y total
- Tiempo de entrega
- Condiciones de pago
- Garantía y soporte
- Cualquier información adicional relevante"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_mini,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,  # Más creativo para redacción
            )

            rfq = response.choices[0].message.content or ""
            logger.info(f"RFQ generado - {len(rfq)} caracteres")
            return rfq

        except OpenAIError as e:
            logger.error(f"Error generando RFQ: {e}")
            raise

    def analizar_cotizacion(
        self,
        contenido_email: str,
        proveedor_nombre: str,
        solicitud_descripcion: str,
    ) -> CotizacionAnalizada:
        """
        Analiza una cotización recibida por email.

        Extrae información estructurada del email de cotización.

        Args:
            contenido_email: Contenido del email con la cotización
            proveedor_nombre: Nombre del proveedor
            solicitud_descripcion: Descripción de la solicitud original

        Returns:
            CotizacionAnalizada con la información extraída

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
            ValueError: Si la respuesta no se puede parsear
        """
        logger.info(f"Analizando cotización de {proveedor_nombre}")

        system_prompt = """Eres un asistente experto en análisis de cotizaciones.
Extrae y analiza información de emails de cotización.

Calcula un score de calidad (0-10) basado en:
- Completitud de la información
- Claridad de los términos
- Profesionalismo
- Garantías ofrecidas

Responde SOLO con un JSON válido siguiendo este formato exacto:
{
    "proveedor": "nombre del proveedor",
    "precio_total": 1000000.0,
    "tiempo_entrega_dias": 15,
    "calidad_score": 8.5,
    "ventajas": ["lista de ventajas de esta cotización"],
    "desventajas": ["lista de desventajas o limitaciones"],
    "recomendacion": "análisis breve con recomendación"
}"""

        user_prompt = f"""Analiza esta cotización:

Proveedor: {proveedor_nombre}
Solicitud original: {solicitud_descripcion}

Email de cotización:
{contenido_email}

Extrae: precio total, tiempo de entrega, ventajas, desventajas, y califica la calidad."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_full,  # Usamos modelo completo para análisis
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Respuesta vacía de OpenAI")

            data = json.loads(content)
            resultado = CotizacionAnalizada(**data)

            logger.info(
                f"Cotización analizada - Precio: ${resultado.precio_total}, "
                f"Score: {resultado.calidad_score}/10"
            )
            return resultado

        except OpenAIError as e:
            logger.error(f"Error analizando cotización: {e}")
            raise
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parseando respuesta: {e}")
            raise ValueError(f"No se pudo parsear la respuesta de IA: {e}")

    def comparar_cotizaciones(
        self,
        cotizaciones: List[Dict[str, Any]],
        criterios: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compara múltiples cotizaciones y genera recomendación.

        Args:
            cotizaciones: Lista de cotizaciones a comparar
            criterios: Pesos para criterios (precio, tiempo, calidad)
                      Ejemplo: {"precio": 0.5, "tiempo": 0.3, "calidad": 0.2}

        Returns:
            Dict con el análisis comparativo y recomendación

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
        """
        logger.info(f"Comparando {len(cotizaciones)} cotizaciones")

        # Criterios por defecto
        if not criterios:
            criterios = {"precio": 0.4, "tiempo": 0.3, "calidad": 0.3}

        system_prompt = """Eres un experto en análisis de cotizaciones y toma de decisiones de compra.
Compara las cotizaciones y genera una recomendación fundamentada.

Considera:
- Relación precio-calidad
- Tiempos de entrega
- Confiabilidad del proveedor
- Riesgos y oportunidades

Sé objetivo y fundamenta tu recomendación con datos."""

        cotizaciones_text = json.dumps(cotizaciones, indent=2, ensure_ascii=False)
        criterios_text = json.dumps(criterios, indent=2)

        user_prompt = f"""Compara estas cotizaciones:

{cotizaciones_text}

Criterios de evaluación (pesos):
{criterios_text}

Genera un análisis comparativo y recomienda la mejor opción."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_full,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
            )

            analisis = response.choices[0].message.content or ""

            logger.info(f"Comparación completada - {len(analisis)} caracteres")
            return {
                "analisis": analisis,
                "num_cotizaciones": len(cotizaciones),
                "criterios_usados": criterios,
            }

        except OpenAIError as e:
            logger.error(f"Error comparando cotizaciones: {e}")
            raise

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_full_model: bool = False,
    ) -> str:
        """
        Método genérico para chat completion.

        Args:
            messages: Lista de mensajes en formato OpenAI
            temperature: Temperatura para la generación (0-2)
            max_tokens: Máximo de tokens en la respuesta
            use_full_model: Si True, usa modelo completo, sino mini

        Returns:
            Contenido de la respuesta

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
        """
        model = self.model_full if use_full_model else self.model_mini

        logger.debug(f"Chat completion - Modelo: {model}, Temp: {temperature}")

        try:
            params: Dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if max_tokens:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)

            content = response.choices[0].message.content or ""
            return content

        except OpenAIError as e:
            logger.error(f"Error en chat completion: {e}")
            raise

    def extraer_json(
        self,
        prompt: str,
        schema_ejemplo: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Extrae información estructurada en formato JSON.

        Método genérico para extraer datos estructurados de texto.

        Args:
            prompt: Prompt describiendo qué extraer
            schema_ejemplo: Ejemplo del schema JSON esperado

        Returns:
            Dict con los datos extraídos

        Raises:
            OpenAIError: Si hay error en la llamada a OpenAI
            ValueError: Si la respuesta no es JSON válido
        """
        logger.debug("Extrayendo JSON estructurado")

        system_prompt = "Eres un asistente que extrae información estructurada en JSON."

        if schema_ejemplo:
            schema_text = json.dumps(schema_ejemplo, indent=2, ensure_ascii=False)
            system_prompt += f"\n\nEjemplo del formato esperado:\n{schema_text}"

        try:
            response = self.client.chat.completions.create(
                model=self.model_mini,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Respuesta vacía de OpenAI")

            return json.loads(content)

        except OpenAIError as e:
            logger.error(f"Error extrayendo JSON: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON: {e}")
            raise ValueError(f"La respuesta no es JSON válido: {e}")


# Instancia global del servicio
openai_service = OpenAIService()
