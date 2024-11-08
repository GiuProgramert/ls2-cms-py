#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <environment> <tag>"
    echo "environment: dev or prod"
    echo "tag: the name of the tag to deploy"
    exit 1
fi

ENVIRONMENT=$1
TAG=$2

if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Error: Invalid environment '$ENVIRONMENT'. Must be 'dev' or 'prod'."
    exit 1
fi

echo "Deploying to environment: $ENVIRONMENT"
echo "Using tag: $TAG"

echo "Starting deployment for $ENVIRONMENT with tag $TAG..."

# Exit on error
set -e

echo "Starting deployment process..."

echo "-------------------------------------------------------"

if ! command -v python3 &> /dev/null; then
    echo "Python 3.10 not found. Installing..."
    sudo apt install -y python3
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip not found. Installing..."
    sudo apt install -y python3-pip
fi

if ! command -v nginx &> /dev/null; then
    echo "Nginx not found. Installing..."
    sudo apt install -y nginx
fi

echo "-------------------------------------------------------"

echo "Creating .env file"

cat > .env << 'EOF'
DEBUG=True
SECRET_KEY="3$to!ng$gy34mt-my+n)9)&s066sppoo$l)^_j7w-slvc8n)2k"

# Database
DB_NAME=cms_py
DB_USER=root
DB_PASSWORD="#^cuz)aczl!-5m8$s*g^=v_ce93^6n*xa6+z9%g#4x$(^^ke_r"
DB_HOST=localhost
DB_PORT=5432

# Resend
RESEND_API_KEY=api_key

SMTP_USERNAME=cmspyls2@gmail.com
SMTP_PASSWORD="vcqn aypt kzod mknt"

URL="http://142.93.1.225"
STRIPE_PUBLIC_KEY = 'pk_test_51Q3IEOFWDLOQpTHGvvQ2a6Kpf2z9JdbMp5NpnMtBFtzUqTNRjLPVxWl1bbd2kvDRslXnEhtI2oCNOHCdktGdW6Zm00fnnxrBgX'
STRIPE_SECRET_KEY = 'sk_test_51Q3IEOFWDLOQpTHGSIl5aIIdgXNzbHsLLKwcOCWYW93Xi48zval6iIPDoWTGRRSm8o89MOHANtDUwn10FVMfGAGS008xqK2zw9'

CLOUDINARY_CLOUD_NAME=dr5bv93mi
CLOUDINARY_API_KEY=721244567857431
CLOUDINARY_API_SECRET=SxA9ZMYRQBuWSKSLAp_HcxA-Mhs
EOF

# Variables
DB_NAME="cms_py"
DB_USER="root"
DB_PASSWORD='#^cuz)aczl!-5m8$s*g^=v_ce93^6n*xa6+z9%g#4x$(^^ke_r'
DB_HOST="localhost"
DB_PORT="5432"

echo "file created"

echo "-------------------------------------------------------"

echo "Creating database"

# Update and install PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found. Installing..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
else
    echo "PostgreSQL is already installed."
fi

# Start PostgreSQL service
echo "Starting PostgreSQL service..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

echo "Configuring the database..."

sudo -u postgres psql <<EOF
-- Create the database
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
      CREATE DATABASE ${DB_NAME};
   END IF;
END
\$\$;

-- Create the user
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
      CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';
      GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
      ALTER USER ${DB_USER} SUPERUSER;
   END IF;
END
\$\$;
EOF

echo "-------------------------------------------------------"

# Stash local changes in settings.py
echo "Saving local changes in settings.py"
git stash

echo "-------------------------------------------------------"

# Pull latest changes from main branch
echo "Pulling latest changes..."

echo "Fetching tags from remote..."
git fetch --tags

echo "Checking out tag: $TAG"
git checkout $TAG

echo "Merging tag '$TAG' into current branch..."
git merge $TAG

echo "-------------------------------------------------------"

# Stash add 
echo "Restoring local changes in settings.py"
git stash apply

echo "-------------------------------------------------------"

echo "creating virtual environment"

# Create virtual environment
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source env/bin/activate

echo "-------------------------------------------------------"

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "-------------------------------------------------------"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

echo "-------------------------------------------------------"

# check if $ENVIROMENT is prod
if [ "$ENVIRONMENT" == "prod" ]; then
    echo "Collecting static files..."

    echo "Collecting static files..."
    cat > /etc/nginx/sites-available/cms_py << 'EOF'
    server {
        listen 80;
        server_name 142.93.1.225;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            alias /root/ls2-cms-py/static/;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/root/ls2-cms-py/cms_py.sock;
        }
    }
    EOF

    cat > /etc/systemd/system/gunicorn.service << 'EOF'
    [Unit]
    Description=gunicorn daemon for CMS Py
    After=network.target

    [Service]
    User=root
    Group=www-data
    UMask=007
    WorkingDirectory=/root/ls2-cms-py
    ExecStart=/root/ls2-cms-py/env/bin/gunicorn --workers 3 --bind unix:/root/ls2-cms-py/cms_py.sock cms_py.wsgi:application

    [Install]
    WantedBy=multi-user.target
    EOF

    sudo systemctl daemon-reload
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn

    echo "-------------------------------------------------------"

    # Restart services
    echo "Restarting Gunicorn..."
    sudo systemctl restart gunicorn

    echo "-------------------------------------------------------"

    echo "Restarting Nginx..."
    sudo systemctl restart nginx

    echo "-------------------------------------------------------"

    echo "Deployment completed successfully!"  
fi

echo "-------------------------------------------------------"

echo "inicializing server"
