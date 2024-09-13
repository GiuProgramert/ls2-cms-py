#!/bin/bash

# Variables
PROJECT_DIR="/home/unixuser/ls2-cms-py"  # Reemplaza con la ruta a tu proyecto
VENV_DIR="$PROJECT_DIR/venv"  # Ruta del entorno virtual
GUNICORN_SERVICE="gunicorn"  # Nombre del servicio Gunicorn
NGINX_SERVICE="nginx"  # Nombre del servicio Nginx

# Función para manejar errores
function check_error {
    if [ $? -ne 0 ]; then
        echo "Error en $1. Abortando despliegue."
        exit 1
    fi
}

# Entrar en el directorio del proyecto
echo "Entrando en el directorio del proyecto..."
cd $PROJECT_DIR
check_error "cambiar a $PROJECT_DIR"

# Actualizar el repositorio
echo "Actualizando el repositorio..."

git config pull.rebase false	#configuramos para realizar la actualizacion del repositorio
git checkout nginx
git pull origin main  # pull del repositorio
check_error "git pull"

# Activar entorno virtual
echo "Activando el entorno virtual..."
source $VENV_DIR/bin/activate
check_error "activar entorno virtual"

# Instalar dependencias
echo "Instalando dependencias..."
git config pull.rebase false
git checkout nginx

pip install -r requirements.txt
check_error "instalación de dependencias"

# Ejecutar migraciones de base de datos
echo "Ejecutando migraciones de base de datos..."
python manage.py migrate
check_error "migraciones de base de datos"

# Recargar Gunicorn
echo "Recargando Gunicorn..."
sudo systemctl restart $GUNICORN_SERVICE
check_error "reiniciar Gunicorn"

# Recargar Nginx
echo "Recargando Nginx..."
sudo systemctl restart $NGINX_SERVICE
check_error "reiniciar Nginx"

# Salida del entorno virtual
deactivate

echo "Despliegue completado exitosamente."
