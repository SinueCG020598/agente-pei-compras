"""
Servicio de búsqueda web usando Serper API.

Este servicio proporciona funcionalidades para:
- Búsqueda de proveedores en Google
- Búsqueda de productos y precios
- Extracción de información de contacto
"""
import logging
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from config.settings import settings

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    """Modelo para un resultado de búsqueda."""

    title: str
    link: str
    snippet: str
    position: int


class ProveedorEncontrado(BaseModel):
    """Modelo para proveedor encontrado en búsqueda."""

    nombre: str
    url: str
    descripcion: str
    telefono: Optional[str] = None
    email: Optional[str] = None
    ubicacion: Optional[str] = None


class SearchService:
    """
    Servicio para realizar búsquedas web usando Serper API.

    Serper API: https://serper.dev
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de búsqueda.

        Args:
            api_key: API key de Serper (usa settings si no se proporciona)
        """
        self.api_key = api_key or settings.SERPER_API_KEY
        self.api_url = "https://google.serper.dev/search"

        self.headers = {
            "X-API-KEY": self.api_key or "",
            "Content-Type": "application/json",
        }

        logger.info("Search Service inicializado")

    def search(
        self,
        query: str,
        num_results: int = 10,
        location: str = "Chile",
        language: str = "es",
    ) -> List[SearchResult]:
        """
        Realiza una búsqueda en Google.

        Args:
            query: Consulta de búsqueda
            num_results: Número de resultados a obtener (máx 100)
            location: Ubicación geográfica para los resultados
            language: Idioma de los resultados

        Returns:
            Lista de resultados de búsqueda

        Raises:
            requests.HTTPError: Si hay error en la llamada a la API
            ValueError: Si no hay API key configurada
        """
        if not self.api_key:
            raise ValueError(
                "API key de Serper no configurada. "
                "Configura SERPER_API_KEY en .env"
            )

        logger.info(f"Buscando: {query} ({num_results} resultados)")

        payload = {
            "q": query,
            "num": min(num_results, 100),  # Máximo 100
            "gl": location,
            "hl": language,
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()
            organic_results = data.get("organic", [])

            results = []
            for idx, result in enumerate(organic_results):
                results.append(
                    SearchResult(
                        title=result.get("title", ""),
                        link=result.get("link", ""),
                        snippet=result.get("snippet", ""),
                        position=idx + 1,
                    )
                )

            logger.info(f"Obtenidos {len(results)} resultados")
            return results

        except requests.HTTPError as e:
            logger.error(f"Error en Serper API: {e}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            raise

    def buscar_proveedores(
        self,
        categoria: str,
        producto: str,
        ubicacion: str = "Chile",
        num_results: int = 10,
    ) -> List[SearchResult]:
        """
        Busca proveedores de un producto específico.

        Args:
            categoria: Categoría del producto (tecnologia, mobiliario, etc.)
            producto: Nombre o descripción del producto
            ubicacion: Ubicación geográfica
            num_results: Número de resultados

        Returns:
            Lista de resultados de búsqueda

        Raises:
            requests.HTTPError: Si hay error en la API
        """
        query = f"proveedores {categoria} {producto} {ubicacion}"
        logger.info(f"Buscando proveedores: {query}")

        return self.search(query=query, num_results=num_results, location=ubicacion)

    def buscar_precios(
        self,
        producto: str,
        ubicacion: str = "Chile",
        num_results: int = 5,
    ) -> List[SearchResult]:
        """
        Busca precios de un producto.

        Args:
            producto: Nombre del producto
            ubicacion: Ubicación geográfica
            num_results: Número de resultados

        Returns:
            Lista de resultados con precios

        Raises:
            requests.HTTPError: Si hay error en la API
        """
        query = f"{producto} precio {ubicacion}"
        logger.info(f"Buscando precios: {query}")

        return self.search(query=query, num_results=num_results, location=ubicacion)

    def buscar_contacto_empresa(
        self,
        nombre_empresa: str,
        ubicacion: str = "Chile",
    ) -> Optional[SearchResult]:
        """
        Busca información de contacto de una empresa.

        Args:
            nombre_empresa: Nombre de la empresa
            ubicacion: Ubicación geográfica

        Returns:
            Primer resultado de búsqueda o None

        Raises:
            requests.HTTPError: Si hay error en la API
        """
        query = f"{nombre_empresa} contacto email teléfono {ubicacion}"
        logger.info(f"Buscando contacto: {query}")

        try:
            results = self.search(query=query, num_results=3, location=ubicacion)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Error buscando contacto: {e}")
            return None

    def extraer_info_proveedor(
        self, result: SearchResult
    ) -> Dict[str, Any]:
        """
        Extrae información estructurada de un resultado de búsqueda.

        Args:
            result: Resultado de búsqueda

        Returns:
            Dict con información del proveedor
        """
        import re

        info: Dict[str, Any] = {
            "nombre": result.title,
            "url": result.link,
            "descripcion": result.snippet,
        }

        # Intentar extraer teléfono del snippet
        phone_pattern = r"\+?\d{1,3}[-\s]?\(?\d{1,4}\)?[-\s]?\d{1,4}[-\s]?\d{1,9}"
        phones = re.findall(phone_pattern, result.snippet)
        if phones:
            info["telefono"] = phones[0]

        # Intentar extraer email
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, result.snippet)
        if emails:
            info["email"] = emails[0]

        # Extraer ubicación de la URL (dominio .cl generalmente es Chile)
        if ".cl" in result.link:
            info["ubicacion"] = "Chile"

        return info

    def buscar_y_extraer_proveedores(
        self,
        categoria: str,
        producto: str,
        ubicacion: str = "Chile",
        num_results: int = 10,
    ) -> List[ProveedorEncontrado]:
        """
        Busca proveedores y extrae información estructurada.

        Args:
            categoria: Categoría del producto
            producto: Nombre del producto
            ubicacion: Ubicación geográfica
            num_results: Número de resultados

        Returns:
            Lista de proveedores encontrados con información extraída

        Raises:
            requests.HTTPError: Si hay error en la API
        """
        logger.info(
            f"Buscando y extrayendo proveedores: {categoria} - {producto}"
        )

        results = self.buscar_proveedores(
            categoria=categoria,
            producto=producto,
            ubicacion=ubicacion,
            num_results=num_results,
        )

        proveedores = []
        for result in results:
            info = self.extraer_info_proveedor(result)

            try:
                proveedor = ProveedorEncontrado(
                    nombre=info["nombre"],
                    url=info["url"],
                    descripcion=info["descripcion"],
                    telefono=info.get("telefono"),
                    email=info.get("email"),
                    ubicacion=info.get("ubicacion"),
                )
                proveedores.append(proveedor)
            except Exception as e:
                logger.warning(f"Error creando proveedor desde resultado: {e}")
                continue

        logger.info(f"Extraídos {len(proveedores)} proveedores")
        return proveedores

    def is_available(self) -> bool:
        """
        Verifica si el servicio está disponible.

        Returns:
            True si la API key está configurada, False en caso contrario
        """
        return self.api_key is not None and self.api_key != ""

    def buscar_proveedores_web(
        self,
        producto: str,
        ubicacion: str = "México",
        num_resultados: int = 10
    ) -> List[Dict]:
        """
        Busca proveedores en internet usando Google Search (FASE 3)

        Args:
            producto: Nombre del producto a buscar
            ubicacion: País o ciudad para filtrar resultados
            num_resultados: Número máximo de resultados

        Returns:
            Lista de proveedores encontrados en web
        """
        if not self.is_available():
            return []

        try:
            query = f"{producto} proveedor mayoreo distribuidor {ubicacion}"

            payload = {
                "q": query,
                "num": num_resultados,
                "gl": "mx",  # Geolocalización México
                "hl": "es"   # Idioma español
            }

            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            resultados = response.json()

            proveedores_web = []
            for item in resultados.get("organic", []):
                proveedores_web.append({
                    "nombre": item.get("title"),
                    "url": item.get("link"),
                    "descripcion": item.get("snippet"),
                    "fuente": "web_search",
                    "score_relevancia": item.get("position", 100)
                })

            logger.info(f"✓ Encontrados {len(proveedores_web)} proveedores web para {producto}")
            return proveedores_web

        except Exception as e:
            logger.error(f"❌ Error buscando proveedores web: {e}")
            return []

    def buscar_en_ecommerce(
        self,
        producto: str,
        marketplaces: List[str] = None
    ) -> List[Dict]:
        """
        Busca producto en marketplaces (Amazon, MercadoLibre, etc.) - FASE 3
        Devuelve enlaces directos para compra manual

        Args:
            producto: Nombre del producto
            marketplaces: Lista de marketplaces a buscar (None = todos)

        Returns:
            Lista de productos encontrados con enlaces de compra
        """
        if not self.is_available():
            return []

        if marketplaces is None:
            marketplaces = ["amazon.com.mx", "mercadolibre.com.mx", "liverpool.com.mx"]

        resultados_ecommerce = []

        for marketplace in marketplaces:
            try:
                query = f"{producto} site:{marketplace}"

                payload = {
                    "q": query,
                    "num": 5,
                    "gl": "mx",
                    "hl": "es"
                }

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()

                marketplace_name = self._get_marketplace_name(marketplace)

                for item in data.get("organic", []):
                    precio_aprox = self._extraer_precio(item.get("snippet", ""))

                    resultados_ecommerce.append({
                        "marketplace": marketplace_name,
                        "producto": item.get("title"),
                        "url_compra": item.get("link"),
                        "precio_aprox": precio_aprox,
                        "descripcion": item.get("snippet"),
                        "disponible_compra_directa": True
                    })

                logger.info(f"✓ Encontrados {len(resultados_ecommerce)} productos en {marketplace_name}")

            except Exception as e:
                logger.error(f"❌ Error buscando en {marketplace}: {e}")
                continue

        return resultados_ecommerce

    def buscar_mejores_precios(self, producto: str) -> Dict:
        """
        Busca mejores precios en múltiples fuentes - FASE 3
        Combina búsqueda de proveedores y ecommerce

        Returns:
            Dict con todos los resultados organizados
        """
        logger.info(f"🔍 Buscando mejores precios para: {producto}")
        return {
            "proveedores_web": self.buscar_proveedores_web(producto),
            "ecommerce": self.buscar_en_ecommerce(producto),
            "producto_buscado": producto
        }

    def _extraer_precio(self, texto: str) -> str:
        """Extrae precio del texto usando regex"""
        import re

        # Buscar patrones como: $1,234.56 o $1234 o MXN 1,234
        patrones = [
            r'\$[\d,]+\.?\d*',  # $1,234.56
            r'MXN\s*[\d,]+\.?\d*',  # MXN 1234
            r'[\d,]+\.?\d*\s*pesos',  # 1234 pesos
        ]

        for patron in patrones:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(0)

        return "Precio no disponible"

    def _get_marketplace_name(self, domain: str) -> str:
        """Convierte dominio en nombre amigable"""
        mapping = {
            "amazon.com.mx": "Amazon México",
            "mercadolibre.com.mx": "MercadoLibre",
            "liverpool.com.mx": "Liverpool",
            "walmart.com.mx": "Walmart México",
            "homedepot.com.mx": "Home Depot"
        }
        return mapping.get(domain, domain)


# Instancia global del servicio
search_service = SearchService()
