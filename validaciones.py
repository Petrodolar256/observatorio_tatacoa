"""
validaciones.py — Revisa los datos que llegan de los formularios.

Regla de oro: nunca confiar en lo que llega del navegador.
Aunque el formulario HTML ya limite lo que se puede escribir (por ejemplo,
con "maxlength"), aquí en el servidor se vuelve a revisar todo antes de guardar.

Casi todas las funciones trabajan igual:
    - Reciben el formulario, el nombre del campo, la etiqueta que ve el
      usuario y la lista de errores.
    - Si el dato está mal, AGREGAN un mensaje a la lista de errores.
    - Devuelven el valor ya limpio (o None si el campo quedó vacío, o si no
      se pudo leer como número o como fecha).

Lo que decide si se guarda es la lista de errores: si tiene algún mensaje,
la ruta no guarda nada y vuelve a mostrar el formulario.

Ejemplo de uso (en un archivo de routes/):
    errores = []
    nombre = validar_texto(formulario, "nombre", "Nombre", errores, maximo=60)
"""
from datetime import date


def leer_campo(formulario, campo):
    """Devuelve lo que se escribió en un campo, sin espacios a los lados."""
    valor = (formulario.get(campo) or "").strip()
    # Un salto de línea escrito en un cuadro de texto llega como dos caracteres
    # (\r\n). Se deja en uno solo, para que cuente igual que en el navegador.
    return valor.replace("\r\n", "\n")


def validar_texto(formulario, campo, etiqueta, errores, obligatorio=True, maximo=None):
    """Texto libre: nombre, descripción, código..."""
    valor = leer_campo(formulario, campo)

    if not valor:
        if obligatorio:
            errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None    # un campo vacío se guarda como NULL

    if maximo is not None and len(valor) > maximo:
        errores.append(f"El campo «{etiqueta}» admite máximo {maximo} caracteres.")

    return valor


def validar_codigo(formulario, campo, etiqueta, errores, maximo=None):
    """Código corto, como TEL-01. Se guarda en MAYÚSCULAS.

    Así "tel-01" y "TEL-01" cuentan como el mismo código y la base de datos
    puede detectar que está repetido.
    """
    valor = validar_texto(formulario, campo, etiqueta, errores, maximo=maximo)
    if valor is None:
        return None
    return valor.upper()


def validar_entero(formulario, campo, etiqueta, errores, minimo=None, maximo=None):
    """Número entero, opcionalmente dentro de un rango (mínimo y máximo)."""
    valor = leer_campo(formulario, campo)

    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None

    try:
        numero = int(valor)
    except ValueError:
        errores.append(f"El campo «{etiqueta}» debe ser un número entero.")
        return None

    if minimo is not None and numero < minimo:
        errores.append(f"El campo «{etiqueta}» debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        errores.append(f"El campo «{etiqueta}» debe ser menor o igual a {maximo}.")

    return numero


def validar_fecha(formulario, campo, etiqueta, errores, permitir_futuro=True):
    """Fecha. El navegador la envía con el formato AAAA-MM-DD."""
    valor = leer_campo(formulario, campo)

    if not valor:
        errores.append(f"El campo «{etiqueta}» es obligatorio.")
        return None

    try:
        fecha = date.fromisoformat(valor)
    except ValueError:
        errores.append(f"El campo «{etiqueta}» debe ser una fecha válida.")
        return None

    if not permitir_futuro and fecha > date.today():
        errores.append(f"El campo «{etiqueta}» no puede ser una fecha futura.")

    return fecha


def validar_correo(formulario, campo, etiqueta, errores, maximo=None):
    """Correo electrónico. Revisión sencilla: algo@dominio.algo, sin espacios."""
    valor = validar_texto(formulario, campo, etiqueta, errores, maximo=maximo)
    if valor is None:
        return None

    # "ana@correo.com".partition("@")  ->  ("ana", "@", "correo.com")
    usuario, arroba, dominio = valor.partition("@")
    if not usuario or not arroba or "." not in dominio or "@" in dominio or " " in valor:
        errores.append(f"El campo «{etiqueta}» no parece un correo válido "
                       "(ejemplo: nombre@correo.com).")

    # Se guarda en minúsculas para que Ana@correo.com y ana@correo.com
    # cuenten como el mismo correo.
    return valor.lower()


def validar_documento(formulario, campo, etiqueta, errores, minimo=6, maximo=15):
    """Número de documento de identidad: solo dígitos, sin puntos ni espacios."""
    valor = validar_texto(formulario, campo, etiqueta, errores)
    if valor is None:
        return None

    # isascii() descarta "números" de otros alfabetos; isdigit() exige solo dígitos.
    if not (valor.isascii() and valor.isdigit()):
        errores.append(f"El campo «{etiqueta}» solo puede tener números "
                       "(sin puntos ni espacios).")
    elif len(valor) < minimo or len(valor) > maximo:
        errores.append(f"El campo «{etiqueta}» debe tener entre {minimo} y {maximo} dígitos.")

    return valor


def validar_opcion(formulario, campo, etiqueta, errores, opciones):
    """Lista desplegable con valores FIJOS (por ejemplo, el tipo de telescopio).

    "opciones" es la lista de textos permitidos.
    """
    valor = leer_campo(formulario, campo)

    if not valor:
        errores.append(f"Debes elegir una opción en «{etiqueta}».")
        return None

    if valor not in opciones:
        errores.append(f"La opción elegida en «{etiqueta}» no es válida.")
        return None

    return valor


def validar_seleccion(formulario, campo, etiqueta, errores, opciones):
    """Lista desplegable que viene de OTRA TABLA (una llave foránea).

    "opciones" son las filas que se mostraron en la lista desplegable.
    El valor que llega debe ser el id de una de esas filas.

    Para que funcione, el campo del formulario se llama igual que la llave
    primaria de la otra tabla. Ejemplo: el campo "id_tipo_astro".
    """
    valor = leer_campo(formulario, campo)

    if not valor:
        errores.append(f"Debes elegir una opción en «{etiqueta}».")
        return None

    # Lista con los id que sí existen, como texto: ["1", "2", "3", ...]
    ids_validos = [str(opcion[campo]) for opcion in opciones]
    if valor not in ids_validos:
        errores.append(f"La opción elegida en «{etiqueta}» no existe.")
        return None

    return int(valor)


def validar_casilla(formulario, campo):
    """Casilla de verificación (checkbox): devuelve True o False.

    Cuando una casilla NO está marcada, el navegador simplemente no envía ese
    campo. Por eso basta con preguntar si el campo llegó en el formulario.
    """
    return campo in formulario
