"""
Script para poblar la base de datos con proveedores de prueba.

Este script crea proveedores de ejemplo en diferentes categorías
para testing y desarrollo.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.session import SessionLocal
from src.database import crud
from config.logging_config import logger

# Datos de proveedores de prueba
PROVEEDORES_SEED = [
    # Tecnología
    {
        "nombre": "Tech Solutions Chile",
        "razon_social": "Tech Solutions Chile SpA",
        "rut": "76.123.456-7",
        "email": "ventas@techsolutions.cl",
        "telefono": "+56 2 2345 6789",
        "direccion": "Av. Apoquindo 4499, Piso 10",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.techsolutions.cl",
        "categoria": "tecnologia",
        "subcategorias": "computadores, laptops, servidores, networking",
        "rating": 4.5,
        "es_verificado": True,
        "notas": "Proveedor especializado en equipos HP y Dell",
    },
    {
        "nombre": "Digitech Store",
        "razon_social": "Digitech Store Ltda",
        "rut": "77.234.567-8",
        "email": "contacto@digitech.cl",
        "telefono": "+56 2 3456 7890",
        "direccion": "Av. Providencia 1650",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.digitech.cl",
        "categoria": "tecnologia",
        "subcategorias": "notebooks, tablets, accesorios, software",
        "rating": 4.2,
        "es_verificado": True,
        "notas": "Importador directo de equipos Lenovo y Asus",
    },
    {
        "nombre": "Infotech Ltda",
        "razon_social": "Infotech Limitada",
        "rut": "78.345.678-9",
        "email": "ventas@infotech.cl",
        "telefono": "+56 2 4567 8901",
        "direccion": "Av. Libertador Bernardo O'Higgins 1234",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.infotech.cl",
        "categoria": "tecnologia",
        "subcategorias": "impresoras, multifuncionales, consumibles",
        "rating": 3.8,
        "es_verificado": False,
        "notas": "Especialista en soluciones de impresión",
    },
    # Mobiliario
    {
        "nombre": "Muebles Corporativos SA",
        "razon_social": "Muebles Corporativos Sociedad Anónima",
        "rut": "79.456.789-0",
        "email": "ventas@mueblescorp.cl",
        "telefono": "+56 2 5678 9012",
        "direccion": "Av. Marathon 2595",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.mueblescorp.cl",
        "categoria": "mobiliario",
        "subcategorias": "sillas, escritorios, muebles de oficina, ergonomía",
        "rating": 4.7,
        "es_verificado": True,
        "notas": "Fabricante nacional de mobiliario ergonómico",
    },
    {
        "nombre": "Oficina Total",
        "razon_social": "Oficina Total SpA",
        "rut": "80.567.890-1",
        "email": "contacto@oficinatotal.cl",
        "telefono": "+56 2 6789 0123",
        "direccion": "Av. Vitacura 5250",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.oficinatotal.cl",
        "categoria": "mobiliario",
        "subcategorias": "mobiliario modular, divisiones, almacenaje",
        "rating": 4.3,
        "es_verificado": True,
        "notas": "Distribuidor autorizado de marcas internacionales",
    },
    # Insumos
    {
        "nombre": "Suministros Empresariales Chile",
        "razon_social": "Suministros Empresariales Chile Ltda",
        "rut": "81.678.901-2",
        "email": "ventas@suministros.cl",
        "telefono": "+56 2 7890 1234",
        "direccion": "Av. Grecia 8735",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.suministros.cl",
        "categoria": "insumos",
        "subcategorias": "papelería, útiles, aseo, cafetería",
        "rating": 4.1,
        "es_verificado": True,
        "notas": "Distribuidor mayorista con entrega rápida",
    },
    {
        "nombre": "Papelería Nacional",
        "razon_social": "Papelería Nacional SA",
        "rut": "82.789.012-3",
        "email": "ventas@papelerianacional.cl",
        "telefono": "+56 2 8901 2345",
        "direccion": "Av. Irarrázaval 4750",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.papelerianacional.cl",
        "categoria": "insumos",
        "subcategorias": "papel, cuadernos, archivadores, tóner",
        "rating": 3.9,
        "es_verificado": False,
        "notas": "Fabricante nacional de productos de papel",
    },
    # Servicios
    {
        "nombre": "Servicios Integrales Empresariales",
        "razon_social": "Servicios Integrales Empresariales SpA",
        "rut": "83.890.123-4",
        "email": "contacto@sie.cl",
        "telefono": "+56 2 9012 3456",
        "direccion": "Av. Américo Vespucio 1501",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.sie.cl",
        "categoria": "servicios",
        "subcategorias": "limpieza, mantención, seguridad, logística",
        "rating": 4.6,
        "es_verificado": True,
        "notas": "Empresa con certificación ISO 9001",
    },
    {
        "nombre": "Aseo Industrial Pro",
        "razon_social": "Aseo Industrial Pro Ltda",
        "rut": "84.901.234-5",
        "email": "ventas@aseoindustrial.cl",
        "telefono": "+56 2 0123 4567",
        "direccion": "Av. Quilín 5100",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.aseoindustrial.cl",
        "categoria": "servicios",
        "subcategorias": "aseo, sanitización, control de plagas",
        "rating": 4.0,
        "es_verificado": True,
        "notas": "Especialistas en aseo industrial",
    },
    # Equipamiento
    {
        "nombre": "Equipos y Maquinaria Chile",
        "razon_social": "Equipos y Maquinaria Chile SA",
        "rut": "85.012.345-6",
        "email": "ventas@equiposchile.cl",
        "telefono": "+56 2 1234 5678",
        "direccion": "Av. Los Militares 6150",
        "ciudad": "Santiago",
        "pais": "Chile",
        "sitio_web": "https://www.equiposchile.cl",
        "categoria": "equipamiento",
        "subcategorias": "herramientas, maquinaria, equipos industriales",
        "rating": 4.4,
        "es_verificado": True,
        "notas": "Importador de equipos europeos",
    },
]


def seed_proveedores() -> None:
    """
    Carga proveedores de prueba en la base de datos.

    Esta función crea proveedores de ejemplo si no existen ya.
    Es idempotente - puede ejecutarse múltiples veces sin duplicar datos.
    """
    db = SessionLocal()

    try:
        logger.info("🌱 Iniciando seed de proveedores...")

        proveedores_creados = 0
        proveedores_existentes = 0

        for proveedor_data in PROVEEDORES_SEED:
            # Verificar si ya existe por email
            existing = crud.proveedor.get_by_email(db, proveedor_data["email"])

            if existing:
                logger.debug(f"Proveedor ya existe: {proveedor_data['nombre']}")
                proveedores_existentes += 1
                continue

            # Crear proveedor
            try:
                proveedor = crud.proveedor.create(db, obj_in=proveedor_data)
                logger.info(f"✅ Creado proveedor: {proveedor.nombre}")
                proveedores_creados += 1
            except Exception as e:
                logger.error(f"❌ Error creando proveedor {proveedor_data['nombre']}: {e}")
                continue

        logger.info(f"\n📊 Resumen del seed:")
        logger.info(f"   - Proveedores creados: {proveedores_creados}")
        logger.info(f"   - Proveedores ya existentes: {proveedores_existentes}")
        logger.info(f"   - Total en base de datos: {proveedores_creados + proveedores_existentes}")

        if proveedores_creados > 0:
            logger.info("✅ Seed de proveedores completado exitosamente")
        else:
            logger.info("ℹ️  No se crearon nuevos proveedores (ya existían)")

    except Exception as e:
        logger.error(f"❌ Error en seed de proveedores: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_proveedores()
