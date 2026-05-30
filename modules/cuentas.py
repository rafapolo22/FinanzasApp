from database.connection import ConexionDB
from mysql.connector import Error

def crear_cuenta(usuario_id, nombre, tipo, saldo_inicial, divisa='USD'):
    """
    Registra una nueva cuenta para el usuario.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO cuentas (usuario_id, nombre, tipo, saldo_inicial, saldo_actual, divisa)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                # El saldo actual inicia igual al inicial
                valores = (usuario_id, nombre, tipo, saldo_inicial, saldo_inicial, divisa)
                cursor.execute(query, valores)
                conexion.commit()
                print(f"Cuenta '{nombre}' creada exitosamente.")
                return True
    except Exception as e:
        print(f"ERROR DETALLADO en crear_cuenta: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def listar_cuentas(usuario_id):
    """
    Obtiene y muestra todas las cuentas de un usuario.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT * FROM cuentas WHERE usuario_id = %s"
                cursor.execute(query, (usuario_id,))
                resultados = cursor.fetchall()
                return resultados
    except Error as e:
        print(f"Error al listar las cuentas: {e}")
        return []

def obtener_cuenta(cuenta_id):
    """
    Obtiene los detalles de una cuenta por su ID.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM cuentas WHERE id = %s", (cuenta_id,))
                return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener la cuenta: {e}")
        return None

def editar_cuenta(cuenta_id, nombre, tipo, saldo_inicial, divisa):
    """
    Actualiza los datos de una cuenta. 
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    UPDATE cuentas 
                    SET nombre = %s, tipo = %s, saldo_inicial = %s, divisa = %s
                    WHERE id = %s
                """
                cursor.execute(query, (nombre, tipo, saldo_inicial, divisa, cuenta_id))
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al editar la cuenta: {e}")
        return False

def eliminar_cuenta(cuenta_id):
    """
    Elimina una cuenta de la base de datos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM cuentas WHERE id = %s", (cuenta_id,))
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al eliminar la cuenta: {e}")
        return False
