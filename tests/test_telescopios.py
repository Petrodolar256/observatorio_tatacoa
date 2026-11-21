"""
Pruebas automáticas de la tabla telescopios.

Cada prueba corresponde a un caso del plan de pruebas
(docs/04_plan_de_pruebas.md) y lleva su mismo código: CP-16, CP-17...
"""
from ayudas import pagina
from db import consultar_uno


def buscar_telescopio(codigo):
    """Busca un telescopio por su código, directamente en la base de datos."""
    return consultar_uno("SELECT * FROM telescopios WHERE codigo = %(codigo)s", {"codigo": codigo})


def test_cp16_listar(cliente):
    """CP-16 Listar: se ven los telescopios cargados."""
    respuesta = cliente.get("/telescopios/")

    assert respuesta.status_code == 200
    assert "TEL-01" in pagina(respuesta)
    assert "Celestron NexStar 8SE" in pagina(respuesta)


def test_cp17_crear(cliente):
    """CP-17 Crear: con datos válidos se guarda y aparece en el listado."""
    respuesta = cliente.post("/telescopios/nuevo", follow_redirects=True, data={
        "codigo": "TEL-11",
        "nombre": "Celestron Inspire 100AZ",
        "tipo": "Refractor",
        "apertura_mm": "100",
    })

    assert "Telescopio creado correctamente." in pagina(respuesta)
    assert "TEL-11" in pagina(respuesta)
    assert buscar_telescopio("TEL-11")["apertura_mm"] == 100


def test_cp18_datos_invalidos(cliente):
    """CP-18 Datos inválidos: apertura en cero, texto donde va un número, tipo sin elegir."""
    respuesta = cliente.post("/telescopios/nuevo", data={
        "codigo": "TEL-99",
        "nombre": "Telescopio de prueba",
        "tipo": "",
        "apertura_mm": "0",
    })
    assert "Debes elegir una opción en «Tipo»." in pagina(respuesta)
    assert "El campo «Apertura (mm)» debe ser mayor o igual a 1." in pagina(respuesta)

    respuesta = cliente.post("/telescopios/nuevo", data={
        "codigo": "TEL-99",
        "nombre": "Telescopio de prueba",
        "tipo": "Un tipo inventado",
        "apertura_mm": "grande",
    })
    assert "La opción elegida en «Tipo» no es válida." in pagina(respuesta)
    assert "El campo «Apertura (mm)» debe ser un número entero." in pagina(respuesta)

    assert buscar_telescopio("TEL-99") is None    # nunca se guardó


def test_cp19_valor_duplicado(cliente):
    """CP-19 Valor duplicado: no se puede repetir el código de un telescopio."""
    respuesta = cliente.post("/telescopios/nuevo", data={
        "codigo": "TEL-01",
        "nombre": "Otro telescopio con el mismo código",
        "tipo": "Reflector",
        "apertura_mm": "150",
    })

    assert "Ya existe un telescopio con ese código." in pagina(respuesta)

    # El código se guarda en mayúsculas: "tel-01" cuenta como el mismo "TEL-01".
    respuesta = cliente.post("/telescopios/nuevo", data={
        "codigo": "tel-01",
        "nombre": "El mismo código, en minúsculas",
        "tipo": "Reflector",
        "apertura_mm": "150",
    })

    assert "Ya existe un telescopio con ese código." in pagina(respuesta)


def test_cp20_editar(cliente):
    """CP-20 Editar: el formulario llega precargado y guarda los cambios."""
    cliente.post("/telescopios/nuevo", data={
        "codigo": "TEL-12", "nombre": "Meade Polaris 90", "tipo": "Refractor", "apertura_mm": "90",
    })
    id_telescopio = buscar_telescopio("TEL-12")["id_telescopio"]

    assert 'value="TEL-12"' in pagina(cliente.get(f"/telescopios/{id_telescopio}/editar"))

    respuesta = cliente.post(f"/telescopios/{id_telescopio}/editar", follow_redirects=True, data={
        "codigo": "TEL-12", "nombre": "Meade Polaris 90", "tipo": "Refractor", "apertura_mm": "92",
    })

    assert "Telescopio actualizado correctamente." in pagina(respuesta)
    assert buscar_telescopio("TEL-12")["apertura_mm"] == 92


def test_cp21_eliminar(cliente):
    """CP-21 Eliminar: pide confirmación y luego elimina."""
    cliente.post("/telescopios/nuevo", data={
        "codigo": "TEL-13", "nombre": "Orion StarBlast 4.5", "tipo": "Reflector", "apertura_mm": "114",
    })
    id_telescopio = buscar_telescopio("TEL-13")["id_telescopio"]

    confirmacion = cliente.get(f"/telescopios/{id_telescopio}/eliminar")
    assert "¿Eliminar el telescopio «TEL-13»?" in pagina(confirmacion)
    assert buscar_telescopio("TEL-13") is not None    # con el GET todavía no se borra

    respuesta = cliente.post(f"/telescopios/{id_telescopio}/eliminar", follow_redirects=True)
    assert "Se eliminó el telescopio «TEL-13»." in pagina(respuesta)
    assert buscar_telescopio("TEL-13") is None


def test_cp22_eliminar_relacionado(cliente):
    """CP-22 Eliminar relacionado: un telescopio con observaciones no se deja eliminar."""
    id_telescopio = buscar_telescopio("TEL-01")["id_telescopio"]

    respuesta = cliente.post(f"/telescopios/{id_telescopio}/eliminar", follow_redirects=True)

    assert "No se pudo eliminar «TEL-01»." in pagina(respuesta)
    assert "está relacionado con otros datos" in pagina(respuesta)
    assert buscar_telescopio("TEL-01") is not None    # sigue existiendo
