from database.connection import ConexionDB
from mysql.connector import Error

def balance_mensual(usuario_id, mes, anio):
    """
    Calcula el balance total (Ingresos - Gastos) de un mes específico.
    Retorna un diccionario con los resultados, siempre inicializado en 0.0.
    """
    default = {'ingresos': 0.0, 'gastos': 0.0, 'balance': 0.0}
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT 
                        SUM(CASE WHEN tipo = 'Ingreso' THEN monto ELSE 0 END) as ingresos,
                        SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END) as gastos
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    WHERE c.usuario_id = %s AND MONTH(t.fecha) = %s AND YEAR(t.fecha) = %s
                """
                cursor.execute(query, (usuario_id, mes, anio))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return default

                ingresos = float(resultado['ingresos'] or 0.0)
                gastos = float(resultado['gastos'] or 0.0)
                return {
                    'ingresos': ingresos,
                    'gastos': gastos,
                    'balance': ingresos - gastos
                }
            return default
    except Error as e:
        print(f"Error al generar balance mensual: {e}")
        return default

def gastos_por_categoria(usuario_id, mes, anio):
    """
    Retorna el total de gastos agrupados por categoría para un mes específico.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT cat.nombre as categoria, SUM(t.monto) as total
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    JOIN categorias cat ON t.categoria_id = cat.id
                    WHERE c.usuario_id = %s AND t.tipo = 'Gasto' 
                      AND MONTH(t.fecha) = %s AND YEAR(t.fecha) = %s
                    GROUP BY cat.id
                    ORDER BY total DESC
                """
                cursor.execute(query, (usuario_id, mes, anio))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al generar gastos por categoría: {e}")
        return []

def top_gastos(usuario_id, limite=5):
    """
    Retorna las transacciones de gasto más altas del usuario.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT t.fecha, cat.nombre as categoria, t.monto, t.descripcion
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    JOIN categorias cat ON t.categoria_id = cat.id
                    WHERE c.usuario_id = %s AND t.tipo = 'Gasto'
                    ORDER BY t.monto DESC
                    LIMIT %s
                """
                cursor.execute(query, (usuario_id, limite))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al obtener top de gastos: {e}")
        return []

def ingresos_gastos_6_meses(usuario_id):
    """
    Retorna los ingresos y gastos de los últimos 6 meses.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT 
                        DATE_FORMAT(t.fecha, '%Y-%m') as mes,
                        SUM(CASE WHEN t.tipo = 'Ingreso' THEN t.monto ELSE 0 END) as ingresos,
                        SUM(CASE WHEN t.tipo = 'Gasto' THEN t.monto ELSE 0 END) as gastos
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    WHERE c.usuario_id = %s AND t.fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                    GROUP BY mes
                    ORDER BY mes ASC
                """
                cursor.execute(query, (usuario_id,))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al generar reporte de 6 meses: {e}")
        return []

def resumen_anual(usuario_id, anio):
    """
    Retorna un resumen mes a mes de ingresos y gastos para un año determinado.
    """
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                query = """
                    SELECT 
                        MONTH(t.fecha) as mes,
                        SUM(CASE WHEN tipo = 'Ingreso' THEN monto ELSE 0 END) as ingresos,
                        SUM(CASE WHEN tipo = 'Gasto' THEN monto ELSE 0 END) as gastos
                    FROM transacciones t
                    JOIN cuentas c ON t.cuenta_id = c.id
                    WHERE c.usuario_id = %s AND YEAR(t.fecha) = %s
                    GROUP BY MONTH(t.fecha)
                    ORDER BY mes ASC
                """
                cursor.execute(query, (usuario_id, anio))
                return cursor.fetchall()
    except Error as e:
        print(f"Error al generar resumen anual: {e}")
        return []

