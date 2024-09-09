#!/bin/bash


# Variables
PROJECT_DIR="/home/unixuser/ls2-cms-py"  # Reemplaza con la ruta a tu proyecto
VENV_DIR="$PROJECT_DIR/venv"  # Ruta del entorno virtual
GUNICORN_SERVICE="gunicorn"  # Nombre del servicio Gunicorn
NGINX_SERVICE="nginx"  # Nombre del servicio Nginx

# Entrar en el directorio del proyecto
cd $PROJECT_DIR

# Actualizar el repositorio
echo "Actualizando el repositorio..."
git config pull.rebase false	#configurar para el pull

git checkout nginx	#Ubicamos la rama

git pull origin main  # Bajamos los cambios

# Activar entorno virtual
echo "Activando el entorno virtual..."
source $VENV_DIR/bin/activate

# Instalar dependencias
echo "Instalando dependencias..."
pip install -r requirements.txt

# Ejecutar migraciones de base de datos
echo "Ejecutando migraciones de base de datos..."
python manage.py migrate

# Recargar Gunicorn
echo "Recargando Gunicorn..."
sudo systemctl restart $GUNICORN_SERVICE

# Recargar Nginx
echo "Recargando Nginx..."
sudo systemctl restart $NGINX_SERVICE

# Salida del entorno virtual
deactivate

echo "Despliegue completado exitosamente."
