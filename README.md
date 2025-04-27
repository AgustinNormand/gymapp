# Run Migrations
docker-compose run web python manage.py makemigrations socios
docker-compose run web python manage.py migrate

# Create Superuser
docker-compose run web python manage.py createsuperuser

# Start/Restart environment in Dev
(This uses docker-compose.override.yml)
docker-compose up

# Start/Restart environment in Prod
(This ignore docker-compose.override.yml)
docker-compose -f docker-compose.yml up --build

## Info
# Supersuer
Username: anormand
Password: asdasd123

## Pending Tasks
[] Add Nginx to production scope
[] Add volume to Postgres to save information
[] Backup postgres information