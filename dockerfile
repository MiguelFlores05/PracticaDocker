# Define la imagen base del contenedor como python:3.9. Esto incluye una instalación 
# mínima de Python 3.9 y todas sus dependencias básicas.

# Define la imagen base del contenedor
FROM python:3.9
# Por medio de esto, se instala Python 3.9 y todas sus dependencias básicas

# Actualizar repositorios e instalar dependencias
RUN apt-get update && apt-get install -y \
    libgomp1 \
    # Elimina los índices locales de paquetes para reducir el tamaño del contenedor.
    && rm -rf /var/lib/apt/lists/*

# Configurar el directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Flask
EXPOSE 6060

# Comando por defecto
CMD ["python", "app.py"]