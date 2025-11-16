"""
Aplicación Web - PEI Compras AI.

Interfaz web con Streamlit para gestión de solicitudes de compra
con procesamiento automático mediante IA.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import streamlit as st
from sqlalchemy.orm import Session

# Importar módulos del proyecto
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.receptor import procesar_solicitud, validar_solicitud
from src.agents.investigador import buscar_proveedores
from src.database.session import get_db
from src.database.crud import solicitud as crud_solicitud
from src.database.models import EstadoSolicitud
from config.settings import settings

# Importar tab Generar RFQs
from frontend.tab_generar_rfqs import tab_generar_rfqs

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="PEI Compras AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# ESTILOS CSS PERSONALIZADOS
# =============================================================================

CUSTOM_CSS = """
<style>
    /* Estilos generales */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Cards de productos */
    .producto-card {
        background-color: #f8f9fa;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }

    .producto-nombre {
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }

    .producto-detalle {
        font-size: 0.9rem;
        color: #666;
        margin: 0.2rem 0;
    }

    /* Badges de urgencia */
    .urgencia-normal {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .urgencia-alta {
        background-color: #ffc107;
        color: #333;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .urgencia-urgente {
        background-color: #dc3545;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Métricas del sidebar */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.2rem;
    }

    /* Botones */
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        border: none;
    }

    .stButton>button:hover {
        background-color: #155a8a;
    }

    /* Alertas */
    .alert-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }

    .alert-error {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================


def get_estadisticas_db(db: Session) -> Dict:
    """
    Obtiene estadísticas de la base de datos.

    Args:
        db: Sesión de base de datos

    Returns:
        Dict con estadísticas
    """
    try:
        # Total de solicitudes
        total = crud_solicitud.count(db)

        # Solicitudes por estado
        pendientes = crud_solicitud.count_by_estado(db, EstadoSolicitud.PENDIENTE)
        en_proceso = crud_solicitud.count_by_estado(db, EstadoSolicitud.EN_PROCESO)
        completadas = crud_solicitud.count_by_estado(db, EstadoSolicitud.COMPLETADA)

        # Solicitudes del último mes
        from datetime import timezone
        fecha_mes_atras = datetime.now(timezone.utc) - timedelta(days=30)
        recientes = len(crud_solicitud.get_by_fecha_rango(db, fecha_mes_atras))

        return {
            "total": total,
            "pendientes": pendientes,
            "en_proceso": en_proceso,
            "completadas": completadas,
            "recientes": recientes,
        }
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {
            "total": 0,
            "pendientes": 0,
            "en_proceso": 0,
            "completadas": 0,
            "recientes": 0,
        }


def mostrar_producto_card(producto: Dict, index: int):
    """
    Muestra un card con información de un producto.

    Args:
        producto: Dict con datos del producto
        index: Índice del producto
    """
    st.markdown(
        f"""
        <div class="producto-card">
            <div class="producto-nombre">
                🔹 {producto.get('nombre', 'Sin nombre')}
            </div>
            <div class="producto-detalle">
                <strong>Cantidad:</strong> {producto.get('cantidad', 1)} unidades
            </div>
            <div class="producto-detalle">
                <strong>Categoría:</strong> {producto.get('categoria', 'N/A').title()}
            </div>
            <div class="producto-detalle">
                <strong>Especificaciones:</strong> {producto.get('especificaciones', 'No especificado')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_urgencia_badge(urgencia: Optional[str]) -> str:
    """
    Retorna el HTML para el badge de urgencia.

    Args:
        urgencia: Nivel de urgencia (puede ser None)

    Returns:
        HTML del badge
    """
    # Manejar caso cuando urgencia es None
    if urgencia is None:
        urgencia = "normal"

    urgencia = urgencia.lower()
    clase = f"urgencia-{urgencia}"

    iconos = {"normal": "🟢", "alta": "🟡", "urgente": "🔴"}

    icono = iconos.get(urgencia, "⚪")

    return f'<span class="{clase}">{icono} {urgencia.upper()}</span>'


def guardar_solicitud_db(datos: Dict, db: Session) -> Optional[int]:
    """
    Guarda una solicitud procesada en la base de datos.

    Args:
        datos: Dict con los datos de la solicitud procesada
        db: Sesión de base de datos

    Returns:
        ID de la solicitud creada o None si hay error
    """
    try:
        # Extraer información
        productos = datos.get("productos", [])
        if not productos:
            return None

        # Crear descripción consolidada
        descripcion_productos = "\n".join(
            [
                f"- {p['nombre']} (Cantidad: {p['cantidad']}, "
                f"Categoría: {p['categoria']})"
                for p in productos
            ]
        )

        # Determinar categoría principal (la más común)
        categorias = [p.get("categoria", "otros") for p in productos]
        categoria_principal = max(set(categorias), key=categorias.count)

        # Crear solicitud
        solicitud_data = {
            "usuario_nombre": st.session_state.get("usuario_nombre", "Usuario Web"),
            "usuario_contacto": st.session_state.get(
                "usuario_contacto", "web@peicompras.cl"
            ),
            "descripcion": descripcion_productos,
            "categoria": categoria_principal,
            "presupuesto": datos.get("presupuesto_estimado"),
            "estado": EstadoSolicitud.PENDIENTE,
            "notas_internas": f"Origen: Formulario Web\n"
            f"Urgencia: {datos.get('urgencia', 'normal')}\n"
            f"Notas: {datos.get('notas_adicionales', 'N/A')}",
        }

        # Guardar en BD
        solicitud = crud_solicitud.create(db, obj_in=solicitud_data)
        logger.info(f"Solicitud creada con ID: {solicitud.id}")

        return solicitud.id

    except Exception as e:
        logger.error(f"Error guardando solicitud: {e}")
        return None


# =============================================================================
# SIDEBAR - MÉTRICAS Y NAVEGACIÓN
# =============================================================================


def mostrar_sidebar():
    """Muestra el sidebar con métricas y configuración."""
    with st.sidebar:
        st.markdown(
            '<div class="main-header">🛒 PEI Compras AI</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sub-header">Sistema Inteligente de Compras</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Obtener estadísticas
        db = next(get_db())
        stats = get_estadisticas_db(db)

        # Mostrar métricas
        st.markdown("### 📊 Estadísticas")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("📝 Total", stats["total"])
            st.metric("⏳ Pendientes", stats["pendientes"])

        with col2:
            st.metric("🔄 En Proceso", stats["en_proceso"])
            st.metric("✅ Completadas", stats["completadas"])

        st.metric("📅 Últimos 30 días", stats["recientes"])

        st.markdown("---")

        # Configuración
        st.markdown("### ⚙️ Configuración")

        # Usuario
        nombre_usuario = st.text_input(
            "Tu nombre", value=st.session_state.get("usuario_nombre", "Usuario Web")
        )
        st.session_state["usuario_nombre"] = nombre_usuario

        email_usuario = st.text_input(
            "Tu email",
            value=st.session_state.get("usuario_contacto", "usuario@empresa.cl"),
        )
        st.session_state["usuario_contacto"] = email_usuario

        st.markdown("---")

        # Información del sistema
        st.markdown("### ℹ️ Sistema")
        st.text(f"Versión: {settings.VERSION}")
        st.text(f"Modelo IA: {settings.OPENAI_MODEL_MINI}")


# =============================================================================
# TAB 1: NUEVA SOLICITUD
# =============================================================================


def tab_nueva_solicitud():
    """Tab para crear nueva solicitud de compra."""
    st.markdown("## 📝 Nueva Solicitud de Compra")

    st.markdown(
        """
        Describe lo que necesitas comprar de forma natural. El sistema extraerá
        automáticamente los productos, cantidades y especificaciones.
        """
    )

    # Formulario
    with st.form("form_solicitud", clear_on_submit=False):
        # Área de texto para la descripción
        descripcion = st.text_area(
            "Describe tu solicitud de compra",
            height=200,
            placeholder="Ejemplo: Necesito 5 laptops HP para el equipo de ventas, "
            "con al menos 16GB RAM y procesador i7. También necesito "
            "2 impresoras láser multifunción. Es urgente.",
            help="Escribe de forma natural lo que necesitas. El sistema lo procesará automáticamente.",
        )

        col1, col2 = st.columns(2)

        with col1:
            # Selector de urgencia
            urgencia_manual = st.selectbox(
                "Urgencia",
                ["Auto-detectar", "Normal", "Alta", "Urgente"],
                help="El sistema puede detectar la urgencia automáticamente o puedes especificarla.",
            )

        with col2:
            # Input de presupuesto (opcional)
            presupuesto_manual = st.number_input(
                "Presupuesto estimado (MXN)",
                min_value=0,
                value=0,
                step=1000,
                help="Opcional: presupuesto disponible en pesos mexicanos.",
            )

        # Botón de envío
        submitted = st.form_submit_button("🚀 Procesar Solicitud", type="primary")

    # Procesar cuando se envía el formulario
    if submitted:
        if not descripcion or not descripcion.strip():
            st.error("❌ Por favor, describe tu solicitud de compra.")
            return

        # Mostrar spinner mientras procesa
        with st.spinner("🤖 Procesando solicitud con IA..."):
            try:
                # Procesar con el agente receptor
                resultado = procesar_solicitud(descripcion, origen="formulario")

                # Sobrescribir urgencia si se especificó manualmente
                if urgencia_manual != "Auto-detectar":
                    resultado["urgencia"] = urgencia_manual.lower()

                # Sobrescribir presupuesto si se especificó manualmente
                if presupuesto_manual > 0:
                    resultado["presupuesto_estimado"] = presupuesto_manual

                # Validar resultado
                es_valida, error = validar_solicitud(resultado)

                if not es_valida:
                    st.error(f"❌ Error en la validación: {error}")
                    return

                # Guardar en session_state
                st.session_state["ultima_solicitud"] = resultado

                # Guardar en base de datos
                db = next(get_db())
                solicitud_id = guardar_solicitud_db(resultado, db)

                if solicitud_id:
                    st.success(
                        f"✅ Solicitud procesada y guardada exitosamente (ID: {solicitud_id})"
                    )
                else:
                    st.warning("⚠️ Solicitud procesada pero no se pudo guardar en BD")

                # Mostrar resultado
                st.markdown("---")
                st.markdown("## 📋 Información Extraída")

                # Mostrar urgencia
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown("**Urgencia:**")
                    st.markdown(
                        get_urgencia_badge(resultado.get("urgencia", "normal")),
                        unsafe_allow_html=True,
                    )

                with col2:
                    presupuesto = resultado.get("presupuesto_estimado")
                    if presupuesto:
                        st.markdown("**Presupuesto Estimado:**")
                        st.markdown(f"💰 ${presupuesto:,.0f} MXN")

                # Mostrar productos
                st.markdown("### 🛍️ Productos Identificados")

                productos = resultado.get("productos", [])
                for i, producto in enumerate(productos, 1):
                    mostrar_producto_card(producto, i)

                # Notas adicionales
                notas = resultado.get("notas_adicionales", "")
                if notas:
                    st.markdown("### 📌 Notas Adicionales")
                    st.info(notas)

            except Exception as e:
                logger.error(f"Error procesando solicitud: {e}")
                st.error(f"❌ Error procesando la solicitud: {str(e)}")


# =============================================================================
# TAB 2: MIS SOLICITUDES
# =============================================================================


def tab_mis_solicitudes():
    """Tab para ver historial de solicitudes."""
    st.markdown("## 📚 Mis Solicitudes")

    # Obtener solicitudes de la BD
    db = next(get_db())

    try:
        # Filtros
        col1, col2, col3 = st.columns(3)

        with col1:
            filtro_estado = st.selectbox(
                "Estado",
                ["Todos", "Pendiente", "En Proceso", "Completada", "Cancelada"],
            )

        with col2:
            limite = st.selectbox("Mostrar", [10, 25, 50, 100], index=0)

        # Obtener solicitudes
        if filtro_estado == "Todos":
            solicitudes = crud_solicitud.get_multi(db, skip=0, limit=limite)
        else:
            estado_enum = EstadoSolicitud[filtro_estado.upper().replace(" ", "_")]
            solicitudes = crud_solicitud.get_by_estado(db, estado_enum, limit=limite)

        # Mostrar solicitudes
        if not solicitudes:
            st.info("📭 No hay solicitudes para mostrar.")
            return

        st.markdown(f"**Total:** {len(solicitudes)} solicitudes")

        # Tabla de solicitudes
        for solicitud in solicitudes:
            with st.expander(
                f"📄 Solicitud #{solicitud.id} - {solicitud.categoria.title()} - "
                f"{solicitud.estado.value.title()}"
            ):
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Usuario:** {solicitud.usuario_nombre}")
                    st.markdown(f"**Categoría:** {solicitud.categoria.title()}")
                    st.markdown(f"**Estado:** {solicitud.estado.value.title()}")

                with col2:
                    st.markdown(
                        f"**Fecha:** {solicitud.created_at.strftime('%Y-%m-%d %H:%M')}"
                    )
                    if solicitud.presupuesto:
                        st.markdown(f"**Presupuesto:** ${solicitud.presupuesto:,.0f}")
                    if solicitud.fecha_limite:
                        st.markdown(
                            f"**Fecha Límite:** {solicitud.fecha_limite.strftime('%Y-%m-%d')}"
                        )

                st.markdown("**Descripción:**")
                st.text(solicitud.descripcion)

                if solicitud.notas_internas:
                    st.markdown("**Notas:**")
                    st.text(solicitud.notas_internas)

    except Exception as e:
        logger.error(f"Error obteniendo solicitudes: {e}")
        st.error(f"❌ Error cargando solicitudes: {str(e)}")


# =============================================================================
# TAB 3: ESTADÍSTICAS
# =============================================================================


def tab_estadisticas():
    """Tab con estadísticas y métricas."""
    st.markdown("## 📊 Estadísticas y Métricas")

    db = next(get_db())
    stats = get_estadisticas_db(db)

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📝 Total Solicitudes", stats["total"])

    with col2:
        st.metric("⏳ Pendientes", stats["pendientes"])

    with col3:
        st.metric("🔄 En Proceso", stats["en_proceso"])

    with col4:
        st.metric("✅ Completadas", stats["completadas"])

    st.markdown("---")

    # Solicitudes recientes
    st.markdown("### 📅 Actividad Reciente (30 días)")
    st.metric("Solicitudes creadas", stats["recientes"])

    # Información adicional
    st.markdown("---")
    st.markdown("### 💡 Información del Sistema")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Versión:** {settings.VERSION}")
        st.markdown(f"**Modelo IA (Mini):** {settings.OPENAI_MODEL_MINI}")
        st.markdown(f"**Modelo IA (Full):** {settings.OPENAI_MODEL_FULL}")

    with col2:
        st.markdown(f"**Base de Datos:** SQLite")
        st.markdown(f"**Debug Mode:** {settings.DEBUG}")


def tab_buscar_proveedores():
    """Tab para buscar proveedores para solicitudes existentes."""
    st.markdown("## 🔍 Buscar Proveedores")
    st.markdown("Busca proveedores en BD, Web y E-commerce para tus solicitudes.")

    # Obtener solicitudes pendientes
    db = next(get_db())
    solicitudes = crud_solicitud.get_multi(db, limit=100)

    if not solicitudes:
        st.info("📭 No hay solicitudes en el sistema. Crea una primero en el tab 'Nueva Solicitud'.")
        return

    # Selectbox para elegir solicitud
    solicitud_options = {
        f"#{sol.id} - {sol.descripcion[:50]}... ({sol.estado.value})": sol
        for sol in solicitudes
    }

    selected_key = st.selectbox(
        "Selecciona una solicitud para buscar proveedores:",
        options=list(solicitud_options.keys())
    )

    solicitud_sel = solicitud_options[selected_key]

    # Mostrar detalles de la solicitud
    with st.expander("📋 Ver detalles de la solicitud", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**ID:** {solicitud_sel.id}")
            st.markdown(f"**Estado:** {solicitud_sel.estado.value}")
            st.markdown(f"**Creada:** {solicitud_sel.created_at.strftime('%Y-%m-%d %H:%M')}")

        with col2:
            st.markdown(f"**Categoría:** {solicitud_sel.categoria}")
            st.markdown(f"**Urgencia:** {get_urgencia_badge(solicitud_sel.urgencia)}", unsafe_allow_html=True)
            if solicitud_sel.presupuesto:
                st.markdown(f"**Presupuesto:** ${solicitud_sel.presupuesto:,.0f} MXN")

        st.markdown(f"**Descripción:** {solicitud_sel.descripcion}")

    # Botón para buscar proveedores
    col1, col2 = st.columns([1, 3])
    with col1:
        usar_web = st.checkbox("Buscar en Web", value=True, help="Incluir búsqueda en internet y e-commerce")

    if st.button("🔍 Buscar Proveedores", type="primary", use_container_width=True):
        # Preparar productos para la búsqueda
        productos = [
            {
                "nombre": solicitud_sel.descripcion,
                "cantidad": 1,  # TODO: extraer de productos relacionados
                "categoria": solicitud_sel.categoria
            }
        ]

        with st.spinner("🌐 Buscando proveedores en múltiples fuentes..."):
            try:
                resultado = buscar_proveedores(productos, usar_web=usar_web)

                # Guardar en session_state
                st.session_state["resultado_proveedores"] = resultado
                st.session_state["solicitud_id_busqueda"] = solicitud_sel.id

                st.success("✅ Búsqueda completada!")

            except Exception as e:
                st.error(f"❌ Error buscando proveedores: {str(e)}")
                logger.error(f"Error en búsqueda: {e}", exc_info=True)
                return

    # Mostrar resultados si existen
    if "resultado_proveedores" in st.session_state and st.session_state.get("solicitud_id_busqueda") == solicitud_sel.id:
        resultado = st.session_state["resultado_proveedores"]

        st.markdown("---")
        st.markdown("## 📊 Resultados de Búsqueda")

        # Resumen
        resumen = resultado.get("resumen", {})
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("🏢 Proveedores BD", resumen.get("total_proveedores_bd", 0))
        with col2:
            st.metric("🌐 Proveedores Web", resumen.get("total_proveedores_web", 0))
        with col3:
            st.metric("🛒 Enlaces E-commerce", resumen.get("total_enlaces_ecommerce", 0))
        with col4:
            status = "✅ Activa" if resumen.get("busqueda_web_activa") else "❌ Inactiva"
            st.metric("Búsqueda Web", status)

        # Tabs para cada tipo de proveedor
        tab_bd, tab_web, tab_ecommerce, tab_recs = st.tabs([
            "🏢 Proveedores BD", "🌐 Proveedores Web", "🛒 E-commerce", "💡 Recomendaciones"
        ])

        with tab_bd:
            proveedores_bd = resultado.get("proveedores_bd", [])
            if proveedores_bd:
                for prov in proveedores_bd:
                    with st.container():
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown(f"### {prov['nombre']}")
                            st.markdown(f"**Categoría:** {prov.get('categoria', 'N/A')}")
                            if prov.get('notas'):
                                st.markdown(f"_{prov['notas']}_")

                        with col2:
                            if prov.get('rating'):
                                st.metric("⭐ Rating", f"{prov['rating']}/5.0")
                            if prov.get('email'):
                                st.markdown(f"📧 `{prov['email']}`")
                            if prov.get('telefono'):
                                st.markdown(f"📞 `{prov['telefono']}`")
                            if prov.get('ciudad'):
                                st.markdown(f"📍 {prov['ciudad']}")

                        st.markdown("---")
            else:
                st.info("No hay proveedores en la base de datos para esta categoría.")

        with tab_web:
            proveedores_web = resultado.get("proveedores_web", [])
            if proveedores_web:
                for prov in proveedores_web:
                    with st.container():
                        st.markdown(f"### {prov['nombre']}")
                        st.markdown(f"**URL:** {prov['url']}")
                        st.markdown(f"{prov.get('descripcion', '')}")
                        st.markdown(f"📊 Relevancia: #{prov.get('score_relevancia', 'N/A')}")
                        st.link_button("🌐 Visitar sitio web", prov['url'])
                        st.markdown("---")
            else:
                st.info("No se encontraron proveedores web. Activa la búsqueda web para ver resultados.")

        with tab_ecommerce:
            enlaces_ecommerce = resultado.get("enlaces_ecommerce", [])
            if enlaces_ecommerce:
                for prod in enlaces_ecommerce:
                    with st.container():
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"### {prod['producto']}")
                            st.markdown(f"**{prod['marketplace']}**")
                            if prod.get('descripcion'):
                                st.markdown(f"_{prod['descripcion'][:150]}..._")

                        with col2:
                            if prod.get('precio_aprox'):
                                st.metric("💰 Precio", prod['precio_aprox'])
                            st.link_button("🛒 Comprar", prod['url_compra'])

                        st.markdown("---")
            else:
                st.info("No se encontraron productos en e-commerce.")

        with tab_recs:
            recomendaciones = resultado.get("recomendaciones", {})
            if recomendaciones:
                st.markdown("### 💡 Proveedores Recomendados")

                for i, rec in enumerate(recomendaciones.get("proveedores_recomendados", []), 1):
                    with st.container():
                        st.markdown(f"#### {i}. {rec.get('nombre', 'N/A')}")

                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown(f"**Fuente:** {rec.get('fuente', 'N/A')}")
                            st.markdown(f"**Estrategia:** {rec.get('estrategia', 'N/A')}")
                            st.markdown(f"**Justificación:** {rec.get('justificacion', 'N/A')}")

                            if rec.get('como_contactar'):
                                st.info(f"📞 {rec['como_contactar']}")

                        with col2:
                            prioridad = rec.get('prioridad', 'media')
                            color = {"alta": "🔴", "media": "🟡", "baja": "🟢"}
                            st.metric("Prioridad", f"{color.get(prioridad, '⚪')} {prioridad.upper()}")

                            # Mostrar contacto si disponible
                            if rec.get('email'):
                                st.markdown(f"📧 {rec['email']}")
                            if rec.get('telefono'):
                                st.markdown(f"📞 {rec['telefono']}")
                            if rec.get('url'):
                                st.link_button("🔗 Ver sitio", rec['url'])

                        st.markdown("---")

                # Estrategia general
                if recomendaciones.get('estrategia_general'):
                    st.markdown("### 📋 Estrategia General")
                    st.info(recomendaciones['estrategia_general'])

                if recomendaciones.get('siguiente_paso'):
                    st.markdown("### 🎯 Siguiente Paso")
                    st.success(recomendaciones['siguiente_paso'])
            else:
                st.info("No hay recomendaciones disponibles.")


# =============================================================================
# APLICACIÓN PRINCIPAL
# =============================================================================


def main():
    """Función principal de la aplicación."""
    # Mostrar sidebar
    mostrar_sidebar()

    # Header principal
    st.markdown(
        '<div class="main-header">Sistema PEI Compras AI</div>',
        unsafe_allow_html=True,
    )

    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📝 Nueva Solicitud", "🔍 Buscar Proveedores", "📧 Generar RFQs", "📚 Mis Solicitudes", "📊 Estadísticas"]
    )

    with tab1:
        tab_nueva_solicitud()

    with tab2:
        tab_buscar_proveedores()

    with tab3:
        tab_generar_rfqs()

    with tab4:
        tab_mis_solicitudes()

    with tab5:
        tab_estadisticas()

if __name__ == "__main__":
    main()
