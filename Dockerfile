# Usa una imagen ligera oficial de Ubuntu
FROM ubuntu:20.04

# Establece el entorno como no interactivo para evitar la configuración manual
ENV DEBIAN_FRONTEND=noninteractive

# Actualiza los repositorios e instala dependencias mínimas Y LAS DE PLAYWRIGHT
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    wget \
    # Dependencias básicas que ya tenías y otras útiles
    libglib2.0-0 \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libexpat1 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxcb1 \
    libasound2 \
    libxkbcommon0 \
    ca-certificates \
    tzdata \
    && pip3 install --no-cache-dir playwright \
    && playwright install-deps \
    # Limpia la caché de apt para reducir el tamaño de la imagen
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar los navegadores de Playwright
# (Lo hacemos después de install-deps para asegurar que las dependencias están)
RUN playwright install

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia todos los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias de Python desde requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expone el puerto 8000 para FastAPI
EXPOSE 8000

# Comando para ejecutar FastAPI cuando el contenedor inicie
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
