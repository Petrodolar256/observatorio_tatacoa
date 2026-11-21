"""
routes/telescopios.py — CRUD de la tabla telescopios.

Un "telescopio" es un equipo del observatorio. Se identifica con un código
de inventario que no se puede repetir (TEL-01, TEL-02...).

Todos los archivos de routes/ tienen las mismas 4 partes, en el mismo orden:
    1. El Blueprint: agrupa las rutas de esta tabla.
    2. Las consultas SQL (parametrizadas).
    3. La validación del formulario.
    4. Las rutas: listar, crear, editar y eliminar.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import ErrorDeDatos, consultar, consultar_uno, ejecutar, traducir_error
from validaciones import validar_codigo, validar_entero, validar_opcion, validar_texto

# ---------------------------------------------------------------------------
# 1. BLUEPRINT
# ---------------------------------------------------------------------------
# Todas las direcciones de este archivo empiezan por /telescopios
bp = Blueprint("telescopios", __name__, url_prefix="/telescopios")


# ---------------------------------------------------------------------------
# 2. CONSULTAS SQL
# ---------------------------------------------------------------------------
# Los valores nunca se pegan dentro del texto del SQL: van como %(nombre)s y
# psycopg2 los pone de forma segura (consultas parametrizadas).

# Además de los datos del telescopio, cuenta cuántas observaciones tiene.
SQL_LISTAR = """
    SELECT te.id_telescopio,
           te.codigo,
           te.nombre,
           te.tipo,
           te.apertura_mm,
           (SELECT COUNT(*)
              FROM observaciones o
             WHERE o.id_telescopio = te.id_telescopio) AS cantidad_observaciones
      FROM telescopios te
     ORDER BY te.codigo
"""

SQL_BUSCAR = """
    SELECT id_telescopio, codigo, nombre, tipo, apertura_mm
      FROM telescopios
     WHERE id_telescopio = %(id_telescopio)s
"""

SQL_INSERTAR = """
    INSERT INTO telescopios (codigo, nombre, tipo, apertura_mm)
    VALUES (%(codigo)s, %(nombre)s, %(tipo)s, %(apertura_mm)s)
"""

SQL_ACTUALIZAR = """
    UPDATE telescopios
       SET codigo      = %(codigo)s,
           nombre      = %(nombre)s,
           tipo        = %(tipo)s,
           apertura_mm = %(apertura_mm)s
     WHERE id_telescopio = %(id_telescopio)s
"""

SQL_ELIMINAR = """
    DELETE FROM telescopios
     WHERE id_telescopio = %(id_telescopio)s
"""


# ---------------------------------------------------------------------------
# 3. VALIDACIÓN DEL FORMULARIO
# ---------------------------------------------------------------------------
# Opciones de la lista desplegable "Tipo". Deben ser las mismas del CHECK
# ck_telescopios_tipo que está en database/01_crear_tablas.sql.
TIPOS_DE_TELESCOPIO = ["Refractor", "Reflector", "Catadióptrico"]


def validar_formulario(formulario):
    """Revisa los campos del formulario.

    Devuelve dos cosas:
        datos   -> diccionario con los valores limpios, listo para el SQL.
        errores -> lista de mensajes para el usuario (vacía si todo está bien).
    """
    errores = []
    datos = {
        "codigo": validar_codigo(formulario, "codigo", "Código", errores, maximo=10),
        "nombre": validar_texto(formulario, "nombre", "Marca y modelo", errores, maximo=80),
        "tipo": validar_opcion(formulario, "tipo", "Tipo", errores, TIPOS_DE_TELESCOPIO),
        "apertura_mm": validar_entero(formulario, "apertura_mm", "Apertura (mm)", errores,
                                      minimo=1, maximo=20000),
    }
    return datos, errores


# ---------------------------------------------------------------------------
# 4. RUTAS
# ---------------------------------------------------------------------------
@bp.route("/")
def listar():
    """LISTAR: muestra todos los telescopios en una tabla."""
    telescopios = consultar(SQL_LISTAR)
    return render_template("telescopios/lista.html", telescopios=telescopios)


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
                flash("Telescopio creado correctamente.", "success")
                return redirect(url_for("telescopios.listar"))
            except ErrorDeDatos as error:
                # Ejemplo: código repetido. Se avisa sin que la app falle.
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (vacío, o con los errores encontrados).
    return render_template("telescopios/formulario.html",
                           titulo="Nuevo telescopio",
                           valores=valores, errores=errores,
                           tipos_de_telescopio=TIPOS_DE_TELESCOPIO)


@bp.route("/<int:id_telescopio>/editar", methods=["GET", "POST"])
def editar(id_telescopio):
    """EDITAR.
    GET  -> muestra el formulario con los datos actuales del registro.
    POST -> valida los cambios y los guarda.
    """
    # Paso 0: buscar el registro. Si no existe, se responde "404 No encontrado".
    telescopio = consultar_uno(SQL_BUSCAR, {"id_telescopio": id_telescopio})
    if telescopio is None:
        abort(404)

    valores = telescopio    # al abrir, el formulario muestra lo que hay en la base
    errores = []

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores)

        # Paso 2: si no hay errores, guardar los cambios.
        if not errores:
            try:
                datos["id_telescopio"] = id_telescopio    # para el WHERE del UPDATE
                ejecutar(SQL_ACTUALIZAR, datos)
                flash("Telescopio actualizado correctamente.", "success")
                return redirect(url_for("telescopios.listar"))
            except ErrorDeDatos as error:
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (con los datos, o con los errores).
    return render_template("telescopios/formulario.html",
                           titulo="Editar telescopio",
                           valores=valores, errores=errores,
                           tipos_de_telescopio=TIPOS_DE_TELESCOPIO)


@bp.route("/<int:id_telescopio>/eliminar", methods=["GET", "POST"])
def eliminar(id_telescopio):
    """ELIMINAR.
    GET  -> muestra una página que pide confirmación.
    POST -> elimina el registro (el usuario ya confirmó).
    """
    telescopio = consultar_uno(SQL_BUSCAR, {"id_telescopio": id_telescopio})
    if telescopio is None:
        abort(404)

    if request.method == "POST":
        try:
            ejecutar(SQL_ELIMINAR, {"id_telescopio": id_telescopio})
            flash(f"Se eliminó el telescopio «{telescopio['codigo']}».", "success")
        except ErrorDeDatos as error:
            # Ejemplo: el telescopio tiene observaciones. La base de datos no deja borrarlo.
            flash(f"No se pudo eliminar «{telescopio['codigo']}». {traducir_error(error)}",
                  "danger")
        return redirect(url_for("telescopios.listar"))

    return render_template("confirmar_eliminacion.html",
                           descripcion=f"el telescopio «{telescopio['codigo']}»",
                           url_cancelar=url_for("telescopios.listar"))
