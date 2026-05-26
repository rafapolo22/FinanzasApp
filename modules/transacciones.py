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
                return True
    except Error as e:
        print(f"Error al agregar la transacción: {e}")
        return False

def obtener_transaccion(transaccion_id):
    """
    Obtiene los detalles de una transacción por su ID.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM transacciones WHERE id = %s", (transaccion_id,))
                return cursor.fetchone()
    except Error as e:
        print(f"Error al obtener la transacción: {e}")
        return None

def editar_transaccion(transaccion_id, cuenta_id, categoria_id, monto, tipo, fecha, descripcion):
    """
    Actualiza una transacción y ajusta los saldos correspondientes.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                
                # 1. Obtener la transacción original para revertir su efecto
                cursor.execute("SELECT * FROM transacciones WHERE id = %s", (transaccion_id,))
                original = cursor.fetchone()
                if not original:
                    return False
                
                # 2. Revertir saldo original
                if original['tipo'] == 'Ingreso':
                    cursor.execute("UPDATE cuentas SET saldo_actual = saldo_actual - %s WHERE id = %s", (original['monto'], original['cuenta_id']))
                else:
                    cursor.execute("UPDATE cuentas SET saldo_actual = saldo_actual + %s WHERE id = %s", (original['monto'], original['cuenta_id']))
                
                # 3. Actualizar la transacción
                query = """
                    UPDATE transacciones 
                    SET cuenta_id = %s, categoria_id = %s, monto = %s, tipo = %s, fecha = %s, descripcion = %s
                    WHERE id = %s
                """
                cursor.execute(query, (cuenta_id, categoria_id, monto, tipo, fecha, descripcion, transaccion_id))
                
                # 4. Aplicar nuevo saldo
                if tipo == 'Ingreso':
                    cursor.execute("UPDATE cuentas SET saldo_actual = saldo_actual + %s WHERE id = %s", (monto, cuenta_id))
                else:
                    cursor.execute("UPDATE cuentas SET saldo_actual = saldo_actual - %s WHERE id = %s", (monto, cuenta_id))
                
                conexion.commit()
                return True
    except Error as e:
        print(f"Error al editar la transacción: {e}")
        return False

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
                    return True
                return False
    except Error as e:
        print(f"Error al eliminar la transacción: {e}")
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
