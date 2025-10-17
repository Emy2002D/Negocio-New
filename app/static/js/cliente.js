let carrito = {};

// Toggle del carrito al hacer click en el botón
const botonCarrito = document.getElementById('boton-carrito');
const contenidoCarrito = document.getElementById('contenido-carrito');
const contadorCarrito = document.getElementById('contador-carrito');

botonCarrito.addEventListener('click', () => {
    contenidoCarrito.style.display = contenidoCarrito.style.display === 'block' ? 'none' : 'block';
});

// Agregar productos al carrito
document.querySelectorAll('.agregar-carrito').forEach(btn => {
    btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const nombre = btn.dataset.nombre;
        const precio = parseFloat(btn.dataset.precio);

        if (carrito[id]) {
            carrito[id].cantidad += 1;
        } else {
            carrito[id] = {nombre: nombre, precio: precio, cantidad: 1};
        }

        actualizarCarrito();
        contenidoCarrito.style.display = 'block';
    });
});

// Actualizar contenido del carrito
function actualizarCarrito() {
    const lista = document.getElementById('lista-carrito');
    lista.innerHTML = '';
    let total = 0;
    let contador = 0;
    for (let key in carrito) {
        const item = carrito[key];
        total += item.precio * item.cantidad;
        contador += item.cantidad;
        lista.innerHTML += `<li>${item.nombre} x ${item.cantidad} - $${(item.precio * item.cantidad).toFixed(2)}</li>`;
    }
    document.getElementById('total-carrito').innerText = total.toFixed(2);
    contadorCarrito.innerText = contador;
}

// Guardar carrito en sesión y redirigir al formulario
document.getElementById('btn-finalizar').addEventListener('click', () => {
    fetch("/guardar_carrito_temporal", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(carrito)
    }).then(() => window.location.href = "/finalizar_pedido");
});
