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

Al pulsar **Guardar**, valido los datos y los envío mediante `fetch`, método HTTP POST y `Content-Type: application/json`. Deshabilito el botón y bloqueo otros envíos simultáneos desde el formulario mientras espero la respuesta. Solo muestro éxito y limpio los campos después de recibir una respuesta satisfactoria con `ok: true`. Ante un fallo conservo los valores. No envío correo de confirmación.

El endpoint exige un objeto JSON con tres cadenas: `nombre`, `email` y `mensaje`. Rechaza campos ausentes, tipos incorrectos, valores vacíos o compuestos únicamente por espacios, formato básico de correo inválido y longitudes excesivas. Recorta los espacios de los extremos antes de almacenar. Cuenta unidades UTF-16 para respetar los límites de las columnas NVARCHAR. No comprueba que la dirección de correo exista.

| Código HTTP | Resultado |
|---|---|
| `201` | Inserción confirmada: `{"ok": true, "mensaje": "Tu mensaje se ha guardado correctamente."}`. |
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

Estas medidas no garantizan seguridad completa ni preparación para producción. El bloqueo del formulario no garantiza evitar duplicados al reintentar después de perder una respuesta. No se han implementado SMTP, FTP ni la API meteorológica.

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
