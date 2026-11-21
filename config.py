"""
config.py — Configuración de la aplicación.

¿Qué hace?
    Lee los datos de conexión (servidor, usuario, contraseña...) del archivo
    .env y los deja disponibles para el resto del proyecto.

¿Por qué en un archivo .env?
    Porque las contraseñas NO deben quedar escritas en el código ni subirse a
    GitHub. El archivo .env se queda solo en este computador: .gitignore le
    dice a Git que lo ignore. Lo que sí se sube es .env.example, una plantilla
    sin datos reales.

¿Cómo se usa desde otros archivos?
    import config
    config.DB_NAME      # -> "observatorio_tatacoa"
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Carga el archivo .env que está en la misma carpeta que este archivo.
CARPETA_DEL_PROYECTO = Path(__file__).parent
load_dotenv(CARPETA_DEL_PROYECTO / ".env")

# os.getenv("NOMBRE", "valor por defecto") lee un valor del archivo .env.
# Si el valor no está en el .env, se usa el que aparece a la derecha.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "observatorio_tatacoa")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Clave que usa Flask para firmar los mensajes que se le muestran al usuario.
SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo")
