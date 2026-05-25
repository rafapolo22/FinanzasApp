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
                print(f"Usuario '{nombre}' registrado exitosamente.")
                return True
    except Error as e:
        if e.errno == 1062:
            print(f"Error: El email '{email}' ya está registrado.")
        else:
            print(f"Error al registrar el usuario: {e}")
        return False

def listar_usuarios():
    """
    Obtiene y muestra todos los usuarios registrados.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = "SELECT id, nombre, email, fecha_registro FROM usuarios"
                cursor.execute(query)
                resultados = cursor.fetchall()
                
                print("\n--- Usuarios Registrados ---")
                print(f"{'ID':<5} | {'Nombre':<25} | {'Email':<30} | {'Registro':<20}")
                print("-" * 85)
                if not resultados:
                    print("No hay usuarios registrados.")
                for row in resultados:
                    print(f"{row['id']:<5} | {row['nombre']:<25} | {row['email']:<30} | {str(row['fecha_registro']):<20}")
                print("-" * 85)
                return resultados
    except Error as e:
        print(f"Error al listar los usuarios: {e}")
        return []
