// Espero a que el documento esté listo antes de seleccionar las tarjetas.
$(document).ready(function () {
    // Busco los botones dentro de Productos y registro su evento de clic.
    $('#productos').find('.boton-detalles').on('click', function () {
        const boton = $(this);
        // Localizo únicamente el contenedor identificado por el botón pulsado.
        const detalles = $('#productos').find('#' + boton.attr('aria-controls'));

        // Ignoro clics durante el breve efecto para evitar animaciones acumuladas.
        if (detalles.is(':animated')) {
            return;
        }

        const expandido = boton.attr('aria-expanded') === 'true';
        // Alterno la visibilidad con un deslizamiento sencillo.
        detalles.slideToggle(200);
        boton.attr('aria-expanded', !expandido);

        // Actualizo el texto del botón de acuerdo con el estado seleccionado.
        if (expandido) {
            boton.text('Ver más información');
        } else {
            boton.text('Ocultar información');
        }
    });
});
