"""
Pruebas automáticas de la tabla astronomos.

Cada prueba corresponde a un caso del plan de pruebas
(docs/04_plan_de_pruebas.md) y lleva su mismo código: CP-23, CP-24...
"""
from ayudas import pagina
from db import consultar_uno


def buscar_astronomo(documento):
    """Busca un astrónomo por su documento, directamente en la base de datos."""
    return consultar_uno("SELECT * FROM astronomos WHERE documento = %(documento)s",
                         {"documento": documento})


def test_cp23_listar(cliente):
    """CP-23 Listar: se ven los astrónomos cargados."""
    respuesta = cliente.get("/astronomos/")

    assert respuesta.status_code == 200
    assert "Valentina Rojas Perdomo" in pagina(respuesta)
    assert "valentina.rojas@example.com" in pagina(respuesta)


def test_cp24_crear(cliente):
    """CP-24 Crear: con datos válidos se guarda y aparece en el listado."""
    respuesta = cliente.post("/astronomos/nuevo", follow_redirects=True, data={
        "documento": "1083456789",
        "nombre": "Laura Sofía Ramírez",
        "correo": "Laura.Ramirez@example.com",
    })

    assert "Astrónomo creado correctamente." in pagina(respuesta)
    assert "Laura Sofía Ramírez" in pagina(respuesta)
    # El correo se guarda en minúsculas.
    assert buscar_astronomo("1083456789")["correo"] == "laura.ramirez@example.com"


def test_cp25_datos_invalidos(cliente):
    """CP-25 Datos inválidos: documento con letras y correo mal escrito."""
    respuesta = cliente.post("/astronomos/nuevo", data={
        "documento": "ABC-123",
        "nombre": "Persona de prueba",
        "correo": "correo-sin-arroba",
    })

    assert "El campo «Documento» solo puede tener números" in pagina(respuesta)
    assert "El campo «Correo» no parece un correo válido" in pagina(respuesta)
    assert buscar_astronomo("ABC-123") is None    # nunca se guardó


def test_cp26_valor_duplicado(cliente):
    """CP-26 Valor duplicado: ni el documento ni el correo se pueden repetir."""
    respuesta = cliente.post("/astronomos/nuevo", data={
        "documento": "1075234567",    # el de Valentina Rojas Perdomo
        "nombre": "Otra persona",
        "correo": "otra.persona@example.com",
    })
    assert "Ya existe un astrónomo con ese documento." in pagina(respuesta)

    respuesta = cliente.post("/astronomos/nuevo", data={
        "documento": "999888777",
        "nombre": "Otra persona",
        "correo": "valentina.rojas@example.com",    # el de Valentina Rojas Perdomo
    })
    assert "Ya existe un astrónomo con ese correo." in pagina(respuesta)


def test_cp27_editar(cliente):
    """CP-27 Editar: el formulario llega precargado y guarda los cambios."""
    cliente.post("/astronomos/nuevo", data={
        "documento": "1084567890", "nombre": "Mateo Vargas Silva", "correo": "mateo.vargas@example.com",
    })
    id_astronomo = buscar_astronomo("1084567890")["id_astronomo"]

    assert 'value="Mateo Vargas Silva"' in pagina(cliente.get(f"/astronomos/{id_astronomo}/editar"))

    respuesta = cliente.post(f"/astronomos/{id_astronomo}/editar", follow_redirects=True, data={
        "documento": "1084567890", "nombre": "Mateo Vargas Silva", "correo": "mateo.silva@example.com",
    })

    assert "Astrónomo actualizado correctamente." in pagina(respuesta)
    assert buscar_astronomo("1084567890")["correo"] == "mateo.silva@example.com"


def test_cp28_eliminar(cliente):
    """CP-28 Eliminar: pide confirmación y luego elimina."""
    cliente.post("/astronomos/nuevo", data={
        "documento": "1085678901", "nombre": "Sara Peña Ortiz", "correo": "sara.pena@example.com",
    })
    id_astronomo = buscar_astronomo("1085678901")["id_astronomo"]

    confirmacion = cliente.get(f"/astronomos/{id_astronomo}/eliminar")
    assert "¿Eliminar al astrónomo «Sara Peña Ortiz»?" in pagina(confirmacion)
    assert buscar_astronomo("1085678901") is not None    # con el GET todavía no se borra

    respuesta = cliente.post(f"/astronomos/{id_astronomo}/eliminar", follow_redirects=True)
    assert "Se eliminó al astrónomo «Sara Peña Ortiz»." in pagina(respuesta)
    assert buscar_astronomo("1085678901") is None


def test_cp29_eliminar_relacionado(cliente):
    """CP-29 Eliminar relacionado: un astrónomo con observaciones no se deja eliminar."""
    id_astronomo = buscar_astronomo("1075234567")["id_astronomo"]    # Valentina Rojas Perdomo

    respuesta = cliente.post(f"/astronomos/{id_astronomo}/eliminar", follow_redirects=True)

    assert "No se pudo eliminar a «Valentina Rojas Perdomo»." in pagina(respuesta)
    assert "está relacionado con otros datos" in pagina(respuesta)
    assert buscar_astronomo("1075234567") is not None    # sigue existiendo
