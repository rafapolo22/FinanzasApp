import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

def obtener_conexion():
    """
    Establece una conexión con la base de datos MySQL usando variables de entorno.
    """
    configuracion = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'finanzas_db'),
        'port': int(os.getenv('DB_PORT', 3306))
    }
    
    try:
        conexion = mysql.connector.connect(**configuracion)
        if conexion.is_connected():
            return conexion
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def cerrar_conexion(conexion):
    """
    Cierra la conexión a la base de datos de manera segura.
    """
    try:
        if conexion and conexion.is_connected():
            conexion.close()
    except Error as e:
        print(f"Error al cerrar la conexión: {e}")

class ConexionDB:
    """
    Clase de contexto para manejar la conexión de forma automática usando 'with'.
    """
    def __enter__(self):
        self.conexion = obtener_conexion()
        return self.conexion

    def __exit__(self, exc_type, exc_val, exc_tb):
        cerrar_conexion(self.conexion)
