# TechMindSolutions_AA2

## Descripción y contexto académico

Proyecto de **Aprendizaje Autónomo 2 (AA2)** de la asignatura **Programación de Middleware y Seguridad de la Base de Datos**, carrera de **Ingeniería de Software**, quinto semestre, de la **Universidad Internacional del Ecuador (UIDE)**. Continúo el trabajo de AA1 incorporando un middleware Python que conecta el formulario web con SQL Server.

TechMindSolutions es un concepto de emprendimiento digital para empresas y emprendedores. Presenta desarrollo de sitios web, tarjetas digitales NFC y ClozerIA CRM, distribuido por Estrategia10X. El sitio describe estas soluciones; no implementa un CRM ni lectura NFC.

Conservo las secciones **Inicio, Empresa, Productos, Oferta del mes, Localización, Contacto y Noticias**, e incorporo **Clima** en el menú antes de Contacto. Mantengo el logotipo y el diseño adaptable. El horario es provisional y la dirección física está pendiente de confirmación. El formulario permite guardar contactos mediante Flask y el reportero consulta datos meteorológicos reales mediante el middleware.

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
| urllib, json y unittest | Consulta meteorológica HTTPS, normalización y pruebas reproducibles sin dependencias nuevas. |
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
├── clima.py
├── tests/
│   ├── test_clima.py
│   └── test_clima_frontend.cjs
├── subir_ftp.py
├── .env                 # Configuración local, excluida de Git
├── .env.example         # Plantilla compartida
├── .gitignore
├── requirements.txt
├── README.md
├── index.html
├── clima.html
├── css/
│   ├── styles.css
│   └── clima.css
├── js/
│   ├── script.js
│   ├── jquery-servicios.js
│   └── clima.js
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
| `clima.py` | Consulta OpenWeatherMap con urllib, valida la respuesta y normaliza el clima. |
| `tests/test_clima.py` | Pruebas del módulo y la ruta Flask con respuestas simuladas. |
| `tests/test_clima_frontend.cjs` | Pruebas JavaScript con DOM y red simulados, mediante Node.js. |
| `clima.html` | Página del reportero meteorológico con navegación y estados accesibles. |
| `css/clima.css` | Diseño adaptable del reportero, separado de los estilos existentes. |
| `js/clima.js` | Consulta asíncrona a Flask, validación de JSON y actualización segura del DOM. |
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
- **Exclusiones de Git:** `.gitignore` excluye `.env`, `.env.*`, `.venv/`, `__pycache__/`, archivos compilados de Python, `.vscode/`, `.idea/`, `*.log`, `*.tmp`, `*.bak`, `Thumbs.db` y `.DS_Store`. La excepción `!.env.example` permite compartir la plantilla. Estas reglas no eliminan archivos que ya estuvieran versionados.
- **Desarrollo local:** servidor limitado a localhost y depurador desactivado. `TrustServerCertificate=yes` omite la validación del certificado SQL Server para este entorno académico; no configura HTTPS en Flask.

Estas medidas no garantizan seguridad completa ni preparación para producción. El bloqueo del formulario no garantiza evitar duplicados al reintentar después de perder una respuesta. La API meteorológica conserva sus credenciales exclusivamente en el backend y ofrece una interfaz de consulta en `/clima`, como documento a continuación.

## Paso 2: reportero meteorológico — GET /api/clima

Implemento `app.py → clima.py → HTTPS → OpenWeatherMap Current Weather Data`, mediante `https://api.openweathermap.org/data/2.5/weather`. Separo la consulta externa de Flask para verificar la normalización y los errores de forma reproducible. Conservo el formulario, SQL Server, SMTP y FTPS. Esta ruta no abre conexiones SQL ni envía correos.

Leo estas variables desde el entorno o el `.env` existente, sin sobrescribirlo ni reemplazar las variables del proceso:

```dotenv
OPENWEATHER_API_KEY=REEMPLAZAR_CON_MI_CLAVE
OPENWEATHER_CITY=Quito,EC
OPENWEATHER_UNITS=metric
OPENWEATHER_LANG=es
```

Los valores anteriores son ejemplos públicos; guardo la clave real únicamente en mi configuración local. Exijo clave y ciudad no vacías. Acepto `metric`, `standard` e `imperial`; si omito unidades utilizo `metric`. Exijo `es` para solicitar la descripción en español; si omito el idioma utilizo `es`. Una configuración incompatible recibe HTTP 503 antes de consultar internet.

Uso `urllib.request`, `urlencode` y `json` de la biblioteca estándar; no agrego dependencias. Verifico TLS con la configuración predeterminada y rechazo redirecciones para proteger la clave. Establezco un timeout de 10 segundos para operaciones de red, que no representa un plazo global estricto de toda la solicitud. Limito la lectura a 1 MiB, valido campos obligatorios, tipos, números finitos, humedad, viento e icono y cierro la respuesta con un administrador de contexto. No publico ni registro la URL autenticada, los cuerpos de error externos ni los detalles de sus excepciones.

Mi contrato JSON satisfactorio es HTTP 200 con esta estructura ilustrativa; los valores reales varían:

```json
{
  "ok": true,
  "clima": {
    "ciudad": "Quito",
    "pais": "EC",
    "temperatura_c": 18.5,
    "humedad": 72,
    "descripcion": "lluvia ligera",
    "viento_kmh": 9.0,
    "icono": "10d"
  }
}
```

Devuelvo el país como código del proveedor, humedad como porcentaje e icono como código, sin descargar imágenes. Convierto m/s a km/h multiplicando por 3,6 para `metric` y `standard`; para `imperial` convierto mph a km/h multiplicando por 1,609344. Convierto Kelvin o Fahrenheit a Celsius cuando corresponde y redondeo temperatura y viento a dos decimales. Solicito `lang=es` al proveedor, sin intentar traducir localmente sus descripciones.

Sigo los parámetros y unidades de la [documentación oficial de OpenWeatherMap](https://openweathermap.org/api/current). Utilizo la consulta por ciudad solicitada para esta actividad; el proveedor indica que su geocodificador integrado está obsoleto, aunque sigue disponible.

| Situación | HTTP de mi endpoint |
|---|---|
| Autenticación rechazada por el proveedor (401) | 502; la clave pertenece al backend, no al visitante. |
| Ciudad no encontrada (404) | 404. |
| Límite de consultas del proveedor (429) | 429. |
| Fallo 5xx del proveedor | 503. |
| Fallo de conexión, DNS o TLS | 503. |
| Timeout de conexión o lectura | 504. |
| JSON, estructura o datos inválidos; redirección u otro estado inesperado | 502. |
| Configuración local inválida | 503. |

En todos los errores controlados devuelvo `{"ok": false, "mensaje": "…"}` con texto seguro. No realizo reintentos automáticos para no aumentar el consumo de la cuota. Cada GET consulta al proveedor; no implemento caché. La interfaz consulta al abrirse y cuando el visitante pulsa el botón de actualización, sin consultas periódicas.

### Validación local del clima

Desde la raíz del proyecto ejecuto las pruebas reproducibles, sin llamadas reales, con `unittest` y `unittest.mock`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Verifico éxito y contrato JSON, parámetros HTTPS, cierre de respuesta, timeout configurado, conversiones, errores HTTP, conexiones fallidas, timeout directo y envuelto, JSON inválido, UTF-8 inválido, datos incompletos o incoherentes, exceso de tamaño, configuración inválida, rechazo de redirecciones y método POST. Uso una clave ficticia en las excepciones simuladas para comprobar que no aparezca en las respuestas. También compruebo que GET no invoque SQL ni SMTP.

Conservo el `.env` que ya funciona e inicio el servidor:

```powershell
.\.venv\Scripts\python.exe -B .\app.py
```

En una segunda terminal PowerShell consulto el endpoint local:

```powershell
curl.exe -i http://127.0.0.1:5000/api/clima
Invoke-RestMethod -Method Get -Uri 'http://127.0.0.1:5000/api/clima' | ConvertTo-Json -Depth 3
```

Cada comando anterior realiza una consulta real y consume cuota. Para validar la integración Flask sin iniciar un proceso servidor utilizo alternativamente:

```powershell
.\.venv\Scripts\python.exe -B -c "from app import app; import json; r = app.test_client().get('/api/clima'); print('HTTP', r.status_code); print(json.dumps(r.get_json(), ensure_ascii=False)); raise SystemExit(0 if r.status_code == 200 else 1)"
```

En la validación inicial del backend ejecuté las siete pruebas automatizadas satisfactoriamente y comprobé la integración con el cliente de pruebas Flask y el proveedor real: recibí HTTP 200, ciudad Quito, país EC y descripción en español. Posteriormente confirmé el funcionamiento de la interfaz en el navegador, la actualización manual y la recuperación del servicio, como registro en las pruebas realizadas. Mantengo la clave fuera de las fuentes y esta actualización documental no modifica `.env` ni realiza commits, subidas o despliegues.

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

### Alcance del hosting y del entorno local

FTPS transfiere archivos, pero no ejecuta Flask ni configura Python en Hostinger. SQL Server y el backend Flask operan en el entorno de desarrollo local. El frontend estático transferido es accesible públicamente; esa accesibilidad no demuestra que las rutas dinámicas estén desplegadas en el hosting.

El formulario requiere `/api/contacto` y el reportero requiere `/api/clima`, atendidos por Flask. El reportero funciona localmente en **http://127.0.0.1:5000/clima**. El script FTP existente no despliega el reportero: su lista permitida no incluye `clima.py`, `clima.html`, `css/clima.css` ni `js/clima.js`. Además, las rutas absolutas de la página requieren Flask o una configuración equivalente; una copia estática en una subcarpeta de Hostinger no habilita estas funciones.

Confirmé manualmente la conexión FTPS autenticada y cifrada con Python `ftplib`, la transferencia de archivos a Hostinger y la accesibilidad pública del frontend. Estos resultados corresponden a las validaciones académicas realizadas; esta actualización documental no repite transferencias ni altera el hosting.

## Acuse de recepción por SMTP

Implemento el requisito 4 del paso 1 de AA2 mediante `correo.py`. Separo la entrega de correo del acceso a datos: Flask termina la transacción y cierra los recursos SQL antes de solicitar el acuse. El destinatario es el correo validado del formulario y el saludo utiliza el nombre proporcionado.

Configuro estas variables en `.env`, utilizando `.env.example` como referencia y conservando la configuración de base de datos:

```dotenv
SMTP_HOST=smtp.hostinger.com
SMTP_PORT=465
SMTP_USER=usuario@example.com
SMTP_PASSWORD=
SMTP_USE_SSL=true
```

Sustituyo `usuario@example.com` por el usuario real únicamente en mi configuración local. Introduzco manualmente la contraseña del buzón únicamente en `.env` y reinicio Flask tras cambiarla. La contraseña se entrega vacía y no se debe incorporar a Git, capturas, registros ni respuestas HTTP. `.env` permanece excluido por `.gitignore`. Las variables del proceso tienen prioridad sobre el archivo local.

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

### Validación manual del acuse y alcance de la entrega

Verifiqué manualmente la recepción del correo automático de confirmación en el buzón de Hostinger después de registrar un contacto. Repetí la comprobación en la regresión final y confirmé tanto la persistencia en SQL Server local como la recepción del acuse en Hostinger. El buzón remoto recibe el correo enviado por el backend local; esto no implica que Flask o SQL Server se ejecuten en Hostinger.

La entrega a destinatarios externos de Gmail no quedó confirmada de forma concluyente. Distingo la aceptación SMTP de la recepción efectiva: la recepción comprobada corresponde al buzón de Hostinger y no permite afirmar entrega universal a otros proveedores.

La entrega es síncrona: el formulario permanece bloqueado mientras espera el resultado SMTP. No debo reenviar un contacto ya guardado únicamente porque falle su acuse.

## Pruebas realizadas

### Pruebas manuales completadas

Registro los siguientes resultados satisfactorios conforme a las validaciones manuales confirmadas por el desarrollador para el proyecto terminado. No se repitieron durante esta actualización documental.

#### Paso 1: formulario, persistencia, correo y transferencia

| Prueba | Resultado observado |
|---|---|
| Envío de contacto válido | El formulario confirmó el guardado y se verificó la persistencia en SQL Server. |
| Campos obligatorios vacíos | La validación rechazó el envío incompleto. |
| Correo de formato inválido | La validación rechazó la dirección incorrecta. |
| Solicitud HTTP directa con datos inválidos | El servidor devolvió HTTP `400`. |
| Intento de inyección SQL | La expresión enviada se almacenó como texto literal y los registros anteriores permanecieron intactos. |
| Correo automático de confirmación | Se recibió satisfactoriamente en el buzón de Hostinger. |
| Conexión FTPS con Python `ftplib` | Autenticación y conexión cifrada satisfactorias. |
| Transferencia a Hostinger | Los archivos se transfirieron correctamente al entorno de hosting. |
| Acceso público al frontend | Se verificó la accesibilidad del sitio estático publicado. |

La prueba de inyección verifica el comportamiento de la inserción evaluada; no constituye una auditoría completa de seguridad. No incluyo datos personales de los contactos utilizados.

#### Paso 2: consulta e interfaz meteorológica

| Prueba | Resultado observado |
|---|---|
| Cuenta y configuración de OpenWeatherMap | Configuración completada; la clave funcional denominada Default se administra mediante `.env`, sin publicarla. |
| Solicitudes HTTPS al proveedor | Respuestas satisfactorias con datos meteorológicos reales. |
| Middleware Flask y `GET /api/clima` | Integración validada y respuesta JSON normalizada correcta. |
| Navegación | Reportero integrado mediante el enlace Clima antes de Contacto. |
| Presentación de datos | Temperatura, humedad, descripción meteorológica y velocidad del viento mostradas correctamente. |
| Actualización manual | Funcionamiento validado mediante Chrome DevTools. |
| Visualización adaptable | Verificada manualmente en distintos tamaños de pantalla. |
| Error de red | Manejo comprobado al detener Flask. |
| Recuperación del servicio | Consulta restablecida satisfactoriamente después de reiniciar Flask. |
| Regresión final del formulario | Se confirmó nuevamente la persistencia en SQL Server local y la entrega de la confirmación SMTP al buzón de Hostinger. |

### Resultados de las pruebas automatizadas

Documento los resultados de la auditoría final, obtenidos con respuestas simuladas y sin operaciones reales SQL, SMTP o FTP:

| Conjunto | Resultado |
|---|---|
| Python: `tests/test_clima.py` | **7/7 satisfactorias**. |
| JavaScript: `tests/test_clima_frontend.cjs` | **4/4 satisfactorias**. |
| Total | **11/11 satisfactorias**. |

Estos resultados complementan las validaciones manuales y no se presentan como pruebas de despliegue del backend en Hostinger.

### Comprobaciones no destructivas de la implementación

Durante la implementación se comprobaron sintaxis Python y JavaScript, configuración, rutas públicas y rechazo del acceso a archivos privados. Se probaron validación, confirmación, reversión y cierre de recursos con conexiones simuladas, además de los estados de éxito y error y el bloqueo de envíos simultáneos en JavaScript. Estas comprobaciones no abrieron conexiones reales ni insertaron registros y se distinguen de las pruebas manuales anteriores.

### Posibles ampliaciones de las pruebas

Como ampliación futura, puedo profundizar las pruebas de límites de longitud, caracteres Unicode, indisponibilidad de SQL Server y solicitudes que excedan el tamaño permitido. Estas propuestas no invalidan las verificaciones ya completadas de visualización adaptable, error de red y recuperación del servicio meteorológico.

## Interfaz del reportero meteorológico

Creo `clima.html`, accesible mediante **http://127.0.0.1:5000/clima**, y agrego «Clima» inmediatamente antes de «Contacto» en la navegación compartida por escritorio y móviles. Desde esta página los demás enlaces regresan a las secciones de la página principal. Marco el enlace activo mediante `aria-current="page"`. Reutilizo el encabezado, el logotipo, el pie, la tipografía y la paleta existentes; limito mis reglas nuevas a `css/clima.css`.

Presento una tarjeta centrada con ciudad, país, icono, temperatura en °C, descripción, humedad y velocidad del viento. Distribuyo las medidas en dos bloques equilibrados y las apilo en pantallas muy estrechas. Uso HTML semántico, una lista descriptiva para las medidas, foco visible, texto alternativo y una región de estado accesible. No incluyo datos meteorológicos ficticios en la página.

Implemento `js/clima.js` con `fetch('/api/clima')` y `async/await`: consulto al abrir la página y al pulsar **Actualizar clima**. El navegador habla con Flask; solamente el backend consulta la API autenticada. La clave permanece en el entorno del servidor y nunca se incorpora al HTML ni al JavaScript. La descarga del icono utiliza una URL HTTPS pública de OpenWeatherMap y un código validado con una lista de formatos permitidos.

Compruebo el estado HTTP, el indicador `ok` y los campos JSON antes de actualizar el DOM. Uso `textContent` para el texto externo, `Intl.NumberFormat('es-EC')` para los números y «Ecuador» cuando el código recibido es `EC`. Deshabilito el botón durante la consulta, evito solicitudes simultáneas y cancelo la espera del navegador tras 15 segundos. Anuncio carga, éxito y errores sin mover el foco. Ante un error oculto el panel para no presentar una observación anterior como actual y permito reintentar. Si falla la imagen, mantengo la descripción meteorológica textual.

### Pruebas locales de la interfaz

Desde la raíz del proyecto inicio Flask:

```powershell
.\.venv\Scripts\python.exe -B .\app.py
```

Abro **http://127.0.0.1:5000/clima** mediante Flask; abrir el archivo HTML directamente no ofrece el endpoint relativo. Necesito conexión a internet y la configuración `.env` ya validada. Cada carga y actualización consulta al proveedor y consume cuota. No modifico `.env` ni necesito credenciales en el navegador.

Compruebo que los datos se carguen automáticamente, que «Actualizar clima» vuelva a consultarlos y que el botón se deshabilite mientras espero. Reviso el menú en ambas páginas, el enlace activo, el uso del teclado y el anuncio de estados. Compruebo anchos de escritorio, tableta y móvil, así como zoom del navegador. Para comprobar recuperación de errores puedo activar temporalmente el modo sin conexión en las herramientas del navegador y volver a pulsar el botón después de restablecer la red.

Ejecuto las siete pruebas existentes del backend y las cuatro pruebas nuevas de JavaScript. Estas últimas usan el ejecutor nativo de Node.js, sin instalar paquetes; simulan el DOM y la red exclusivamente dentro de las pruebas:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
node --test tests/test_clima_frontend.cjs
```

Las pruebas de JavaScript verifican carga automática, endpoint relativo, formato numérico, texto seguro, icono, actualización, exclusión de consultas simultáneas, restauración del botón y manejo de errores HTTP, red, timeout y respuestas inválidas. La simulación del DOM no sustituye la revisión visual ni una evaluación con lector de pantalla en un navegador real.

## Autoría académica

- **Estudiante:** Samuel Guasco.
- **Universidad:** Universidad Internacional del Ecuador (UIDE).
- **Carrera y nivel:** Ingeniería de Software, quinto semestre.
- **Asignatura:** Programación de Middleware y Seguridad de la Base de Datos.
- **Actividad:** Aprendizaje Autónomo 2 (AA2), continuación de AA1.

Desarrollo este trabajo con fines académicos para integrar una interfaz web, un middleware Flask y persistencia relacional en SQL Server.
