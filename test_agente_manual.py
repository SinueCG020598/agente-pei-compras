"""
Script de prueba manual del Agente Receptor.

Este script permite probar el Agente Receptor de forma interactiva
sin necesidad de ejecutar la interfaz web de Streamlit.
"""
from src.agents.receptor import procesar_solicitud, validar_solicitud


def test_solicitud_simple():
    """Test con solicitud simple."""
    print("\n" + "="*70)
    print("TEST 1: SOLICITUD SIMPLE")
    print("="*70)

    texto = "Necesito 5 laptops HP para el equipo de ventas"
    print(f"\n📝 Input:\n{texto}\n")

    print("⏳ Procesando con IA...")
    resultado = procesar_solicitud(texto, origen="formulario")

    print("\n✅ Output:")
    print(f"   📦 Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"      {i}. {p['nombre']}")
        print(f"         • Cantidad: {p['cantidad']}")
        print(f"         • Categoría: {p['categoria']}")
        print(f"         • Especificaciones: {p['especificaciones']}")

    urgencia_icons = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}
    icono = urgencia_icons.get(resultado['urgencia'], "⚪")
    print(f"\n   {icono} Urgencia: {resultado['urgencia'].upper()}")

    if resultado['presupuesto_estimado']:
        print(f"   💰 Presupuesto: ${resultado['presupuesto_estimado']:,.0f} CLP")
    else:
        print(f"   💰 Presupuesto: No especificado")

    if resultado['notas_adicionales']:
        print(f"\n   📌 Notas: {resultado['notas_adicionales']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    if es_valida:
        print(f"\n   ✅ Validación: SOLICITUD VÁLIDA")
    else:
        print(f"\n   ❌ Validación: ERROR - {error}")

    return resultado


def test_solicitud_compleja():
    """Test con solicitud compleja."""
    print("\n" + "="*70)
    print("TEST 2: SOLICITUD COMPLEJA (Múltiples Productos)")
    print("="*70)

    texto = """
    Hola! Necesitamos urgente 10 escritorios ejecutivos y 10 sillas ergonómicas
    para la nueva oficina. También 2 impresoras láser multifunción.
    Tenemos un presupuesto de 8 millones. Es para este viernes!
    """
    print(f"\n📝 Input:\n{texto.strip()}\n")

    print("⏳ Procesando con IA...")
    resultado = procesar_solicitud(texto, origen="formulario")

    print("\n✅ Output:")
    print(f"   📦 Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"\n      {i}. {p['nombre']}")
        print(f"         • Cantidad: {p['cantidad']} unidades")
        print(f"         • Categoría: {p['categoria'].title()}")
        print(f"         • Especificaciones: {p['especificaciones']}")

    urgencia_icons = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}
    icono = urgencia_icons.get(resultado['urgencia'], "⚪")
    print(f"\n   {icono} Urgencia: {resultado['urgencia'].upper()}")

    if resultado['presupuesto_estimado']:
        print(f"   💰 Presupuesto: ${resultado['presupuesto_estimado']:,.0f} CLP")
    else:
        print(f"   💰 Presupuesto: No especificado")

    if resultado['notas_adicionales']:
        print(f"\n   📌 Notas: {resultado['notas_adicionales']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    if es_valida:
        print(f"\n   ✅ Validación: SOLICITUD VÁLIDA")
    else:
        print(f"\n   ❌ Validación: ERROR - {error}")

    return resultado


def test_solicitud_informal():
    """Test con solicitud informal."""
    print("\n" + "="*70)
    print("TEST 3: SOLICITUD INFORMAL (Lenguaje Coloquial)")
    print("="*70)

    texto = "oye necesito unas sillas pa la sala de reuniones, como 6 o 7, nada muy caro, pa la prox semana porfa"
    print(f"\n📝 Input:\n{texto}\n")

    print("⏳ Procesando con IA...")
    resultado = procesar_solicitud(texto, origen="whatsapp")

    print("\n✅ Output:")
    print(f"   📦 Productos: {len(resultado['productos'])}")
    for i, p in enumerate(resultado['productos'], 1):
        print(f"      {i}. {p['nombre']}")
        print(f"         • Cantidad: {p['cantidad']}")
        print(f"         • Categoría: {p['categoria']}")
        print(f"         • Especificaciones: {p['especificaciones']}")

    urgencia_icons = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}
    icono = urgencia_icons.get(resultado['urgencia'], "⚪")
    print(f"\n   {icono} Urgencia: {resultado['urgencia'].upper()}")

    if resultado['presupuesto_estimado']:
        print(f"   💰 Presupuesto: ${resultado['presupuesto_estimado']:,.0f} CLP")
    else:
        print(f"   💰 Presupuesto: No especificado")

    if resultado['notas_adicionales']:
        print(f"\n   📌 Notas: {resultado['notas_adicionales']}")

    # Validar
    es_valida, error = validar_solicitud(resultado)
    if es_valida:
        print(f"\n   ✅ Validación: SOLICITUD VÁLIDA")
    else:
        print(f"\n   ❌ Validación: ERROR - {error}")

    return resultado


def test_solicitud_personalizada():
    """Test con solicitud personalizada del usuario."""
    print("\n" + "="*70)
    print("TEST 4: SOLICITUD PERSONALIZADA")
    print("="*70)

    print("\n📝 Escribe tu solicitud de compra (o presiona Enter para saltar):")
    texto = input(">>> ").strip()

    if not texto:
        print("\n⏭️  Test omitido")
        return None

    print("\n⏳ Procesando con IA...")
    try:
        resultado = procesar_solicitud(texto, origen="terminal")

        print("\n✅ Output:")
        print(f"   📦 Productos: {len(resultado['productos'])}")
        for i, p in enumerate(resultado['productos'], 1):
            print(f"\n      {i}. {p['nombre']}")
            print(f"         • Cantidad: {p['cantidad']} unidades")
            print(f"         • Categoría: {p['categoria'].title()}")
            print(f"         • Especificaciones: {p['especificaciones']}")

        urgencia_icons = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}
        icono = urgencia_icons.get(resultado['urgencia'], "⚪")
        print(f"\n   {icono} Urgencia: {resultado['urgencia'].upper()}")

        if resultado['presupuesto_estimado']:
            print(f"   💰 Presupuesto: ${resultado['presupuesto_estimado']:,.0f} CLP")
        else:
            print(f"   💰 Presupuesto: No especificado")

        if resultado['notas_adicionales']:
            print(f"\n   📌 Notas: {resultado['notas_adicionales']}")

        # Validar
        es_valida, error = validar_solicitud(resultado)
        if es_valida:
            print(f"\n   ✅ Validación: SOLICITUD VÁLIDA")
        else:
            print(f"\n   ❌ Validación: ERROR - {error}")

        return resultado

    except Exception as e:
        print(f"\n   ❌ ERROR: {str(e)}")
        return None


def main():
    """Función principal."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  PRUEBAS MANUALES DEL AGENTE RECEPTOR - FASE 2".center(68) + "║")
    print("║" + "  Sistema PEI Compras AI".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    resultados = []

    try:
        # Test 1: Solicitud simple
        r1 = test_solicitud_simple()
        resultados.append(("Simple", r1))

        # Test 2: Solicitud compleja
        r2 = test_solicitud_compleja()
        resultados.append(("Compleja", r2))

        # Test 3: Solicitud informal
        r3 = test_solicitud_informal()
        resultados.append(("Informal", r3))

        # Test 4: Solicitud personalizada (opcional)
        r4 = test_solicitud_personalizada()
        if r4:
            resultados.append(("Personalizada", r4))

        # Resumen final
        print("\n" + "="*70)
        print("RESUMEN DE PRUEBAS")
        print("="*70)

        tests_exitosos = sum(1 for _, r in resultados if r is not None)

        print(f"\n✅ Tests completados exitosamente: {tests_exitosos}/{len(resultados)}")
        print(f"\n📊 Productos totales extraídos: {sum(len(r['productos']) for _, r in resultados if r is not None)}")

        print("\n📈 Distribución por categoría:")
        categorias = {}
        for _, r in resultados:
            if r is not None:
                for p in r['productos']:
                    cat = p['categoria']
                    categorias[cat] = categorias.get(cat, 0) + 1

        for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {cat.title()}: {count}")

        print("\n📈 Distribución por urgencia:")
        urgencias = {}
        for _, r in resultados:
            if r is not None:
                urg = r['urgencia']
                urgencias[urg] = urgencias.get(urg, 0) + 1

        urgencia_icons = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}
        for urg, count in sorted(urgencias.items(), key=lambda x: x[1], reverse=True):
            icono = urgencia_icons.get(urg, "⚪")
            print(f"   {icono} {urg.title()}: {count}")

        print("\n" + "="*70)
        print("✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("="*70)

        print("\n💡 Próximo paso:")
        print("   Ejecuta la aplicación Streamlit para probar la interfaz web:")
        print("   $ streamlit run frontend/app.py")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Pruebas interrumpidas por el usuario")
        print()
    except Exception as e:
        print(f"\n\n❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
        print()


if __name__ == "__main__":
    main()
