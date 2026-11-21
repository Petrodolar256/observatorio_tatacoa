"""
Pruebas automáticas de la tabla astros.

Cada prueba corresponde a un caso del plan de pruebas
(docs/04_plan_de_pruebas.md) y lleva su mismo código: CP-09, CP-10...
"""
from ayudas import pagina
from db import consultar_uno


def buscar_astro(nombre):
    """Busca un astro por su nombre, directamente en la base de datos."""
    return consultar_uno("SELECT * FROM astros WHERE nombre = %(nombre)s", {"nombre": nombre})


def id_del_tipo(nombre):
    """Devuelve el id de un tipo de astro (para elegirlo en la lista desplegable)."""
    tipo = consultar_uno("SELECT id_tipo_astro FROM tipos_astro WHERE nombre = %(nombre)s",
                         {"nombre": nombre})
    return tipo["id_tipo_astro"]


def test_cp09_listar(cliente):
    """CP-09 Listar: se ve el NOMBRE del tipo de cada astro, no solo su id."""
    respuesta = cliente.get("/astros/")

    assert respuesta.status_code == 200
    assert "Júpiter" in pagina(respuesta)
    assert "Satélite natural" in pagina(respuesta)    # nombre del tipo de la Luna


def test_cp10_crear(cliente):
    """CP-10 Crear: con datos válidos se guarda y aparece en el listado."""
    respuesta = cliente.post("/astros/nuevo", follow_redirects=True, data={
        "nombre": "Marte",
        "id_tipo_astro": id_del_tipo("Planeta"),
        "constelacion": "",
        "visible_a_simple_vista": "on",    # casilla marcada
    })

    assert "Astro creado correctamente." in pagina(respuesta)
    marte = buscar_astro("Marte")
    assert marte["id_tipo_astro"] == id_del_tipo("Planeta")
    assert marte["constelacion"] is None
    assert marte["visible_a_simple_vista"] is True


def test_cp11_datos_invalidos(cliente):
    """CP-11 Datos inválidos: sin nombre y sin tipo no se guarda."""
    respuesta = cliente.post("/astros/nuevo", data={
        "nombre": "",
        "id_tipo_astro": "",
        "constelacion": "Orión",
    })

    assert "El campo «Nombre» es obligatorio." in pagina(respuesta)
    assert "Debes elegir una opción en «Tipo de astro»." in pagina(respuesta)
    # Lo que el usuario sí escribió no se pierde.
    assert 'value="Orión"' in pagina(respuesta)


def test_cp12_valor_duplicado(cliente):
    """CP-12 Valor duplicado: no se puede repetir el nombre de un astro."""
    respuesta = cliente.post("/astros/nuevo", data={
        "nombre": "Júpiter",
        "id_tipo_astro": id_del_tipo("Planeta"),
    })

    assert "Ya existe un astro con ese nombre." in pagina(respuesta)


def test_cp13_editar(cliente):
    """CP-13 Editar: el formulario llega precargado y guarda los cambios."""
    cliente.post("/astros/nuevo", data={"nombre": "Vega", "id_tipo_astro": id_del_tipo("Estrella")})
    id_astro = buscar_astro("Vega")["id_astro"]

    assert 'value="Vega"' in pagina(cliente.get(f"/astros/{id_astro}/editar"))

    respuesta = cliente.post(f"/astros/{id_astro}/editar", follow_redirects=True, data={
        "nombre": "Vega",
        "id_tipo_astro": id_del_tipo("Estrella"),
        "constelacion": "Lira",
        "visible_a_simple_vista": "on",
    })

    assert "Astro actualizado correctamente." in pagina(respuesta)
    vega = buscar_astro("Vega")
    assert vega["constelacion"] == "Lira"
    assert vega["visible_a_simple_vista"] is True


def test_cp14_eliminar(cliente):
    """CP-14 Eliminar: pide confirmación y luego elimina."""
    cliente.post("/astros/nuevo", data={"nombre": "Ceres", "id_tipo_astro": id_del_tipo("Planeta enano")})
    id_astro = buscar_astro("Ceres")["id_astro"]

    confirmacion = cliente.get(f"/astros/{id_astro}/eliminar")
    assert "¿Eliminar el astro «Ceres»?" in pagina(confirmacion)
    assert buscar_astro("Ceres") is not None    # con el GET todavía no se borra

    respuesta = cliente.post(f"/astros/{id_astro}/eliminar", follow_redirects=True)
    assert "Se eliminó el astro «Ceres»." in pagina(respuesta)
    assert buscar_astro("Ceres") is None


def test_cp15_eliminar_relacionado(cliente):
    """CP-15 Eliminar relacionado: un astro con observaciones no se deja eliminar."""
    id_astro = buscar_astro("Júpiter")["id_astro"]

    respuesta = cliente.post(f"/astros/{id_astro}/eliminar", follow_redirects=True)

    assert "No se pudo eliminar «Júpiter»." in pagina(respuesta)
    assert "está relacionado con otros datos" in pagina(respuesta)
    assert buscar_astro("Júpiter") is not None    # sigue existiendo
