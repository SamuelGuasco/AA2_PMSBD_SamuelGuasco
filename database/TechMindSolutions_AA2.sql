
-- Creo la base de datos para el proyecto TechMindSolutions.
CREATE DATABASE TechMindSolutions_AA2;
GO

-- Selecciono la base de datos para trabajar con ella.
USE TechMindSolutions_AA2;
GO


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Creo la tabla Cliente para almacenar sus datos.
CREATE TABLE Cliente (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) NULL
);
GO

-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Creo la tabla Servicio para registrar los servicios de la empresa.
CREATE TABLE Servicio (
    id_servicio INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255) NULL,
    precio DECIMAL(10,2) NULL
);
GO

-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Creo la tabla Solicitud para relacionar clientes y servicios.
CREATE TABLE Solicitud (
    id_solicitud INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_servicio INT NOT NULL,
    fecha_solicitud DATE NOT NULL,
    estado VARCHAR(30) NOT NULL,

    -- Relaciono la solicitud con la tabla Cliente.
    FOREIGN KEY (id_cliente)
        REFERENCES Cliente(id_cliente),

    -- Relaciono la solicitud con la tabla Servicio.
    FOREIGN KEY (id_servicio)
        REFERENCES Servicio(id_servicio)
);
GO


-- Selecciono la base de datos del proyecto.
USE TechMindSolutions_AA2;
GO

-- Elimino la relación directa entre Solicitud y Servicio.
DECLARE @restriccion NVARCHAR(128);

SELECT @restriccion = fk.name
FROM sys.foreign_keys AS fk
WHERE fk.parent_object_id = OBJECT_ID('dbo.Solicitud')
  AND fk.referenced_object_id = OBJECT_ID('dbo.Servicio');

IF @restriccion IS NOT NULL
BEGIN
    DECLARE @sentencia NVARCHAR(MAX);
    SET @sentencia = N'ALTER TABLE dbo.Solicitud DROP CONSTRAINT '
                     + QUOTENAME(@restriccion);
    EXEC sp_executesql @sentencia;
END;
GO

-- Elimino la columna que trasladaremos al detalle.
ALTER TABLE dbo.Solicitud
DROP COLUMN id_servicio;
GO

-- Selecciono la base de datos del proyecto.
USE TechMindSolutions_AA2;
GO

-- Declaro las variables necesarias.
DECLARE @restriccion NVARCHAR(128);
DECLARE @sql NVARCHAR(MAX);

-- Identifico la clave foránea entre Solicitud y Servicio.
SELECT @restriccion = fk.name
FROM sys.foreign_keys AS fk
WHERE fk.parent_object_id = OBJECT_ID('dbo.Solicitud')
  AND fk.referenced_object_id = OBJECT_ID('dbo.Servicio');

-- Elimino la restricción si existe.
IF @restriccion IS NOT NULL
BEGIN
    SET @sql = N'ALTER TABLE dbo.Solicitud DROP CONSTRAINT '
               + QUOTENAME(@restriccion);

    EXEC sp_executesql @sql;
END;
GO

-- Elimino la columna id_servicio si todavía existe.
IF COL_LENGTH('dbo.Solicitud', 'id_servicio') IS NOT NULL
BEGIN
    ALTER TABLE dbo.Solicitud
    DROP COLUMN id_servicio;
END;
GO

-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Creo la tabla Detalle_Solicitud para registrar
-- los servicios que forman parte de cada solicitud.
CREATE TABLE Detalle_Solicitud (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_solicitud INT NOT NULL,
    id_servicio INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NULL,

    -- Relaciono cada detalle con una solicitud.
    FOREIGN KEY (id_solicitud)
        REFERENCES Solicitud(id_solicitud),

    -- Relaciono cada detalle con un servicio.
    FOREIGN KEY (id_servicio)
        REFERENCES Servicio(id_servicio)
);
GO

USE TechMindSolutions_AA2;
GO

SELECT
    fk.name AS restriccion,
    OBJECT_NAME(fk.parent_object_id) AS tabla_origen,
    OBJECT_NAME(fk.referenced_object_id) AS tabla_destino
FROM sys.foreign_keys AS fk
WHERE fk.parent_object_id = OBJECT_ID('dbo.Solicitud');


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Registro tres clientes de ejemplo en la tabla Cliente.
INSERT INTO Cliente (nombre, correo, telefono)
VALUES
('Carlos Perez', 'carlos@example.com', '0991111111'),
('Maria Lopez', 'maria@example.com', '0992222222'),
('Andres Torres', 'andres@example.com', '0993333333');
GO

-- Consulto los registros almacenados en la tabla Cliente.
SELECT * FROM Cliente;
GO


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Registro los tres servicios que ofrece la empresa.
INSERT INTO Servicio (nombre, descripcion, precio)
VALUES
('Desarrollo de sitios web',
 'Diseño y desarrollo de paginas web corporativas',
 250.00),

('Tarjetas digitales NFC',
 'Credenciales digitales para compartir informacion de contacto',
 35.00),

('ClozerIA CRM',
 'Sistema para gestionar clientes y oportunidades comerciales',
 100.00);
GO

-- Consulto los servicios registrados en la base de datos.
SELECT * FROM Servicio;
GO


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Registro tres solicitudes asociadas a los clientes.
INSERT INTO Solicitud (id_cliente, fecha_solicitud, estado)
VALUES
(1, '2026-11-15', 'Pendiente'),
(2, '2026-11-15', 'En proceso'),
(3, '2026-11-15', 'Completada');
GO

-- Consulto las solicitudes registradas.
SELECT * FROM Solicitud;
GO


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Registro los servicios asociados a cada solicitud.
INSERT INTO Detalle_Solicitud
    (id_solicitud, id_servicio, cantidad, precio_unitario)
VALUES
    (1, 1, 1, 250.00),
    (1, 2, 2, 35.00),
    (2, 3, 1, 100.00),
    (3, 2, 1, 35.00);
GO

-- Consulto los detalles registrados.
SELECT * FROM Detalle_Solicitud;
GO






-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Actualizo el estado de la solicitud del cliente Carlos Perez.
UPDATE Solicitud
SET estado = 'En proceso'
WHERE id_solicitud = 1;
GO

-- Consulto los registros para verificar la actualizacion.
SELECT * FROM Solicitud;
GO


-- Selecciono la base de datos de TechMindSolutions.
USE TechMindSolutions_AA2;
GO

-- Creo un cliente temporal para probar la eliminacion.
INSERT INTO Cliente (nombre, correo, telefono)
VALUES ('Cliente Temporal', 'temporal@example.com', '0999999999');

-- Guardo el identificador del cliente insertado.
DECLARE @id_temporal INT = SCOPE_IDENTITY();

-- Consulto el registro antes de eliminarlo.
SELECT * FROM Cliente
WHERE id_cliente = @id_temporal;

-- Elimino solamente el cliente temporal.
DELETE FROM Cliente
WHERE id_cliente = @id_temporal;

-- Compruebo que el registro ya no existe.
SELECT * FROM Cliente
WHERE id_cliente = @id_temporal;

-- Verifico que los clientes originales se conservan.
SELECT * FROM Cliente;
GO


-- Selecciono la base de datos de AA2 para incorporar la tabla de contacto.
USE TechMindSolutions_AA2;
GO

-- Creo la tabla dbo.Contacto para almacenar los mensajes enviados desde el formulario web.
-- Mantengo esta información en una tabla independiente para conservar las relaciones existentes.
CREATE TABLE dbo.Contacto (
    -- Creo un identificador de tipo INT para distinguir cada contacto mediante un número entero.
    -- Utilizo IDENTITY(1,1) para generarlo automáticamente desde 1, con incrementos de 1.
    -- Defino PRIMARY KEY para garantizar su unicidad y evitar valores nulos.
    id_contacto INT IDENTITY(1,1) PRIMARY KEY,

    -- Almaceno el nombre con NVARCHAR(100) para admitir hasta 100 caracteres Unicode,
    -- incluidos nombres con tildes y otros caracteres propios de diferentes idiomas.
    -- Establezco NOT NULL porque considero obligatorio registrar el nombre del remitente.
    nombre NVARCHAR(100) NOT NULL,

    -- Guardo el correo electrónico con NVARCHAR(150) para admitir hasta 150 caracteres Unicode.
    -- Aplico NOT NULL para exigir este dato como medio de respuesta al remitente.
    email NVARCHAR(150) NOT NULL,

    -- Registro el contenido del mensaje con NVARCHAR(MAX) para admitir texto Unicode extenso
    -- sin limitarlo a la longitud que asigno al nombre o al correo electrónico.
    -- Utilizo NOT NULL porque necesito conservar el mensaje asociado a cada contacto.
    mensaje NVARCHAR(MAX) NOT NULL,

    -- Registro la fecha y la hora con DATETIME2 para conservar su precisión fraccionaria.
    -- Defino NOT NULL para que cada contacto tenga una fecha y hora registradas.
    -- Asigno DEFAULT SYSDATETIME() para obtener la fecha y hora del servidor
    -- automáticamente cuando omito esta columna al insertar un contacto.
    fecha_contacto DATETIME2 NOT NULL DEFAULT SYSDATETIME()
);
GO
