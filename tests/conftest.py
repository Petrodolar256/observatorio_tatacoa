"""
conftest.py — Preparación de las pruebas automáticas. pytest lo lee solo.

Las pruebas NO tocan la base de datos real. Usan una copia aparte, llamada
observatorio_tatacoa_test, que se crea de cero cada vez que se ejecutan.
Así los datos reales nunca se dañan.

Para ejecutar las pruebas (con el entorno virtual activado):
    pytest
"""
import os

# IMPORTANTE: esta línea va ANTES de importar la aplicación, para que
# config.py tome el nombre de la base de datos de prueba y no el del .env.
NOMBRE_BD_DE_PRUEBA = "observatorio_tatacoa_test"
os.environ["DB_NAME"] = NOMBRE_BD_DE_PRUEBA

import pytest  # noqa: E402  (este import va después a propósito)

from app import crear_app  # noqa: E402
from crear_base_de_datos import crear_base_de_datos  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def base_de_datos_de_prueba():
    """Antes de la primera prueba: crea la base de prueba con los datos de ejemplo."""
    crear_base_de_datos(NOMBRE_BD_DE_PRUEBA)


@pytest.fixture
def cliente():
    """Un "navegador de mentiras": pide páginas a la app sin abrir un navegador real."""
    aplicacion = crear_app()
    aplicacion.config["TESTING"] = True
    return aplicacion.test_client()
