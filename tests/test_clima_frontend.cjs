// Pruebo mi script con el ejecutor nativo de Node, sin instalar dependencias ni consultar la API.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const vm = require('node:vm');
const codigo = readFileSync(join(__dirname, '../js/clima.js'), 'utf8');
// Estos datos son exclusivos de las pruebas; la aplicación siempre consulta su backend.
const clima = { ciudad: 'Quito', pais: 'EC', descripcion: 'lluvia ligera',
    humedad: 94, icono: '10n', temperatura_c: 12.53, viento_kmh: 2.02 };

function iniciar(fetch) {
    const elementos = new Map();
    const contexto = { Intl, TypeError, AbortController, setTimeout, clearTimeout, fetch,
        document: { getElementById(id) {
            if (!elementos.has(id)) elementos.set(id, {
                textContent: '', hidden: true, disabled: false,
                setAttribute(nombre, valor) { this[nombre] = valor; },
                addEventListener(nombre, funcion) { this[nombre] = funcion; }
            });
            return elementos.get(id);
        } }
    };
    vm.runInNewContext(codigo, contexto);
    return (id) => contexto.document.getElementById(id);
}
const terminar = () => new Promise((resolve) => setImmediate(resolve));

test('Cargo datos reales del endpoint relativo y formateo texto e icono', async () => {
    let llamadas = 0;
    const elemento = iniciar(async (url, opciones) => {
        llamadas++;
        assert.equal(url, '/api/clima');
        assert.equal(opciones.cache, 'no-store');
        return { ok: true, json: async () => ({ ok: true, clima }) };
    });
    await terminar();
    assert.equal(elemento('clima-ciudad').textContent, 'Quito, Ecuador');
    assert.equal(elemento('clima-temperatura').textContent, '12,53 °C');
    assert.equal(elemento('clima-viento').textContent, '2,02 km/h');
    assert.equal(elemento('clima-datos').hidden, false);
    assert.equal(elemento('clima-icono').src, 'https://openweathermap.org/img/wn/10n@2x.png');
    elemento('clima-icono').onerror();
    assert.equal(elemento('clima-icono').hidden, true);
    await elemento('actualizar-clima').click();
    assert.equal(llamadas, 2);
});

test('Impido solicitudes simultáneas y restauro el botón al terminar', async () => {
    let resolver;
    let llamadas = 0;
    const elemento = iniciar(() => { llamadas++; return new Promise((resolve) => { resolver = resolve; }); });
    assert.equal(elemento('actualizar-clima').disabled, true);
    assert.match(elemento('clima-estado').textContent, /Consultando/);
    await elemento('actualizar-clima').click();
    assert.equal(llamadas, 1);
    resolver({ ok: true, json: async () => ({ ok: true, clima }) });
    await terminar();
    assert.equal(elemento('actualizar-clima').disabled, false);
    assert.equal(elemento('clima-datos')['aria-busy'], 'false');
});

test('Manejo errores HTTP, red, timeout, JSON y contrato inválidos', async () => {
    const casos = [
        [async () => ({ ok: false, status: 429 }), /límite/],
        [async () => ({ ok: false, status: 503 }), /no está disponible/],
        [async () => { throw new TypeError('red'); }, /conexión/],
        [async () => { const error = new Error(); error.name = 'AbortError'; throw error; }, /tiempo de espera/],
        [async () => ({ ok: true, json: async () => { throw new SyntaxError(); } }), /respuesta no válida/],
        [async () => ({ ok: true, json: async () => ({ ok: false }) }), /inválidos/],
        [async () => ({ ok: true, json: async () => ({ ok: true, clima: { ...clima, icono: '../../privado' } }) }), /inválidos/]
    ];
    for (const [fetch, mensaje] of casos) {
        const elemento = iniciar(fetch);
        await terminar();
        assert.match(elemento('clima-estado').textContent, mensaje);
        assert.equal(elemento('actualizar-clima').disabled, false);
        assert.equal(elemento('clima-datos').hidden, true);
    }
});

test('Presento texto externo literalmente y oculto datos tras un fallo de actualización', async () => {
    let llamadas = 0;
    const elemento = iniciar(async () => ++llamadas === 1
        ? { ok: true, json: async () => ({ ok: true, clima: { ...clima, ciudad: '<script>texto</script>' } }) }
        : { ok: false, status: 504 });
    await terminar();
    assert.equal(elemento('clima-ciudad').textContent, '<script>texto</script>, Ecuador');
    await elemento('actualizar-clima').click();
    assert.equal(elemento('clima-datos').hidden, true);
    assert.match(elemento('clima-estado').textContent, /tiempo de espera/);
});
