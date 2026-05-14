#!/bin/bash

# ==========================================
# Crear entorno virtual
# ==========================================

echo "Creando entorno virtual..."

python3 -m venv venv

# ==========================================
# Activar entorno virtual
# ==========================================

echo "Activando entorno virtual..."

source venv/bin/activate

# ==========================================
# Instalar dependencias
# ==========================================

echo "Instalando dependencias..."

pip install -r requirements.txt

# ==========================================
# Levantar PostgreSQL con Docker
# ==========================================

echo "Levantando base de datos..."

docker compose up -d

# ==========================================
# Ejecutar migraciones
# ==========================================

echo "Aplicando migraciones..."

python manage.py migrate

# ==========================================
# Ejecutar pruebas
# ==========================================

echo "Ejecutando pruebas..."

python manage.py test

# ==========================================
# Iniciar servidor Django
# ==========================================

echo "Iniciando servidor..."

python manage.py runserver