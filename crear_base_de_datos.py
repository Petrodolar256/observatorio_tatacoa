"""
crear_base_de_datos.py — Deja la base de datos lista con un solo comando.

    python crear_base_de_datos.py

Hace 3 cosas:
    1. Crea la base de datos (si todavía no existe).
    2. Ejecuta database/01_crear_tablas.sql   -> crea las 5 tablas.
    3. Ejecuta database/02_cargar_datos.sql   -> carga 10 registros por tabla.

También sirve para VOLVER A LOS DATOS INICIALES en cualquier momento.
¡Cuidado!: lo que se haya creado o cambiado desde la aplicación se pierde.
"""
from psycopg2 import sql

import config
from db import ErrorDeConexion, conectar

CARPETA_SQL = config.CARPETA_DEL_PROYECTO / "database"
TABLAS = ["tipos_astro", "astros", "telescopios", "astronomos", "observaciones"]


def crear_base_si_no_existe(nombre_bd):
    """Paso 1: crea la base de datos vacía. Si ya existe, no hace nada."""
    # Para crear una base hay que estar conectado a otra que ya exista.
    # "postgres" es la base que PostgreSQL trae siempre.
    conexion = conectar("postgres")
    conexion.autocommit = True    # CREATE DATABASE no puede ir dentro de una transacción
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %(nombre)s",
                       {"nombre": nombre_bd})
        if cursor.fetchone() is not None:
            print(f"  La base de datos '{nombre_bd}' ya existía.")
            return

        # El nombre de una base de datos no puede viajar como parámetro %(...)s.
        # sql.Identifier lo escribe de forma segura, sin pegar texto a mano.
        cursor.execute(
            sql.SQL("CREATE DATABASE {} ENCODING 'UTF8' TEMPLATE template0")
            .format(sql.Identifier(nombre_bd))
        )
        print(f"  Base de datos '{nombre_bd}' creada.")
    finally:
        conexion.close()


def ejecutar_archivo_sql(nombre_bd, nombre_archivo):
    """Pasos 2 y 3: ejecuta todas las sentencias de un archivo .sql."""
    contenido = (CARPETA_SQL / nombre_archivo).read_text(encoding="utf-8")
    conexion = conectar(nombre_bd)
    try:
        cursor = conexion.cursor()
        cursor.execute(contenido)
        conexion.commit()
        print(f"  {nombre_archivo} ejecutado.")
    finally:
        conexion.close()


def mostrar_resumen(nombre_bd):
    """Muestra cuántos registros quedaron en cada tabla."""
    conexion = conectar(nombre_bd)
    try:
        cursor = conexion.cursor()
        for tabla in TABLAS:
            cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(tabla)))
            cantidad = cursor.fetchone()[0]
            print(f"  {tabla:<14} {cantidad} registros")
    finally:
        conexion.close()


def crear_base_de_datos(nombre_bd=None):
    """Ejecuta los 3 pasos. Sin nombre, usa la base de datos del archivo .env."""
    nombre_bd = nombre_bd or config.DB_NAME
    print(f"Preparando la base de datos '{nombre_bd}'...")
    crear_base_si_no_existe(nombre_bd)
    ejecutar_archivo_sql(nombre_bd, "01_crear_tablas.sql")
    ejecutar_archivo_sql(nombre_bd, "02_cargar_datos.sql")
    mostrar_resumen(nombre_bd)
    print("Listo.")


# Esto solo se ejecuta al escribir:  python crear_base_de_datos.py
if __name__ == "__main__":
    try:
        crear_base_de_datos()
    except ErrorDeConexion as error:
        print()
        print("No se pudo conectar a PostgreSQL. Revisa que:")
        print("  1. El servidor PostgreSQL esté encendido.")
        print("  2. Exista el archivo .env (copia de .env.example).")
        print("  3. DB_USER y DB_PASSWORD del .env sean los de tu PostgreSQL.")
        print(f"Detalle: {error}")
        raise SystemExit(1)
