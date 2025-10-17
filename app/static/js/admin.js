document.addEventListener("DOMContentLoaded", () => {
  // 🔍 Buscador de productos
  const buscador = document.getElementById('buscador');
  const tabla = document.getElementById('tabla-productos');

  buscador.addEventListener('keyup', function () {
    const texto = this.value.toLowerCase();
    const filas = tabla.getElementsByTagName('tr');
    for (let i = 1; i < filas.length; i++) {
      const nombre = filas[i].getElementsByTagName('input')[1]?.value.toLowerCase() || '';
      filas[i].style.display = nombre.includes(texto) ? '' : 'none';
    }
  });

  // ⚙️ Modal abrir/cerrar producto/usuario
  const modal = document.getElementById("modalAgregar");
  const btnAbrir = document.getElementById("abrirModal");
  const btnCerrar = document.getElementById("cerrarModal");
  const btnProducto = document.getElementById("btnProducto");
  const btnUsuario = document.getElementById("btnUsuario");
  const formProducto = document.getElementById("formProducto");
  const formUsuario = document.getElementById("formUsuario");
  const seccionUsuarios = document.getElementById("seccionUsuarios");

  btnAbrir.onclick = () => {
    modal.style.display = "block";
    formProducto.style.display = "none";
    formUsuario.style.display = "none";
    seccionUsuarios.style.display = "none";
  };

  btnCerrar.onclick = () => modal.style.display = "none";
  window.onclick = (e) => { if (e.target == modal) modal.style.display = "none"; };

  btnProducto.onclick = () => {
    formProducto.style.display = "block";
    formUsuario.style.display = "none";
    seccionUsuarios.style.display = "none";
  };

  btnUsuario.onclick = () => {
    formUsuario.style.display = "block";
    formProducto.style.display = "none";
    seccionUsuarios.style.display = "block"; // ✅ esto activa la sección completa
  };

  // 📦 Modal abrir/cerrar pedidos
  const btnPedidos = document.getElementById("verPedidos");
  const modalPedidos = document.getElementById("modalPedidos");
  const cerrarPedidos = document.getElementById("cerrarPedidos");
  const contenidoPedidos = document.getElementById("contenidoPedidos");

  btnPedidos.onclick = async () => {
    modalPedidos.style.display = "block";
    contenidoPedidos.innerHTML = "<p>Cargando pedidos...</p>";

    try {
      const res = await fetch("/pedidos");
      const pedidos = await res.json();

      if (pedidos.length === 0) {
        contenidoPedidos.innerHTML = "<p>No hay pedidos registrados.</p>";
      } else {
        contenidoPedidos.innerHTML = pedidos
          .filter(p => p.estado !== 'listo')
          .map(p => `
            <div class="pedido" data-id="${p._id}" style="border-bottom:1px solid #444; padding:10px; margin-bottom:10px;">
              <strong>🧑 Cliente:</strong> ${p.cliente || 'N/A'}<br>
              <strong>📞 Teléfono:</strong> ${p.telefono || 'N/A'}<br>
              <strong>📍 Dirección:</strong> ${p.direccion || 'N/A'}<br>
              <strong>🛒 Productos:</strong> ${
                Array.isArray(p.productos)
                  ? p.productos.map(prod => `${prod.nombre} x${prod.cantidad}`).join(', ')
                  : 'N/A'
              }<br>
              <strong>📅 Fecha:</strong> ${p.fecha || 'Sin fecha registrada'}<br>
              <strong>💰 Total:</strong> $${p.total || '0.00'}<br>
              <strong>📦 Estado:</strong> ${p.estado || 'pendiente'}<br>
              <button class="btn-listo" data-id="${p._id}" style="
                margin-top: 10px;
                background-color: #00cc66;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
              ">✅ Listo</button>
            </div>
          `).join('');
      }
    } catch (err) {
      contenidoPedidos.innerHTML = "<p>Error al cargar pedidos.</p>";
      console.error(err);
    }
  };

  // ✅ Marcar pedido como listo
  contenidoPedidos.addEventListener('click', async (e) => {
    if (e.target.classList.contains('btn-listo')) {
      const pedidoId = e.target.getAttribute('data-id');
      try {
        const res = await fetch(`/marcar_listo/${pedidoId}`, {
          method: 'POST'
        });
        const data = await res.json();
        if (data.success) {
          const pedidoDiv = e.target.closest('.pedido');
          if (pedidoDiv) pedidoDiv.remove();
        } else {
          alert("Error al actualizar el pedido.");
        }
      } catch (err) {
        console.error("Error al marcar como listo:", err);
        alert("Error de conexión al servidor.");
      }
    }
  });

  cerrarPedidos.onclick = () => modalPedidos.style.display = "none";
  window.onclick = (e) => {
    if (e.target === modalPedidos) {
      modalPedidos.style.display = "none";
    }
  };

  // 💰 Ventas botón
  const btnVentas = document.getElementById("verVentas");
  const modalVentas = document.getElementById("modalVentas");
  const cerrarVentas = document.getElementById("cerrarVentas");
  const contenidoVentas = document.getElementById("contenidoVentas");

  btnVentas.onclick = async () => {
    modalVentas.style.display = "block";
    contenidoVentas.innerHTML = "<p>Cargando pedidos...</p>";

    try {
      const res = await fetch("/ventas_hoy");
      const data = await res.json();

      if (data.success && data.pedidos.length > 0) {
        const lista = data.pedidos.map(p => `
          <div class="pedido" data-id="${p._id}" style="border-bottom:1px solid #444; padding:10px; margin-bottom:10px;">
            <strong>🧑 Cliente:</strong> ${p.cliente || 'N/A'}<br>
            <strong>📞 Teléfono:</strong> ${p.telefono || 'N/A'}<br>
            <strong>📍 Dirección:</strong> ${p.direccion || 'N/A'}<br>
            <strong>💰 Total:</strong> $${p.total}<br>
            <strong>🛒 Productos:</strong> ${
              Array.isArray(p.productos)
                ? p.productos.map(prod => `${prod.nombre} x${prod.cantidad}`).join(', ')
                : 'N/A'
            }<br>
            <strong>📅 Fecha:</strong> ${p.fecha || 'Sin fecha registrada'}
          </div>
        `).join('');

        contenidoVentas.innerHTML = lista;
      } else {
        contenidoVentas.innerHTML = "<p>No hay pedidos listos.</p>";
      }
    } catch (err) {
      contenidoVentas.innerHTML = "<p>Error al cargar pedidos.</p>";
      console.error(err);
    }
  };

  cerrarVentas.onclick = () => modalVentas.style.display = "none";
  window.onclick = (e) => {
    if (e.target === modalVentas) {
      modalVentas.style.display = "none";
    }
  };
});