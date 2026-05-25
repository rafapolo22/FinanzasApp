-- Creación de la base de datos
CREATE DATABASE IF NOT EXISTS finanzas_db;
USE finanzas_db;

-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabla de Cuentas
CREATE TABLE IF NOT EXISTS cuentas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('Ahorros', 'Corriente', 'Efectivo', 'Tarjeta de Crédito') NOT NULL,
    saldo_inicial DECIMAL(15, 2) DEFAULT 0.00,
    saldo_actual DECIMAL(15, 2) DEFAULT 0.00,
    divisa VARCHAR(3) DEFAULT 'USD',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla de Categorías
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NULL, -- NULL para categorías del sistema (globales)
    nombre VARCHAR(100) NOT NULL,
    tipo ENUM('Ingreso', 'Gasto') NOT NULL,
    INDEX (usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla de Transacciones
CREATE TABLE IF NOT EXISTS transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta_id INT NOT NULL,
    categoria_id INT NOT NULL,
    monto DECIMAL(15, 2) NOT NULL,
    tipo ENUM('Ingreso', 'Gasto') NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (cuenta_id),
    INDEX (categoria_id),
    INDEX (fecha),
    FOREIGN KEY (cuenta_id) REFERENCES cuentas(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Tabla de Transferencias (Entre cuentas del mismo usuario)
CREATE TABLE IF NOT EXISTS transferencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cuenta_origen_id INT NOT NULL,
    cuenta_destino_id INT NOT NULL,
    monto DECIMAL(15, 2) NOT NULL,
    fecha DATE NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cuenta_origen_id) REFERENCES cuentas(id) ON DELETE CASCADE,
    FOREIGN KEY (cuenta_destino_id) REFERENCES cuentas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabla de Presupuestos
CREATE TABLE IF NOT EXISTS presupuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    categoria_id INT NOT NULL,
    monto_limite DECIMAL(15, 2) NOT NULL,
    periodo ENUM('Mensual', 'Anual') DEFAULT 'Mensual',
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX (usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Inserción de Categorías por Defecto (Globales)
INSERT IGNORE INTO categorias (usuario_id, nombre, tipo) VALUES 
(NULL, 'Alimentación', 'Gasto'),
(NULL, 'Transporte', 'Gasto'),
(NULL, 'Vivienda', 'Gasto'),
(NULL, 'Salud', 'Gasto'),
(NULL, 'Educación', 'Gasto'),
(NULL, 'Entretenimiento', 'Gasto'),
(NULL, 'Sueldo', 'Ingreso'),
(NULL, 'Ventas', 'Ingreso'),
(NULL, 'Otros Ingresos', 'Ingreso'),
(NULL, 'Otros Gastos', 'Gasto');
