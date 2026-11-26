"""Consulto y normalizo el clima sin compartir credenciales con el navegador."""

import json
import math
import os
import re
import socket
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, build_opener

from dotenv import load_dotenv


# Cargo mi configuración también al utilizar este módulo de forma independiente.
# Respeto las variables del proceso y nunca modifico el archivo de credenciales.
load_dotenv(Path(__file__).resolve().parent / ".env")
URL_CLIMA = "https://api.openweathermap.org/data/2.5/weather"
TIMEOUT = 10
MAX_RESPUESTA = 1024 * 1024


class ErrorClima(Exception):
    """Represento un fallo mediante un mensaje público y un estado HTTP local."""

    def __init__(self, mensaje, estado):
        super().__init__(mensaje)
        self.estado = estado


class _SinRedirecciones(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Rechazo redirecciones para no reenviar mi clave a otro destino o a HTTP.
        return None


def _error_http(codigo):
    # Distingo errores del proveedor sin publicar su cuerpo, URL ni excepción,
    # porque cualquiera de esos datos podría incluir mi clave de acceso.
    if codigo == 401:
        return ErrorClima("El servicio meteorológico rechazó la autenticación.", 502)
    if codigo == 404:
        return ErrorClima("No se encontró la ciudad configurada.", 404)
    if codigo == 429:
        return ErrorClima("Se alcanzó el límite de consultas meteorológicas. Inténtalo más tarde.", 429)
    if 500 <= codigo <= 599:
        return ErrorClima("El servicio meteorológico no está disponible.", 503)
    return ErrorClima("El servicio meteorológico devolvió una respuesta no válida.", 502)


def _normalizar(datos, unidades):
    # Compruebo estructura, tipos y rangos antes de confiar en un servicio externo.
    # Rechazo booleanos y números no finitos para producir JSON interoperable.
    def numero(valor):
        if type(valor) not in (int, float) or not math.isfinite(valor):
            raise ValueError
        return valor

    def texto(valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError
        return valor.strip()

    if type(datos.get("cod")) not in (int, str) or str(datos["cod"]) != "200":
        raise ValueError
    ciudad = texto(datos["name"])
    pais = texto(datos["sys"]["country"])
    temperatura = numero(datos["main"]["temp"])
    humedad = numero(datos["main"]["humidity"])
    viento = numero(datos["wind"]["speed"])
    descripcion = texto(datos["weather"][0]["description"])
    icono = texto(datos["weather"][0]["icon"])
    if not 0 <= humedad <= 100 or viento < 0 or not re.fullmatch(r"(?:01|02|03|04|09|10|11|13|50)[dn]", icono):
        raise ValueError
    # Mantengo un contrato estable: convierto Kelvin o Fahrenheit a Celsius.
    # En metric/standard recibo m/s y multiplico por 3,6; en imperial recibo mph.
    if unidades == "standard":
        temperatura -= 273.15
    elif unidades == "imperial":
        temperatura = (temperatura - 32) * 5 / 9
    viento *= 1.609344 if unidades == "imperial" else 3.6
    if temperatura < -273.15 or not math.isfinite(viento):
        raise ValueError
    return {
        "ciudad": ciudad, "pais": pais, "temperatura_c": round(temperatura, 2),
        "humedad": humedad, "descripcion": descripcion,
        "viento_kmh": round(viento, 2), "icono": icono,
    }


def obtener_clima():
    """Obtengo una observación actual con HTTPS y espera de red limitada."""
    clave = os.getenv("OPENWEATHER_API_KEY", "").strip()
    ciudad = os.getenv("OPENWEATHER_CITY", "").strip()
    unidades = os.getenv("OPENWEATHER_UNITS", "metric").strip().lower()
    idioma = os.getenv("OPENWEATHER_LANG", "es").strip().lower()
    if not clave or not ciudad or unidades not in {"metric", "standard", "imperial"} or idioma != "es":
        raise ErrorClima("La configuración del servicio meteorológico no es válida.", 503)

    # Codifico los parámetros con urlencode para admitir espacios y acentos.
    # Uso urllib de la biblioteca estándar y conservo la verificación TLS por defecto.
    consulta = urlencode({"q": ciudad, "appid": clave, "units": unidades, "lang": idioma})
    try:
        with build_opener(_SinRedirecciones()).open(URL_CLIMA + "?" + consulta, timeout=TIMEOUT) as respuesta:
            if respuesta.status != 200:
                raise _error_http(respuesta.status)
            # Limito la lectura para evitar consumir memoria sin control.
            contenido = respuesta.read(MAX_RESPUESTA + 1)
        if len(contenido) > MAX_RESPUESTA:
            raise ValueError
        return _normalizar(json.loads(contenido.decode("utf-8")), unidades)
    except HTTPError as error:
        error.close()
        raise _error_http(error.code) from None
    except (TimeoutError, socket.timeout):
        raise ErrorClima("La consulta meteorológica excedió el tiempo de espera.", 504) from None
    except URLError as error:
        if isinstance(error.reason, (TimeoutError, socket.timeout)):
            raise ErrorClima("La consulta meteorológica excedió el tiempo de espera.", 504) from None
        raise ErrorClima("No se pudo conectar con el servicio meteorológico.", 503) from None
    except (OSError, HTTPException):
        raise ErrorClima("No se pudo conectar con el servicio meteorológico.", 503) from None
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError):
        raise ErrorClima("El servicio meteorológico devolvió una respuesta no válida.", 502) from None
