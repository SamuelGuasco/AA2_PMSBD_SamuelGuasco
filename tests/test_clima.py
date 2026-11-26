"""Verifico mi backend con respuestas simuladas, sin red, SQL ni SMTP."""

import copy
import io
import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

import clima
from app import app


DATOS = {
    "cod": 200, "name": "Quito", "sys": {"country": "EC"},
    "main": {"temp": 18.5, "humidity": 72}, "wind": {"speed": 2.5},
    "weather": [{"description": "lluvia ligera", "icon": "10d"}],
}
ENTORNO = {
    "OPENWEATHER_API_KEY": "clave-ficticia-de-prueba",
    "OPENWEATHER_CITY": "Quito,EC", "OPENWEATHER_UNITS": "metric",
    "OPENWEATHER_LANG": "es",
}


class PruebasClima(unittest.TestCase):
    def setUp(self):
        # Aíslo mi configuración para no depender de las credenciales del equipo.
        self.entorno = patch.dict("os.environ", ENTORNO)
        self.entorno.start()
        self.addCleanup(self.entorno.stop)
        self.apertura = patch("clima.build_opener")
        self.abrir = self.apertura.start().return_value.open
        self.addCleanup(self.apertura.stop)
        self.respuesta = MagicMock(status=200)
        self.abrir.return_value.__enter__.return_value = self.respuesta
        self.responder(DATOS)
        self.cliente = app.test_client()

    def responder(self, datos):
        self.respuesta.read.return_value = json.dumps(datos, ensure_ascii=False).encode("utf-8")

    def test_integracion_y_parametros(self):
        with patch("app.obtener_conexion") as sql, patch("app.enviar_acuse") as smtp:
            respuesta = self.cliente.get("/api/clima")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json, {"ok": True, "clima": {
            "ciudad": "Quito", "pais": "EC", "temperatura_c": 18.5,
            "humedad": 72, "descripcion": "lluvia ligera", "viento_kmh": 9.0, "icono": "10d",
        }})
        sql.assert_not_called()
        smtp.assert_not_called()
        url = urlsplit(self.abrir.call_args.args[0])
        self.assertEqual((url.scheme, url.netloc, url.path), ("https", "api.openweathermap.org", "/data/2.5/weather"))
        self.assertEqual(parse_qs(url.query), {"q": ["Quito,EC"], "appid": [ENTORNO["OPENWEATHER_API_KEY"]], "units": ["metric"], "lang": ["es"]})
        self.assertEqual(self.abrir.call_args.kwargs["timeout"], 10)
        self.respuesta.read.assert_called_once_with(clima.MAX_RESPUESTA + 1)
        self.abrir.return_value.__exit__.assert_called_once()
        self.assertNotIn(ENTORNO["OPENWEATHER_API_KEY"], respuesta.get_data(as_text=True))

    def test_conversiones(self):
        for unidades, temperatura, viento, esperado in [
            ("standard", 291.65, 2.5, 9.0), ("imperial", 65.3, 10, 16.09),
        ]:
            with self.subTest(unidades=unidades), patch.dict("os.environ", {"OPENWEATHER_UNITS": unidades}):
                datos = copy.deepcopy(DATOS)
                datos["main"]["temp"] = temperatura
                datos["wind"]["speed"] = viento
                self.responder(datos)
                resultado = clima.obtener_clima()
                self.assertEqual(resultado["temperatura_c"], 18.5)
                self.assertEqual(resultado["viento_kmh"], esperado)

    def test_errores_http_seguros(self):
        # Incluyo una clave ficticia en el error para comprobar que no la publico.
        for codigo, estado in [(401, 502), (404, 404), (429, 429), (500, 503), (503, 503), (302, 502), (400, 502)]:
            with self.subTest(codigo=codigo):
                self.abrir.side_effect = HTTPError("https://ejemplo.invalid/?appid=" + ENTORNO["OPENWEATHER_API_KEY"], codigo, ENTORNO["OPENWEATHER_API_KEY"], {}, io.BytesIO(b"privado"))
                respuesta = self.cliente.get("/api/clima")
                self.assertEqual(respuesta.status_code, estado)
                self.assertFalse(respuesta.json["ok"])
                self.assertNotIn(ENTORNO["OPENWEATHER_API_KEY"], respuesta.get_data(as_text=True))

    def test_red_y_timeout(self):
        for error, estado in [(URLError("DNS"), 503), (ConnectionError(), 503), (TimeoutError(), 504), (URLError(TimeoutError()), 504)]:
            with self.subTest(error=type(error).__name__):
                self.abrir.side_effect = error
                self.assertEqual(self.cliente.get("/api/clima").status_code, estado)

    def test_respuestas_invalidas(self):
        casos = [None, [], {}, {**DATOS, "cod": 401}, {**DATOS, "weather": []}, {**DATOS, "name": ""}]
        for campo, valor in [("temp", True), ("temp", float("nan")), ("temp", -300), ("humidity", 101), ("humidity", "72")]:
            datos = copy.deepcopy(DATOS)
            datos["main"][campo] = valor
            casos.append(datos)
        datos = copy.deepcopy(DATOS)
        datos["wind"]["speed"] = -1
        casos.append(datos)
        for datos in casos:
            with self.subTest(datos=datos):
                self.responder(datos)
                self.assertEqual(self.cliente.get("/api/clima").status_code, 502)
        for contenido in [b"no es JSON", b"\xff", b"x" * (clima.MAX_RESPUESTA + 1)]:
            with self.subTest(contenido=contenido[:12]):
                self.respuesta.read.return_value = contenido
                self.assertEqual(self.cliente.get("/api/clima").status_code, 502)

    def test_configuracion_invalida(self):
        for variable, valor in [("OPENWEATHER_API_KEY", ""), ("OPENWEATHER_CITY", ""), ("OPENWEATHER_UNITS", "otra"), ("OPENWEATHER_LANG", "en")]:
            with self.subTest(variable=variable), patch.dict("os.environ", {variable: valor}):
                self.assertEqual(self.cliente.get("/api/clima").status_code, 503)
        self.abrir.assert_not_called()

    def test_rechazo_redirecciones_y_metodo(self):
        self.assertIsNone(clima._SinRedirecciones().redirect_request(None, None, 302, "", {}, "http://ejemplo.invalid"))
        self.assertEqual(self.cliente.post("/api/clima").status_code, 405)
        self.abrir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
