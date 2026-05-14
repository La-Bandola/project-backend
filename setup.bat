@echo off

echo ==========================================
echo Creando entorno virtual
echo ==========================================

python -m venv venv

echo ==========================================
echo Activando entorno virtual
echo ==========================================

call venv\Scripts\activate

echo ==========================================
echo Instalando dependencias
echo ==========================================

pip install -r requirements.txt

echo ==========================================
echo Levantando PostgreSQL
echo ==========================================

docker compose up -d

echo ==========================================
echo Aplicando migraciones
echo ==========================================

python manage.py migrate

echo ==========================================
echo Ejecutando pruebas
echo ==========================================

python manage.py test

echo ==========================================
echo Iniciando servidor Django
echo ==========================================

python manage.py runserver