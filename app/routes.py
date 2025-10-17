from flask import Blueprint, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

main = Blueprint('main', __name__)

# 🔗 Conexión a MongoDB Atlas
client = MongoClient("mongodb+srv://Emiliano_2002:Emy200272D@cluster0.g38lrmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['mi_base']
usuarios = db['usuarios']
productos = db['productos']
pedidos = db['pedidos'] 

# ✅ Verificación de conexión
try:
    client.admin.command('ping')
    print("✅ Conexión a MongoDB exitosa")
except Exception as e:
    print("❌ Error al conectar a MongoDB:", e)

# 🔐 Página de login
@main.route('/')
def login():
    return render_template('login.html')

# 🔑 Validación de usuario
@main.route('/ingresar', methods=['POST'])
def ingresar():
    usuario = request.form['usuario']
    contraseña = request.form['contraseña']

    user = db.usuarios.find_one({'usuario': usuario, 'contraseña': contraseña})

    if user:
        session['usuario'] = usuario
        session['rol'] = user.get('rol', 'cliente')

        if session['rol'] == 'admin':
            return redirect(url_for('main.dashboard_admin'))
        elif session['rol'] == 'trabajador':
            return redirect(url_for('main.dashboard_trabajador'))
        else:
            return redirect(url_for('main.dashboard_cliente'))

    return "Usuario o contraseña incorrectos"

# 🆕 Agregar nuevo producto desde el panel admin
@main.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if session.get('rol') != 'admin':
        return redirect(url_for('main.login'))

    nombre = request.form['nuevo_nombre']
    precio = float(request.form['nuevo_precio'])
    imagen = request.form['nuevo_imagen']
    disponible = request.form.get('nuevo_disponible') == 'on'

    nuevo = {
        "nombre": nombre,
        "precio": precio,
        "imagen": imagen,
        "disponible": disponible
    }

    productos.insert_one(nuevo)
    return redirect(url_for('main.dashboard_admin'))

# 🛠 Panel administrador con edición masiva y eliminación
@main.route('/admin', methods=['GET', 'POST'])
def dashboard_admin():
    if session.get('rol') != 'admin':
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        total = int(request.form['total'])
        for i in range(total):
            id = request.form[f'id_{i}']
            nombre = request.form[f'nombre_{i}']
            precio = float(request.form[f'precio_{i}'])
            disponible = request.form.get(f'disponible_{i}') == 'on'
            imagen = request.form[f'imagen_{i}']

            productos.update_one(
                {'_id': ObjectId(id)},
                {'$set': {
                    'nombre': nombre,
                    'precio': precio,
                    'disponible': disponible,
                    'imagen': imagen
                }}
            )
        return redirect(url_for('main.dashboard_admin'))

    lista = list(productos.find())
    return render_template('dashboard_admin.html', productos=lista)

# 🗑 Eliminar producto
@main.route('/eliminar_producto/<id>')
def eliminar_producto(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('main.login'))
    productos.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('main.dashboard_admin'))

# 👤 Panel cliente (requiere login)
@main.route('/cliente')
def dashboard_cliente():
    if session.get('rol') == 'cliente':
        disponibles = list(productos.find({'disponible': True}))
        return render_template('dashboard_cliente.html', productos=disponibles)
    return redirect(url_for('main.login'))

# 🌐 Galería pública sin login
@main.route('/galeria')
def galeria_publica():
    disponibles = list(productos.find({'disponible': True}))
    return render_template('dashboard_cliente.html', productos=disponibles)

# 🧪 Ruta de prueba
@main.route('/testmongo')
def test_mongo():
    try:
        resultado = usuarios.find_one()
        return f"Conectado. Usuario encontrado: {resultado['usuario']}" if resultado else "Conectado, pero no hay usuarios."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

@main.route('/guardar_carrito_temporal', methods=['POST'])
def guardar_carrito_temporal():
    carrito = request.get_json()
    session['carrito'] = carrito
    return '', 200

from datetime import datetime

@main.route('/finalizar_pedido', methods=['GET', 'POST'])
def finalizar_pedido():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        carrito = session.get('carrito', {})

        if not carrito:
            return redirect(url_for('main.dashboard_cliente'))

        productos_pedido = []
        total = 0
        for pid, item in carrito.items():
            productos_pedido.append({
                'producto_id': pid,
                'nombre': item['nombre'],
                'precio': item['precio'],
                'cantidad': item['cantidad']
            })
            total += item['precio'] * item['cantidad']

        db['pedidos'].insert_one({
            'cliente': nombre,
            'telefono': telefono,
            'direccion': direccion,
            'productos': productos_pedido,
            'total': total,
            'estado': 'pendiente',
            'fecha': datetime.now()  # ← aquí se guarda la fecha actual
        })

        session.pop('carrito', None)
        return "✅ Pedido realizado con éxito"

    return render_template('finalizar_pedido.html')

from flask import jsonify

#lista de pedidos
@main.route('/pedidos')
def obtener_pedidos():
    try:
        pedidos = list(db['pedidos'].find())
        for p in pedidos:
            p['_id'] = str(p['_id'])  # Convertir ObjectId a string
        return jsonify(pedidos)
    except Exception as e:
        print("❌ Error al obtener pedidos:", e)
        return jsonify({"error": "No se pudieron cargar los pedidos"}), 500

#lista de productos update
@main.route('/marcar_listo/<pedido_id>', methods=['POST'])
def marcar_pedido_listo(pedido_id):
    try:
        db['pedidos'].update_one(
            {'_id': ObjectId(pedido_id)},
            {'$set': {'estado': 'listo'}}
        )
        return jsonify({'success': True})
    except Exception as e:
        print("❌ Error al marcar pedido como listo:", e)
        return jsonify({'success': False, 'error': str(e)}), 500

## Trabajador

@main.route('/dashboard_trabajador')
def dashboard_trabajador():
    if session.get("rol") != "trabajador":
        return redirect(url_for("main.login"))
    lista_productos = list(productos.find())
    lista_pedidos = list(pedidos.find({"estado": {"$ne": "listo"}}))  # ← solo pedidos no listos
    return render_template('dashboard_trabajador.html', productos=lista_productos, pedidos=lista_pedidos)

@main.route("/agregar_producto_trabajador", methods=["POST"])
def agregar_producto_trabajador():
    if session.get("rol") != "trabajador":
        return redirect(url_for("main.login"))

    nuevo_producto = {
        "nombre": request.form["nombre"],
        "precio": float(request.form["precio"]),
        "imagen": request.form["imagen"],
        "disponible": True
    }
    productos.insert_one(nuevo_producto)
    return redirect(url_for("main.dashboard_trabajador"))

@main.route("/actualizar_producto_trabajador/<id>", methods=["POST"])
def actualizar_producto_trabajador(id):
    if session.get("rol") != "trabajador":
        return redirect(url_for("main.login"))

    productos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "nombre": request.form["nombre"],
            "precio": float(request.form["precio"]),
            "imagen": request.form["imagen"],
            "disponible": "disponible" in request.form
        }}
    )
    return redirect(url_for("main.dashboard_trabajador"))


@main.route("/pedido_listo/<id>", methods=["POST"])
def pedido_listo(id):
    if session.get("rol") != "trabajador":
        return redirect(url_for("main.login"))

    pedidos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"estado": "listo"}}
    )
    return redirect(url_for("main.dashboard_trabajador"))

@main.route("/ventas_hoy")
def ventas_hoy():
    pedidos_listos = list(pedidos.find({"estado": "listo"}))

    pedidos_serializados = []
    for p in pedidos_listos:
        pedidos_serializados.append({
            "_id": str(p["_id"]),
            "cliente": p.get("cliente", "N/A"),
            "telefono": p.get("telefono", "N/A"),
            "direccion": p.get("direccion", "N/A"),
            "total": p.get("total", 0),
            "productos": p.get("productos", []),
            "fecha": p.get("fecha", datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({
        "success": True,
        "pedidos": pedidos_serializados
    })

##admin Agregar usuarios.
@main.route("/agregar_admin", methods=["POST"])
def registrar_admin():  # ✅ nombre único
    usuario = request.form.get("admin_usuario")
    contraseña = request.form.get("admin_contraseña")
    rol = request.form.get("admin_rol")

    if not usuario or not contraseña or not rol:
        return "Faltan datos", 400

    nuevo_usuario = {
        "usuario": usuario,
        "contraseña": contraseña,
        "rol": rol
    }

    usuarios.insert_one(nuevo_usuario)
    return redirect("/admin")
###### actualizar y borrar users

@main.route('/actualizar_usuarios', methods=['POST'])
def actualizar_usuarios():
    total = int(request.form['total'])
    for i in range(total):
        id = request.form[f'id_{i}']
        usuario = request.form[f'usuario_{i}']
        contraseña = request.form[f'contraseña_{i}']
        rol = request.form[f'rol_{i}']

        usuarios.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'usuario': usuario,
                'contraseña': contraseña,
                'rol': rol
            }}
        )
    return redirect(url_for('main.dashboard_admin'))

# 🗑 Eliminar usuario desde la tabla
@main.route('/eliminar_usuario/<id>')
def eliminar_usuario(id):
    usuarios.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('main.dashboard_admin'))

