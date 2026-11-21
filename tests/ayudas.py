"""
ayudas.py — Funciones pequeñas que usan todas las pruebas.
"""


def pagina(respuesta):
    """Devuelve como texto el HTML que respondió la aplicación."""
    return respuesta.get_data(as_text=True)
