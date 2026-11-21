"""
routes/observaciones.py — CRUD de la tabla observaciones.

Una "observación" es el registro central del proyecto:
    "Un astrónomo observa un astro con un telescopio."

Por eso esta tabla tiene TRES llaves foráneas:
    observaciones.id_astronomo   ->  astronomos.id_astronomo
    observaciones.id_telescopio  ->  telescopios.id_telescopio
    observaciones.id_astro       ->  astros.id_astro

Todos los archivos de routes/ tienen las mismas 4 partes, en el mismo orden:
    1. El Blueprint: agrupa las rutas de esta tabla.
    2. Las consultas SQL (parametrizadas).
    3. La validación del formulario.
    4. Las rutas: listar, crear, editar y eliminar.
"""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import ErrorDeDatos, consultar, consultar_uno, ejecutar, traducir_error
from validaciones import validar_entero, validar_fecha, validar_seleccion, validar_texto

# ---------------------------------------------------------------------------
# 1. BLUEPRINT
# ---------------------------------------------------------------------------
# Todas las direcciones de este archivo empiezan por /observaciones
bp = Blueprint("observaciones", __name__, url_prefix="/observaciones")


# ---------------------------------------------------------------------------
# 2. CONSULTAS SQL
# ---------------------------------------------------------------------------
# Los valores nunca se pegan dentro del texto del SQL: van como %(nombre)s y
# psycopg2 los pone de forma segura (consultas parametrizadas).

# Los 3 JOIN traen los NOMBRES del astrónomo, del telescopio y del astro
# (no solo sus id) para mostrarlos en el listado.
SQL_LISTAR = """
    SELECT o.id_observacion,
           o.fecha,
           o.duracion_min,
           o.calidad_cielo,
           o.notas,
           an.nombre AS astronomo,
           te.codigo AS codigo_telescopio,
           te.nombre AS telescopio,
           a.nombre  AS astro
      FROM observaciones o
      JOIN astronomos  an ON an.id_astronomo  = o.id_astronomo
      JOIN telescopios te ON te.id_telescopio = o.id_telescopio
      JOIN astros      a  ON a.id_astro       = o.id_astro
     ORDER BY o.fecha DESC, o.id_observacion DESC
"""

SQL_BUSCAR = """
    SELECT id_observacion, fecha, id_astronomo, id_telescopio, id_astro,
           duracion_min, calidad_cielo, notas
      FROM observaciones
     WHERE id_observacion = %(id_observacion)s
"""

SQL_INSERTAR = """
    INSERT INTO observaciones
        (fecha, id_astronomo, id_telescopio, id_astro, duracion_min, calidad_cielo, notas)
    VALUES
        (%(fecha)s, %(id_astronomo)s, %(id_telescopio)s, %(id_astro)s,
         %(duracion_min)s, %(calidad_cielo)s, %(notas)s)
"""

SQL_ACTUALIZAR = """
    UPDATE observaciones
       SET fecha         = %(fecha)s,
           id_astronomo  = %(id_astronomo)s,
           id_telescopio = %(id_telescopio)s,
           id_astro      = %(id_astro)s,
           duracion_min  = %(duracion_min)s,
           calidad_cielo = %(calidad_cielo)s,
           notas         = %(notas)s
     WHERE id_observacion = %(id_observacion)s
"""

SQL_ELIMINAR = """
    DELETE FROM observaciones
     WHERE id_observacion = %(id_observacion)s
"""

# Opciones de las 3 listas desplegables del formulario.
SQL_OPCIONES_ASTRONOMOS = """
    SELECT id_astronomo, nombre
      FROM astronomos
     ORDER BY nombre
"""

SQL_OPCIONES_TELESCOPIOS = """
    SELECT id_telescopio, codigo, nombre
      FROM telescopios
     ORDER BY codigo
"""

SQL_OPCIONES_ASTROS = """
    SELECT id_astro, nombre
      FROM astros
     ORDER BY nombre
"""


# ---------------------------------------------------------------------------
# 3. VALIDACIÓN DEL FORMULARIO
# ---------------------------------------------------------------------------
# Opciones de la lista desplegable "Calidad del cielo": el número que se guarda
# y el texto que ve el usuario. El rango (1 a 5) debe ser el mismo del CHECK
# ck_observaciones_calidad que está en database/01_crear_tablas.sql.
CALIDADES_DEL_CIELO = [
    (1, "1 — Muy nublado"),
    (2, "2 — Nublado"),
    (3, "3 — Regular"),
    (4, "4 — Bueno"),
    (5, "5 — Despejado"),
]


def validar_formulario(formulario, listas):
    """Revisa los campos del formulario.

    "listas" son las opciones de las listas desplegables: el astrónomo, el
    telescopio y el astro elegidos deben estar en ellas.

    Devuelve dos cosas:
        datos   -> diccionario con los valores limpios, listo para el SQL.
        errores -> lista de mensajes para el usuario (vacía si todo está bien).
    """
    errores = []
    datos = {
        "fecha": validar_fecha(formulario, "fecha", "Fecha", errores, permitir_futuro=False),
        "id_astronomo": validar_seleccion(formulario, "id_astronomo", "Astrónomo",
                                          errores, listas["astronomos"]),
        "id_telescopio": validar_seleccion(formulario, "id_telescopio", "Telescopio",
                                           errores, listas["telescopios"]),
        "id_astro": validar_seleccion(formulario, "id_astro", "Astro",
                                      errores, listas["astros"]),
        "duracion_min": validar_entero(formulario, "duracion_min", "Duración (minutos)", errores,
                                       minimo=1, maximo=1440),
        "calidad_cielo": validar_entero(formulario, "calidad_cielo", "Calidad del cielo", errores,
                                        minimo=1, maximo=5),
        "notas": validar_texto(formulario, "notas", "Notas", errores,
                               obligatorio=False, maximo=300),
    }
    return datos, errores


# ---------------------------------------------------------------------------
# 4. RUTAS
# ---------------------------------------------------------------------------
def cargar_listas():
    """Trae de la base de datos las opciones de las 3 listas desplegables.

    La usan las rutas crear() y editar().
    """
    return {
        "astronomos": consultar(SQL_OPCIONES_ASTRONOMOS),
        "telescopios": consultar(SQL_OPCIONES_TELESCOPIOS),
        "astros": consultar(SQL_OPCIONES_ASTROS),
    }


@bp.route("/")
def listar():
    """LISTAR: muestra las observaciones con los nombres de astrónomo, telescopio y astro."""
    observaciones = consultar(SQL_LISTAR)
    return render_template("observaciones/lista.html", observaciones=observaciones)


@bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    """CREAR.
    GET  -> muestra el formulario vacío.
    POST -> valida lo que escribió el usuario y lo guarda.
    """
    listas = cargar_listas()    # opciones de las listas desplegables
    valores = {}    # lo que se muestra dentro de los campos del formulario
    errores = []    # mensajes de error para el usuario

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores, listas)

        # Paso 2: si no hay errores, guardar en la base de datos.
        if not errores:
            try:
                ejecutar(SQL_INSERTAR, datos)
                flash("Observación registrada correctamente.", "success")
                return redirect(url_for("observaciones.listar"))
            except ErrorDeDatos as error:
                # Si la base de datos rechaza los datos, se avisa sin que la app falle.
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (vacío, o con los errores encontrados).
    return render_template("observaciones/formulario.html",
                           titulo="Nueva observación",
                           valores=valores, errores=errores, listas=listas,
                           calidades_del_cielo=CALIDADES_DEL_CIELO)


@bp.route("/<int:id_observacion>/editar", methods=["GET", "POST"])
def editar(id_observacion):
    """EDITAR.
    GET  -> muestra el formulario con los datos actuales del registro.
    POST -> valida los cambios y los guarda.
    """
    # Paso 0: buscar el registro. Si no existe, se responde "404 No encontrado".
    observacion = consultar_uno(SQL_BUSCAR, {"id_observacion": id_observacion})
    if observacion is None:
        abort(404)

    listas = cargar_listas()    # opciones de las listas desplegables
    valores = observacion    # al abrir, el formulario muestra lo que hay en la base
    errores = []

    if request.method == "POST":
        # Paso 1: leer y validar el formulario.
        valores = request.form
        datos, errores = validar_formulario(valores, listas)

        # Paso 2: si no hay errores, guardar los cambios.
        if not errores:
            try:
                datos["id_observacion"] = id_observacion    # para el WHERE del UPDATE
                ejecutar(SQL_ACTUALIZAR, datos)
                flash("Observación actualizada correctamente.", "success")
                return redirect(url_for("observaciones.listar"))
            except ErrorDeDatos as error:
                errores.append(traducir_error(error))

    # Paso 3: mostrar el formulario (con los datos, o con los errores).
    return render_template("observaciones/formulario.html",
                           titulo="Editar observación",
                           valores=valores, errores=errores, listas=listas,
                           calidades_del_cielo=CALIDADES_DEL_CIELO)


@bp.route("/<int:id_observacion>/eliminar", methods=["GET", "POST"])
def eliminar(id_observacion):
    """ELIMINAR.
    GET  -> muestra una página que pide confirmación.
    POST -> elimina el registro (el usuario ya confirmó).
    """
    observacion = consultar_uno(SQL_BUSCAR, {"id_observacion": id_observacion})
    if observacion is None:
        abort(404)

    if request.method == "POST":
        try:
            ejecutar(SQL_ELIMINAR, {"id_observacion": id_observacion})
            flash(f"Se eliminó la observación número {id_observacion}.", "success")
        except ErrorDeDatos as error:
            # Hoy ninguna tabla usa las observaciones. Si algún día la base de
            # datos se negara a borrar una, se avisa sin que la app falle.
            flash(f"No se pudo eliminar la observación número {id_observacion}. "
                  f"{traducir_error(error)}", "danger")
        return redirect(url_for("observaciones.listar"))

    return render_template("confirmar_eliminacion.html",
                           descripcion=f"la observación número {id_observacion}",
                           url_cancelar=url_for("observaciones.listar"))
