import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.connection import ConexionDB
from modules import transacciones, reportes, presupuestos, cuentas, usuarios
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_finanzas_app'

def inicializar_db():
    try:
        config = {'host': 'localhost', 'user': 'root', 'password': ''}
        import mysql.connector
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        ruta_sql = os.path.join('database', 'schema.sql')
        if os.path.exists(ruta_sql):
            with open(ruta_sql, 'r', encoding='utf-8') as f:
                sql_commands = f.read().split(';')
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al inicializar DB: {e}")

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
                flash(f'Error: {e}', 'danger')
        
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
    mis_cuentas = cuentas.listar_cuentas(uid)
    ultimas_transacciones = transacciones.listar_transacciones(uid)[:5]
    alertas = presupuestos.verificar_alertas(uid)
    
    # Obtener categorías para un posible formulario rápido
    try:
        with ConexionDB() as conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = %s", (uid,))
            categorias = cursor.fetchall()
    except:
        categorias = []
    
    return render_template('dashboard.html', 
                           cuentas=mis_cuentas, 
                           transacciones=ultimas_transacciones,
                           alertas=alertas,
                           categorias=categorias,
                           now=datetime.now().strftime('%Y-%m-%d'))

@app.route('/transacciones', methods=['GET', 'POST'])
def gestion_transacciones():
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
        transacciones.agregar_transaccion(cuenta_id, cat_id, monto, tipo, fecha, desc)
        flash('Transacción agregada', 'success')

    lista = transacciones.listar_transacciones(uid)
    mis_cuentas = cuentas.listar_cuentas(uid)
    # Categorías (podrían listarse desde un módulo, aquí usaremos una lista simple o consulta rápida)
    try:
        with ConexionDB() as conexion:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categorias WHERE usuario_id IS NULL OR usuario_id = %s", (uid,))
            categorias = cursor.fetchall()
    except:
        categorias = []

    return render_template('transacciones.html', transacciones=lista, cuentas=mis_cuentas, categorias=categorias)

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
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM categorias WHERE tipo = 'Gasto' AND (usuario_id IS NULL OR usuario_id = %s)", (uid,))
            categorias = cursor.fetchall()
    except:
        categorias = []

    return render_template('presupuestos.html', presupuestos=lista, categorias=categorias)

if __name__ == '__main__':
    inicializar_db()
    app.run(debug=True)
