from database.connection import ConexionDB
from mysql.connector import Error

def registrar_usuario(nombre, email, contrasena):
    """
    Registra un nuevo usuario en la base de datos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO usuarios (nombre, email, contrasena)
                    VALUES (%s, %s, %s)
                """
                valores = (nombre, email, contrasena)
                cursor.execute(query, valores)
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al registrar el usuario: {e}")
        return False

def listar_usuarios():
    """
    Obtiene todos los usuarios registrados.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT id, nombre, email, fecha_registro FROM usuarios"
                cursor.execute(query)
                return cursor.fetchall()
    except Error as e:
        print(f"Error al listar los usuarios: {e}")
        return []

def obtener_usuario(usuario_id):
    """
    Obtiene los detalles de un usuario por su ID.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT id, nombre, email, fecha_registro, contrasena FROM usuarios WHERE id = %s", (usuario_id,))
                return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener el usuario: {e}")
        return None

def cambiar_contrasena(usuario_id, nueva_contrasena):
    """
    Actualiza la contraseña de un usuario.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = "UPDATE usuarios SET contrasena = %s WHERE id = %s"
                cursor.execute(query, (nueva_contrasena, usuario_id))
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al cambiar la contraseña: {e}")
        return False
