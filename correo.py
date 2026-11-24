"""Separo la entrega del acuse SMTP de la persistencia gestionada por Flask."""

import os
import smtplib
import ssl
from email.message import EmailMessage


def enviar_acuse(nombre, destinatario):
    """Devuelvo si el servidor SMTP aceptó el correo, sin revelar credenciales."""
    # Leo variables de entorno cargadas por conexion.py; no guardo claves en el código.
    # Uso SMTP para entregar correo y SSL/TLS para cifrar y verificar la conexión.
    try:
        host = os.environ.get("SMTP_HOST", "").strip()
        puerto = int(os.environ.get("SMTP_PORT", "465"))
        usuario = os.environ.get("SMTP_USER", "").strip()
        clave = os.environ.get("SMTP_PASSWORD", "")
        usar_ssl = os.environ.get("SMTP_USE_SSL", "").lower() == "true"
        if not host or not usuario or not clave or not usar_ssl or not 1 <= puerto <= 65535:
            return False

        correo = EmailMessage()
        correo["Subject"] = "Confirmación de recepción - TechMindSolutions"
        correo["From"] = usuario
        correo["To"] = destinatario
        correo.set_content(
            f"Estimado/a {nombre}:\n\n"
            "Gracias por contactar con TechMindSolutions.\n\n"
            "Hemos recibido correctamente tu mensaje. Nuestro equipo revisará tu solicitud "
            "y se pondrá en contacto contigo lo antes posible.\n\n"
            "Saludos cordiales,\n"
            "Equipo de TechMindSolutions\n"
        )
        # Verifico el certificado con el contexto seguro predeterminado y limito la espera.
        with smtplib.SMTP_SSL(host, puerto, context=ssl.create_default_context(), timeout=10) as smtp:
            smtp.login(usuario, clave)
            rechazados = smtp.send_message(correo)
            return not rechazados
    except (smtplib.SMTPException, OSError, ValueError, UnicodeError):
        # Convierto fallos de configuración, autenticación o entrega en un resultado controlado.
        # No registro la excepción SMTP porque podría contener datos del buzón o credenciales.
        return False
