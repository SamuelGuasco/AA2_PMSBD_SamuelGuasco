"""Transfiero una copia académica mediante FTPS sin publicar ni ejecutar Flask."""

import argparse
import base64
import ftplib
import io
import os
from pathlib import Path, PurePosixPath
import re
import ssl
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler

from dotenv import load_dotenv


RAIZ = Path(__file__).resolve().parent
DESTINO = "/public_html/TechMindSolutions_AA2"
# Enumero archivos concretos para no incluir secretos, datos personales ni archivos nuevos
# por accidente. No recorro carpetas indiscriminadamente ni sigo enlaces simbólicos.
PERMITIDOS = (
    "app.py", "conexion.py", "correo.py", "subir_ftp.py",
    "requirements.txt", "README.md", "index.html", "css/styles.css",
    "js/script.js", "js/jquery-servicios.js", "images/logo/logo-techminds.png",
    "database/TechMindSolutions_AA2.sql",
)
# Excluyo .env, .env.example, Git, entornos, cachés y cualquier archivo no enumerado.
# Solo transfiero el script SQL académico a la subcarpeta protegida, nunca a la pública.


class TransferenciaInsegura(Exception):
    """Interrumpo la operación cuando no puedo comprobar un destino seguro."""


def sanear_detalle(error):
    # Oculto valores sensibles incluso si el servidor los repite en una respuesta.
    # No activo set_debuglevel: podría mostrar comandos de autenticación completos.
    texto = str(error)
    secretos = []
    for nombre, valor in os.environ.items():
        if valor and any(marca in nombre.upper() for marca in
                         ("PASSWORD", "SECRET", "TOKEN", "CREDENTIAL", "USER", "HOST")):
            secretos.append(valor)
            secretos.append(base64.b64encode(valor.encode("utf-8")).decode("ascii"))
    for secreto in sorted(set(secretos), key=len, reverse=True):
        texto = re.sub(re.escape(secreto), "[oculto]", texto, flags=re.IGNORECASE)
    texto = re.sub(r"(?i)\b(PASS|USER|AUTH)\s+\S+", r"\1 [oculto]", texto)
    texto = re.sub(r"[^\s<>]+@[^\s<>]+", "[dirección oculta]", texto)
    # Elimino controles de terminal y limito la salida, conservando códigos FTP/SSL útiles.
    texto = " ".join("".join(c for c in texto if c.isprintable() or c.isspace()).split())
    return texto[:600] or "Sin detalles adicionales."


class FTPSDiagnosticado(ftplib.FTP_TLS):
    """Identifico la operación activa sin alterar el cifrado ni las transferencias."""

    etapa = "configuración local"

    def ejecutar(self, etapa, metodo, *args, **kwargs):
        self.etapa = etapa
        return metodo(*args, **kwargs)

    def connect(self, *args, **kwargs):
        return self.ejecutar("conexión TCP y saludo FTP", super().connect, *args, **kwargs)

    def auth(self):
        return self.ejecutar("negociación TLS del canal de control", super().auth)

    def login(self, *args, **kwargs):
        return self.ejecutar("autenticación", super().login, *args, **kwargs)

    def prot_p(self):
        return self.ejecutar("protección del canal de datos (PBSZ/PROT P)", super().prot_p)

    def pwd(self):
        return self.ejecutar("consulta del directorio y permisos (PWD)", super().pwd)

    def cwd(self, *args):
        return self.ejecutar("acceso al directorio y permisos (CWD)", super().cwd, *args)

    def mkd(self, *args):
        return self.ejecutar("creación del destino y permisos (MKD)", super().mkd, *args)

    def mlsd(self, *args, **kwargs):
        # Consumo el generador dentro de la etapa para capturar fallos de la transferencia.
        return self.ejecutar("listado protegido y permisos (MLSD)",
                             lambda: list(super(FTPSDiagnosticado, self).mlsd(*args, **kwargs)))

    def ntransfercmd(self, *args, **kwargs):
        # Distingo la apertura y negociación TLS de datos del comando que la solicitó.
        anterior = self.etapa
        resultado = self.ejecutar("conexión y negociación TLS del canal de datos",
                                  super().ntransfercmd, *args, **kwargs)
        self.etapa = anterior
        return resultado

    def storbinary(self, *args, **kwargs):
        return self.ejecutar("transferencia de archivo y permisos (STOR)",
                             super().storbinary, *args, **kwargs)


def configuracion():
    # Cargo variables externas sin imprimir sus valores ni reemplazar las del proceso.
    load_dotenv(RAIZ / ".env")
    host = os.getenv("FTP_HOST", "").strip()
    usuario = os.getenv("FTP_USER", "").strip()
    clave = os.getenv("FTP_PASSWORD", "")
    puerto = int(os.getenv("FTP_PORT", "21"))
    if os.getenv("FTP_USE_TLS", "").strip().lower() != "true":
        raise ValueError("FTPS obligatorio")
    if not host or not usuario or not clave or not 1 <= puerto <= 65535:
        raise ValueError("Configuración incompleta")
    return host, puerto, usuario, clave


def archivos_locales():
    archivos = []
    for relativo in PERMITIDOS:
        ruta = RAIZ / relativo
        # Compruebo cada componente para impedir que un enlace redirija la lectura.
        if any(parte.is_symlink() for parte in (ruta, *ruta.parents)):
            raise TransferenciaInsegura()
        if not ruta.is_file() or not ruta.resolve().is_relative_to(RAIZ.resolve()):
            raise TransferenciaInsegura()
        archivos.append((relativo, ruta))
    return archivos


def listado(ftp):
    # Exijo MLSD para verificar nombres sin interpretar listados de texto ambiguos.
    # Si el servidor no permite esta comprobación, detengo la subida.
    return {nombre.casefold() for nombre, datos in ftp.mlsd()}


class SinRedirecciones(HTTPRedirectHandler):
    # Rechazo redirecciones para no confundir otra página con la protección del destino.
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def consultar_http(url):
    # Verifico HTTPS con certificados válidos sin enviar credenciales FTP al sitio web.
    cliente = build_opener(HTTPSHandler(context=ssl.create_default_context()), SinRedirecciones())
    solicitud = Request(url, headers={"Cache-Control": "no-cache"})
    try:
        with cliente.open(solicitud, timeout=15) as respuesta:
            return respuesta.status, respuesta.read(1024)
    except HTTPError as error:
        return error.code, b""


def preparar_carpeta(ftp, ruta):
    # Reutilizo solo directorios reales; rechazo enlaces y rutas inesperadas.
    padre = str(ruta.parent)
    ftp.cwd(padre)
    entradas = {nombre.casefold(): (nombre, datos) for nombre, datos in ftp.mlsd()}
    entrada = entradas.get(ruta.name.casefold())
    if entrada is None:
        ftp.mkd(ruta.name)
    elif entrada[0] != ruta.name or entrada[1].get("type") != "dir":
        raise TransferenciaInsegura()
    ftp.cwd(str(ruta))
    if PurePosixPath(ftp.pwd()) != ruta:
        raise TransferenciaInsegura()


def subir(ftp, url_base):
    archivos = archivos_locales()
    url = urlsplit(url_base)
    if (url.scheme != "https" or not url.hostname or url.username or url.password
            or url.query or url.fragment or url.path != "/TechMindSolutions_AA2/"):
        raise TransferenciaInsegura()
    destino = PurePosixPath(DESTINO)
    preparar_carpeta(ftp, destino)
    # Exijo una subcarpeta protegida nueva: nunca confío en una protección anterior.
    if "protegido" in listado(ftp):
        raise TransferenciaInsegura()

    enviados = 0
    total_bytes = 0

    def transferir(nombre, contenido, etiqueta):
        nonlocal enviados, total_bytes
        if nombre.casefold() in listado(ftp):
            raise TransferenciaInsegura()
        ftp.storbinary(f"STOR {nombre}", io.BytesIO(contenido))
        enviados += 1
        total_bytes += len(contenido)
        print(f"Subí el archivo: {etiqueta}")

    try:
        protegido = destino / "protegido"
        preparar_carpeta(ftp, protegido)
        token = secrets.token_hex(24)
        testigo = f"verificacion-{token}.txt"
        transferir(testigo, token.encode("ascii"), f"protegido/{testigo}")
        ftp.etapa = "verificación HTTPS de la correspondencia del destino"
        # Primero demuestro que la URL corresponde al archivo real y no a un error genérico.
        estado, cuerpo = consultar_http(url_base + f"protegido/{testigo}?v={secrets.token_hex(8)}")
        if estado != 200 or cuerpo != token.encode("ascii"):
            raise TransferenciaInsegura()
        # Configuro Apache/LiteSpeed antes de transferir cualquier fuente real.
        reglas = b"# Deniego el acceso HTTP a las fuentes academicas.\nRequire all denied\n"
        transferir(".htaccess", reglas, "protegido/.htaccess")
        # Uso contenido inocuo para verificar extensiones sensibles además del testigo.
        for nombre in (f"verificacion-{token}.py", f"verificacion-{token}.sql"):
            transferir(nombre, b"# Verifico la proteccion sin incluir fuentes reales.\n", f"protegido/{nombre}")
        for nombre in (testigo, f"verificacion-{token}.py", f"verificacion-{token}.sql", ".htaccess"):
            ftp.etapa = "verificación de denegación HTTP antes de subir fuentes"
            estado, _ = consultar_http(url_base + f"protegido/{nombre}?v={secrets.token_hex(8)}")
            if estado != 403:
                raise TransferenciaInsegura()
        print("Verifiqué HTTP 403 en la subcarpeta protegida antes de transferir fuentes.")

        for relativo, ruta in archivos:
            # Mantengo la estructura del sitio; separo Python, SQL y documentación del área pública.
            remoto = PurePosixPath(relativo)
            if ruta.suffix in (".py", ".sql", ".md", ".txt"):
                remoto = PurePosixPath("protegido") / remoto
            ftp.cwd(str(destino))
            acumulada = destino
            for parte in remoto.parts[:-1]:
                acumulada = acumulada / parte
                preparar_carpeta(ftp, acumulada)
            transferir(remoto.name, ruta.read_bytes(), remoto.as_posix())
    finally:
        # Informo también el avance parcial si hay un fallo; nunca elimino archivos remotos.
        print(f"Resumen: confirmé {enviados} archivos, incluidos controles de protección; {total_bytes} bytes.")


def main():
    parser = argparse.ArgumentParser(description="Pruebo o subo el proyecto mediante FTPS seguro.")
    parser.add_argument("modo", choices=("probar", "subir"))
    parser.add_argument("--url-base", help="Indico la URL HTTPS del sitio terminada en /TechMindSolutions_AA2/.")
    args = parser.parse_args()
    if args.modo == "subir" and not args.url_base:
        parser.error("Necesito --url-base https://DOMINIO/TechMindSolutions_AA2/ para verificar la protección.")
    ftp = None
    try:
        host, puerto, usuario, clave = configuracion()
        # ftplib forma parte de Python. FTP_TLS cifra el canal de control con AUTH TLS;
        # verifico el certificado y no permito degradación a FTP sin cifrado.
        ftp = FTPSDiagnosticado(context=ssl.create_default_context(), timeout=15)
        ftp.connect(host, puerto)
        print("Completé la conexión TCP y recibí el saludo FTP.")
        # Separo AUTH TLS de login para localizar errores antes de enviar credenciales.
        ftp.auth()
        print("Completé la negociación TLS con verificación del certificado.")
        ftp.login(usuario, clave, secure=True)
        print("Completé la autenticación.")
        # Cifro también los canales de datos utilizados por listados y transferencias.
        ftp.prot_p()
        print("Activé la protección del canal de datos.")
        if args.modo == "probar":
            # Consulto PWD y leo un listado para probar también el canal de datos cifrado.
            # No muestro los nombres listados ni creo, subo, borro o modifico archivos.
            print("Conexión FTPS y autenticación correctas.")
            print(f"Directorio remoto actual: {sanear_detalle(ftp.pwd())}")
            ftp.mlsd()
            print("Comprobé la lectura del directorio mediante el canal de datos cifrado.")
        else:
            subir(ftp, args.url_base)
            print("Finalicé la transferencia en /public_html/TechMindSolutions_AA2/ con fuentes protegidas.")
        return 0
    except TransferenciaInsegura:
        print("Detuve la operación: no pude verificar la seguridad del destino, la denegación HTTP o la ausencia de archivos existentes. No transferiré más fuentes.")
        return 1
    except (ftplib.Error, OSError, ValueError, EOFError, URLError) as error:
        etapa = ftp.etapa if ftp is not None else "configuración local y contexto SSL"
        if isinstance(error, ssl.SSLCertVerificationError):
            etapa = f"verificación del certificado SSL durante {etapa}"
        print(f"Identifiqué el fallo en: {etapa}.")
        print(f"Tipo de excepción: {type(error).__name__}.")
        print(f"Detalle saneado: {sanear_detalle(error)}")
        print("Mantengo la verificación del certificado y no intentaré FTP sin cifrado.")
        print("Un puerto TCP accesible no garantiza que TLS, autenticación o los puertos de datos funcionen.")
        print("Si la subida comenzó, puede quedar una copia parcial; no se borrará ni reutilizará automáticamente.")
        return 1
    finally:
        if ftp is not None:
            # Cierro el socket incluso si fallan autenticación o transferencia.
            ftp.close()


if __name__ == "__main__":
    raise SystemExit(main())
