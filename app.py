"""
app.py — Punto de entrada de la aplicación.

Para iniciar la aplicación:
    python app.py
y luego abrir en el navegador:
    http://127.0.0.1:5001

¿Qué hace este archivo?
    1. Crea la aplicación Flask.
    2. Registra un Blueprint por cada tabla (carpeta routes/).
    3. Define la página de inicio y las páginas de error.
"""
from flask import Flask, render_template

import config
from db import ErrorDeConexion, consultar_uno
from routes.astronomos import bp as astronomos_bp
from routes.astros import bp as astros_bp
from routes.observaciones import bp as observaciones_bp
from routes.telescopios import bp as telescopios_bp
from routes.tipos_astro import bp as tipos_astro_bp

# Cuenta los registros de cada tabla para las tarjetas de la página de inicio.
SQL_CONTEOS = """
    SELECT (SELECT COUNT(*) FROM tipos_astro)   AS tipos_astro,
           (SELECT COUNT(*) FROM astros)        AS astros,
           (SELECT COUNT(*) FROM telescopios)   AS telescopios,
           (SELECT COUNT(*) FROM astronomos)    AS astronomos,
           (SELECT COUNT(*) FROM observaciones) AS observaciones
"""


def crear_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)

    # Flask necesita una clave secreta para los mensajes "flash"
    # (los avisos de "creado correctamente", "no se pudo eliminar", etc.).
    app.secret_key = config.SECRET_KEY

    # --- Un Blueprint por tabla -------------------------------------------
    # Cada Blueprint trae las 4 rutas de su tabla: listar, crear, editar y
    # eliminar. Están en la carpeta routes/, un archivo por tabla.
    app.register_blueprint(tipos_astro_bp)
    app.register_blueprint(astros_bp)
    app.register_blueprint(telescopios_bp)
    app.register_blueprint(astronomos_bp)
    app.register_blueprint(observaciones_bp)

    # --- Página de inicio -------------------------------------------------
    @app.route("/")
    def inicio():
        """Muestra una tarjeta por tabla con la cantidad de registros."""
        conteos = consultar_uno(SQL_CONTEOS)
        return render_template("inicio.html", conteos=conteos)

    # --- Páginas de error -------------------------------------------------
    @app.errorhandler(404)
    def pagina_no_encontrada(error):
        """La dirección o el registro pedido no existe."""
        return render_template("errores/404.html"), 404

    @app.errorhandler(ErrorDeConexion)
    def sin_conexion(error):
        """No se pudo llegar a PostgreSQL: se explica qué revisar."""
        return render_template("errores/sin_conexion.html", detalle=str(error)), 500

    return app


# La aplicación que se inicia al escribir:  python app.py
app = crear_app()

# Esto solo se ejecuta al escribir:  python app.py
if __name__ == "__main__":
    # debug=True: si algo falla, el navegador muestra el archivo y la línea
    # exactos del error, y la app se reinicia sola al guardar un cambio.
    # port=5001: en macOS el puerto 5000 suele estar ocupado por AirPlay.
    app.run(debug=True, port=5001)
