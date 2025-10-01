# Usamos una imagen base oficial de Python, ligera y estable
FROM python:3.11-slim-bullseye

# Establecemos variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalamos las dependencias del sistema operativo que fallaban antes
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos e instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de nuestro proyecto al contenedor
COPY . .

# Creamos un script de inicio que ejecutará las migraciones
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponemos el puerto que Gunicorn usará
EXPOSE 8000

# El comando por defecto para iniciar el contenedor
ENTRYPOINT ["/entrypoint.sh"]