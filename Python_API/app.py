from flask import Flask, jsonify, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS  # 🔹 Importar CORS
from sqlalchemy import text
import os

# Configurar la app Flask
app = Flask(__name__)
CORS(app)  # 🔹 Habilitar CORS en toda la API

# Configuración de la base de datos MySQL en XAMPP
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/miapi_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelo de la base de datos
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

# Ruta para obtener el JSON de Swagger
@app.route('/swagger.json')
def swagger_json():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "swagger.json")

# Configurar Swagger UI
SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

# Endpoint para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        usuarios = Usuario.query.all()
        if not usuarios:
            return jsonify({"mensaje": "No hay usuarios en la base de datos"}), 404
        resultado = [{'id': u.id, 'nombre': u.nombre, 'correo': u.correo,'password': u.password} for u in usuarios]
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Agregar un usuario
@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    try:
        data = request.json
        nuevo_usuario = Usuario(nombre=data['nombre'], correo=data['correo'], password=data['password'])
        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario agregado correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Actualizar un usuario por ID
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        data = request.json
        usuario.nombre = data.get('nombre', usuario.nombre)
        usuario.correo = data.get('correo', usuario.correo)
        usuario.password = data.get('password', usuario.password)

        db.session.commit()
        return jsonify({"mensaje": "Usuario actualizado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Eliminar un usuario por ID
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if not usuario:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Iniciar la app
if __name__ == '__main__':
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))  # Prueba de conexión corregida
            print("✅ Conexión a MySQL exitosa")
        except Exception as e:
            print(f"❌ Error en la conexión a MySQL: {e}")

    app.run(debug=True)

