# CMS-PY

Proyecto realizado en la matería Ingenieria de Software 2 permite subir contenidos y contenidos

## Requerimientos
- Python 3.10.*
- postgresql

## Instalación

### 1. Clonar el proyecto
```
git clone https://github.com/GiuProgramert/ls2-cms-py.git
```

### 2. Entorno virtual

#### Instalar la librería virtualenv

```bash
python -m pip install virtualenv
```

#### Crear el entorno virtual
```bash
virtualenv env
```

#### Activar entorno virtual
```bash
source env/bin/activate
```

### 3. Instalación de requerimientos
```bash
pip install -r requirements.txt
```

### 4. Variables de entorno

#### hacer una copia del archivo .env.example con nombre .env
```bash
cp .env.example .env
```

#### modificar los valores de las variables de entorno y a continuación aplicar al entorno
```bash
source .env
```

### 5. Ejecutar el código
```bash
python manage.py runserver
```

### Documentación
```
python django_pydoc.py -p 1234
```# ls2-cms-py
