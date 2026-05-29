import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.connection import ConexionDB
from modules import transacciones, reportes, presupuestos, cuentas, usuarios
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_finanzas_app')

def inicializar_db():
    """
    Inicializa la base de datos al arrancar, compatible con local y Railway.
    """
    print(f"DEBUG DB: HOST={os.getenv('DB_HOST')}, PORT={os.getenv('DB_PORT')}, NAME={os.getenv('DB_NAME')}, USER={os.getenv('DB_USER')}")
    try:
        # Configuración desde variables de entorno (compatible con Railway)
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        import mysql.connector
        print(f"Intentando inicializar base de datos en {config['host']}...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        ruta_sql = os.path.join('database', 'schema.sql')
        if os.path.exists(ruta_sql):
            with open(ruta_sql, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                
            # Procesar el script: quitar comentarios y dividir por ;
            sql_clean = []
            for line in sql_script.splitlines():
                if not line.strip().startswith('--') and line.strip():
                    sql_clean.append(line)
            
            sql_commands = "\n".join(sql_clean).split(';')
            
            for command in sql_commands:
                cmd = command.strip()
                if cmd:
                    db_name_env = os.getenv('DB_NAME')
                    if db_name_env:
                        if cmd.upper().startswith('CREATE DATABASE'):
                            cmd = f"CREATE DATABASE IF NOT EXISTS {db_name_env}"
                        elif cmd.upper().startswith('USE'):
                            cmd = f"USE {db_name_env}"
                        
                    cursor.execute(cmd)
            
            conn.commit()
            print("Base de datos inicializada o verificada correctamente.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Aviso en inicializar_db: {e}")

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        action = request.form.get('action')
        email = request.form.get('email')
        password = request.form.get('password')

        if action == 'login':
            try:
                with ConexionDB() as conexion:
                    if conexion is None:
                        flash('Error: No se pudo conectar a la base de datos. Verifique su configuración.', 'danger')
                    else:
                        cursor = conexion.cursor(dictionary=True)
                        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                        usuario = cursor.fetchone()
                        if usuario:
                            # En una app real usaríamos hash de contraseñas
                            session['usuario_id'] = usuario['id']
                            session['nombre'] = usuario['nombre']
                            flash(f'Bienvenido, {usuario["nombre"]}', 'success')
                            return redirect(url_for('dashboard'))
                        else:
                            flash('Usuario o contraseña incorrectos', 'danger')
            except Exception as e:
                flash(f'Error de sistema: {e}', 'danger')
        
        elif action == 'register':
            nombre = request.form.get('nombre')
            if usuarios.registrar_usuario(nombre, email, password):
                flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            else:
                flash('Error al registrar. El email podría ya existir.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    mis_cuentas = cuentas.listar_cuentas(uid) or []
    ultimas_transacciones = transacciones.listar_transacciones(uid) or []
    ultimas_transacciones = ultimas_transacciones[:5]
    alertas = presupuestos.verificar_alertas(uid) or []
    
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = %s ORDER BY nombre", (uid,))
                categorias = cursor.fetchall()
            else:
                categorias = []
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        categorias = []
    
    return render_template('dashboard.html', 
                           cuentas=mis_cuentas, 
                           transacciones=ultimas_transacciones,
                           alertas=alertas,
                           categorias=categorias,
                           now=datetime.now().strftime('%Y-%m-%d'))

# --- RUTAS DE TRANSACCIONES ---

@app.route('/transacciones', methods=['GET', 'POST'])
def gestion_transacciones():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    if request.method == 'POST':
        try:
            cuenta_id = request.form['cuenta_id']
            cat_id = request.form['categoria_id']
            monto = float(request.form['monto'])
            tipo = request.form['tipo']
            fecha = request.form['fecha']
            desc = request.form['descripcion']
            if transacciones.agregar_transaccion(cuenta_id, cat_id, monto, tipo, fecha, desc):
                flash('Transacción agregada con éxito', 'success')
            else:
                flash('Error al procesar la transacción', 'danger')
        except Exception as e:
            flash(f'Error en los datos: {e}', 'warning')

    lista = transacciones.listar_transacciones(uid) or []
    mis_cuentas = cuentas.listar_cuentas(uid) or []
    
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = %s ORDER BY nombre", (uid,))
                categorias = cursor.fetchall()
            else:
                categorias = []
    except:
        categorias = []

    return render_template('transacciones.html', transacciones=lista, cuentas=mis_cuentas, categorias=categorias)

@app.route('/transacciones/editar/<int:id>', methods=['GET', 'POST'])
def editar_transaccion(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    if request.method == 'POST':
        cuenta_id = request.form['cuenta_id']
        cat_id = request.form['categoria_id']
        monto = float(request.form['monto'])
        tipo = request.form['tipo']
        fecha = request.form['fecha']
        desc = request.form['descripcion']
        if transacciones.editar_transaccion(id, cuenta_id, cat_id, monto, tipo, fecha, desc):
            flash('Transacción actualizada', 'success')
            return redirect(url_for('gestion_transacciones'))
        flash('Error al actualizar', 'danger')

    t = transacciones.obtener_transaccion(id)
    mis_cuentas = cuentas.listar_cuentas(uid)
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = %s ORDER BY nombre", (uid,))
                categorias = cursor.fetchall()
            else:
                categorias = []
    except:
        categorias = []
        
    return render_template('editar_transaccion.html', t=t, cuentas=mis_cuentas, categorias=categorias)

@app.route('/transacciones/eliminar/<int:id>')
def eliminar_transaccion(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if transacciones.eliminar_transaccion(id):
        flash('Transacción eliminada', 'success')
    else:
        flash('Error al eliminar', 'danger')
    return redirect(url_for('gestion_transacciones'))

# --- RUTAS DE CUENTAS ---

@app.route('/cuentas', methods=['GET', 'POST'])
def gestion_cuentas():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        saldo_ini = float(request.form['saldo_inicial'])
        divisa = request.form.get('divisa', 'USD')
        if cuentas.crear_cuenta(uid, nombre, tipo, saldo_ini, divisa):
            flash(f'Cuenta "{nombre}" creada con éxito', 'success')
        else:
            flash('Error al crear la cuenta', 'danger')

    mis_cuentas = cuentas.listar_cuentas(uid) or []
    return render_template('cuentas.html', cuentas=mis_cuentas)

@app.route('/cuentas/editar/<int:id>', methods=['GET', 'POST'])
def editar_cuenta(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        saldo_ini = float(request.form['saldo_inicial'])
        divisa = request.form['divisa']
        if cuentas.editar_cuenta(id, nombre, tipo, saldo_ini, divisa):
            flash('Cuenta actualizada', 'success')
            return redirect(url_for('gestion_cuentas'))
        flash('Error al actualizar', 'danger')

    c = cuentas.obtener_cuenta(id)
    return render_template('editar_cuenta.html', c=c)

@app.route('/cuentas/eliminar/<int:id>')
def eliminar_cuenta(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if cuentas.eliminar_cuenta(id):
        flash('Cuenta eliminada', 'success')
    else:
        flash('Error al eliminar', 'danger')
    return redirect(url_for('gestion_cuentas'))

# --- RUTAS DE PRESUPUESTOS ---

@app.route('/presupuestos', methods=['GET', 'POST'])
def gestion_presupuestos():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    if request.method == 'POST':
        cat_id = request.form['categoria_id']
        monto = float(request.form['monto'])
        periodo = request.form['periodo']
        inicio = request.form['fecha_inicio']
        fin = request.form['fecha_fin']
        presupuestos.crear_presupuesto(uid, cat_id, monto, periodo, inicio, fin)
        flash('Presupuesto creado', 'success')

    lista = presupuestos.listar_presupuestos(uid)
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM categorias WHERE tipo = 'Gasto' AND (usuario_id IS NULL OR usuario_id = %s)", (uid,))
                categorias = cursor.fetchall()
            else:
                categorias = []
    except:
        categorias = []

    return render_template('presupuestos.html', presupuestos=lista, categorias=categorias)

@app.route('/presupuestos/editar/<int:id>', methods=['GET', 'POST'])
def editar_presupuesto(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    if request.method == 'POST':
        cat_id = request.form['categoria_id']
        monto = float(request.form['monto'])
        periodo = request.form['periodo']
        inicio = request.form['fecha_inicio']
        fin = request.form['fecha_fin']
        if presupuestos.editar_presupuesto(id, cat_id, monto, periodo, inicio, fin):
            flash('Presupuesto actualizado', 'success')
            return redirect(url_for('gestion_presupuestos'))
        flash('Error al actualizar', 'danger')

    p = presupuestos.obtener_presupuesto(id)
    try:
        with ConexionDB() as conexion:
            if conexion:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM categorias WHERE tipo = 'Gasto' AND (usuario_id IS NULL OR usuario_id = %s)", (uid,))
                categorias = cursor.fetchall()
            else:
                categorias = []
    except:
        categorias = []
        
    return render_template('editar_presupuesto.html', p=p, categorias=categorias)

@app.route('/presupuestos/eliminar/<int:id>')
def eliminar_presupuesto(id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    if presupuestos.eliminar_presupuesto(id):
        flash('Presupuesto eliminado', 'success')
    else:
        flash('Error al eliminar', 'danger')
    return redirect(url_for('gestion_presupuestos'))

@app.route('/reportes')
def gestion_reportes():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    uid = session['usuario_id']
    ahora = datetime.now()
    balance = reportes.balance_mensual(uid, ahora.month, ahora.year)
    gastos_cat = reportes.gastos_por_categoria(uid, ahora.month, ahora.year)
    top = reportes.top_gastos(uid)
    
    return render_template('reportes.html', balance=balance, gastos_cat=gastos_cat, top=top)

# Inicializar la base de datos automáticamente al arrancar (compatible con Gunicorn)
inicializar_db()

if __name__ == '__main__':
    # Usar el puerto definido por el entorno (Railway usa PORT)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
