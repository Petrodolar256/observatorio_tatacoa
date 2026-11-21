"""
Pruebas automáticas de la tabla observaciones (la que tiene 3 llaves foráneas).

Cada prueba corresponde a un caso del plan de pruebas
(docs/04_plan_de_pruebas.md) y lleva su mismo código: CP-30, CP-31...

Esta tabla no tiene tablas "hijas", así que no existe el caso "eliminar un
registro relacionado". En su lugar hay dos casos de datos inválidos.
"""
from ayudas import pagina
from db import consultar_uno


def buscar_observacion(notas):
    """Busca una observación por el texto de sus notas, directamente en la base de datos."""
    return consultar_uno("SELECT * FROM observaciones WHERE notas = %(notas)s", {"notas": notas})


def datos_validos(notas):
    """Un formulario completo y correcto. Cada prueba cambia solo lo que necesita."""
    return {
        "fecha": "2026-11-15",
        "id_astronomo": "7",     # Gloria Inés Tovar
        "id_telescopio": "6",    # TEL-06
        "id_astro": "5",         # Sirio
        "duracion_min": "30",
        "calidad_cielo": "4",
        "notas": notas,
    }


def test_cp30_listar(cliente):
    """CP-30 Listar: se ven los NOMBRES de astrónomo, telescopio y astro, no solo sus id."""
    respuesta = cliente.get("/observaciones/")

    assert respuesta.status_code == 200
    assert "Valentina Rojas Perdomo" in pagina(respuesta)    # astrónomo
    assert "Celestron NexStar 8SE" in pagina(respuesta)      # telescopio
    assert "Saturno" in pagina(respuesta)                    # astro
    assert "18/07/2026" in pagina(respuesta)                 # fecha con formato día/mes/año


def test_cp31_crear(cliente):
    """CP-31 Crear: eligiendo las 3 llaves foráneas en listas desplegables."""
    # El formulario ofrece los nombres en las listas desplegables.
    formulario = pagina(cliente.get("/observaciones/nuevo"))
    assert "Gloria Inés Tovar" in formulario
    assert "TEL-06 — Orion SkyQuest XT8" in formulario
    assert "Sirio" in formulario

    respuesta = cliente.post("/observaciones/nuevo", follow_redirects=True,
                             data=datos_validos("Prueba CP-31"))

    assert "Observación registrada correctamente." in pagina(respuesta)
    observacion = buscar_observacion("Prueba CP-31")
    assert observacion["id_astro"] == 5
    assert observacion["calidad_cielo"] == 4


def test_cp32_datos_invalidos_valores(cliente):
    """CP-32 Datos inválidos: fecha futura, duración en cero y calidad fuera de 1 a 5."""
    datos = datos_validos("Prueba CP-32")
    datos["fecha"] = "2999-01-01"
    datos["duracion_min"] = "0"
    datos["calidad_cielo"] = "9"

    respuesta = cliente.post("/observaciones/nuevo", data=datos)

    assert "El campo «Fecha» no puede ser una fecha futura." in pagina(respuesta)
    assert "El campo «Duración (minutos)» debe ser mayor o igual a 1." in pagina(respuesta)
    assert "El campo «Calidad del cielo» debe ser menor o igual a 5." in pagina(respuesta)
    assert buscar_observacion("Prueba CP-32") is None    # nunca se guardó


def test_cp33_datos_invalidos_llaves_foraneas(cliente):
    """CP-33 Datos inválidos: llaves foráneas sin elegir o que no existen."""
    datos = datos_validos("Prueba CP-33")
    datos["id_astronomo"] = ""          # sin elegir
    datos["id_telescopio"] = ""         # sin elegir
    datos["id_astro"] = "999999"        # un id que no existe

    respuesta = cliente.post("/observaciones/nuevo", data=datos)

    assert "Debes elegir una opción en «Astrónomo»." in pagina(respuesta)
    assert "Debes elegir una opción en «Telescopio»." in pagina(respuesta)
    assert "La opción elegida en «Astro» no existe." in pagina(respuesta)
    assert buscar_observacion("Prueba CP-33") is None    # nunca se guardó


def test_cp34_editar(cliente):
    """CP-34 Editar: el formulario llega precargado y guarda los cambios."""
    cliente.post("/observaciones/nuevo", data=datos_validos("Prueba CP-34"))
    id_observacion = buscar_observacion("Prueba CP-34")["id_observacion"]

    # El formulario de edición trae la fecha y deja marcada la opción guardada.
    formulario = pagina(cliente.get(f"/observaciones/{id_observacion}/editar"))
    assert 'value="2026-11-15"' in formulario
    assert "Prueba CP-34" in formulario

    datos = datos_validos("Prueba CP-34")
    datos["calidad_cielo"] = "5"
    datos["id_astro"] = "6"    # Betelgeuse
    respuesta = cliente.post(f"/observaciones/{id_observacion}/editar",
                             follow_redirects=True, data=datos)

    assert "Observación actualizada correctamente." in pagina(respuesta)
    observacion = buscar_observacion("Prueba CP-34")
    assert observacion["calidad_cielo"] == 5
    assert observacion["id_astro"] == 6


def test_cp35_eliminar(cliente):
    """CP-35 Eliminar: pide confirmación y luego elimina."""
    cliente.post("/observaciones/nuevo", data=datos_validos("Prueba CP-35"))
    id_observacion = buscar_observacion("Prueba CP-35")["id_observacion"]

    confirmacion = cliente.get(f"/observaciones/{id_observacion}/eliminar")
    assert f"¿Eliminar la observación número {id_observacion}?" in pagina(confirmacion)
    assert buscar_observacion("Prueba CP-35") is not None    # con el GET todavía no se borra

    respuesta = cliente.post(f"/observaciones/{id_observacion}/eliminar", follow_redirects=True)
    assert f"Se eliminó la observación número {id_observacion}." in pagina(respuesta)
    assert buscar_observacion("Prueba CP-35") is None
