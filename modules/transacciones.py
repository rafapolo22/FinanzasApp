from database.connection import ConexionDB
from mysql.connector import Error

def agregar_transaccion(cuenta_id, categoria_id, monto, tipo, fecha, descripcion):
    """
    Registra una nueva transacción en la base de datos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor()
                query = """
                    INSERT INTO transacciones (cuenta_id, categoria_id, monto, tipo, fecha, descripcion)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (cuenta_id, categoria_id, monto, tipo, fecha, descripcion)
                cursor.execute(query, valores)
                
                # Actualizar el saldo de la cuenta
                if tipo == 'Ingreso':
                    query_saldo = "UPDATE cuentas SET saldo_actual = saldo_actual + %s WHERE id = %s"
                else:
                    query_saldo = "UPDATE cuentas SET saldo_actual = saldo_actual - %s WHERE id = %s"
                
                cursor.execute(query_saldo, (monto, cuenta_id))
                
                conexion.commit()
                print("Transacción agregada exitosamente y saldo actualizado.")
                return True
    except Error as e:
        print(f"Error al agregar la transacción: {e}")
        return False

def listar_transacciones(usuario_id):
    """
    Obtiene todas las transacciones de un usuario específico.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT t.*, c.nombre as nombre_cuenta, cat.nombre as nombre_categoria 
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    JOIN categorias cat ON t.categoria_id = cat.id
                    WHERE c.usuario_id = %s
                    ORDER BY t.fecha DESC
                """
                cursor.execute(query, (usuario_id,))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al listar transacciones: {e}")
        return []

def listar_por_mes(usuario_id, mes, anio):
    """
    Obtiene las transacciones de un usuario para un mes y año específicos.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT t.*, c.nombre as nombre_cuenta, cat.nombre as nombre_categoria 
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    JOIN categorias cat ON t.categoria_id = cat.id
                    WHERE c.usuario_id = %s AND MONTH(t.fecha) = %s AND YEAR(t.fecha) = %s
                    ORDER BY t.fecha DESC
                """
                cursor.execute(query, (usuario_id, mes, anio))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al listar transacciones por mes: {e}")
        return []

def listar_por_categoria(usuario_id, categoria_id):
    """
    Obtiene las transacciones de un usuario filtradas por una categoría.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT t.*, c.nombre as nombre_cuenta, cat.nombre as nombre_categoria 
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    JOIN categorias cat ON t.categoria_id = cat.id
                    WHERE c.usuario_id = %s AND t.categoria_id = %s
                    ORDER BY t.fecha DESC
                """
                cursor.execute(query, (usuario_id, categoria_id))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al listar transacciones por categoría: {e}")
        return []

def eliminar_transaccion(transaccion_id):
    """
    Elimina una transacción y revierte su impacto en el saldo de la cuenta.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                
                # Obtener datos de la transacción antes de eliminarla para ajustar el saldo
                cursor.execute("SELECT cuenta_id, monto, tipo FROM transacciones WHERE id = %s", (transaccion_id,))
                transaccion = cursor.fetchone()
                
                if transaccion:
                    # Revertir el saldo
                    if transaccion['tipo'] == 'Ingreso':
                        query_saldo = "UPDATE cuentas SET saldo_actual = saldo_actual - %s WHERE id = %s"
                    else:
                        query_saldo = "UPDATE cuentas SET saldo_actual = saldo_actual + %s WHERE id = %s"
                    
                    cursor.execute(query_saldo, (transaccion['monto'], transaccion['cuenta_id']))
                    
                    # Eliminar la transacción
                    cursor.execute("DELETE FROM transacciones WHERE id = %s", (transaccion_id,))
                    
                    conexion.commit()
                    print("Transacción eliminada y saldo revertido.")
                    return True
                else:
                    print("Transacción no encontrada.")
                    return False
    except Error as e:
        print(f"Error al eliminar la transacción: {e}")
        return False
