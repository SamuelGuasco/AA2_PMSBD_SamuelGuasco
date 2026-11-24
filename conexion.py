"""Configuro el acceso a SQL Server sin abrir conexiones al importar el módulo."""

import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv


# Cargo variables del archivo local sin reemplazar las que ya existen en el entorno.
# Separo la configuración del código para no incluirla en el control de versiones.
load_dotenv(Path(__file__).resolve().parent / ".env")


def obtener_conexion():
    """Abro mediante pyodbc una conexión ODBC con transacciones explícitas."""
    variables = (
        "DB_DRIVER", "DB_SERVER", "DB_DATABASE", "DB_TRUSTED_CONNECTION",
        "DB_ENCRYPT", "DB_TRUST_SERVER_CERTIFICATE",
    )
    valores = {}
    for variable in variables:
        valor = os.getenv(variable, "").strip()
        if not valor:
            raise ValueError("Falta una variable de configuración de la base de datos.")
        # Encierro los valores entre llaves y escapo su cierre para formar la cadena ODBC.
        valores[variable] = "{" + valor.replace("}", "}}") + "}"

    cadena = (
        f"DRIVER={valores['DB_DRIVER']};"
        f"SERVER={valores['DB_SERVER']};"
        f"DATABASE={valores['DB_DATABASE']};"
        f"Trusted_Connection={valores['DB_TRUSTED_CONNECTION']};"
        f"Encrypt={valores['DB_ENCRYPT']};"
        f"TrustServerCertificate={valores['DB_TRUST_SERVER_CERTIFICATE']};"
    )
    # Uso la identidad de Windows; no almaceno usuarios ni contraseñas de SQL Server.
    return pyodbc.connect(cadena, autocommit=False, timeout=5)
