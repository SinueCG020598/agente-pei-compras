"""
Pestaña para Generar RFQs - Frontend Streamlit

Esta pestaña permite:
1. Buscar solicitudes procesadas
2. Ver proveedores recomendados
3. Generar borradores de RFQs
4. Revisar y editar RFQs
5. Enviar RFQs por email
"""
import streamlit as st
from datetime import datetime

# Imports del sistema
import sys
from pathlib import Path

# Agregar path del proyecto
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.session import SessionLocal
from src.database.models import Solicitud, EstadoSolicitud
from src.database.crud import solicitud as crud_solicitud
from src.agents.investigador import buscar_proveedores
from src.agents.generador_rfq import (
    generar_borrador_rfq,
    enviar_rfq_existente,
    obtener_rfqs_pendientes,
)


def tab_generar_rfqs():
    """Tab para generar y enviar RFQs a proveedores."""
    st.header("📧 Generar RFQs (Solicitudes de Cotización)")

    st.markdown("""
    Esta sección te permite generar y enviar **Solicitudes de Cotización (RFQs)** profesionales
    a los proveedores recomendados para cada solicitud.

    **Proceso:**
    1. Selecciona una solicitud procesada
    2. Busca proveedores recomendados
    3. Genera borradores de RFQs
    4. Revisa y edita el contenido
    5. Envía por email
    """)

    # Paso 1: Seleccionar Solicitud
    st.subheader("1️⃣ Seleccionar Solicitud")

    db = SessionLocal()
    try:
        # Obtener solicitudes pendientes o en proceso
        solicitudes = crud_solicitud.get_by_estado(
            db, EstadoSolicitud.PENDIENTE, limit=50
        ) + crud_solicitud.get_by_estado(
            db, EstadoSolicitud.EN_PROCESO, limit=50
        )

        if not solicitudes:
            st.warning("No hay solicitudes disponibles para generar RFQs")
            st.info("Crea una nueva solicitud en la pestaña 'Nueva Solicitud'")
            return

        # Dropdown para seleccionar solicitud
        solicitud_options = {
            f"ID:{sol.id} - {sol.descripcion[:50]}... ({sol.urgencia}) - {sol.created_at.strftime('%d/%m/%Y')}": sol
            for sol in solicitudes
        }

        selected_option = st.selectbox(
            "Selecciona una solicitud:",
            options=list(solicitud_options.keys()),
            help="Muestra las solicitudes pendientes o en proceso"
        )

        solicitud_seleccionada = solicitud_options[selected_option]

        # Mostrar detalles de la solicitud
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estado", solicitud_seleccionada.estado.value)
        with col2:
            st.metric("Urgencia", solicitud_seleccionada.urgencia)
        with col3:
            st.metric("Prioridad", solicitud_seleccionada.prioridad)

        st.text_area(
            "Descripción de la Solicitud:",
            solicitud_seleccionada.descripcion,
            height=100,
            disabled=True
        )

        # Paso 2: Buscar Proveedores
        st.subheader("2️⃣ Buscar Proveedores Recomendados")

        if 'proveedores_encontrados' not in st.session_state:
            st.session_state.proveedores_encontrados = None

        col1, col2 = st.columns([3, 1])
        with col1:
            usar_web = st.checkbox(
                "Incluir búsqueda web (Serper API)",
                value=True,
                help="Busca proveedores adicionales en internet",
                key="chk_usar_web_rfq"
            )
        with col2:
            btn_buscar = st.button(
                "🔍 Buscar Proveedores",
                type="primary",
                use_container_width=True,
                key="btn_buscar_proveedores_rfq"
            )

        if btn_buscar:
            with st.spinner("Buscando proveedores..."):
                try:
                    # Extraer productos de la descripción
                    # Asumimos que ya fueron procesados en el receptor
                    productos = [
                        {
                            "nombre": solicitud_seleccionada.categoria,
                            "cantidad": solicitud_seleccionada.cantidad or "1",
                            "categoria": solicitud_seleccionada.categoria
                        }
                    ]

                    resultado = buscar_proveedores(productos, usar_web=usar_web)
                    st.session_state.proveedores_encontrados = resultado
                    st.success(f"✓ Encontrados {len(resultado.get('proveedores_recomendados', []))} proveedores")
                except Exception as e:
                    st.error(f"Error buscando proveedores: {str(e)}")

        if st.session_state.proveedores_encontrados:
            resultado_proveedores = st.session_state.proveedores_encontrados
            proveedores_recomendados = resultado_proveedores.get("proveedores_recomendados", [])

            if proveedores_recomendados:
                st.success(f"🎯 {len(proveedores_recomendados)} proveedores recomendados")

                # Paso 3: Seleccionar Proveedores para RFQ
                st.subheader("3️⃣ Seleccionar Proveedores para RFQ")

                selected_proveedores = []

                for idx, prov_rec in enumerate(proveedores_recomendados[:10], 1):  # Limitar a 10
                    prov = prov_rec.get("proveedor_data", {})
                    score = prov_rec.get("score", 0)

                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])

                    with col1:
                        seleccionado = st.checkbox(
                            f"#{idx}",
                            key=f"prov_{idx}",
                            value=(idx <= 3)  # Primeros 3 seleccionados por defecto
                        )

                    with col2:
                        st.write(f"**{prov.get('nombre', 'N/A')}**")

                    with col3:
                        st.write(f"📊 Score: {score:.0f}")

                    with col4:
                        st.write(f"✉️ {prov.get('email', 'N/A')}")

                    if seleccionado:
                        selected_proveedores.append({
                            "proveedor_data": prov,
                            "score": score
                        })

                if selected_proveedores:
                    st.info(f"📌 {len(selected_proveedores)} proveedor(es) seleccionado(s)")

                    # Paso 4: Generar Borradores de RFQs
                    st.subheader("4️⃣ Generar Borradores de RFQs")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(
                            f"📝 Generar {len(selected_proveedores)} Borrador(es)",
                            type="primary",
                            use_container_width=True,
                            key="btn_generar_borradores_rfq"
                        ):
                            with st.spinner("Generando borradores con IA..."):
                                try:
                                    # Extraer productos
                                    productos = [
                                        {
                                            "nombre": solicitud_seleccionada.categoria,
                                            "cantidad": solicitud_seleccionada.cantidad or "1",
                                            "categoria": solicitud_seleccionada.categoria,
                                            "especificaciones": solicitud_seleccionada.descripcion[:200]
                                        }
                                    ]

                                    borradores_creados = 0
                                    for prov_rec in selected_proveedores:
                                        prov = prov_rec["proveedor_data"]

                                        resultado_rfq = generar_borrador_rfq(
                                            solicitud_id=solicitud_seleccionada.id,
                                            proveedor=prov,
                                            productos=productos,
                                            urgencia=solicitud_seleccionada.urgencia
                                        )

                                        if resultado_rfq.get("exito"):
                                            borradores_creados += 1

                                    st.success(f"✓ {borradores_creados} borrador(es) de RFQ creado(s)")
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"Error generando borradores: {str(e)}")
            else:
                st.warning("No se encontraron proveedores recomendados")

        # Paso 5: Ver y Enviar Borradores Pendientes
        st.subheader("5️⃣ Borradores Pendientes de Envío")

        borradores = obtener_rfqs_pendientes(solicitud_id=solicitud_seleccionada.id)

        if borradores:
            st.info(f"📋 {len(borradores)} borrador(es) pendiente(s) de envío")

            for borrador in borradores:
                with st.expander(
                    f"📄 {borrador['numero_rfq']} - {borrador['proveedor_nombre']}",
                    expanded=False
                ):
                    st.write(f"**Destinatario:** {borrador['proveedor_nombre']}")
                    st.write(f"**Email:** {borrador['proveedor_email']}")
                    st.write(f"**Creado:** {borrador['created_at'].strftime('%d/%m/%Y %H:%M')}")

                    # Mostrar contenido
                    contenido_editado = st.text_area(
                        "Contenido del RFQ:",
                        value=borrador['contenido'],
                        height=300,
                        key=f"contenido_{borrador['id']}"
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if st.button(
                            "📤 Enviar RFQ",
                            key=f"enviar_{borrador['id']}",
                            type="primary"
                        ):
                            with st.spinner(f"Enviando a {borrador['proveedor_nombre']}..."):
                                try:
                                    # Usar contenido editado si es diferente
                                    contenido_final = contenido_editado if contenido_editado != borrador['contenido'] else None

                                    resultado = enviar_rfq_existente(
                                        borrador['id'],
                                        contenido_editado=contenido_final
                                    )

                                    if resultado.get("exito"):
                                        st.success(f"✓ RFQ enviado a {borrador['proveedor_email']}")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {resultado.get('error')}")
                                except Exception as e:
                                    st.error(f"Error enviando: {str(e)}")

                    with col2:
                        if st.button(
                            "👁️ Vista Previa",
                            key=f"preview_{borrador['id']}"
                        ):
                            st.code(contenido_editado, language="text")

                    with col3:
                        if st.button(
                            "🗑️ Eliminar",
                            key=f"delete_{borrador['id']}"
                        ):
                            st.warning("Funcionalidad de eliminar próximamente")
        else:
            st.info("No hay borradores pendientes para esta solicitud")
            st.markdown("💡 **Tip:** Genera borradores en el paso 4 para verlos aquí")

    finally:
        db.close()
