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
    except Error as e:
        print(f"Error al crear la cuenta: {e}")
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
                
                print("\n--- Mis Cuentas ---")
                print(f"{'ID':<5} | {'Nombre':<20} | {'Tipo':<15} | {'Saldo Actual':>12} | {'Divisa':<5}")
                print("-" * 65)
                if not resultados:
                    print("No tienes cuentas registradas.")
                for row in resultados:
                    print(f"{row['id']:<5} | {row['nombre']:<20} | {row['tipo']:<15} | {row['saldo_actual']:>12.2f} | {row['divisa']:<5}")
                print("-" * 65)
                return resultados
    except Error as e:
        print(f"Error al listar las cuentas: {e}")
        return []
