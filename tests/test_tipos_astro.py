"""
Pruebas automáticas de la tabla tipos_astro.

Cada prueba corresponde a un caso del plan de pruebas
(docs/04_plan_de_pruebas.md) y lleva su mismo código: CP-01, CP-02...
"""
from ayudas import pagina
from db import consultar_uno


def buscar_tipo(nombre):
    """Busca un tipo de astro por su nombre, directamente en la base de datos."""
    return consultar_uno("SELECT * FROM tipos_astro WHERE nombre = %(nombre)s",
                         {"nombre": nombre})


def test_cp01_listar(cliente):
    """CP-01 Listar: se ven los tipos de astro cargados."""
    respuesta = cliente.get("/tipos_astro/")

    assert respuesta.status_code == 200
    assert "Planeta" in pagina(respuesta)
    assert "Galaxia" in pagina(respuesta)


def test_cp02_crear(cliente):
    """CP-02 Crear: con datos válidos se guarda y aparece en el listado."""
    respuesta = cliente.post("/tipos_astro/nuevo", follow_redirects=True, data={
        "nombre": "Agujero negro",
        "descripcion": "Región del espacio de la que no puede salir ni la luz",
    })

    assert "Tipo de astro creado correctamente." in pagina(respuesta)
    assert "Agujero negro" in pagina(respuesta)
    assert buscar_tipo("Agujero negro") is not None


def test_cp03_datos_invalidos(cliente):
    """CP-03 Datos inválidos: sin nombre no se guarda y se explica por qué."""
    respuesta = cliente.post("/tipos_astro/nuevo", data={
        "nombre": "   ",
        "descripcion": "Solo espacios en el nombre",
    })

    assert "El campo «Nombre» es obligatorio." in pagina(respuesta)


def test_cp04_valor_duplicado(cliente):
    """CP-04 Valor duplicado: no se puede repetir el nombre de un tipo."""
    respuesta = cliente.post("/tipos_astro/nuevo", data={
        "nombre": "Planeta",
        "descripcion": "Este nombre ya existe",
    })

    assert "Ya existe un tipo de astro con ese nombre." in pagina(respuesta)


def test_cp05_editar(cliente):
    """CP-05 Editar: el formulario llega precargado y guarda los cambios."""
    cliente.post("/tipos_astro/nuevo", data={"nombre": "Púlsar", "descripcion": "Antes"})
    id_tipo = buscar_tipo("Púlsar")["id_tipo_astro"]

    # El formulario de edición muestra el dato actual.
    assert 'value="Púlsar"' in pagina(cliente.get(f"/tipos_astro/{id_tipo}/editar"))

    respuesta = cliente.post(f"/tipos_astro/{id_tipo}/editar", follow_redirects=True, data={
        "nombre": "Púlsar",
        "descripcion": "Estrella que gira muy rápido y emite pulsos",
    })

    assert "Tipo de astro actualizado correctamente." in pagina(respuesta)
    assert buscar_tipo("Púlsar")["descripcion"] == "Estrella que gira muy rápido y emite pulsos"


def test_cp06_eliminar(cliente):
    """CP-06 Eliminar: pide confirmación y luego elimina."""
    cliente.post("/tipos_astro/nuevo", data={"nombre": "Cuásar", "descripcion": ""})
    id_tipo = buscar_tipo("Cuásar")["id_tipo_astro"]

    # GET: solo muestra la página de confirmación, todavía no borra.
    confirmacion = cliente.get(f"/tipos_astro/{id_tipo}/eliminar")
    assert "¿Eliminar el tipo de astro «Cuásar»?" in pagina(confirmacion)
    assert buscar_tipo("Cuásar") is not None

    # POST: el usuario confirmó, ahora sí se elimina.
    respuesta = cliente.post(f"/tipos_astro/{id_tipo}/eliminar", follow_redirects=True)
    assert "Se eliminó el tipo de astro «Cuásar»." in pagina(respuesta)
    assert buscar_tipo("Cuásar") is None


def test_cp07_eliminar_relacionado(cliente):
    """CP-07 Eliminar relacionado: un tipo con astros no se deja eliminar."""
    id_tipo = buscar_tipo("Planeta")["id_tipo_astro"]

    respuesta = cliente.post(f"/tipos_astro/{id_tipo}/eliminar", follow_redirects=True)

    assert "No se pudo eliminar «Planeta»." in pagina(respuesta)
    assert "está relacionado con otros datos" in pagina(respuesta)
    assert buscar_tipo("Planeta") is not None    # sigue existiendo


def test_cp08_inyeccion_sql(cliente):
    """CP-08 Seguridad: un texto con SQL malicioso se guarda como simple texto."""
    texto_malicioso = "'); DROP TABLE astros; --"

    cliente.post("/tipos_astro/nuevo", data={"nombre": texto_malicioso, "descripcion": ""})

    # Se guardó tal cual, como un nombre más...
    assert buscar_tipo(texto_malicioso) is not None
    # ...y la tabla astros sigue existiendo, con sus registros.
    assert consultar_uno("SELECT COUNT(*) AS cantidad FROM astros")["cantidad"] >= 10
