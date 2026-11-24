"""Implemento con Flask el middleware entre el formulario y SQL Server."""

import re
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from conexion import obtener_conexion
from correo import enviar_acuse


RAIZ = Path(__file__).resolve().parent
# Utilizo Flask para recibir solicitudes HTTP y devolver archivos o respuestas JSON.
# Desactivo su carpeta estática automática para publicar solo las rutas que defino.
app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024
FORMATO_EMAIL = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")


@app.get("/")
def inicio():
    # Uso GET para consultar la página sin modificar información.
    return send_from_directory(RAIZ, "index.html")


@app.get("/css/<path:archivo>")
def estilos(archivo):
    return send_from_directory(RAIZ / "css", archivo)


@app.get("/js/<path:archivo>")
def scripts(archivo):
    return send_from_directory(RAIZ / "js", archivo)


@app.get("/images/<path:archivo>")
def imagenes(archivo):
    # Limito cada ruta a su directorio; send_from_directory rechaza salir de él.
    return send_from_directory(RAIZ / "images", archivo)


@app.errorhandler(RequestEntityTooLarge)
def solicitud_demasiado_grande(error):
    return jsonify(ok=False, mensaje="El contenido enviado es demasiado grande."), 413


@app.post("/api/contacto")
def guardar_contacto():
    # Uso POST para registrar datos y JSON para intercambiar campos con JavaScript.
    if not request.is_json:
        return jsonify(ok=False, mensaje="Envía los datos en formato JSON."), 415
    try:
        datos = request.get_json()
    except BadRequest:
        return jsonify(ok=False, mensaje="El contenido JSON no es válido."), 400

    if not isinstance(datos, dict):
        return jsonify(ok=False, mensaje="Envía un objeto JSON con los campos del formulario."), 400

    # Valido otra vez en el servidor porque las comprobaciones del navegador se pueden omitir.
    campos = {}
    for campo, etiqueta, limite in (
        ("nombre", "nombre completo", 100),
        ("email", "correo electrónico", 150),
        ("mensaje", "mensaje", None),
    ):
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            return jsonify(ok=False, mensaje=f"El campo {etiqueta} es obligatorio y debe ser texto."), 400
        # Cuento unidades UTF-16 para respetar la capacidad de las columnas NVARCHAR.
        try:
            longitud = len(valor.encode("utf-16-le")) // 2
        except UnicodeEncodeError:
            return jsonify(ok=False, mensaje=f"El campo {etiqueta} contiene texto no válido."), 400
        if limite is not None and longitud > limite:
            return jsonify(ok=False, mensaje=f"El campo {etiqueta} admite como máximo {limite} caracteres."), 400
        campos[campo] = valor.strip()

    if not FORMATO_EMAIL.fullmatch(campos["email"]):
        return jsonify(ok=False, mensaje="Escribe un correo electrónico válido."), 400

    conexion = None
    cursor = None
    try:
        conexion = obtener_conexion()
        conexion.timeout = 10
        cursor = conexion.cursor()
        # Parametrizo con ? para que pyodbc trate las entradas como datos y no como SQL.
        # Omito el identificador y la fecha para que SQL Server genere sus valores.
        cursor.execute(
            "INSERT INTO dbo.Contacto (nombre, email, mensaje) VALUES (?, ?, ?)",
            campos["nombre"], campos["email"], campos["mensaje"],
        )
        # Confirmo la transacción antes de comunicar que el registro se guardó.
        conexion.commit()
    except Exception:
        # Capturo fallos de conexión o escritura sin revelar detalles técnicos al navegador.
        app.logger.exception("No pude guardar el contacto.")
        if conexion is not None:
            try:
                conexion.rollback()
            except Exception:
                app.logger.exception("No pude revertir la transacción.")
        return jsonify(ok=False, mensaje="No se pudo guardar el contacto. Inténtalo más tarde."), 503
    finally:
        # Cierro ambos recursos incluso si la operación falla; intento cada cierre por separado.
        for recurso in (cursor, conexion):
            if recurso is not None:
                try:
                    recurso.close()
                except Exception:
                    app.logger.exception("No pude cerrar un recurso de la base de datos.")

    # Intento el acuse solo después del commit y fuera del bloque de transacción.
    # Un fallo SMTP no revierte un contacto que ya quedó guardado.
    correo_enviado = enviar_acuse(campos["nombre"], campos["email"])
    if correo_enviado:
        mensaje = "Tu mensaje se ha guardado correctamente y el servidor de correo ha aceptado el acuse de recepción."
    else:
        mensaje = "Tu mensaje se ha guardado correctamente, pero no se pudo enviar el correo de acuse de recepción. No necesitas volver a enviarlo."
    return jsonify(ok=True, correo_enviado=correo_enviado, mensaje=mensaje), 201


if __name__ == "__main__":
    # Limito el servidor académico al equipo local y mantengo desactivado el depurador.
    app.run(host="127.0.0.1", port=5000, debug=False)
