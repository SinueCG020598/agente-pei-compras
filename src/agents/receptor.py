"""
Agente Receptor - Procesamiento de Solicitudes de Compra.

Este agente es responsable de recibir solicitudes de compra en lenguaje natural
(desde formulario web, WhatsApp, o email) y extraer información estructurada.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import OpenAI, OpenAIError
from pydantic import BaseModel, Field, validator

from config.settings import settings

logger = logging.getLogger(__name__)


class ProductoExtraido(BaseModel):
    """Modelo para un producto extraído de la solicitud."""

    nombre: str = Field(..., description="Nombre descriptivo del producto/servicio")
    cantidad: int = Field(
        default=1, ge=1, description="Cantidad solicitada (mínimo 1)"
    )
    categoria: str = Field(..., description="Categoría del producto")
    especificaciones: str = Field(
        default="", description="Especificaciones técnicas y detalles"
    )

    @validator("categoria")
    def validar_categoria(cls, v):
        """Valida que la categoría sea una de las permitidas."""
        categorias_validas = {
            "tecnologia",
            "mobiliario",
            "insumos",
            "servicios",
            "equipamiento",
            "otros",
        }
        if v.lower() not in categorias_validas:
            logger.warning(
                f"Categoría '{v}' no válida, usando 'otros'. "
                f"Válidas: {categorias_validas}"
            )
            return "otros"
        return v.lower()


class SolicitudProcesada(BaseModel):
    """Modelo para una solicitud procesada por el agente receptor."""

    productos: List[ProductoExtraido] = Field(
        ..., description="Lista de productos extraídos", min_items=1
    )
    urgencia: str = Field(
        default="normal", description="Nivel de urgencia: normal, alta, urgente"
    )
    presupuesto_estimado: Optional[float] = Field(
        None, ge=0, description="Presupuesto estimado en pesos chilenos"
    )
    notas_adicionales: str = Field(
        default="", description="Notas adicionales o contexto"
    )

    @validator("urgencia")
    def validar_urgencia(cls, v):
        """Valida que la urgencia sea una de las permitidas."""
        urgencias_validas = {"normal", "alta", "urgente"}
        if v.lower() not in urgencias_validas:
            logger.warning(
                f"Urgencia '{v}' no válida, usando 'normal'. "
                f"Válidas: {urgencias_validas}"
            )
            return "normal"
        return v.lower()


class ReceptorAgent:
    """
    Agente Receptor para procesamiento de solicitudes de compra.

    Este agente utiliza OpenAI para extraer información estructurada
    de textos informales en lenguaje natural.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa el agente receptor.

        Args:
            api_key: API key de OpenAI (usa settings si no se proporciona)
            model: Modelo a usar (gpt-4o-mini por defecto)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL_MINI
        self.client = OpenAI(api_key=self.api_key)

        # Cargar el prompt del agente
        self.system_prompt = self._cargar_prompt()

        logger.info(f"Agente Receptor inicializado - Modelo: {self.model}")

    def _cargar_prompt(self) -> str:
        """
        Carga el prompt del agente desde el archivo.

        Returns:
            Contenido del prompt

        Raises:
            FileNotFoundError: Si el archivo de prompt no existe
        """
        # Buscar el archivo de prompt
        prompt_paths = [
            Path(__file__).parent.parent / "prompts" / "receptor_prompt.txt",
            Path("src/prompts/receptor_prompt.txt"),
            Path("prompts/receptor_prompt.txt"),
        ]

        for prompt_path in prompt_paths:
            if prompt_path.exists():
                logger.info(f"Cargando prompt desde: {prompt_path}")
                return prompt_path.read_text(encoding="utf-8")

        # Si no se encuentra, usar un prompt básico
        logger.warning("Archivo de prompt no encontrado, usando prompt por defecto")
        return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """
        Retorna un prompt por defecto si no se encuentra el archivo.

        Returns:
            Prompt por defecto
        """
        return """Eres un agente especializado en procesar solicitudes de compra.
Extrae información estructurada y responde SOLO con JSON válido.

Formato de respuesta:
{
    "productos": [
        {
            "nombre": "...",
            "cantidad": 1,
            "categoria": "tecnologia|mobiliario|insumos|servicios|equipamiento|otros",
            "especificaciones": "..."
        }
    ],
    "urgencia": "normal|alta|urgente",
    "presupuesto_estimado": 0.0 o null,
    "notas_adicionales": "..."
}"""

    def procesar_solicitud(
        self, texto: str, origen: str = "formulario"
    ) -> Dict:
        """
        Procesa una solicitud de compra en lenguaje natural.

        Extrae información estructurada de la solicitud usando IA.

        Args:
            texto: Texto de la solicitud en lenguaje natural
            origen: Origen de la solicitud (formulario, whatsapp, email)

        Returns:
            Dict con la información extraída:
            {
                "productos": [{"nombre": "...", "cantidad": 1, ...}],
                "urgencia": "normal",
                "presupuesto_estimado": 1000000.0,
                "notas_adicionales": "..."
            }

        Raises:
            ValueError: Si el texto está vacío o la respuesta no es válida
            OpenAIError: Si hay error en la llamada a OpenAI
        """
        # Validar entrada
        if not texto or not texto.strip():
            raise ValueError("El texto de la solicitud no puede estar vacío")

        logger.info(
            f"Procesando solicitud - Origen: {origen}, Longitud: {len(texto)} chars"
        )

        try:
            # Preparar el prompt
            user_prompt = f"""Origen de la solicitud: {origen}

Texto de la solicitud:
{texto}

Extrae la información y responde con el JSON estructurado."""

            # Llamar a OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,  # Baja temperatura para mayor precisión
                response_format={"type": "json_object"},
            )

            # Extraer y parsear respuesta
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Respuesta vacía de OpenAI")

            data = json.loads(content)

            # Validar con Pydantic
            solicitud_procesada = SolicitudProcesada(**data)

            # Convertir a dict para retornar
            resultado = solicitud_procesada.model_dump()

            logger.info(
                f"Solicitud procesada exitosamente - "
                f"Productos: {len(resultado['productos'])}, "
                f"Urgencia: {resultado['urgencia']}"
            )

            return resultado

        except OpenAIError as e:
            logger.error(f"Error en OpenAI API: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando JSON de respuesta: {e}")
            raise ValueError(f"La respuesta de IA no es JSON válido: {e}")
        except Exception as e:
            logger.error(f"Error procesando solicitud: {e}")
            raise


def validar_solicitud(datos: Dict) -> Tuple[bool, str]:
    """
    Valida que una solicitud procesada tenga los datos mínimos requeridos.

    Args:
        datos: Dict con la solicitud procesada

    Returns:
        Tupla (es_valida, mensaje_error)
        - es_valida: True si la solicitud es válida
        - mensaje_error: Mensaje de error si no es válida, vacío si es válida
    """
    try:
        # Validar que exista la clave productos
        if "productos" not in datos:
            return False, "Falta la clave 'productos' en la solicitud"

        # Validar que haya al menos un producto
        productos = datos["productos"]
        if not productos or len(productos) == 0:
            return False, "Debe haber al menos un producto en la solicitud"

        # Validar cada producto
        for i, producto in enumerate(productos, 1):
            # Validar nombre
            if not producto.get("nombre") or not str(producto["nombre"]).strip():
                return False, f"El producto #{i} no tiene nombre"

            # Validar cantidad
            cantidad = producto.get("cantidad", 0)
            if not isinstance(cantidad, (int, float)) or cantidad < 1:
                return False, f"El producto #{i} tiene cantidad inválida: {cantidad}"

            # Validar categoría
            if not producto.get("categoria"):
                return False, f"El producto #{i} no tiene categoría"

        # Validar urgencia si existe
        urgencia = datos.get("urgencia", "normal")
        if urgencia not in ["normal", "alta", "urgente"]:
            return False, f"Urgencia inválida: {urgencia}"

        # Validar presupuesto si existe
        presupuesto = datos.get("presupuesto_estimado")
        if presupuesto is not None:
            if not isinstance(presupuesto, (int, float)) or presupuesto < 0:
                return False, f"Presupuesto inválido: {presupuesto}"

        logger.info("Solicitud validada exitosamente")
        return True, ""

    except Exception as e:
        logger.error(f"Error validando solicitud: {e}")
        return False, f"Error en validación: {str(e)}"


def procesar_solicitud(texto: str, origen: str = "formulario") -> Dict:
    """
    Función de conveniencia para procesar una solicitud.

    Crea una instancia del agente y procesa la solicitud.

    Args:
        texto: Texto de la solicitud en lenguaje natural
        origen: Origen de la solicitud (formulario, whatsapp, email)

    Returns:
        Dict con la información extraída

    Raises:
        ValueError: Si el texto está vacío o la respuesta no es válida
        OpenAIError: Si hay error en la llamada a OpenAI
    """
    agente = ReceptorAgent()
    return agente.procesar_solicitud(texto, origen)


# Instancia global del agente (opcional, para reutilización)
_agente_global: Optional[ReceptorAgent] = None


def get_agente() -> ReceptorAgent:
    """
    Obtiene la instancia global del agente receptor.

    Returns:
        Instancia del ReceptorAgent
    """
    global _agente_global
    if _agente_global is None:
        _agente_global = ReceptorAgent()
    return _agente_global
