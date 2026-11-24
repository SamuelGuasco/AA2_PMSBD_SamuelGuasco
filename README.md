# TechMindSolutions_AA2

## Descripción y contexto académico

Proyecto de **Aprendizaje Autónomo 2 (AA2)** de la asignatura **Programación de Middleware y Seguridad de la Base de Datos**, carrera de **Ingeniería de Software**, quinto semestre, de la **Universidad Internacional del Ecuador (UIDE)**. Continúo el trabajo de AA1 incorporando un middleware Python que conecta el formulario web con SQL Server.

TechMindSolutions es un concepto de emprendimiento digital para empresas y emprendedores. Presenta desarrollo de sitios web, tarjetas digitales NFC y ClozerIA CRM, distribuido por Estrategia10X. El sitio describe estas soluciones; no implementa un CRM ni lectura NFC.

Conservo las secciones **Inicio, Empresa, Productos, Oferta del mes, Localización, Contacto y Noticias**, la navegación interna, el logotipo y el diseño adaptable. El horario es provisional y la dirección física está pendiente de confirmación. El formulario permite guardar contactos mediante Flask.

## Objetivos

- Integrar la interfaz HTML, CSS y JavaScript con Flask y SQL Server.
- Aplicar validación de entradas en el navegador y en el servidor.
- Registrar contactos mediante consultas parametrizadas y transacciones.
- Conservar el modelo relacional y las demostraciones CRUD anteriores.
- Documentar la configuración local, las medidas de seguridad y las pruebas académicas.

## Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| HTML5 | Estructura semántica, navegación y formulario accesible. |
| CSS3 | Identidad visual, Flexbox y diseño adaptable. |
| JavaScript | Manipulación del DOM, validación y solicitudes con `fetch`. |
| jQuery 3.7.1 | Eventos y animación `slideToggle` de los detalles de servicios. |
| Python | Lógica del middleware, recursos y excepciones. |
| Flask | Publicación del sitio y endpoint de contacto. |
| pyodbc | Acceso a SQL Server mediante ODBC y consultas parametrizadas. |
| python-dotenv | Carga de configuración desde variables de entorno y `.env`. |
| smtplib, ssl y EmailMessage | Acuse de recepción por SMTP con SSL/TLS; bibliotecas estándar de Python. |
| Microsoft SQL Server | Persistencia, relaciones, restricciones y operaciones T-SQL. |
| ODBC Driver 18 for SQL Server | Controlador utilizado por pyodbc. |

`requirements.txt` fija las dependencias Python. También incluye `requests` y dependencias asociadas, aunque el flujo actual de contacto no utiliza esa biblioteca. jQuery se carga desde `code.jquery.com`; se necesita internet para desplegar los detalles de servicios.

## Arquitectura y comunicación

```text
Navegador: HTML + CSS + JavaScript + jQuery
    │ GET / y recursos /css/, /js/, /images/
    │ POST /api/contacto con JSON
    ▼
Flask: app.py → validación del servidor
    │ conexion.py → pyodbc → ODBC Driver 18
    ▼
SQL Server: TechMindSolutions_AA2 → dbo.Contacto
    │ confirmación de la transacción
    ▼
Respuesta JSON y código HTTP → resultado en el formulario
```

Utilizo Flask como intermediario: el navegador no accede directamente a SQL Server. La página y la API comparten el origen `http://127.0.0.1:5000`, por lo que JavaScript utiliza la ruta relativa `/api/contacto`.

`GET /` entrega `index.html` sin modificar datos. Las rutas de recursos se limitan a sus directorios. `POST /api/contacto` recibe, valida y registra el contacto. La aplicación no crea ni modifica tablas al iniciarse.

## Estructura del proyecto

```text
TechMindSolutions_AA2/
├── app.py
├── conexion.py
├── correo.py
├── subir_ftp.py
├── .env                 # Configuración local, excluida de Git
├── .env.example         # Plantilla compartida
├── .gitignore
├── requirements.txt
├── README.md
├── index.html
├── css/
│   └── styles.css
├── js/
│   ├── script.js
│   └── jquery-servicios.js
├── images/
│   └── logo/
│       └── logo-techminds.png
├── database/
│   └── TechMindSolutions_AA2.sql
├── .venv/               # Entorno local, excluido de Git
└── __pycache__/         # Caché de Python, excluida de Git
```

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Rutas Flask, validación, inserción, transacciones y respuestas HTTP. |
| `conexion.py` | Carga de variables y apertura de conexiones con autenticación de Windows. |
| `correo.py` | Entrega del acuse personalizado mediante SMTP_SSL, independiente de la transacción SQL. |
| `subir_ftp.py` | Prueba de conexión y copia controlada de fuentes por FTPS explícito. |
| `index.html` | Contenido y formulario con etiquetas visibles y región de estado accesible. |
| `css/styles.css` | Colores, tipografía y distribución; ancho máximo de 1120 px y ajustes para pantallas de hasta 700 px. |
| `js/script.js` | Validación, envío JSON, bloqueo de solicitudes simultáneas y resultados. |
| `js/jquery-servicios.js` | Detalles de servicios con actualización de texto y `aria-expanded`. |
| `database/TechMindSolutions_AA2.sql` | Definición de base, tablas, relaciones y demostraciones CRUD, incluida Contacto. |
| `.env.example` | Plantilla de variables necesarias para el entorno local. |
| `requirements.txt` | Dependencias Python para instalar el entorno. |

## Base de datos

La base utilizada es **TechMindSolutions_AA2**. Todas las claves primarias son `INT IDENTITY(1,1)`.

| Tabla | Clave primaria | Otros campos del modelo final |
|---|---|---|
| `Cliente` | `id_cliente` | `nombre VARCHAR(100) NOT NULL`, `correo VARCHAR(150) NOT NULL`, `telefono VARCHAR(20) NULL`. |
| `Servicio` | `id_servicio` | `nombre VARCHAR(100) NOT NULL`, `descripcion VARCHAR(255) NULL`, `precio DECIMAL(10,2) NULL`. |
| `Solicitud` | `id_solicitud` | `id_cliente INT NOT NULL`, `fecha_solicitud DATE NOT NULL`, `estado VARCHAR(30) NOT NULL`. |
| `Detalle_Solicitud` | `id_detalle` | `id_solicitud INT NOT NULL`, `id_servicio INT NOT NULL`, `cantidad INT NOT NULL DEFAULT 1`, `precio_unitario DECIMAL(10,2) NULL`. |
| `dbo.Contacto` | `id_contacto` | Datos del formulario, detallados a continuación. |

Las claves foráneas establecen relaciones uno a muchos entre Cliente y Solicitud, Solicitud y Detalle_Solicitud, y Servicio y Detalle_Solicitud. El detalle representa la relación muchos a muchos entre solicitudes y servicios, con cantidad y precio unitario. El script crea inicialmente una relación directa entre Solicitud y Servicio y después elimina esa clave foránea y la columna `Solicitud.id_servicio` para establecer el modelo final.

### Tabla dbo.Contacto

| Columna | Tipo y restricciones | Propósito |
|---|---|---|
| `id_contacto` | `INT IDENTITY(1,1) PRIMARY KEY` | Identificador automático. |
| `nombre` | `NVARCHAR(100) NOT NULL` | Nombre completo. |
| `email` | `NVARCHAR(150) NOT NULL` | Correo electrónico. |
| `mensaje` | `NVARCHAR(MAX) NOT NULL` | Mensaje en texto Unicode. |
| `fecha_contacto` | `DATETIME2 NOT NULL DEFAULT SYSDATETIME()` | Fecha y hora del servidor. |

Contacto es independiente y no tiene claves foráneas. El middleware inserta solo `nombre`, `email` y `mensaje`; SQL Server genera el identificador y la fecha. El script no inserta ejemplos en Contacto.

### Operaciones CRUD conservadas

El script registra tres clientes, tres servicios, tres solicitudes y cuatro detalles de ejemplo; consulta las tablas, actualiza la solicitud 1 a `En proceso` y crea y elimina un cliente temporal identificado con `SCOPE_IDENTITY()`. La aplicación web permite crear contactos; no ofrece una interfaz para consultarlos, editarlos o eliminarlos.

## Requisitos e instalación en Windows

Necesito PowerShell, Python 3 con pip y soporte para entornos virtuales, SQL Server con la instancia local `SQLEXPRESS`, SQL Server Management Studio (SSMS), **ODBC Driver 18 for SQL Server** y un navegador con JavaScript. La identidad de Windows que ejecuta Python debe tener acceso a la base y permiso para insertar en `dbo.Contacto`. Preparar una base nueva requiere los permisos correspondientes en SQL Server.

### Creación y activación del entorno virtual

Desde PowerShell, sitúo la terminal en la carpeta del proyecto:

```powershell
Set-Location "ruta\a\TechMindSolutions_AA2"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si `.venv` ya existe y funciona, omito su creación. Si PowerShell bloquea la activación, puedo instalar las dependencias con el intérprete del entorno sin modificar la política de ejecución:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

El controlador ODBC se instala por separado en Windows: `pip` instala pyodbc, no el controlador de SQL Server.

### Configuración del entorno

Si todavía no tengo `.env`, copio la plantilla sin sobrescribir una configuración existente:

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
```

Reviso localmente las variables documentadas en `.env.example`:

| Variable | Función según la plantilla |
|---|---|
| `DB_DRIVER` | Selecciona `ODBC Driver 18 for SQL Server`. |
| `DB_SERVER` | Identifica `localhost\SQLEXPRESS`. |
| `DB_DATABASE` | Selecciona `TechMindSolutions_AA2`. |
| `DB_TRUSTED_CONNECTION` | Activa autenticación de Windows con `yes`. |
| `DB_ENCRYPT` | Solicita cifrado de la conexión ODBC con `yes`. |
| `DB_TRUST_SERVER_CERTIFICATE` | Acepta el certificado del servidor con `yes`, exclusivamente para desarrollo académico local. |

Esta descripción procede de la plantilla compartida y no reproduce el contenido de `.env`. La autenticación de Windows no requiere guardar contraseñas SQL. `conexion.py` carga `.env` desde la raíz y conserva las variables que ya estén definidas en el entorno del proceso.

### Preparación de SQL Server

1. Compruebo que `SQLEXPRESS` esté disponible y me conecto desde SSMS mediante autenticación de Windows.
2. Si la base **no existe**, abro `database/TechMindSolutions_AA2.sql` y ejecuto el script completo respetando sus lotes `GO`. Crea la base, las cinco tablas y realiza las demostraciones CRUD descritas.
3. Si la base ya existe, **no repito el script completo**: no está preparado para ejecutarse íntegramente sobre una base creada. Verifico las cinco tablas. Si únicamente falta Contacto, ejecuto manualmente solo su sección final, incluido `USE TechMindSolutions_AA2` y sus separadores `GO`, tras confirmar que esa tabla no existe.
4. Confirmo los permisos de la identidad de Windows utilizada por Python.

Mantengo todas las definiciones en un único archivo SQL. Estos pasos corresponden a AA2 y no requieren modificar la base de AA1.

### Ejecución de Flask

Desde la raíz, con o sin activar el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -B .\app.py
```

Abro **http://127.0.0.1:5000**. Accedo mediante Flask para que funcione la API relativa; abrir `index.html` directamente no inicia el middleware. El servidor escucha únicamente en `127.0.0.1:5000`, con el depurador desactivado. Lo detengo con `Ctrl+C`. Su inicio no ejecuta el script SQL ni inserta contactos automáticamente.

## Formulario y POST /api/contacto

El formulario contiene **Nombre completo**, **Correo electrónico** y **Mensaje**, todos obligatorios y marcados con asterisco. Sus atributos `name` son `nombre`, `email` y `mensaje`. Nombre admite hasta 100 caracteres y correo hasta 150.

Al pulsar **Guardar**, valido los datos y los envío mediante `fetch`, método HTTP POST y `Content-Type: application/json`. Deshabilito el botón y bloqueo otros envíos simultáneos desde el formulario mientras espero la respuesta. Solo muestro éxito y limpio los campos después de recibir una respuesta satisfactoria con `ok: true`. Ante un fallo de guardado conservo los valores. Después del commit intento enviar un acuse de recepción personalizado; si falla SMTP, informo que el contacto quedó guardado y limpio el formulario para evitar un nuevo envío innecesario.

El endpoint exige un objeto JSON con tres cadenas: `nombre`, `email` y `mensaje`. Rechaza campos ausentes, tipos incorrectos, valores vacíos o compuestos únicamente por espacios, formato básico de correo inválido y longitudes excesivas. Recorta los espacios de los extremos antes de almacenar. Cuenta unidades UTF-16 para respetar los límites de las columnas NVARCHAR. No comprueba que la dirección de correo exista.

| Código HTTP | Resultado |
|---|---|
| `201` | Inserción confirmada; devuelve `ok: true`, `correo_enviado` y un `mensaje` que distingue aceptación SMTP o fallo del acuse. |
| `400` | Datos inválidos, objeto incorrecto o JSON mal formado. |
| `413` | Solicitud superior al límite de 1 MiB. |
| `415` | Contenido que no se declara como JSON. |
| `503` | Fallo al conectar o guardar; respuesta general sin detalles de SQL Server. |

Las respuestas controladas de error contienen `ok: false` y `mensaje`. No hay un límite individual adicional para mensaje, pero se aplica el límite global de solicitud. La inserción utiliza `INSERT INTO dbo.Contacto (nombre, email, mensaje) VALUES (?, ?, ?)` y entrega los valores por separado.

## Seguridad implementada y límites

- **Validación en dos niveles:** JavaScript orienta al usuario y Flask comprueba las entradas de forma independiente, incluso ante solicitudes HTTP directas.
- **Consultas parametrizadas:** los marcadores `?` hacen que las entradas se traten como datos en la inserción implementada.
- **Transacciones y recursos:** utilizo `autocommit=False`, `commit()` tras insertar y `rollback()` ante fallos. Cierro cursor y conexión en `finally`, intentando cada cierre por separado.
- **Variables de entorno:** separo configuración y código mediante python-dotenv y utilizo autenticación de Windows.
- **Excepciones:** envío errores comprensibles al navegador y registro detalles técnicos en el servidor para diagnóstico.
- **Archivos públicos limitados:** publico la página y las carpetas de recursos; no hay rutas para descargar `.env`, Python ni SQL.
- **Mensajes seguros en el DOM:** utilizo `textContent` para no interpretar las respuestas como HTML.
- **Exclusiones de Git:** `.gitignore` excluye `.env`, `.env.*`, `.venv/`, `__pycache__/`, archivos compilados de Python, `.vscode/` y `*.log`. La excepción `!.env.example` permite compartir la plantilla. Estas reglas no eliminan archivos que ya estuvieran versionados.
- **Desarrollo local:** servidor limitado a localhost y depurador desactivado. `TrustServerCertificate=yes` omite la validación del certificado SQL Server para este entorno académico; no configura HTTPS en Flask.

Estas medidas no garantizan seguridad completa ni preparación para producción. El bloqueo del formulario no garantiza evitar duplicados al reintentar después de perder una respuesta. No se ha implementado la API meteorológica.

## Transferencia académica a Hostinger mediante FTPS

Utilizo `subir_ftp.py` y `ftplib`, sin dependencias adicionales. El acceso probado corresponde a `srv1939.hstgr.io`, puerto 21, mediante FTPS explícito. Mantengo `FTP_USE_TLS=true`, la verificación de certificados con `ssl.create_default_context()` y el cifrado de datos con `prot_p()`. No uso FTP sin cifrado. Conservo las credenciales únicamente en `.env`, excluido de Git, junto con la configuración SQL y SMTP existente.

El destino es **`/public_html/TechMindSolutions_AA2/`**, porque la cuenta no permite transferencias fuera de `public_html`. Creo la carpeta si no existe, sin modificar el sitio situado fuera de ella. El script no borra ni sobrescribe archivos existentes, tampoco dentro de esta carpeta. Rechaza enlaces o directorios cuya ubicación no pueda verificar mediante PWD y MLSD.

Desde PowerShell, en la raíz del proyecto, pruebo conexión, autenticación, directorio actual y lectura por el canal de datos cifrado:

```powershell
.\.venv\Scripts\python.exe -B .\subir_ftp.py probar
```

`probar` no crea carpetas ni modifica archivos. Para subir, indico también la URL HTTPS real que corresponde a la carpeta del proyecto. Sustituyo `DOMINIO` por el dominio del sitio que sirve ese `public_html`, no por el servidor FTP:

```powershell
.\.venv\Scripts\python.exe -B .\subir_ftp.py subir --url-base "https://DOMINIO/TechMindSolutions_AA2/"
```

La URL debe terminar exactamente en `/TechMindSolutions_AA2/`, sin usuario, contraseña, consulta ni fragmento. El script verifica el certificado HTTPS y rechaza redirecciones. Una configuración de dominio incorrecta, un firewall, un proxy o reglas del hosting pueden impedir la comprobación: en ese caso no transfiero fuentes reales.

### Protección de Python y SQL antes de transferirlos

Creo una subcarpeta nueva **`protegido/`** dentro del destino. Primero subo un testigo aleatorio sin información sensible y verifico por HTTPS que devuelve HTTP 200 y exactamente su contenido. Esta comprobación confirma la correspondencia entre la ruta FTP y la URL pública.

Después creo `protegido/.htaccess` con `Require all denied`, destinado a Apache/LiteSpeed. Verifico HTTP **403** para el testigo, dos archivos inocuos con extensiones `.py` y `.sql`, y el propio `.htaccess`. Solo después de completar estas comprobaciones transfiero Python y SQL reales. Si las reglas no son reconocidas, recibo otro código, falla TLS o no puedo comprobar la protección, aborto la subida de fuentes. No acepto un simple 404 como prueba de protección.

La lista explícita permite el HTML, CSS, dos archivos JavaScript y logotipo en sus rutas relativas públicas. En `protegido/` guardo los cuatro módulos Python de la aplicación y transferencia, `requirements.txt`, `README.md` y `database/TechMindSolutions_AA2.sql`, conservando las subcarpetas. No transfiero `.env`, `.env.example`, `.git`, `.venv`, cachés, copias de seguridad ni archivos no enumerados. Debo revisar que los archivos permitidos no incluyan credenciales o datos personales añadidos manualmente; el script no analiza semánticamente su contenido.

Los testigos y `.htaccess` permanecen para evidenciar el control; el script no elimina archivos remotos. Si ya existe `protegido/`, detengo la subida antes de escribir en ella, para no confiar en reglas previas ni sobrescribir fuentes. Una interrupción puede dejar una copia parcial; debo revisarla manualmente antes de decidir cómo continuar. Evito transferencias concurrentes porque FTP no garantiza una creación atómica sin sobrescritura mediante STOR.

Muestro cada archivo confirmado y un resumen con cantidad y bytes, incluidos los controles de protección. Esta verificación refleja el estado observado antes de transferir y depende de que el hosting conserve sus reglas. Conviene comprobar después que las URLs de las fuentes reales siguen devolviendo 403 y repetir la revisión tras cambios de configuración.

La copia no ejecuta Flask ni configura Python en Hostinger: el formulario conserva su endpoint relativo, que requiere un backend Flask desplegado por separado para funcionar allí. SQL Server continúa siendo local. Esta tarea no cambia el frontend ni configura ese despliegue.

La conexión FTPS fue confirmada manualmente por el desarrollador. No se ejecutó la nueva subida ni se verificaron reglas HTTP en el hosting durante esta modificación; esas pruebas quedan pendientes para obtener las capturas académicas.

## Acuse de recepción por SMTP

Implemento el requisito 4 del paso 1 de AA2 mediante `correo.py`. Separo la entrega de correo del acceso a datos: Flask termina la transacción y cierra los recursos SQL antes de solicitar el acuse. El destinatario es el correo validado del formulario y el saludo utiliza el nombre proporcionado.

Configuro estas variables en `.env`, utilizando `.env.example` como referencia y conservando la configuración de base de datos:

```dotenv
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USER=info@tech-mindsolutions.com
SMTP_PASSWORD=
SMTP_USE_SSL=true
```

Introduzco manualmente la contraseña del buzón únicamente en `.env` y reinicio Flask tras cambiarla. La contraseña se entrega vacía y no se debe incorporar a Git, capturas, registros ni respuestas HTTP. `.env` permanece excluido por `.gitignore`. Las variables del proceso tienen prioridad sobre el archivo local.

Utilizo las bibliotecas estándar `smtplib`, `ssl` y `email.message.EmailMessage`, sin añadir dependencias. `SMTP_SSL` establece SSL/TLS desde el inicio en el puerto 465, con `ssl.create_default_context()` para verificar certificados y un timeout de 10 segundos. No desactivo la verificación TLS ni habilito depuración SMTP. Las excepciones se convierten en un resultado controlado sin registrar sus detalles, que podrían contener información sensible.

El asunto es **Confirmación de recepción - TechMindSolutions** y el cuerpo es:

```text
Estimado/a [nombre]:

Gracias por contactar con TechMindSolutions.

Hemos recibido correctamente tu mensaje. Nuestro equipo revisará tu solicitud y se pondrá en contacto contigo lo antes posible.

Saludos cordiales,
Equipo de TechMindSolutions
```

Si falta la contraseña o la configuración es inválida, no intento la conexión SMTP y devuelvo `correo_enviado: false`. Cuando el servidor acepta el correo, devuelvo `correo_enviado: true`; esa aceptación no garantiza su llegada a la bandeja de entrada. Un fallo SMTP mantiene HTTP `201` y `ok: true` porque el registro ya se guardó. No ejecuto rollback ni reintentos automáticos por un fallo del correo.

### Prueba manual del acuse pendiente

No se han enviado correos reales durante esta implementación. Para probar posteriormente:

1. Con `SMTP_PASSWORD` vacío, inicio Flask y envío un contacto con una dirección propia. Compruebo el guardado en SQL Server y el aviso de que no se pudo enviar el acuse. Esta prueba crea un contacto real, pero no intenta SMTP.
2. Introduzco la contraseña válida en `.env`, reinicio Flask y envío otro contacto a un buzón controlado por mí. Compruebo el guardado, `correo_enviado: true` y la recepción del asunto y cuerpo personalizados, incluida la carpeta de correo no deseado.
3. Para comprobar un fallo de autenticación, uso temporalmente una clave incorrecta, reinicio Flask y envío un nuevo contacto. Verifico que el registro permanezca, que se muestre el aviso de fallo del acuse y que la respuesta no incluya detalles técnicos ni credenciales. Restauro después la configuración correcta.
4. Compruebo que una solicitud inválida reciba HTTP `400`, sin insertar un contacto ni intentar enviar un correo.

La entrega es síncrona: el formulario permanece bloqueado mientras espera el resultado SMTP. No debo reenviar un contacto ya guardado únicamente porque falle su acuse.

## Pruebas realizadas

### Pruebas manuales completadas

Registro los siguientes resultados satisfactorios conforme a las pruebas manuales informadas por el desarrollador para esta etapa. No se repitieron durante la actualización de este documento.

| Prueba | Resultado observado |
|---|---|
| Envío de contacto válido | El formulario confirmó el guardado y se verificó la persistencia en SQL Server. |
| Campos obligatorios vacíos | La validación rechazó el envío incompleto. |
| Correo de formato inválido | La validación rechazó la dirección incorrecta. |
| Solicitud HTTP directa con datos inválidos | El servidor devolvió HTTP `400`. |
| Intento de inyección SQL | La expresión enviada se almacenó como texto literal y los registros anteriores permanecieron intactos. |

La prueba de inyección verifica el comportamiento de la inserción evaluada; no constituye una auditoría completa de seguridad. No incluyo datos personales de los contactos utilizados.

### Comprobaciones no destructivas de la implementación

Durante la implementación se comprobaron sintaxis Python y JavaScript, configuración, rutas públicas y rechazo del acceso a archivos privados. Se probaron validación, confirmación, reversión y cierre de recursos con conexiones simuladas, además de los estados de éxito y error y el bloqueo de envíos simultáneos en JavaScript. Estas comprobaciones no abrieron conexiones reales ni insertaron registros y se distinguen de las pruebas manuales anteriores.

### Recomendaciones adicionales pendientes

Recomiendo ampliar las pruebas manuales a límites de longitud, caracteres Unicode, indisponibilidad de SQL Server, pérdida de conexión y solicitudes que excedan el tamaño permitido. También conviene revisar el formulario en distintos tamaños de pantalla y comprobar las interacciones jQuery. Estas recomendaciones no se presentan como pruebas manuales completadas.

## Autoría académica

- **Estudiante:** Samuel Guasco.
- **Universidad:** Universidad Internacional del Ecuador (UIDE).
- **Carrera y nivel:** Ingeniería de Software, quinto semestre.
- **Asignatura:** Programación de Middleware y Seguridad de la Base de Datos.
- **Actividad:** Aprendizaje Autónomo 2 (AA2), continuación de AA1.

Desarrollo este trabajo con fines académicos para integrar una interfaz web, un middleware Flask y persistencia relacional en SQL Server.
