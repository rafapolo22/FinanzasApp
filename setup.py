import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
load_dotenv()

def inicializar_base_datos():
    """
    Lee y ejecuta el archivo schema.sql para inicializar la base de datos
    con todas las tablas y categorías por defecto.
    """
    # Configuración de conexión (inicialmente sin base de datos para crearla si no existe)
    configuracion = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '3306')
    }
    
    conexion = None
    try:
        print(f"Conectando al servidor MySQL en {configuracion['host']}...")
        conexion = mysql.connector.connect(**configuracion)
        
        if conexion.is_connected():
            cursor = conexion.cursor()
            
            # Leer el archivo schema.sql
            ruta_sql = os.path.join('database', 'schema.sql')
            if not os.path.exists(ruta_sql):
                print(f"Error: El archivo {ruta_sql} no existe.")
                return

            print(f"Leyendo {ruta_sql}...")
            with open(ruta_sql, 'r', encoding='utf-8') as archivo:
                sql_script = archivo.read()

            # Ejecutar el script SQL (dividido por sentencias)
            print("Ejecutando script de inicialización...")
            sentencias = sql_script.split(';')
            
            for sentencia in sentencias:
                sentencia_limpia = sentencia.strip()
                if sentencia_limpia:
                    cursor.execute(sentencia_limpia)
            
            conexion.commit()
            print(f"Éxito: La base de datos '{os.getenv('DB_NAME', 'finanzas_db')}' ha sido inicializada.")
            
    except Error as e:
        print(f"Error al inicializar la base de datos: {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("Conexión cerrada.")

if __name__ == "__main__":
    inicializar_base_datos()
