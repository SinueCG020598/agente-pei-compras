"""
Script de prueba manual para FASE 3
Prueba SearchService, Investigador y Comparador de Precios
"""
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.search_service import search_service
from src.agents.investigador import buscar_proveedores
from src.agents.comparador_precios import comparar_precios_multiples_fuentes

def print_separator():
    print("\n" + "="*80 + "\n")

def test_search_service():
    """Test 1: SearchService - Búsqueda web de proveedores"""
    print_separator()
    print("TEST 1: SearchService - Búsqueda de Proveedores Web")
    print_separator()
    
    if not search_service.is_available():
        print("⚠️  SearchService NO disponible (SERPER_API_KEY no configurada)")
        print("   Para habilitar, configura SERPER_API_KEY en .env")
        return False
    
    print("✅ SearchService disponible")
    print("\n🔍 Buscando proveedores de 'Mouse inalámbrico'...")
    
    try:
        # Buscar proveedores web
        proveedores = search_service.buscar_proveedores_web(
            producto="Mouse inalámbrico",
            ubicacion="México",
            num_resultados=3
        )
        
        print(f"\n📋 Encontrados {len(proveedores)} proveedores:")
        for i, p in enumerate(proveedores, 1):
            print(f"\n  {i}. {p['nombre']}")
            print(f"     URL: {p['url']}")
            print(f"     Descripción: {p['descripcion'][:100]}...")
        
        # Buscar en ecommerce
        print("\n🛒 Buscando en marketplaces...")
        ecommerce = search_service.buscar_en_ecommerce("Mouse inalámbrico")
        
        print(f"\n📦 Encontrados {len(ecommerce)} productos en ecommerce:")
        for i, e in enumerate(ecommerce[:3], 1):
            print(f"\n  {i}. {e['producto']}")
            print(f"     Marketplace: {e['marketplace']}")
            print(f"     Precio: {e['precio_aprox']}")
            print(f"     URL: {e['url_compra']}")
        
        print("\n✅ Test 1: EXITOSO")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en Test 1: {e}")
        return False

def test_investigador():
    """Test 2: Agente Investigador - Búsqueda multi-fuente"""
    print_separator()
    print("TEST 2: Agente Investigador - Búsqueda Multi-fuente")
    print_separator()
    
    productos = [
        {
            "nombre": "Teclado mecánico",
            "cantidad": 5,
            "categoria": "tecnologia",
            "especificaciones": "RGB, switches cherry"
        }
    ]
    
    print("📝 Productos a buscar:")
    print(f"   - {productos[0]['nombre']} x{productos[0]['cantidad']}")
    
    try:
        print("\n🤖 Ejecutando Agente Investigador...")
        print("   (Buscando en BD + Web + Ecommerce)")
        
        resultado = buscar_proveedores(productos, usar_web=True)
        
        print("\n📊 RESUMEN DE BÚSQUEDA:")
        resumen = resultado.get("resumen", {})
        print(f"   • Proveedores en BD: {resumen.get('total_proveedores_bd', 0)}")
        print(f"   • Proveedores Web: {resumen.get('total_proveedores_web', 0)}")
        print(f"   • Enlaces Ecommerce: {resumen.get('total_enlaces_ecommerce', 0)}")
        print(f"   • Búsqueda Web: {'✅ Activa' if resumen.get('busqueda_web_activa') else '❌ Inactiva'}")
        
        if "recomendaciones" in resultado:
            recs = resultado["recomendaciones"]
            provs_rec = recs.get("proveedores_recomendados", [])
            
            print(f"\n💡 RECOMENDACIONES ({len(provs_rec)} proveedores):")
            for i, p in enumerate(provs_rec[:3], 1):
                print(f"\n   {i}. {p.get('nombre', 'N/A')}")
                print(f"      Fuente: {p.get('fuente', 'N/A')}")
                print(f"      Estrategia: {p.get('estrategia', 'N/A')}")
                print(f"      Prioridad: {p.get('prioridad', 'N/A')}")
                print(f"      Justificación: {p.get('justificacion', 'N/A')[:80]}...")
            
            if "estrategia_general" in recs:
                print(f"\n📋 Estrategia General: {recs['estrategia_general']}")
        
        print("\n✅ Test 2: EXITOSO")
        return True
        
    except Exception as e:
        print(f"\n❌ Error en Test 2: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparador():
    """Test 3: Comparador de Precios - Análisis multi-fuente"""
    print_separator()
    print("TEST 3: Comparador de Precios - Análisis Multi-fuente")
    print_separator()
    
    # Datos de ejemplo
    productos = [
        {"nombre": "Monitor 27 pulgadas", "cantidad": 3, "categoria": "tecnologia"}
    ]
    
    proveedores_bd = [
        {
            "id": 1,
            "nombre": "TechSupply MX",
            "rating": 4.5,
            "fuente": "base_de_datos"
        }
    ]
    
    proveedores_web = [
        {
            "nombre": "Monitores Pro",
            "url": "https://monitorespro.mx",
            "fuente": "web_search"
        }
    ]
    
    enlaces_ecommerce = [
        {
            "marketplace": "Amazon México",
            "producto": "Monitor LG 27\" Full HD",
            "precio_aprox": "$3,999",
            "url_compra": "https://amazon.com.mx/test"
        }
    ]
    
    try:
        print("🤖 Ejecutando Comparador de Precios...")
        print(f"   Analizando {len(productos)} productos")
        print(f"   Fuentes: {len(proveedores_bd)} BD, {len(proveedores_web)} Web, {len(enlaces_ecommerce)} Ecommerce")
        
        resultado = comparar_precios_multiples_fuentes(
            productos=productos,
            proveedores_bd=proveedores_bd,
            proveedores_web=proveedores_web,
            enlaces_ecommerce=enlaces_ecommerce,
            urgencia="normal"
        )
        
        if resultado.get("exito"):
            analisis = resultado["analisis"]
            rec = analisis.get("recomendacion_principal", {})
            
            print("\n💰 RECOMENDACIÓN PRINCIPAL:")
            print(f"   • Acción: {rec.get('accion', 'N/A').upper()}")
            print(f"   • Fuente: {rec.get('fuente_recomendada', 'N/A')}")
            print(f"   • Ahorro estimado: ${rec.get('ahorro_estimado', 0):,.2f}")
            print(f"   • Tiempo estimado: {rec.get('tiempo_estimado', 'N/A')}")
            print(f"   • Justificación: {rec.get('justificacion', 'N/A')[:150]}...")
            
            if "comparativa_precios" in analisis:
                print("\n📊 COMPARATIVA DE FUENTES:")
                for comp in analisis["comparativa_precios"]:
                    print(f"\n   {comp.get('fuente', 'N/A').upper()}:")
                    precio = comp.get('precio_estimado', 0)
                    if isinstance(precio, (int, float)):
                        print(f"      Precio estimado: ${precio:,.2f}")
                    else:
                        print(f"      Precio estimado: {precio}")
                    print(f"      Ventajas: {', '.join(comp.get('ventajas', [])[:3])}")
                    print(f"      Desventajas: {', '.join(comp.get('desventajas', [])[:3])}")
            
            print("\n✅ Test 3: EXITOSO")
            return True
        else:
            print(f"\n❌ Error: {resultado.get('error', 'Desconocido')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error en Test 3: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print(" "*20 + "PRUEBA MANUAL - FASE 3")
    print(" "*15 + "SearchService + Investigador + Comparador")
    print("="*80)
    
    resultados = []
    
    # Test 1: SearchService
    resultados.append(("SearchService", test_search_service()))
    
    # Test 2: Agente Investigador
    resultados.append(("Investigador", test_investigador()))
    
    # Test 3: Comparador de Precios
    resultados.append(("Comparador", test_comparador()))
    
    # Resumen final
    print_separator()
    print("RESUMEN DE PRUEBAS")
    print_separator()
    
    for nombre, exito in resultados:
        status = "✅ EXITOSO" if exito else "❌ FALLIDO"
        print(f"{nombre:.<50} {status}")
    
    exitosos = sum(1 for _, exito in resultados if exito)
    total = len(resultados)
    
    print(f"\nTotal: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 ¡Todos los tests pasaron! FASE 3 funcionando correctamente.")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa la configuración y logs.")
    
    print_separator()

if __name__ == "__main__":
    main()
