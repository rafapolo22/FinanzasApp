# Usar la imagen oficial de Python 3.11 slim
FROM python:3.11-slim

# Definir argumentos de construcción (build-time)
# Railway pasará estos valores si se configuran en el panel
ARG ANTHROPIC_API_KEY

# Convertir el argumento en variable de entorno (run-time)
ENV ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto que usará Railway
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
