echo "Starting Deploy"

set -e

echo "-------------------------------------------------------"
echo "Saving local changes in settings.py"
git stash

echo "-------------------------------------------------------"
echo "Pulling fron repository"
git pull origin main

echo "-------------------------------------------------------"
echo "Restoring local changes in settings.py"
git stash apply

echo "-------------------------------------------------------"
echo "Activating virtual environment..."
source env/bin/activate

echo "-------------------------------------------------------"
echo "Installing/updating dependencies..."
pip install -r requirements.txt

echo "-------------------------------------------------------"
echo "Running database migrations..."
python manage.py migrate

echo "-------------------------------------------------------"
echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "-------------------------------------------------------"
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "Finish Deploy"