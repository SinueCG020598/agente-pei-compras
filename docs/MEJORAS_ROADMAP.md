# 🚀 MEJORAS AL ROADMAP - Sistema PEI Compras AI

**Fecha de creación:** 2025-01-11
**Versión:** 1.0
**Autor:** Análisis basado en objetivos del usuario

---

## 📊 Resumen Ejecutivo

Este documento detalla las mejoras propuestas al roadmap original para cumplir completamente con los objetivos del sistema:

### Objetivos del Sistema (Requisitos del Usuario):
1. ✅ Transformar requisición u orden en orden de compra
2. ✅ Buscar proveedores o producto en internet **[MEJORAR]**
3. ✅ Dar mejores precios **[MEJORAR]**
4. ✅ Enviar correo a proveedores para solicitar cotización
5. ✅ Devolver enlaces de compra en ecommerce **[AGREGAR]**
6. ✅ Leer correos
7. ✅ Actualizar, eliminar y consultar información **[MEJORAR]**
8. ✅ Gestionar status de envíos **[AGREGAR]**

---

## 🎯 GAPS Identificados en Roadmap Original

| # | Objetivo | Estado Actual | Gap Identificado |
|---|----------|---------------|------------------|
| 1 | Buscar proveedores en Internet | ⚠️ Serper API "opcional" | NO implementado, solo mencionado |
| 2 | Dar mejores precios | ❌ No busca precios web | No compara BD vs Internet |
| 3 | Enlaces de ecommerce | ❌ No existe | No devuelve enlaces para compra manual |
| 4 | CRUD completo | ⚠️ Solo CREATE/READ | Falta UPDATE/DELETE |
| 5 | Gestión de envíos | ❌ No existe | Sin tracking de entregas |

---

## 📋 MEJORAS POR FASE

### **FASE 0: Setup Inicial**
**Estado:** ✅ Sin cambios necesarios

---

### **FASE 1: Core + Base de Datos** [MEJORAR]

#### ✅ **Existente:**
- Modelos: Solicitud, Proveedor, RFQ, Cotizacion, OrdenCompra
- CRUD básico: CREATE, READ

#### ➕ **MEJORAS PROPUESTAS:**

##### 1.1 Nuevo Modelo: EnvioTracking

**Archivo:** `database/models.py`

```python
class EnvioTracking(Base):
    """Tracking de envíos y entregas"""
    __tablename__ = "envios_tracking"

    id = Column(Integer, primary_key=True, index=True)
    orden_compra_id = Column(Integer, ForeignKey('ordenes_compra.id'))

    # Información del envío
    status = Column(String, default='pendiente')  # pendiente, en_transito, entregado, cancelado
    tracking_number = Column(String, nullable=True)
    proveedor_envio = Column(String, nullable=True)  # DHL, FedEx, Estafeta, etc.

    # Fechas
    fecha_envio = Column(DateTime, nullable=True)
    fecha_entrega_estimada = Column(DateTime, nullable=True)
    fecha_entrega_real = Column(DateTime, nullable=True)

    # Ubicación y detalles
    ubicacion_actual = Column(String, nullable=True)
    ciudad_origen = Column(String, nullable=True)
    ciudad_destino = Column(String, nullable=True)

    # Información adicional
    notas = Column(Text, nullable=True)
    eventos = Column(JSON, nullable=True)  # Historial de eventos del tracking

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación
    orden_compra = relationship("OrdenCompra", back_populates="envio_tracking")
```

**Actualizar modelo OrdenCompra:**
```python
class OrdenCompra(Base):
    # ... código existente ...

    # AGREGAR relación:
    envio_tracking = relationship("EnvioTracking", back_populates="orden_compra", uselist=False)
```

##### 1.2 CRUD Completo: UPDATE y DELETE

**Archivo:** `database/crud.py`

```python
# ===== PROVEEDORES - OPERACIONES COMPLETAS =====

def actualizar_proveedor(db: Session, proveedor_id: int, datos: dict):
    """
    Actualiza información de un proveedor

    Args:
        db: Sesión de base de datos
        proveedor_id: ID del proveedor
        datos: Dict con campos a actualizar

    Returns:
        Proveedor actualizado
    """
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id == proveedor_id
    ).first()

    if not proveedor:
        return None

    # Actualizar solo los campos proporcionados
    for key, value in datos.items():
        if hasattr(proveedor, key):
            setattr(proveedor, key, value)

    proveedor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(proveedor)
    return proveedor


def eliminar_proveedor(db: Session, proveedor_id: int, hard_delete: bool = False):
    """
    Elimina un proveedor (soft delete por defecto)

    Args:
        db: Sesión de base de datos
        proveedor_id: ID del proveedor
        hard_delete: Si True, elimina permanentemente. Si False, solo marca como inactivo

    Returns:
        True si se eliminó exitosamente
    """
    proveedor = db.query(models.Proveedor).filter(
        models.Proveedor.id == proveedor_id
    ).first()

    if not proveedor:
        return False

    if hard_delete:
        # Eliminación permanente
        db.delete(proveedor)
    else:
        # Soft delete: solo marcar como inactivo
        proveedor.activo = 0

    db.commit()
    return True


# ===== SOLICITUDES - OPERACIONES COMPLETAS =====

def actualizar_solicitud(db: Session, solicitud_id: int, datos: dict):
    """Actualiza campos de una solicitud"""
    solicitud = db.query(models.Solicitud).filter(
        models.Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        return None

    for key, value in datos.items():
        if hasattr(solicitud, key):
            setattr(solicitud, key, value)

    solicitud.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(solicitud)
    return solicitud


def eliminar_solicitud(db: Session, solicitud_id: int):
    """Cancela una solicitud (soft delete)"""
    solicitud = db.query(models.Solicitud).filter(
        models.Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        return False

    solicitud.estado = 'cancelada'
    solicitud.updated_at = datetime.utcnow()
    db.commit()
    return True


# ===== ÓRDENES DE COMPRA - OPERACIONES COMPLETAS =====

def actualizar_orden_compra(db: Session, orden_id: int, datos: dict):
    """Actualiza una orden de compra"""
    orden = db.query(models.OrdenCompra).filter(
        models.OrdenCompra.id == orden_id
    ).first()

    if not orden:
        return None

    for key, value in datos.items():
        if hasattr(orden, key):
            setattr(orden, key, value)

    db.commit()
    db.refresh(orden)
    return orden


def cancelar_orden_compra(db: Session, orden_id: int, motivo: str = ""):
    """Cancela una orden de compra"""
    orden = db.query(models.OrdenCompra).filter(
        models.OrdenCompra.id == orden_id
    ).first()

    if not orden:
        return False

    orden.estado = 'cancelada'
    if motivo:
        orden.notas = f"{orden.notas or ''}\nCANCELADA: {motivo}"
    db.commit()
    return True
```

##### 1.3 Función Consultar Historial Completo

**Archivo:** `database/crud.py`

```python
# ===== CONSULTAS AVANZADAS =====

def consultar_historial(db: Session, solicitud_id: int) -> dict:
    """
    Devuelve historial completo de una solicitud con todas sus relaciones

    Args:
        db: Sesión de base de datos
        solicitud_id: ID de la solicitud

    Returns:
        Dict con historial completo:
        - Solicitud original
        - RFQs enviados
        - Cotizaciones recibidas
        - Orden de compra (si existe)
        - Tracking de envío (si existe)
    """
    solicitud = db.query(models.Solicitud).filter(
        models.Solicitud.id == solicitud_id
    ).first()

    if not solicitud:
        return {"error": "Solicitud no encontrada"}

    # Obtener RFQs
    rfqs = db.query(models.RFQ).filter(
        models.RFQ.solicitud_id == solicitud_id
    ).all()

    # Obtener cotizaciones
    cotizaciones = []
    for rfq in rfqs:
        if rfq.cotizacion:
            cotizaciones.append({
                "id": rfq.cotizacion.id,
                "rfq_id": rfq.id,
                "proveedor": rfq.proveedor.nombre,
                "precio_total": rfq.cotizacion.precio_total,
                "plazo_entrega": rfq.cotizacion.plazo_entrega,
                "score": rfq.cotizacion.score,
                "seleccionada": rfq.cotizacion.seleccionada,
                "fecha": rfq.cotizacion.created_at
            })

    # Obtener orden de compra si existe
    orden_compra = None
    envio_tracking = None

    if cotizaciones:
        for cot in cotizaciones:
            cot_obj = db.query(models.Cotizacion).filter(
                models.Cotizacion.id == cot["id"]
            ).first()

            if cot_obj and cot_obj.orden_compra:
                orden_compra = {
                    "id": cot_obj.orden_compra.id,
                    "numero_oc": cot_obj.orden_compra.numero_oc,
                    "estado": cot_obj.orden_compra.estado,
                    "pdf_path": cot_obj.orden_compra.pdf_path,
                    "autorizado_por": cot_obj.orden_compra.autorizado_por,
                    "fecha_creacion": cot_obj.orden_compra.created_at
                }

                # Obtener tracking si existe
                if cot_obj.orden_compra.envio_tracking:
                    envio = cot_obj.orden_compra.envio_tracking
                    envio_tracking = {
                        "status": envio.status,
                        "tracking_number": envio.tracking_number,
                        "proveedor_envio": envio.proveedor_envio,
                        "fecha_envio": envio.fecha_envio,
                        "fecha_entrega_estimada": envio.fecha_entrega_estimada,
                        "fecha_entrega_real": envio.fecha_entrega_real,
                        "ubicacion_actual": envio.ubicacion_actual
                    }
                break

    # Construir historial completo
    historial = {
        "solicitud": {
            "id": solicitud.id,
            "origen": solicitud.origen,
            "contenido_original": solicitud.contenido_original,
            "productos": solicitud.productos,
            "estado": solicitud.estado,
            "urgencia": solicitud.urgencia,
            "presupuesto": solicitud.presupuesto,
            "fecha_creacion": solicitud.created_at,
            "ultima_actualizacion": solicitud.updated_at
        },
        "rfqs_enviados": [
            {
                "id": rfq.id,
                "proveedor": rfq.proveedor.nombre,
                "estado": rfq.estado,
                "fecha_envio": rfq.enviado_at,
                "fecha_respuesta": rfq.respondido_at
            }
            for rfq in rfqs
        ],
        "cotizaciones_recibidas": cotizaciones,
        "orden_compra": orden_compra,
        "envio_tracking": envio_tracking,
        "timeline": _generar_timeline(solicitud, rfqs, cotizaciones, orden_compra, envio_tracking)
    }

    return historial


def _generar_timeline(solicitud, rfqs, cotizaciones, orden_compra, envio_tracking) -> list:
    """
    Genera timeline cronológica de eventos
    """
    eventos = []

    # Evento 1: Solicitud creada
    eventos.append({
        "fecha": solicitud.created_at,
        "tipo": "solicitud_creada",
        "descripcion": f"Solicitud #{solicitud.id} creada vía {solicitud.origen}"
    })

    # Evento 2: RFQs enviados
    for rfq in rfqs:
        eventos.append({
            "fecha": rfq.enviado_at,
            "tipo": "rfq_enviado",
            "descripcion": f"RFQ enviado a {rfq.proveedor.nombre}"
        })

        if rfq.respondido_at:
            eventos.append({
                "fecha": rfq.respondido_at,
                "tipo": "cotizacion_recibida",
                "descripcion": f"Cotización recibida de {rfq.proveedor.nombre}"
            })

    # Evento 3: Orden de compra
    if orden_compra:
        eventos.append({
            "fecha": orden_compra["fecha_creacion"],
            "tipo": "orden_compra_generada",
            "descripcion": f"Orden de compra {orden_compra['numero_oc']} generada"
        })

    # Evento 4: Envío
    if envio_tracking:
        if envio_tracking["fecha_envio"]:
            eventos.append({
                "fecha": envio_tracking["fecha_envio"],
                "tipo": "producto_enviado",
                "descripcion": f"Producto enviado - Tracking: {envio_tracking['tracking_number']}"
            })

        if envio_tracking["fecha_entrega_real"]:
            eventos.append({
                "fecha": envio_tracking["fecha_entrega_real"],
                "tipo": "producto_entregado",
                "descripcion": "Producto entregado exitosamente"
            })

    # Ordenar por fecha
    eventos.sort(key=lambda x: x["fecha"] if x["fecha"] else datetime.min)

    return eventos


# ===== TRACKING DE ENVÍOS =====

def crear_tracking_envio(db: Session, orden_compra_id: int, datos: dict):
    """Crea registro de tracking para una orden de compra"""
    tracking = models.EnvioTracking(
        orden_compra_id=orden_compra_id,
        **datos
    )
    db.add(tracking)
    db.commit()
    db.refresh(tracking)
    return tracking


def actualizar_tracking_envio(db: Session, tracking_id: int, datos: dict):
    """Actualiza información de tracking"""
    tracking = db.query(models.EnvioTracking).filter(
        models.EnvioTracking.id == tracking_id
    ).first()

    if not tracking:
        return None

    for key, value in datos.items():
        if hasattr(tracking, key):
            setattr(tracking, key, value)

    tracking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(tracking)
    return tracking


def obtener_envios_pendientes(db: Session):
    """Obtiene todos los envíos que están en tránsito"""
    return db.query(models.EnvioTracking).filter(
        models.EnvioTracking.status.in_(["pendiente", "en_transito"])
    ).all()
```

#### 📝 **Checklist de Implementación FASE 1:**

- [ ] Agregar modelo `EnvioTracking` a `database/models.py`
- [ ] Agregar relación en `OrdenCompra` model
- [ ] Implementar funciones UPDATE:
  - [ ] `actualizar_proveedor()`
  - [ ] `actualizar_solicitud()`
  - [ ] `actualizar_orden_compra()`
- [ ] Implementar funciones DELETE:
  - [ ] `eliminar_proveedor()`
  - [ ] `eliminar_solicitud()`
  - [ ] `cancelar_orden_compra()`
- [ ] Implementar `consultar_historial()`
- [ ] Implementar funciones de tracking:
  - [ ] `crear_tracking_envio()`
  - [ ] `actualizar_tracking_envio()`
  - [ ] `obtener_envios_pendientes()`
- [ ] Ejecutar migraciones de BD
- [ ] Probar CRUD completo

---

### **FASE 2: Agente Receptor + Formulario**
**Estado:** ✅ Sin cambios necesarios

---

### **FASE 3: Agente Investigador + BD Proveedores** [MEJORA CRÍTICA]

#### ✅ **Existente:**
- Búsqueda en BD local de proveedores
- Match producto-proveedor

#### ➕ **MEJORAS PROPUESTAS:**

##### 3.1 Nuevo Servicio: SearchService

**Archivo:** `services/search_service.py` (CREAR NUEVO)

```python
"""
Servicio de búsqueda web usando Serper API
Permite buscar proveedores y productos en internet
"""

import requests
import os
from typing import List, Dict
import re


class SearchService:
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"

        if not self.serper_api_key:
            print("⚠️  SERPER_API_KEY no configurada - búsqueda web deshabilitada")

    def is_available(self) -> bool:
        """Verifica si el servicio está disponible"""
        return self.serper_api_key is not None and self.serper_api_key != "your-serper-key"

    def buscar_proveedores_web(
        self,
        producto: str,
        ubicacion: str = "México",
        num_resultados: int = 10
    ) -> List[Dict]:
        """
        Busca proveedores en internet usando Google Search

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

            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }

            response = requests.post(self.base_url, json=payload, headers=headers)
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

            return proveedores_web

        except Exception as e:
            print(f"❌ Error buscando proveedores web: {e}")
            return []

    def buscar_en_ecommerce(
        self,
        producto: str,
        marketplaces: List[str] = None
    ) -> List[Dict]:
        """
        Busca producto en marketplaces (Amazon, MercadoLibre, etc.)
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

                headers = {
                    "X-API-KEY": self.serper_api_key,
                    "Content-Type": "application/json"
                }

                response = requests.post(self.base_url, json=payload, headers=headers)
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

            except Exception as e:
                print(f"❌ Error buscando en {marketplace}: {e}")
                continue

        return resultados_ecommerce

    def buscar_mejores_precios(self, producto: str) -> Dict:
        """
        Busca mejores precios en múltiples fuentes
        Combina búsqueda de proveedores y ecommerce

        Returns:
            Dict con todos los resultados organizados
        """
        return {
            "proveedores_web": self.buscar_proveedores_web(producto),
            "ecommerce": self.buscar_en_ecommerce(producto),
            "producto_buscado": producto
        }

    def _extraer_precio(self, texto: str) -> str:
        """Extrae precio del texto usando regex"""
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


# Instancia global
search_service = SearchService()
```

##### 3.2 Actualizar Agente Investigador

**Archivo:** `agents/investigador.py` (MODIFICAR)

Agregar al inicio:
```python
from services.search_service import search_service
```

Modificar función `buscar_proveedores()`:

```python
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
        # 1. Obtener todos los proveedores activos de BD LOCAL
        proveedores_bd = db.query(Proveedor).filter(Proveedor.activo == 1).all()

        if not proveedores_bd:
            proveedores_bd = []

        # Preparar info para el agente
        info_proveedores_bd = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "productos": p.productos,
                "rating": p.rating,
                "email": p.email,
                "telefono": p.telefono,
                "notas": p.notas,
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

Analiza TODAS las opciones y recomienda:
1. Qué proveedores de BD contactar
2. Qué proveedores web investigar más
3. Qué productos se pueden comprar directo en ecommerce (más rápido)
4. Cuál es la estrategia más eficiente (precio vs tiempo)
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
                        "contacto": proveedor.contacto
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
```

##### 3.3 Actualizar Prompt del Investigador

**Archivo:** `prompts/investigador_prompt.txt` (MODIFICAR)

Agregar soporte para múltiples fuentes:

```
Eres un agente experto en sourcing y procurement.

Tu tarea es analizar múltiples fuentes de proveedores y recomendar la mejor estrategia de compra:

FUENTES DISPONIBLES:
1. BASE DE DATOS LOCAL: Proveedores con los que ya tenemos relación
2. PROVEEDORES WEB: Proveedores encontrados en internet mediante búsqueda
3. ECOMMERCE: Productos disponibles para compra inmediata en marketplaces

CRITERIOS DE EVALUACIÓN:
1. PROVEEDORES BD (prioridad alta):
   - Ya tenemos relación comercial
   - Conocemos su confiabilidad (rating)
   - Proceso de cotización establecido
   - Pueden ofrecer mejores términos de pago

2. PROVEEDORES WEB (prioridad media):
   - Nuevas opciones potencialmente más económicas
   - Requieren validación antes de comprar
   - Buenos para comparar precios de mercado

3. ECOMMERCE (prioridad según urgencia):
   - Compra inmediata sin proceso de cotización
   - Útil para urgencias o cantidades pequeñas
   - Precio visible de inmediato
   - Sin negociación de términos

ANÁLISIS REQUERIDO:
- Para cada producto, identifica la MEJOR estrategia:
  * ¿Solicitar cotización a proveedores BD/Web?
  * ¿Comprar directo en ecommerce?
  * ¿Combinar ambas opciones?

- Justifica tu recomendación considerando:
  * Urgencia de la compra
  * Cantidad solicitada
  * Complejidad del producto
  * Precio estimado vs presupuesto

FORMATO DE SALIDA JSON:
{
  "proveedores_recomendados": [
    {
      "proveedor_id": 0,  // ID si es de BD, null si es web
      "nombre": "...",
      "fuente": "base_de_datos|web|ecommerce",
      "productos_asignados": [...],
      "justificacion": "...",
      "prioridad": "alta|media|baja",
      "estrategia": "cotizacion|compra_directa|investigar"
    }
  ],
  "enlaces_ecommerce_recomendados": [
    {
      "producto": "...",
      "marketplace": "...",
      "url": "...",
      "precio_aprox": "...",
      "razon_recomendacion": "..."
    }
  ],
  "productos_sin_fuente": [...],
  "estrategia_general": "...",
  "estimado_ahorro": "..."
}
```

#### 📝 **Checklist de Implementación FASE 3:**

- [ ] Crear `services/search_service.py`
- [ ] Implementar `SearchService` class
- [ ] Implementar `buscar_proveedores_web()`
- [ ] Implementar `buscar_en_ecommerce()`
- [ ] Implementar `buscar_mejores_precios()`
- [ ] Actualizar `agents/investigador.py`
- [ ] Modificar función `buscar_proveedores()`
- [ ] Actualizar `prompts/investigador_prompt.txt`
- [ ] Configurar `SERPER_API_KEY` en `.env`
- [ ] Probar búsqueda web
- [ ] Probar búsqueda ecommerce
- [ ] Validar integración con flujo existente

---

### **FASE 3.5: Comparador de Precios Web** [NUEVA FASE]

**Objetivo:** Comparar precios de BD vs Web vs Ecommerce y recomendar mejor estrategia

#### 📦 **Implementación:**

**Archivo:** `agents/comparador_precios.py` (CREAR NUEVO)

```python
"""
Agente Comparador de Precios
Analiza precios de múltiples fuentes y recomienda mejor opción
"""

from services.openai_service import llamar_agente
import json
import os

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
```

#### 📝 **Checklist de Implementación FASE 3.5:**

- [ ] Crear `agents/comparador_precios.py`
- [ ] Crear `prompts/comparador_precios_prompt.txt`
- [ ] Implementar función `comparar_precios_multiples_fuentes()`
- [ ] Integrar con `agents/orquestador.py`
- [ ] Probar comparaciones
- [ ] Validar recomendaciones

---

### **FASE 4: Generador RFQ + Email**
**Estado:** ✅ Sin cambios necesarios

---

### **FASE 5: WhatsApp Básico**
**Estado:** ✅ Sin cambios necesarios

---

### **FASE 6: Monitor + Comparador** [MEJORAR]

#### ✅ **Existente:**
- Monitor de emails
- Extracción de cotizaciones
- Comparación de cotizaciones

#### ➕ **MEJORAS PROPUESTAS:**

##### 6.1 Comparar Cotizaciones vs Precios Web

**Archivo:** `agents/analista.py` (MODIFICAR)

Agregar nueva función:

```python
def comparar_cotizaciones_vs_web(cotizaciones: list, productos_originales: list) -> dict:
    """
    Compara cotizaciones recibidas vs precios encontrados en web
    Alerta si hay mejores opciones disponibles

    Args:
        cotizaciones: Cotizaciones recibidas de proveedores
        productos_originales: Productos solicitados originalmente

    Returns:
        Dict con comparación y alertas
    """
    from services.search_service import search_service

    if not search_service.is_available():
        return {
            "mensaje": "Búsqueda web no disponible",
            "cotizaciones_analizadas": cotizaciones
        }

    alertas = []

    # Para cada producto en las cotizaciones, buscar en web
    for producto in productos_originales:
        # Buscar precio actual en ecommerce
        ecommerce_results = search_service.buscar_en_ecommerce(producto.get("nombre"))

        if not ecommerce_results:
            continue

        # Obtener precio más bajo de ecommerce
        precios_ecommerce = []
        for item in ecommerce_results:
            precio_str = item.get("precio_aprox", "")
            # Extraer número del precio
            import re
            match = re.search(r'[\d,]+\.?\d*', precio_str.replace(',', ''))
            if match:
                try:
                    precio_num = float(match.group(0))
                    precios_ecommerce.append({
                        "marketplace": item.get("marketplace"),
                        "precio": precio_num,
                        "url": item.get("url_compra")
                    })
                except:
                    pass

        if not precios_ecommerce:
            continue

        precio_min_ecommerce = min(precios_ecommerce, key=lambda x: x["precio"])

        # Comparar con cotizaciones recibidas
        for cot in cotizaciones:
            precio_cotizacion = cot.get("precio_total", 0)
            cantidad = producto.get("cantidad", 1)
            precio_unitario_cot = precio_cotizacion / cantidad if cantidad > 0 else precio_cotizacion

            # Si ecommerce es significativamente más barato (>15%)
            if precio_min_ecommerce["precio"] < precio_unitario_cot * 0.85:
                ahorro = precio_unitario_cot - precio_min_ecommerce["precio"]
                ahorro_total = ahorro * cantidad

                alertas.append({
                    "tipo": "precio_web_mejor",
                    "producto": producto.get("nombre"),
                    "proveedor_cotizacion": cot.get("proveedor"),
                    "precio_cotizacion": precio_unitario_cot,
                    "precio_web": precio_min_ecommerce["precio"],
                    "marketplace": precio_min_ecommerce["marketplace"],
                    "url_alternativa": precio_min_ecommerce["url"],
                    "ahorro_unitario": ahorro,
                    "ahorro_total": ahorro_total,
                    "porcentaje_ahorro": ((ahorro / precio_unitario_cot) * 100)
                })

    return {
        "cotizaciones_analizadas": cotizaciones,
        "alertas_precio": alertas,
        "tiene_mejores_opciones": len(alertas) > 0
    }
```

#### 📝 **Checklist de Implementación FASE 6:**

- [ ] Modificar `agents/analista.py`
- [ ] Implementar `comparar_cotizaciones_vs_web()`
- [ ] Agregar alertas en dashboard
- [ ] Integrar con flujo de comparación
- [ ] Probar con casos reales

---

### **FASE 7: Audio + Imágenes + Refinamiento**
**Estado:** ✅ Sin cambios necesarios

---

### **FASE 8: Tracking de Envíos** [NUEVA FASE]

**Objetivo:** Tracking automático de envíos con APIs de paqueterías

#### 📦 **Implementación:**

**Archivo:** `agents/tracking_agent.py` (CREAR NUEVO)

```python
"""
Agente de Tracking de Envíos
Monitorea entregas usando APIs de paqueterías
"""

import requests
from database.models import EnvioTracking, SessionLocal
from database.crud import actualizar_tracking_envio, obtener_envios_pendientes
from datetime import datetime
import os


class TrackingAgent:
    def __init__(self):
        # APIs de paqueterías (configurar según disponibilidad)
        self.dhl_api_key = os.getenv("DHL_API_KEY")
        self.fedex_api_key = os.getenv("FEDEX_API_KEY")
        self.estafeta_api_key = os.getenv("ESTAFETA_API_KEY")

    def consultar_status_envio(self, tracking_number: str, proveedor_envio: str) -> dict:
        """
        Consulta status de envío según la paquetería

        Args:
            tracking_number: Número de rastreo
            proveedor_envio: Nombre de la paquetería (DHL, FedEx, etc.)

        Returns:
            Dict con información actualizada del envío
        """
        proveedor_lower = proveedor_envio.lower()

        if "dhl" in proveedor_lower:
            return self._consultar_dhl(tracking_number)
        elif "fedex" in proveedor_lower:
            return self._consultar_fedex(tracking_number)
        elif "estafeta" in proveedor_lower:
            return self._consultar_estafeta(tracking_number)
        else:
            return self._consultar_generico(tracking_number)

    def _consultar_dhl(self, tracking_number: str) -> dict:
        """Consulta tracking de DHL"""
        # Implementar según documentación de DHL API
        # https://developer.dhl.com/api-reference/shipment-tracking

        if not self.dhl_api_key:
            return {"error": "DHL API no configurada"}

        try:
            url = f"https://api-eu.dhl.com/track/shipments"
            headers = {
                "DHL-API-Key": self.dhl_api_key
            }
            params = {
                "trackingNumber": tracking_number
            }

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            # Parsear respuesta DHL (adaptar según API real)
            return {
                "status": self._mapear_status_dhl(data),
                "ubicacion": data.get("location"),
                "eventos": data.get("events", []),
                "fecha_entrega_estimada": data.get("estimatedDelivery")
            }

        except Exception as e:
            return {"error": f"Error consultando DHL: {e}"}

    def _consultar_fedex(self, tracking_number: str) -> dict:
        """Consulta tracking de FedEx"""
        # Similar a DHL, implementar según API de FedEx
        return {"error": "FedEx API no implementada aún"}

    def _consultar_estafeta(self, tracking_number: str) -> dict:
        """Consulta tracking de Estafeta"""
        # Implementar según API de Estafeta
        return {"error": "Estafeta API no implementada aún"}

    def _consultar_generico(self, tracking_number: str) -> dict:
        """
        Consulta genérica usando web scraping o API universal
        Como alternativa: usar AfterShip API que soporta múltiples paqueterías
        """
        return {"mensaje": "Consulta manual requerida"}

    def _mapear_status_dhl(self, data: dict) -> str:
        """Mapea status de DHL a nuestros estados internos"""
        # Mapear estados de DHL a: pendiente, en_transito, entregado, cancelado
        dhl_status = data.get("status", "").lower()

        if "delivered" in dhl_status:
            return "entregado"
        elif "transit" in dhl_status or "shipment" in dhl_status:
            return "en_transito"
        elif "pending" in dhl_status:
            return "pendiente"
        else:
            return "en_transito"

    def actualizar_tracking_automatico(self):
        """
        Revisa todos los envíos pendientes/en tránsito
        y actualiza su información automáticamente
        """
        db = SessionLocal()

        try:
            envios_pendientes = obtener_envios_pendientes(db)

            print(f"🚚 Actualizando {len(envios_pendientes)} envíos...")

            for envio in envios_pendientes:
                if not envio.tracking_number or not envio.proveedor_envio:
                    continue

                # Consultar status actual
                status_actual = self.consultar_status_envio(
                    envio.tracking_number,
                    envio.proveedor_envio
                )

                if "error" in status_actual:
                    print(f"  ⚠️  Error tracking {envio.tracking_number}: {status_actual['error']}")
                    continue

                # Actualizar en BD
                datos_actualizacion = {
                    "status": status_actual.get("status", envio.status),
                    "ubicacion_actual": status_actual.get("ubicacion"),
                    "eventos": status_actual.get("eventos")
                }

                if status_actual.get("fecha_entrega_estimada"):
                    datos_actualizacion["fecha_entrega_estimada"] = status_actual["fecha_entrega_estimada"]

                # Si está entregado, registrar fecha real
                if status_actual.get("status") == "entregado" and not envio.fecha_entrega_real:
                    datos_actualizacion["fecha_entrega_real"] = datetime.now()

                    # Notificar entrega
                    self._notificar_entrega(envio)

                actualizar_tracking_envio(db, envio.id, datos_actualizacion)
                print(f"  ✓ Actualizado: {envio.tracking_number} - {status_actual.get('status')}")

            print("✅ Tracking actualizado")

        except Exception as e:
            print(f"❌ Error actualizando tracking: {e}")

        finally:
            db.close()

    def _notificar_entrega(self, envio: EnvioTracking):
        """Notifica al usuario que el paquete fue entregado"""
        from services.email_service import email_service
        from services.whatsapp import whatsapp_service

        # Obtener datos de la orden
        orden = envio.orden_compra

        mensaje = f"""
🎉 ¡Entrega Completada!

Orden de Compra: {orden.numero_oc}
Tracking: {envio.tracking_number}
Paquetería: {envio.proveedor_envio}
Fecha de entrega: {envio.fecha_entrega_real.strftime('%d/%m/%Y %H:%M')}

El pedido ha sido entregado exitosamente.
        """

        # Enviar notificación por email (si está configurado)
        try:
            email_service.enviar_email(
                destinatario=os.getenv("GMAIL_USER"),
                asunto=f"📦 Entrega Completada - OC {orden.numero_oc}",
                cuerpo=mensaje
            )
        except:
            pass

        print(f"📧 Notificación de entrega enviada para OC {orden.numero_oc}")


# Instancia global
tracking_agent = TrackingAgent()
```

**Archivo:** `scripts/actualizar_tracking.py` (CREAR NUEVO)

```python
#!/usr/bin/env python3
"""
Script para actualizar tracking de envíos
Puede ejecutarse como cron job cada hora
"""

import sys
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.tracking_agent import tracking_agent

if __name__ == "__main__":
    print("🚀 Iniciando actualización de tracking...")
    tracking_agent.actualizar_tracking_automatico()
    print("✅ Actualización completada")
```

#### 📝 **Checklist de Implementación FASE 8:**

- [ ] Crear `agents/tracking_agent.py`
- [ ] Implementar clase `TrackingAgent`
- [ ] Implementar `consultar_status_envio()`
- [ ] Implementar integraciones con APIs:
  - [ ] DHL API
  - [ ] FedEx API
  - [ ] Estafeta API
  - [ ] Alternativa: AfterShip API (universal)
- [ ] Crear `scripts/actualizar_tracking.py`
- [ ] Configurar cron job para actualización automática
- [ ] Implementar notificaciones de entrega
- [ ] Agregar dashboard de tracking en frontend
- [ ] Probar con números de tracking reales

---

## 📊 Resumen de Costos Adicionales

### Costos Mensuales Estimados (Ampliado):

| Servicio | Costo Original | Costo con Mejoras |
|----------|----------------|-------------------|
| OpenAI API | $10-30/mes | $15-40/mes |
| Serper API | OPCIONAL | **$0-50/mes** |
| APIs Paqueterías | No incluido | $0-20/mes |
| **TOTAL** | **$10-30/mes** | **$15-110/mes** |

**Desglose Serper API:**
- 2,500 búsquedas gratis/mes
- Después: $50/mes (50,000 búsquedas)
- Para MVP: **Gratis** (bajo volumen)

**APIs de Tracking:**
- DHL, FedEx: Generalmente gratis con cuenta comercial
- AfterShip: $9/mes plan básico (100 trackings/mes)

---

## 🎯 Priorización de Implementación

### **🔴 PRIORIDAD CRÍTICA** (Implementar YA):
1. ✅ **FASE 1**: CRUD completo + Modelo EnvioTracking
2. ✅ **FASE 3**: Búsqueda web (Serper API)
3. ✅ **FASE 3**: Enlaces de ecommerce

### **🟡 PRIORIDAD ALTA** (Semana 2):
4. **FASE 3.5**: Comparador de precios web
5. **FASE 6**: Comparación cotizaciones vs web

### **🟢 PRIORIDAD MEDIA** (Después del MVP):
6. **FASE 8**: Tracking básico de envíos
7. APIs de paqueterías

---

## 📝 Plan de Implementación Sugerido

### **Semana 1:**
- Día 1-2: FASE 1 mejorada
- Día 3-4: FASE 3 con búsqueda web
- Día 5: Integración y pruebas

### **Semana 2:**
- Día 1-2: FASE 3.5 (Comparador)
- Día 3-4: FASE 6 mejorada
- Día 5: Pruebas end-to-end

### **Semana 3:**
- Día 1-3: FASE 8 (Tracking)
- Día 4-5: Refinamiento y optimización

---

## 🧪 Scripts de Prueba

### Probar Búsqueda Web:
```bash
python scripts/test_search_service.py
```

### Probar CRUD Completo:
```bash
python scripts/test_crud_completo.py
```

### Probar Tracking:
```bash
python scripts/test_tracking.py
```

---

## 📚 Referencias

- [Serper API Docs](https://serper.dev/docs)
- [DHL Tracking API](https://developer.dhl.com/api-reference/shipment-tracking)
- [FedEx Developer](https://developer.fedex.com/)
- [AfterShip API](https://www.aftership.com/docs/api/4)

---

## ✅ Checklist General del Proyecto

### FASE 1:
- [ ] Modelo EnvioTracking
- [ ] CRUD completo implementado
- [ ] consultar_historial() funcionando

### FASE 3:
- [ ] SearchService creado
- [ ] Búsqueda web funcionando
- [ ] Enlaces ecommerce devueltos
- [ ] Integrado con Investigador

### FASE 3.5:
- [ ] Comparador de precios implementado
- [ ] Recomendaciones BD vs Web vs Ecommerce

### FASE 6:
- [ ] Comparación cotizaciones vs web
- [ ] Alertas de mejores precios

### FASE 8:
- [ ] TrackingAgent implementado
- [ ] Al menos 1 API de paquetería integrada
- [ ] Notificaciones de entrega
- [ ] Dashboard de tracking

---

**Última actualización:** 2025-01-11
**Próxima revisión:** Después de implementar FASE 1 y 3
