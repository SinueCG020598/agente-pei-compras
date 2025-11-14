"""
Tests para FASE 3: SearchService, Investigador y Comparador de Precios
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_serper_response():
    """Mock response from Serper API"""
    return {
        "organic": [
            {
                "title": "Proveedor Tech MX - Laptops y Equipos",
                "link": "https://proveedortech.com.mx",
                "snippet": "Laptops HP desde $15,000 MXN. Distribuidor autorizado.",
                "position": 1
            },
            {
                "title": "Computadoras al Mayoreo",
                "link": "https://computadorasmayor.mx",
                "snippet": "Venta por mayoreo de laptops HP, Dell, Lenovo",
                "position": 2
            }
        ]
    }

@pytest.fixture
def mock_ecommerce_response():
    """Mock response for ecommerce search"""
    return {
        "organic": [
            {
                "title": "HP Laptop 15.6\" Core i5 8GB RAM",
                "link": "https://www.amazon.com.mx/dp/B09ABC123",
                "snippet": "Precio: $12,999 MXN. Envío gratis con Prime"
            }
        ]
    }

@pytest.fixture
def productos_ejemplo():
    """Productos de ejemplo para tests"""
    return [
        {
            "nombre": "Laptop HP",
            "cantidad": 5,
            "categoria": "tecnologia",
            "especificaciones": "Para equipo de ventas"
        }
    ]

@pytest.fixture
def proveedores_bd_ejemplo():
    """Proveedores de BD de ejemplo"""
    return [
        {
            "id": 1,
            "nombre": "TechSupply SA",
            "productos": "tecnologia,computadoras",
            "rating": 4.5,
            "email": "ventas@techsupply.mx",
            "telefono": "+52-55-1234-5678",
            "fuente": "base_de_datos"
        }
    ]

# =============================================================================
# TESTS SearchService
# =============================================================================

@pytest.mark.integration
@patch('requests.post')
def test_buscar_proveedores_web_exitoso(mock_post, mock_serper_response):
    """Test búsqueda de proveedores web funciona correctamente"""
    from src.services.search_service import SearchService
    
    # Configurar mock
    mock_response = Mock()
    mock_response.json.return_value = mock_serper_response
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    # Crear servicio con API key mock
    service = SearchService(api_key="test-key")
    
    # Ejecutar búsqueda
    resultados = service.buscar_proveedores_web("Laptop HP", ubicacion="México")
    
    # Verificar resultados
    assert len(resultados) == 2
    assert resultados[0]["nombre"] == "Proveedor Tech MX - Laptops y Equipos"
    assert resultados[0]["fuente"] == "web_search"
    assert "url" in resultados[0]
    assert "descripcion" in resultados[0]

@patch('requests.post')
def test_buscar_en_ecommerce_exitoso(mock_post, mock_ecommerce_response):
    """Test búsqueda en marketplaces funciona"""
    from src.services.search_service import SearchService
    
    mock_response = Mock()
    mock_response.json.return_value = mock_ecommerce_response
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response
    
    service = SearchService(api_key="test-key")
    resultados = service.buscar_en_ecommerce("Laptop HP")
    
    assert len(resultados) > 0
    assert "marketplace" in resultados[0]
    assert "url_compra" in resultados[0]
    assert "precio_aprox" in resultados[0]

def test_extraer_precio_formato_pesos():
    """Test extracción de precio en formato pesos"""
    from src.services.search_service import SearchService
    
    service = SearchService(api_key="test-key")
    
    # Test diferentes formatos
    assert "$12,999" in service._extraer_precio("Precio: $12,999 MXN")
    assert "$15,000" in service._extraer_precio("Desde $15,000 hasta $20,000")

def test_get_marketplace_name():
    """Test conversión de dominio a nombre amigable"""
    from src.services.search_service import SearchService
    
    service = SearchService(api_key="test-key")
    
    assert service._get_marketplace_name("amazon.com.mx") == "Amazon México"
    assert service._get_marketplace_name("mercadolibre.com.mx") == "MercadoLibre"
    assert service._get_marketplace_name("liverpool.com.mx") == "Liverpool"

def test_search_service_no_api_key():
    """Test SearchService sin API key retorna listas vacías"""
    from src.services.search_service import SearchService
    from unittest.mock import patch

    # Mock settings to have no API key
    with patch('src.services.search_service.settings.SERPER_API_KEY', None):
        service = SearchService(api_key="")

        assert service.is_available() is False
        assert service.buscar_proveedores_web("test") == []
        assert service.buscar_en_ecommerce("test") == []

# =============================================================================
# TESTS Agente Investigador
# =============================================================================

@pytest.mark.integration
@patch('src.agents.investigador.search_service')
@patch('src.agents.investigador.llamar_agente')
@patch('src.agents.investigador.SessionLocal')
def test_buscar_proveedores_con_web(mock_session, mock_llamar, mock_search, 
                                     productos_ejemplo, proveedores_bd_ejemplo):
    """Test buscar_proveedores con búsqueda web habilitada"""
    from src.agents.investigador import buscar_proveedores
    
    # Mock BD
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # Mock search service
    mock_search.is_available.return_value = True
    mock_search.buscar_proveedores_web.return_value = [
        {
            "nombre": "Proveedor Web Test",
            "url": "https://test.com",
            "descripcion": "Test",
            "fuente": "web_search",
            "score_relevancia": 1
        }
    ]
    mock_search.buscar_en_ecommerce.return_value = [
        {
            "marketplace": "Amazon México",
            "producto": "Laptop HP Test",
            "url_compra": "https://amazon.com.mx/test",
            "precio_aprox": "$12,999",
            "disponible_compra_directa": True
        }
    ]
    
    # Mock llamada al agente
    mock_llamar.return_value = json.dumps({
        "proveedores_recomendados": [
            {
                "proveedor_id": None,
                "nombre": "Proveedor Web Test",
                "fuente": "web",
                "productos_asignados": ["Laptop HP"],
                "justificacion": "Buena opción web",
                "prioridad": "media",
                "estrategia": "investigar"
            }
        ],
        "enlaces_ecommerce_recomendados": [],
        "productos_sin_fuente": [],
        "estrategia_general": "Comparar opciones",
        "estimado_ahorro": "10%"
    })
    
    # Ejecutar
    resultado = buscar_proveedores(productos_ejemplo, usar_web=True)
    
    # Verificar
    assert "proveedores_web" in resultado
    assert "enlaces_ecommerce" in resultado
    assert "recomendaciones" in resultado
    assert "resumen" in resultado
    assert resultado["resumen"]["busqueda_web_activa"] is True
    assert len(resultado["proveedores_web"]) == 1
    assert len(resultado["enlaces_ecommerce"]) == 1

@pytest.mark.integration
@patch('src.agents.investigador.search_service')
@patch('src.agents.investigador.llamar_agente')
@patch('src.agents.investigador.SessionLocal')
def test_buscar_proveedores_sin_web(mock_session, mock_llamar, mock_search, 
                                     productos_ejemplo):
    """Test buscar_proveedores con búsqueda web deshabilitada"""
    from src.agents.investigador import buscar_proveedores
    
    # Mock BD
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.all.return_value = []
    
    # Mock llamada al agente
    mock_llamar.return_value = json.dumps({
        "proveedores_recomendados": [],
        "enlaces_ecommerce_recomendados": [],
        "productos_sin_fuente": productos_ejemplo,
        "estrategia_general": "Buscar proveedores",
        "estimado_ahorro": "0%"
    })
    
    # Ejecutar
    resultado = buscar_proveedores(productos_ejemplo, usar_web=False)
    
    # Verificar
    assert resultado["resumen"]["busqueda_web_activa"] is False
    assert len(resultado["proveedores_web"]) == 0
    assert len(resultado["enlaces_ecommerce"]) == 0

# =============================================================================
# TESTS Comparador de Precios
# =============================================================================

@patch('src.agents.comparador_precios.llamar_agente')
def test_comparar_precios_exitoso(mock_llamar, productos_ejemplo, 
                                  proveedores_bd_ejemplo):
    """Test comparación de precios exitosa"""
    from src.agents.comparador_precios import comparar_precios_multiples_fuentes
    
    # Mock respuesta del agente
    mock_llamar.return_value = json.dumps({
        "recomendacion_principal": {
            "accion": "cotizar",
            "fuente_recomendada": "proveedores_bd",
            "justificacion": "Mejor relación calidad-precio",
            "ahorro_estimado": 15000.0,
            "tiempo_estimado": "2-3 días"
        },
        "comparativa_precios": [
            {
                "fuente": "proveedores_bd",
                "precio_estimado": 65000.0,
                "ventajas": ["Confiable", "Buen soporte"],
                "desventajas": ["Requiere cotización"]
            }
        ],
        "alertas": [],
        "siguiente_paso": "Solicitar cotización"
    })
    
    # Ejecutar
    resultado = comparar_precios_multiples_fuentes(
        productos=productos_ejemplo,
        proveedores_bd=proveedores_bd_ejemplo,
        proveedores_web=[],
        enlaces_ecommerce=[],
        urgencia="normal"
    )
    
    # Verificar
    assert resultado["exito"] is True
    assert "analisis" in resultado
    assert "recomendacion_principal" in resultado["analisis"]
    assert resultado["analisis"]["recomendacion_principal"]["accion"] == "cotizar"

@patch('src.agents.comparador_precios.llamar_agente')
def test_comparar_precios_con_error(mock_llamar, productos_ejemplo):
    """Test manejo de error en comparación de precios"""
    from src.agents.comparador_precios import comparar_precios_multiples_fuentes
    
    # Simular error
    mock_llamar.side_effect = Exception("Error de conexión")
    
    # Ejecutar
    resultado = comparar_precios_multiples_fuentes(
        productos=productos_ejemplo,
        proveedores_bd=[],
        proveedores_web=[],
        enlaces_ecommerce=[]
    )
    
    # Verificar
    assert resultado["exito"] is False
    assert "error" in resultado

# =============================================================================
# TESTS DE INTEGRACIÓN E2E
# =============================================================================

@pytest.mark.integration
@pytest.mark.skip(reason="Test E2E requiere API keys válidas - ejecutar manualmente")
def test_flujo_completo_fase_3():
    """Test de flujo completo de FASE 3 con APIs reales"""
    from src.agents.investigador import buscar_proveedores
    from src.agents.comparador_precios import comparar_precios_multiples_fuentes
    
    productos = [
        {
            "nombre": "Mouse inalámbrico",
            "cantidad": 10,
            "categoria": "tecnologia"
        }
    ]
    
    # 1. Buscar proveedores (BD + Web + Ecommerce)
    resultado_busqueda = buscar_proveedores(productos, usar_web=True)
    
    assert "proveedores_bd" in resultado_busqueda
    assert "proveedores_web" in resultado_busqueda
    assert "enlaces_ecommerce" in resultado_busqueda
    
    # 2. Comparar precios
    resultado_comparacion = comparar_precios_multiples_fuentes(
        productos=productos,
        proveedores_bd=resultado_busqueda["proveedores_bd"],
        proveedores_web=resultado_busqueda["proveedores_web"],
        enlaces_ecommerce=resultado_busqueda["enlaces_ecommerce"],
        urgencia="normal"
    )
    
    if resultado_comparacion["exito"]:
        assert "recomendacion_principal" in resultado_comparacion["analisis"]
