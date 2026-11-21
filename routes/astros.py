"""
routes/astros.py — CRUD de la tabla astros.

Un "astro" es lo que se observa en el cielo: Júpiter, Sirio, la Luna...
Cada astro pertenece a un tipo, por eso esta tabla tiene UNA llave foránea:
    astros.id_tipo_astro  ->  tipos_astro.id_tipo_astro

Todos los archivos de routes/ tienen las mismas 4 partes, en el mismo orden:
    1. El Blueprint: agrupa las rutas de esta tabla.
    2. Las consultas SQL (parametrizadas).
    3. La validación del formulario.
    4. Las rutas: listar, crear, editar y eliminar.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import ErrorDeDatos, consultar, consultar_uno, ejecutar, traducir_error
from validaciones import validar_casilla, validar_seleccion, validar_texto

# ---------------------------------------------------------------------------
# 1. BLUEPRINT
# ---------------------------------------------------------------------------
# Todas las direcciones de este archivo empiezan por /astros
bp = Blueprint("astros", __name__, url_prefix="/astros")


# ---------------------------------------------------------------------------
# 2. CONSULTAS SQL
# ---------------------------------------------------------------------------
# Los valores nunca se pegan dentro del texto del SQL: van como %(nombre)s y
# psycopg2 los pone de forma segura (consultas parametrizadas).

# El JOIN trae el NOMBRE del tipo (no solo su id) para mostrarlo en el listado.
# Además cuenta cuántas observaciones tiene cada astro.
SQL_LISTAR = """
    SELECT a.id_astro,
           a.nombre,
           a.constelacion,
           a.visible_a_simple_vista,
           t.nombre AS tipo,
           (SELECT COUNT(*)
              FROM observaciones o
             WHERE o.id_astro = a.id_astro) AS cantidad_observaciones
      FROM astros a
      JOIN tipos_astro t ON t.id_tipo_astro = a.id_tipo_astro
     ORDER BY a.nombre
"""

SQL_BUSCAR = """
    SELECT id_astro, nombre, id_tipo_astro, constelacion, visible_a_simple_vista
      FROM astros
     WHERE id_astro = %(id_astro)s
"""

SQL_INSERTAR = """
    INSERT INTO astros (nombre, id_tipo_astro, constelacion, visible_a_simple_vista)
    VALUES (%(nombre)s, %(id_tipo_astro)s, %(constelacion)s, %(visible_a_simple_vista)s)
"""

SQL_ACTUALIZAR = """
    UPDATE astros
       SET nombre                 = %(nombre)s,
           id_tipo_astro          = %(id_tipo_astro)s,
           constelacion           = %(constelacion)s,
           visible_a_simple_vista = %(visible_a_simple_vista)s
     WHERE id_astro = %(id_astro)s
"""

SQL_ELIMINAR = """
    DELETE FROM astros
     WHERE id_astro = %(id_astro)s
"""

# Opciones de la lista desplegable "Tipo de astro" del formulario.
SQL_OPCIONES_TIPOS = """
    SELECT id_tipo_astro, nombre
      FROM tipos_astro
     ORDER BY nombre
"""


# ---------------------------------------------------------------------------
# 3. VALIDACIÓN DEL FORMULARIO
# ---------------------------------------------------------------------------
def validar_formulario(formulario, tipos):
    """Revisa los campos del formulario.

    "tipos" son las opciones de la lista desplegable: el tipo elegido debe
    ser uno de ellos.

    Devuelve dos cosas:
        datos   -> diccionario con los valores limpios, listo para el SQL.
        errores -> lista de mensajes para el usuario (vacía si todo está bien).
    """
    errores = []
    datos = {
        "nombre": validar_texto(formulario, "nombre", "Nombre", errores, maximo=80),
        "id_tipo_astro": validar_seleccion(formulario, "id_tipo_astro", "Tipo de astro",
                                           errores, tipos),
        "constelacion": validar_texto(formulario, "constelacion", "Constelación", errores,
                                      obligatorio=False, maximo=60),
        "visible_a_simple_vista": validar_casilla(formulario, "visible_a_simple_vista"),
    }
    return datos, errores


# ---------------------------------------------------------------------------
# 4. RUTAS
# ---------------------------------------------------------------------------
@bp.route("/")
def listar():
    """LISTAR: muestra todos los astros con el nombre de su tipo."""
    astros = consultar(SQL_LISTAR)
    return render_template("astros/lista.html", astros=astros)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    """CREAR.
    GET  -> muestra el formulario vacío.
    POST -> valida lo que escribió el usuario y lo guarda.
    """
    tipos = consultar(SQL_OPCIONES_TIPOS)    # opciones de la lista desplegable
    valores = {}    # lo que se muestra dentro de los campos del formulario
    errores = []    # mensajes de error para el usuario

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores, tipos)

        # Paso 2: si no hay errores, guardar en la base de datos.
        if not errores:
            try:
                ejecutar(SQL_INSERTAR, datos)
                flash("Astro creado correctamente.", "success")
                return redirect(url_for("astros.listar"))
            except ErrorDeDatos as error:
                # Ejemplo: nombre repetido. Se avisa sin que la app falle.
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (vacío, o con los errores encontrados).
    return render_template("astros/formulario.html",
                           titulo="Nuevo astro",
                           valores=valores, errores=errores, tipos=tipos)


@bp.route("/<int:id_astro>/editar", methods=["GET", "POST"])
def editar(id_astro):
    """EDITAR.
    GET  -> muestra el formulario con los datos actuales del registro.
    POST -> valida los cambios y los guarda.
    """
    # Paso 0: buscar el registro. Si no existe, se responde "404 No encontrado".
    astro = consultar_uno(SQL_BUSCAR, {"id_astro": id_astro})
    if astro is None:
        abort(404)

    tipos = consultar(SQL_OPCIONES_TIPOS)    # opciones de la lista desplegable
    valores = astro    # al abrir, el formulario muestra lo que hay en la base
    errores = []

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores, tipos)

        # Paso 2: si no hay errores, guardar los cambios.
        if not errores:
            try:
                datos["id_astro"] = id_astro    # para el WHERE del UPDATE
                ejecutar(SQL_ACTUALIZAR, datos)
                flash("Astro actualizado correctamente.", "success")
                return redirect(url_for("astros.listar"))
            except ErrorDeDatos as error:
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (con los datos, o con los errores).
    return render_template("astros/formulario.html",
                           titulo="Editar astro",
                           valores=valores, errores=errores, tipos=tipos)


@bp.route("/<int:id_astro>/eliminar", methods=["GET", "POST"])
def eliminar(id_astro):
    """ELIMINAR.
    GET  -> muestra una página que pide confirmación.
    POST -> elimina el registro (el usuario ya confirmó).
    """
    astro = consultar_uno(SQL_BUSCAR, {"id_astro": id_astro})
    if astro is None:
        abort(404)

    if request.method == "POST":
        try:
            ejecutar(SQL_ELIMINAR, {"id_astro": id_astro})
            flash(f"Se eliminó el astro «{astro['nombre']}».", "success")
        except ErrorDeDatos as error:
            # Ejemplo: el astro tiene observaciones. La base de datos no deja borrarlo.
            flash(f"No se pudo eliminar «{astro['nombre']}». {traducir_error(error)}", "danger")
        return redirect(url_for("astros.listar"))

    return render_template("confirmar_eliminacion.html",
                           descripcion=f"el astro «{astro['nombre']}»",
                           url_cancelar=url_for("astros.listar"))
