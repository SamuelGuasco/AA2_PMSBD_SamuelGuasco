// Encapsulo mi código para no compartir variables con los scripts del formulario.
(() => {
    'use strict';
    const buscar = (id) => document.getElementById(id);
    const boton = buscar('actualizar-clima');
    const estado = buscar('clima-estado');
    const panel = buscar('clima-datos');
    const icono = buscar('clima-icono');
    const numero = new Intl.NumberFormat('es-EC', { maximumFractionDigits: 2 });
    let consultando = false;

    // Valido el contrato JSON antes de modificar el DOM, incluso si la respuesta es HTTP 200.
    function esClimaValido(clima) {
        return clima && typeof clima === 'object'
            && ['ciudad', 'pais', 'descripcion'].every((campo) =>
                typeof clima[campo] === 'string' && clima[campo].trim().length > 0)
            && ['temperatura_c', 'humedad', 'viento_kmh'].every((campo) =>
                typeof clima[campo] === 'number' && Number.isFinite(clima[campo]))
            && clima.temperatura_c >= -273.15
            && clima.humedad >= 0 && clima.humedad <= 100 && clima.viento_kmh >= 0
            && typeof clima.icono === 'string'
            && /^(01|02|03|04|09|10|11|13|50)[dn]$/.test(clima.icono);
    }

    async function actualizarClima() {
        // Uso una bandera y deshabilito el botón para impedir consultas simultáneas.
        if (consultando) return;
        consultando = true;
        boton.disabled = true;
        panel.hidden = true;
        panel.setAttribute('aria-busy', 'true');
        estado.className = '';
        estado.textContent = 'Consultando las condiciones meteorológicas…';
        // Limito la espera del navegador y cancelo la solicitud si deja de responder.
        const controlador = new AbortController();
        const temporizador = setTimeout(() => controlador.abort(), 15000);
        try {
            // Consulto únicamente Flask: el middleware conserva la clave y habla con la API externa.
            // Con async/await espero la red y la lectura de JSON sin bloquear la interfaz.
            const respuesta = await fetch('/api/clima', {
                headers: { Accept: 'application/json' },
                signal: controlador.signal,
                cache: 'no-store'
            });
            if (!respuesta.ok) {
                const mensajes = {
                    404: 'No se encontró la ciudad configurada.',
                    429: 'Se alcanzó el límite de consultas. Inténtalo más tarde.',
                    502: 'El servicio meteorológico no pudo entregar datos válidos.',
                    503: 'El servicio meteorológico no está disponible. Inténtalo más tarde.',
                    504: 'La consulta excedió el tiempo de espera. Inténtalo de nuevo.'
                };
                throw new Error(mensajes[respuesta.status] || 'No se pudo consultar el clima. Inténtalo de nuevo.');
            }
            let datos;
            try {
                datos = await respuesta.json();
            } catch (error) {
                if (error.name === 'AbortError') throw error;
                throw new Error('El servidor devolvió una respuesta no válida. Inténtalo de nuevo.');
            }
            if (!datos || datos.ok !== true || !esClimaValido(datos.clima)) {
                throw new Error('El servidor devolvió datos meteorológicos incompletos o inválidos.');
            }
            const clima = datos.clima;
            // Uso textContent para mostrar texto externo sin interpretarlo como HTML.
            buscar('clima-ciudad').textContent = `${clima.ciudad}, ${clima.pais === 'EC' ? 'Ecuador' : clima.pais}`;
            buscar('clima-temperatura').textContent = `${numero.format(clima.temperatura_c)} °C`;
            buscar('clima-descripcion').textContent = clima.descripcion;
            buscar('clima-humedad').textContent = `${numero.format(clima.humedad)} %`;
            buscar('clima-viento').textContent = `${numero.format(clima.viento_kmh)} km/h`;
            // Construyo la URL desde un dominio HTTPS fijo y un código previamente validado.
            // La imagen pública no necesita credenciales; si falla, conservo la descripción textual.
            icono.alt = `Condiciones meteorológicas: ${clima.descripcion}`;
            icono.hidden = false;
            icono.onerror = () => { icono.hidden = true; };
            icono.src = `https://openweathermap.org/img/wn/${clima.icono}@2x.png`;
            panel.hidden = false;
            estado.textContent = 'Información meteorológica actualizada.';
        } catch (error) {
            // Publico mensajes controlados y permito reintentar sin mostrar información antigua como actual.
            estado.className = 'mensaje-error';
            estado.textContent = error.name === 'AbortError'
                ? 'La consulta excedió el tiempo de espera. Inténtalo de nuevo.'
                : error instanceof TypeError
                    ? 'No se pudo conectar. Revisa tu conexión e inténtalo de nuevo.'
                    : error.message;
        } finally {
            clearTimeout(temporizador);
            panel.setAttribute('aria-busy', 'false');
            boton.disabled = false;
            consultando = false;
        }
    }

    boton.addEventListener('click', actualizarClima);
    // Cargo automáticamente datos reales cuando defer termina de preparar el documento.
    actualizarClima();
})();
