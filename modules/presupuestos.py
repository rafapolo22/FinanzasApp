from database.connection import ConexionDB
from mysql.connector import Error
from datetime import datetime

def crear_presupuesto(usuario_id, categoria_id, monto_limite, periodo, fecha_inicio, fecha_fin):
    """
    Registra un nuevo presupuesto para una categoría y periodo específicos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO presupuestos (usuario_id, categoria_id, monto_limite, periodo, fecha_inicio, fecha_fin)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (usuario_id, categoria_id, monto_limite, periodo, fecha_inicio, fecha_fin)
                cursor.execute(query, valores)
                conexion.commit()
                print("Presupuesto creado exitosamente.")
                return True
    except Error as e:
        print(f"Error al crear el presupuesto: {e}")
        return False

def listar_presupuestos(usuario_id):
    """
    Lista todos los presupuestos activos de un usuario.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT p.*, c.nombre as nombre_categoria 
                    FROM presupuestos p
                    JOIN categorias c ON p.categoria_id = c.id
                    WHERE p.usuario_id = %s
                """
                cursor.execute(query, (usuario_id,))
                resultados = cursor.fetchall()
                return resultados
    except Error as e:
        print(f"Error al listar presupuestos: {e}")
        return []

def obtener_presupuesto(presupuesto_id):
    """
    Obtiene los detalles de un presupuesto por su ID.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM presupuestos WHERE id = %s", (presupuesto_id,))
                return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener el presupuesto: {e}")
        return None

def editar_presupuesto(presupuesto_id, categoria_id, monto_limite, periodo, fecha_inicio, fecha_fin):
    """
    Actualiza los datos de un presupuesto.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    UPDATE presupuestos 
                    SET categoria_id = %s, monto_limite = %s, periodo = %s, fecha_inicio = %s, fecha_fin = %s
                    WHERE id = %s
                """
                cursor.execute(query, (categoria_id, monto_limite, periodo, fecha_inicio, fecha_fin, presupuesto_id))
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al editar el presupuesto: {e}")
        return False

def eliminar_presupuesto(presupuesto_id):
    """
    Elimina un presupuesto de la base de datos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("DELETE FROM presupuestos WHERE id = %s", (presupuesto_id,))
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al eliminar el presupuesto: {e}")
        return False

def verificar_alertas(usuario_id):
    """
    Compara el gasto real del mes actual contra los presupuestos establecidos.
    Retorna una lista de diccionarios con las alertas encontradas.
    """
    alertas = []
    try:
        ahora = datetime.now()
        mes_actual = ahora.month
        anio_actual = ahora.year

        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT 
                        p.categoria_id,
                        cat.nombre as nombre_categoria,
                        p.monto_limite,
                        COALESCE(SUM(t.monto), 0) as gasto_real
                    FROM presupuestos p
                    JOIN categorias cat ON p.categoria_id = cat.id
                    LEFT JOIN transacciones t ON p.categoria_id = t.categoria_id 
                        AND MONTH(t.fecha) = %s 
                        AND YEAR(t.fecha) = %s
                        AND t.tipo = 'Gasto'
                    WHERE p.usuario_id = %s
                    GROUP BY p.id
                """
                cursor.execute(query, (mes_actual, anio_actual, usuario_id))
                resultados = cursor.fetchall()
                
                for row in resultados:
                    limite = float(row['monto_limite'])
                    gasto = float(row['gasto_real'])
                    porcentaje = (gasto / limite) * 100 if limite > 0 else 0
                    
                    if porcentaje >= 80:
                        estado = "¡CRÍTICO!" if porcentaje >= 100 else "ADVERTENCIA"
                        alertas.append({
                            'categoria': row['nombre_categoria'],
                            'gasto_real': gasto,
                            'limite': limite,
                            'porcentaje': porcentaje,
                            'estado': estado
                        })
                return alertas
    except Error as e:
        print(f"Error al verificar alertas: {e}")
        return []
    except Exception as ex:
        print(f"Error inesperado: {ex}")
        return []
