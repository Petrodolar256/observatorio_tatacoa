"""
routes/astronomos.py — CRUD de la tabla astronomos.

Un "astrónomo" es la persona que hace las observaciones. Ni su documento ni
su correo se pueden repetir.

Todos los archivos de routes/ tienen las mismas 4 partes, en el mismo orden:
    1. El Blueprint: agrupa las rutas de esta tabla.
    2. Las consultas SQL (parametrizadas).
    3. La validación del formulario.
    4. Las rutas: listar, crear, editar y eliminar.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import ErrorDeDatos, consultar, consultar_uno, ejecutar, traducir_error
from validaciones import validar_correo, validar_documento, validar_texto

# ---------------------------------------------------------------------------
# 1. BLUEPRINT
# ---------------------------------------------------------------------------
# Todas las direcciones de este archivo empiezan por /astronomos
bp = Blueprint("astronomos", __name__, url_prefix="/astronomos")


# ---------------------------------------------------------------------------
# 2. CONSULTAS SQL
# ---------------------------------------------------------------------------
# Los valores nunca se pegan dentro del texto del SQL: van como %(nombre)s y
# psycopg2 los pone de forma segura (consultas parametrizadas).

# Además de los datos del astrónomo, cuenta cuántas observaciones ha hecho.
SQL_LISTAR = """
    SELECT an.id_astronomo,
           an.documento,
           an.nombre,
           an.correo,
           (SELECT COUNT(*)
              FROM observaciones o
             WHERE o.id_astronomo = an.id_astronomo) AS cantidad_observaciones
      FROM astronomos an
     ORDER BY an.nombre
"""

SQL_BUSCAR = """
    SELECT id_astronomo, documento, nombre, correo
      FROM astronomos
     WHERE id_astronomo = %(id_astronomo)s
"""

SQL_INSERTAR = """
    INSERT INTO astronomos (documento, nombre, correo)
    VALUES (%(documento)s, %(nombre)s, %(correo)s)
"""

SQL_ACTUALIZAR = """
    UPDATE astronomos
       SET documento = %(documento)s,
           nombre    = %(nombre)s,
           correo    = %(correo)s
     WHERE id_astronomo = %(id_astronomo)s
"""

SQL_ELIMINAR = """
    DELETE FROM astronomos
     WHERE id_astronomo = %(id_astronomo)s
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
        "documento": validar_documento(formulario, "documento", "Documento", errores),
        "nombre": validar_texto(formulario, "nombre", "Nombre completo", errores, maximo=100),
        "correo": validar_correo(formulario, "correo", "Correo", errores, maximo=120),
    }
    return datos, errores


# ---------------------------------------------------------------------------
# 4. RUTAS
# ---------------------------------------------------------------------------
@bp.route("/")
def listar():
    """LISTAR: muestra todos los astrónomos en una tabla."""
    astronomos = consultar(SQL_LISTAR)
    return render_template("astronomos/lista.html", astronomos=astronomos)


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
                flash("Astrónomo creado correctamente.", "success")
                return redirect(url_for("astronomos.listar"))
            except ErrorDeDatos as error:
                # Ejemplo: documento o correo repetido. Se avisa sin que la app falle.
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (vacío, o con los errores encontrados).
    return render_template("astronomos/formulario.html",
                           titulo="Nuevo astrónomo",
                           valores=valores, errores=errores)


@bp.route("/<int:id_astronomo>/editar", methods=["GET", "POST"])
def editar(id_astronomo):
    """EDITAR.
    GET  -> muestra el formulario con los datos actuales del registro.
    POST -> valida los cambios y los guarda.
    """
    # Paso 0: buscar el registro. Si no existe, se responde "404 No encontrado".
    astronomo = consultar_uno(SQL_BUSCAR, {"id_astronomo": id_astronomo})
    if astronomo is None:
        abort(404)

    valores = astronomo    # al abrir, el formulario muestra lo que hay en la base
    errores = []

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores)

        # Paso 2: si no hay errores, guardar los cambios.
        if not errores:
            try:
                datos["id_astronomo"] = id_astronomo    # para el WHERE del UPDATE
                ejecutar(SQL_ACTUALIZAR, datos)
                flash("Astrónomo actualizado correctamente.", "success")
                return redirect(url_for("astronomos.listar"))
            except ErrorDeDatos as error:
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (con los datos, o con los errores).
    return render_template("astronomos/formulario.html",
                           titulo="Editar astrónomo",
                           valores=valores, errores=errores)


@bp.route("/<int:id_astronomo>/eliminar", methods=["GET", "POST"])
def eliminar(id_astronomo):
    """ELIMINAR.
    GET  -> muestra una página que pide confirmación.
    POST -> elimina el registro (el usuario ya confirmó).
    """
    astronomo = consultar_uno(SQL_BUSCAR, {"id_astronomo": id_astronomo})
    if astronomo is None:
        abort(404)

    if request.method == "POST":
        try:
            ejecutar(SQL_ELIMINAR, {"id_astronomo": id_astronomo})
            flash(f"Se eliminó al astrónomo «{astronomo['nombre']}».", "success")
        except ErrorDeDatos as error:
            # Ejemplo: el astrónomo tiene observaciones. La base de datos no deja borrarlo.
            flash(f"No se pudo eliminar a «{astronomo['nombre']}». {traducir_error(error)}",
                  "danger")
        return redirect(url_for("astronomos.listar"))

    return render_template("confirmar_eliminacion.html",
                           descripcion=f"al astrónomo «{astronomo['nombre']}»",
                           url_cancelar=url_for("astronomos.listar"))
