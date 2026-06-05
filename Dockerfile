# Usar la imagen oficial de Python 3.11 slim para un contenedor ligero
FROM python:3.11-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para mysql-connector y otras librerías
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos primero para aprovechar la caché de capas de Docker
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación al contenedor
COPY . .

# Exponer el puerto que usará la aplicación (Railway usa la variable de entorno PORT)
EXPOSE 8080

# Comando para ejecutar la aplicación usando gunicorn
# Se usa 0.0.0.0 para que sea accesible desde fuera del contenedor
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
