"""
db.py — Conexión a PostgreSQL.

Aquí viven las ÚNICAS funciones del proyecto que hablan con la base de datos.
Las rutas (carpeta routes/) nunca se conectan por su cuenta: llaman a estas.

    consultar(sql, parametros)      -> lista de filas           (SELECT)
    consultar_uno(sql, parametros)  -> una sola fila, o None    (SELECT de un registro)
    ejecutar(sql, parametros)       -> cuántas filas cambiaron  (INSERT, UPDATE, DELETE)
    traducir_error(error)           -> mensaje en español para el usuario

Cada función hace siempre los mismos 3 pasos:
    1. Abrir una conexión.
    2. Ejecutar el SQL.
    3. Cerrar la conexión (pase lo que pase).

Consultas parametrizadas
    El SQL se escribe con marcadores como %(nombre)s y los valores viajan
    aparte, en un diccionario. psycopg2 los une de forma segura. Así nadie
    puede "inyectar" SQL escribiendo cosas raras en un formulario.
"""
import psycopg2
import psycopg2.extras

import config

# ---------------------------------------------------------------------------
# Nombres en español para los errores de la base de datos
# ---------------------------------------------------------------------------

# No se pudo llegar a PostgreSQL: servidor apagado, contraseña mala, etc.
ErrorDeConexion = psycopg2.OperationalError

# PostgreSQL rechazó los DATOS: valor repetido, registro en uso, número fuera
# de rango... Son errores que causa el usuario, no el programa.
ErrorDeDatos = (psycopg2.IntegrityError, psycopg2.DataError)


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------
def conectar(nombre_bd=None):
    """Abre una conexión nueva a PostgreSQL con los datos del archivo .env.

    nombre_bd casi nunca se indica: se usa la base de datos del .env.
    (Solo crear_base_de_datos.py pide conectarse a otra base.)
    """
    try:
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=nombre_bd or config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )
    except UnicodeDecodeError:
        # En Windows en español, PostgreSQL a veces responde su mensaje de
        # error ("contraseña incorrecta", "no existe la base de datos") con
        # tildes que psycopg2 no logra leer. Se convierte en un error de
        # conexión normal, con un mensaje que sí se entiende.
        raise ErrorDeConexion(
            "PostgreSQL rechazó la conexión. Revisa DB_USER y DB_PASSWORD en "
            "el archivo .env, y que la base de datos exista "
            "(se crea con: python crear_base_de_datos.py)."
        )


# ---------------------------------------------------------------------------
# Leer datos (SELECT)
# ---------------------------------------------------------------------------
def consultar(sql, parametros=None):
    """Ejecuta un SELECT y devuelve una lista de filas.

    Cada fila es un diccionario: fila["nombre"], fila["id_astro"], etc.
    """
    conexion = conectar()
    try:
        # RealDictCursor hace que cada fila llegue como diccionario.
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        # "finally" se ejecuta siempre: la conexión nunca queda abierta.
        conexion.close()


def consultar_uno(sql, parametros=None):
    """Ejecuta un SELECT y devuelve solo la primera fila (o None si no hay)."""
    filas = consultar(sql, parametros)
    if filas:
        return filas[0]
    return None


# ---------------------------------------------------------------------------
# Cambiar datos (INSERT, UPDATE, DELETE)
# ---------------------------------------------------------------------------
def ejecutar(sql, parametros=None):
    """Ejecuta un INSERT, UPDATE o DELETE y devuelve cuántas filas cambió."""
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        conexion.commit()      # confirma el cambio en la base de datos
        return cursor.rowcount
    except psycopg2.Error:
        conexion.rollback()    # si algo falló, se deshace el intento...
        raise                  # ...y se le avisa a quien llamó (la ruta)
    finally:
        conexion.close()


# ---------------------------------------------------------------------------
# Mensajes de error claros para el usuario
# ---------------------------------------------------------------------------
# PostgreSQL identifica cada tipo de error con un código.
CODIGO_VALOR_DUPLICADO = "23505"                # se violó un UNIQUE
CODIGO_REGLA_INCUMPLIDA = "23514"               # se violó un CHECK
CODIGO_DATO_FALTANTE = "23502"                  # se violó un NOT NULL
# Se violó una llave foránea. Al borrar un registro que otra tabla usa,
# PostgreSQL 18 responde 23001; las versiones anteriores responden 23503.
CODIGOS_REGISTRO_EN_USO = ("23503", "23001")

# Mensaje exacto para cada restricción UNIQUE. Los nombres uq_... son los
# mismos que aparecen en database/01_crear_tablas.sql.
MENSAJES_DE_DUPLICADO = {
    "uq_tipos_astro_nombre": "Ya existe un tipo de astro con ese nombre.",
    "uq_astros_nombre": "Ya existe un astro con ese nombre.",
    "uq_telescopios_codigo": "Ya existe un telescopio con ese código.",
    "uq_astronomos_documento": "Ya existe un astrónomo con ese documento.",
    "uq_astronomos_correo": "Ya existe un astrónomo con ese correo.",
}


def traducir_error(error):
    """Convierte un error de PostgreSQL en un mensaje claro en español."""
    codigo = error.pgcode

    if codigo == CODIGO_VALOR_DUPLICADO:
        # PostgreSQL dice cuál restricción UNIQUE se violó; con ese nombre
        # se busca el mensaje exacto en el diccionario de arriba.
        restriccion = error.diag.constraint_name
        return MENSAJES_DE_DUPLICADO.get(restriccion, "Ya existe un registro con ese valor.")

    if codigo in CODIGOS_REGISTRO_EN_USO:
        return ("El registro está relacionado con otros datos. "
                "Primero elimina o cambia los registros que lo usan.")

    if codigo == CODIGO_REGLA_INCUMPLIDA:
        return ("Algún valor no cumple una regla de la base de datos "
                "(por ejemplo, un número fuera del rango permitido).")

    if codigo == CODIGO_DATO_FALTANTE:
        return "Falta un dato obligatorio."

    return f"La base de datos no aceptó la operación: {error}"
