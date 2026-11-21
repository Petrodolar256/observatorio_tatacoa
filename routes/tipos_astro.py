"""
routes/tipos_astro.py — CRUD de la tabla tipos_astro.

Un "tipo de astro" es una categoría: Planeta, Estrella, Galaxia...
Cada astro pertenece a un tipo (tabla astros).

Todos los archivos de routes/ tienen las mismas 4 partes, en el mismo orden:
    1. El Blueprint: agrupa las rutas de esta tabla.
    2. Las consultas SQL (parametrizadas).
    3. La validación del formulario.
    4. Las rutas: listar, crear, editar y eliminar.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import ErrorDeDatos, consultar, consultar_uno, ejecutar, traducir_error
from validaciones import validar_texto

# ---------------------------------------------------------------------------
# 1. BLUEPRINT
# ---------------------------------------------------------------------------
# Todas las direcciones de este archivo empiezan por /tipos_astro
bp = Blueprint("tipos_astro", __name__, url_prefix="/tipos_astro")


# ---------------------------------------------------------------------------
# 2. CONSULTAS SQL
# ---------------------------------------------------------------------------
# Los valores nunca se pegan dentro del texto del SQL: van como %(nombre)s y
# psycopg2 los pone de forma segura (consultas parametrizadas).

# Además de los datos del tipo, cuenta cuántos astros tiene cada uno.
SQL_LISTAR = """
    SELECT t.id_tipo_astro,
           t.nombre,
           t.descripcion,
           (SELECT COUNT(*)
              FROM astros a
             WHERE a.id_tipo_astro = t.id_tipo_astro) AS cantidad_astros
      FROM tipos_astro t
     ORDER BY t.nombre
"""

SQL_BUSCAR = """
    SELECT id_tipo_astro, nombre, descripcion
      FROM tipos_astro
     WHERE id_tipo_astro = %(id_tipo_astro)s
"""

SQL_INSERTAR = """
    INSERT INTO tipos_astro (nombre, descripcion)
    VALUES (%(nombre)s, %(descripcion)s)
"""

SQL_ACTUALIZAR = """
    UPDATE tipos_astro
       SET nombre      = %(nombre)s,
           descripcion = %(descripcion)s
     WHERE id_tipo_astro = %(id_tipo_astro)s
"""

SQL_ELIMINAR = """
    DELETE FROM tipos_astro
     WHERE id_tipo_astro = %(id_tipo_astro)s
"""


# ---------------------------------------------------------------------------
# 3. VALIDACIÓN DEL FORMULARIO
# ---------------------------------------------------------------------------
def validar_formulario(formulario):
    """Revisa los campos del formulario.

    Devuelve dos cosas:
        datos   -> diccionario con los valores limpios, listo para el SQL.
        errores -> lista de mensajes para el usuario (vacía si todo está bien).
    """
    errores = []
    datos = {
        "nombre": validar_texto(formulario, "nombre", "Nombre", errores, maximo=60),
        "descripcion": validar_texto(formulario, "descripcion", "Descripción", errores,
                                     obligatorio=False, maximo=200),
    }
    return datos, errores


# ---------------------------------------------------------------------------
# 4. RUTAS
# ---------------------------------------------------------------------------
@bp.route("/")
def listar():
    """LISTAR: muestra todos los tipos de astro en una tabla."""
    tipos = consultar(SQL_LISTAR)
    return render_template("tipos_astro/lista.html", tipos=tipos)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    """CREAR.
    GET  -> muestra el formulario vacío.
    POST -> valida lo que escribió el usuario y lo guarda.
    """
    valores = {}    # lo que se muestra dentro de los campos del formulario
    errores = []    # mensajes de error para el usuario

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores)

        # Paso 2: si no hay errores, guardar en la base de datos.
        if not errores:
            try:
                ejecutar(SQL_INSERTAR, datos)
                flash("Tipo de astro creado correctamente.", "success")
                return redirect(url_for("tipos_astro.listar"))
            except ErrorDeDatos as error:
                # Ejemplo: nombre repetido. Se avisa sin que la app falle.
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (vacío, o con los errores encontrados).
    return render_template("tipos_astro/formulario.html",
                           titulo="Nuevo tipo de astro",
                           valores=valores, errores=errores)


@bp.route("/<int:id_tipo_astro>/editar", methods=["GET", "POST"])
def editar(id_tipo_astro):
    """EDITAR.
    GET  -> muestra el formulario con los datos actuales del registro.
    POST -> valida los cambios y los guarda.
    """
    # Paso 0: buscar el registro. Si no existe, se responde "404 No encontrado".
    tipo = consultar_uno(SQL_BUSCAR, {"id_tipo_astro": id_tipo_astro})
    if tipo is None:
        abort(404)

    valores = tipo    # al abrir, el formulario muestra lo que hay en la base
    errores = []

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores)

        # Paso 2: si no hay errores, guardar los cambios.
        if not errores:
            try:
                datos["id_tipo_astro"] = id_tipo_astro    # para el WHERE del UPDATE
                ejecutar(SQL_ACTUALIZAR, datos)
                flash("Tipo de astro actualizado correctamente.", "success")
                return redirect(url_for("tipos_astro.listar"))
            except ErrorDeDatos as error:
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (con los datos, o con los errores).
    return render_template("tipos_astro/formulario.html",
                           titulo="Editar tipo de astro",
                           valores=valores, errores=errores)


@bp.route("/<int:id_tipo_astro>/eliminar", methods=["GET", "POST"])
def eliminar(id_tipo_astro):
    """ELIMINAR.
    GET  -> muestra una página que pide confirmación.
    POST -> elimina el registro (el usuario ya confirmó).
    """
    tipo = consultar_uno(SQL_BUSCAR, {"id_tipo_astro": id_tipo_astro})
    if tipo is None:
        abort(404)

    if request.method == "POST":
        try:
            ejecutar(SQL_ELIMINAR, {"id_tipo_astro": id_tipo_astro})
            flash(f"Se eliminó el tipo de astro «{tipo['nombre']}».", "success")
        except ErrorDeDatos as error:
            # Ejemplo: el tipo tiene astros. La base de datos no deja borrarlo.
            flash(f"No se pudo eliminar «{tipo['nombre']}». {traducir_error(error)}", "danger")
        return redirect(url_for("tipos_astro.listar"))

    return render_template("confirmar_eliminacion.html",
                           descripcion=f"el tipo de astro «{tipo['nombre']}»",
                           url_cancelar=url_for("tipos_astro.listar"))
