// Obtengo los elementos del formulario mediante sus identificadores.
const formulario = document.getElementById('formulario-contacto');
const nombre = document.getElementById('nombre');
const correo = document.getElementById('correo');
const mensaje = document.getElementById('mensaje');
const resultado = document.getElementById('resultado-formulario');
const botonGuardar = document.getElementById('boton-guardar');

// Reviso los tres campos obligatorios y devuelvo el primer error encontrado.
// Uso trim para rechazar valores vacíos o compuestos solo por espacios.
// Compruebo también los límites de maxlength, incluso si asigno valores mediante JavaScript.
function validarFormulario() {
    let error = '';
    const correoTexto = correo.value.trim();
    // Compruebo un formato básico: texto, arroba, dominio y extensión sin espacios.
    const formatoCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (nombre.value.trim() === '') {
        error = 'Escribe tu nombre completo.';
    } else if (nombre.value.length > nombre.maxLength) {
        error = 'El nombre completo debe tener como máximo 100 caracteres.';
    } else if (correoTexto === '') {
        error = 'Escribe tu correo electrónico.';
    } else if (correo.value.length > correo.maxLength) {
        error = 'El correo electrónico debe tener como máximo 150 caracteres.';
    } else if (!formatoCorreo.test(correoTexto) || correo.validity.typeMismatch) {
        error = 'Escribe un correo válido, por ejemplo: nombre@empresa.com.';
    } else if (mensaje.value.trim() === '') {
        error = 'Escribe un mensaje.';
    }

    return error;
}

// Mantengo una bandera además del botón deshabilitado para impedir envíos simultáneos.
let guardando = false;

// Intercepto tanto el clic en el botón como el envío mediante Enter.
formulario.addEventListener('submit', async function (event) {
    event.preventDefault();
    if (guardando) {
        return;
    }
    const error = validarFormulario();

    // Actualizo únicamente el texto y la clase del mensaje, sin interpretar HTML.
    if (error !== '') {
        resultado.textContent = error;
        resultado.className = 'mensaje-error';
        return;
    }

    guardando = true;
    botonGuardar.disabled = true;
    botonGuardar.textContent = 'Guardando...';
    formulario.setAttribute('aria-busy', 'true');
    resultado.textContent = 'Estoy guardando tu mensaje...';
    resultado.className = '';

    try {
        // Envío JSON mediante POST a una ruta relativa del mismo servidor Flask.
        const respuesta = await fetch('/api/contacto', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                nombre: nombre.value.trim(),
                email: correo.value.trim(),
                mensaje: mensaje.value.trim()
            })
        });
        const datos = await respuesta.json();
        if (!respuesta.ok || datos.ok !== true) {
            resultado.textContent = typeof datos.mensaje === 'string'
                ? datos.mensaje : 'No se pudo guardar el contacto. Inténtalo más tarde.';
            resultado.className = 'mensaje-error';
            return;
        }
        // Solo anuncio el éxito y limpio los campos después de la confirmación del servidor.
        // Muestro también el estado del acuse: un fallo SMTP no significa que falló el guardado.
        resultado.textContent = datos.mensaje;
        resultado.className = 'mensaje-exito';
        formulario.reset();
    } catch (error) {
        // Conservo los campos cuando falla la red o recibo una respuesta que no es JSON.
        resultado.textContent = 'No se pudo confirmar el guardado. Revisa la conexión e inténtalo más tarde.';
        resultado.className = 'mensaje-error';
    } finally {
        // Restauro los controles para permitir otro intento cuando termina la solicitud.
        guardando = false;
        botonGuardar.disabled = false;
        botonGuardar.textContent = 'Guardar';
        formulario.setAttribute('aria-busy', 'false');
    }
});

// Desactivo los avisos automáticos para mostrar los errores en la página.
// Conservo required, maxlength y type="email" en el HTML y aplico las comprobaciones anteriores.
// Complemento estas comprobaciones con la validación independiente del servidor.
formulario.noValidate = true;
// Habilito el botón solo después de registrar el controlador que impide el envío.
botonGuardar.disabled = false;
