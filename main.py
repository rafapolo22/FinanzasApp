import os
import sys
from database.connection import ConexionDB, obtener_conexion
from modules import transacciones, reportes, presupuestos, cuentas, usuarios
from mysql.connector import Error

def inicializar_base_de_datos():
    """
    Crea la base de datos y las tablas si no existen leyendo el archivo schema.sql.
    """
    print("Iniciando sistema...")
    try:
        # Intentamos conectar sin especificar base de datos primero para crearla
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        ruta_sql = os.path.join('database', 'schema.sql')
        if not os.path.exists(ruta_sql):
            print(f"Error: No se encontró el archivo {ruta_sql}")
            return False

        with open(ruta_sql, 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')

        for command in sql_commands:
            if command.strip():
                cursor.execute(command)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Base de datos inicializada correctamente.")
        return True
    except Error as e:
        print(f"Error crítico al inicializar la base de datos: {e}")
        return False
    except Exception as ex:
        print(f"Error inesperado: {ex}")
        return False

def menu_transacciones(usuario_id):
    while True:
        print("\n--- GESTIÓN DE TRANSACCIONES ---")
        print("1. Agregar Transacción")
        print("2. Listar Todas las Transacciones")
        print("3. Eliminar Transacción")
        print("0. Volver al Menú Principal")
        
        opcion = input("Seleccione una opción: ")
        
        try:
            if opcion == '1':
                cuenta_id = int(input("ID de la Cuenta: "))
                categoria_id = int(input("ID de la Categoría: "))
                monto = float(input("Monto: "))
                tipo = input("Tipo (Ingreso/Gasto): ")
                fecha = input("Fecha (AAAA-MM-DD): ")
                desc = input("Descripción: ")
                transacciones.agregar_transaccion(cuenta_id, categoria_id, monto, tipo, fecha, desc)
            elif opcion == '2':
                lista = transacciones.listar_transacciones(usuario_id)
                print(f"\n{'ID':<5} | {'Fecha':<12} | {'Categoría':<15} | {'Monto':>10} | {'Tipo':<10}")
                print("-" * 60)
                for t in lista:
                    print(f"{t['id']:<5} | {str(t['fecha']):<12} | {t['nombre_categoria']:<15} | {t['monto']:>10.2f} | {t['tipo']:<10}")
            elif opcion == '3':
                tid = int(input("ID de la transacción a eliminar: "))
                transacciones.eliminar_transaccion(tid)
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
        except ValueError:
            print("Error: Por favor ingrese datos válidos.")
        except Exception as e:
            print(f"Error: {e}")

def menu_reportes(usuario_id):
    while True:
        print("\n--- REPORTES Y ANÁLISIS ---")
        print("1. Balance Mensual")
        print("2. Gastos por Categoría")
        print("3. Top 5 Gastos")
        print("4. Resumen Anual")
        print("0. Volver al Menú Principal")
        
        opcion = input("Seleccione una opción: ")
        
        try:
            if opcion == '1':
                mes = int(input("Mes (1-12): "))
                anio = int(input("Año: "))
                reportes.balance_mensual(usuario_id, mes, anio)
            elif opcion == '2':
                mes = int(input("Mes (1-12): "))
                anio = int(input("Año: "))
                reportes.gastos_por_categoria(usuario_id, mes, anio)
            elif opcion == '3':
                reportes.top_gastos(usuario_id)
            elif opcion == '4':
                anio = int(input("Año: "))
                reportes.resumen_anual(usuario_id, anio)
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
        except ValueError:
            print("Error: Ingrese números válidos.")

def menu_presupuestos(usuario_id):
    while True:
        print("\n--- PRESUPUESTOS ---")
        print("1. Crear Presupuesto")
        print("2. Listar Presupuestos")
        print("3. Verificar Alertas (Mes Actual)")
        print("0. Volver al Menú Principal")
        
        opcion = input("Seleccione una opción: ")
        
        try:
            if opcion == '1':
                cat_id = int(input("ID de Categoría: "))
                monto = float(input("Límite de Monto: "))
                periodo = input("Periodo (Mensual/Anual): ")
                inicio = input("Fecha Inicio (AAAA-MM-DD): ")
                fin = input("Fecha Fin (AAAA-MM-DD): ")
                presupuestos.crear_presupuesto(usuario_id, cat_id, monto, periodo, inicio, fin)
            elif opcion == '2':
                presupuestos.listar_presupuestos(usuario_id)
            elif opcion == '3':
                presupuestos.verificar_alertas(usuario_id)
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
        except ValueError:
            print("Error: Datos inválidos.")

def menu_cuentas(usuario_id):
    while True:
        print("\n--- GESTIÓN DE CUENTAS ---")
        print("1. Crear Nueva Cuenta")
        print("2. Listar Mis Cuentas")
        print("0. Volver al Menú Principal")
        
        opcion = input("Seleccione una opción: ")
        
        try:
            if opcion == '1':
                nombre = input("Nombre de la cuenta: ")
                print("Tipos: Ahorros, Corriente, Efectivo, Tarjeta de Crédito")
                tipo = input("Tipo de cuenta: ")
                saldo_ini = float(input("Saldo Inicial: "))
                divisa = input("Divisa (ej. USD, EUR, MXN) [USD]: ") or 'USD'
                cuentas.crear_cuenta(usuario_id, nombre, tipo, saldo_ini, divisa)
            elif opcion == '2':
                cuentas.listar_cuentas(usuario_id)
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
        except ValueError:
            print("Error: Ingrese valores numéricos correctos.")
        except Exception as e:
            print(f"Error: {e}")

def menu_usuarios():
    while True:
        print("\n--- GESTIÓN DE USUARIOS ---")
        print("1. Registrar Nuevo Usuario")
        print("2. Listar Usuarios")
        print("0. Volver al Menú Principal")
        
        opcion = input("Seleccione una opción: ")
        
        try:
            if opcion == '1':
                nombre = input("Nombre: ")
                email = input("Email: ")
                contrasena = input("Contraseña: ")
                usuarios.registrar_usuario(nombre, email, contrasena)
            elif opcion == '2':
                usuarios.listar_usuarios()
            elif opcion == '0':
                break
            else:
                print("Opción no válida.")
        except Exception as e:
            print(f"Error: {e}")

def main():
    if not inicializar_base_de_datos():
        print("No se pudo iniciar la aplicación debido a problemas con la base de datos.")
        sys.exit(1)
    
    # Usuario por defecto para esta versión (ID 1)
    # En una versión completa aquí iría un login/registro
    usuario_id = 1
    
    while True:
        print("\n==============================")
        print("   BIENVENIDO A FINANZASAPP")
        print("==============================")
        print("1. Transacciones")
        print("2. Reportes")
        print("3. Presupuestos")
        print("4. Cuentas")
        print("5. Usuarios")
        print("0. Salir")
        
        opcion = input("Seleccione una sección: ")
        
        if opcion == '1':
            menu_transacciones(usuario_id)
        elif opcion == '2':
            menu_reportes(usuario_id)
        elif opcion == '3':
            menu_presupuestos(usuario_id)
        elif opcion == '4':
            menu_cuentas(usuario_id)
        elif opcion == '5':
            menu_usuarios()
        elif opcion == '0':
            print("Gracias por usar FinanzasApp. ¡Hasta pronto!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()
