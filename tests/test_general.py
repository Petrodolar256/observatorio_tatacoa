"""
Pruebas automáticas generales: la página de inicio, las páginas de error y
una revisión rápida de que TODAS las páginas de la aplicación abren.
"""
import pytest

from ayudas import pagina

TABLAS = ["tipos_astro", "astros", "telescopios", "astronomos", "observaciones"]


def test_la_pagina_de_inicio_muestra_las_cinco_tablas(cliente):
    """La página de inicio abre y tiene una tarjeta por cada tabla."""
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    for titulo in ["Tipos de astro", "Astros", "Telescopios", "Astrónomos", "Observaciones"]:
        assert titulo in pagina(respuesta)


# parametrize repite la misma prueba una vez por cada tabla.
@pytest.mark.parametrize("tabla", TABLAS)
def test_todas_las_paginas_de_cada_tabla_abren(cliente, tabla):
    """El listado, el formulario nuevo, el de editar y la confirmación de eliminar abren."""
    for direccion in [f"/{tabla}/", f"/{tabla}/nuevo", f"/{tabla}/1/editar", f"/{tabla}/1/eliminar"]:
        respuesta = cliente.get(direccion)
        assert respuesta.status_code == 200, f"No abrió {direccion}"


@pytest.mark.parametrize("tabla", TABLAS)
def test_un_registro_que_no_existe_responde_404(cliente, tabla):
    """Editar o eliminar un id que no existe responde "404 No encontrado", sin fallar."""
    assert cliente.get(f"/{tabla}/999999/editar").status_code == 404
    assert cliente.get(f"/{tabla}/999999/eliminar").status_code == 404
    assert cliente.post(f"/{tabla}/999999/eliminar").status_code == 404


def test_una_direccion_que_no_existe_responde_404(cliente):
    """Una dirección inventada muestra la página 404 del proyecto."""
    respuesta = cliente.get("/esta-pagina-no-existe")

    assert respuesta.status_code == 404
    assert "La página o el registro que buscas no existe." in pagina(respuesta)
