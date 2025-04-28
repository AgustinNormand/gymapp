# Gym Management APP

## Django 
### Run Migrations
docker-compose run web python manage.py makemigrations socios
docker-compose run web python manage.py migrate

### Create Superuser
docker-compose run web python manage.py createsuperuser

### Start/Restart environment in Dev
(This uses docker-compose.override.yml)
docker-compose up

### Start/Restart environment in Prod
(This ignore docker-compose.override.yml)
docker-compose -f docker-compose.yml up --build

### Build a new app
docker-compose run web python manage.py startapp pagos

## Info
### Supersuer
Username: anormand
Password: asdasd123

## Pending Tasks
### Infra
[] Add Nginx to production scope
[] Add volume to Postgres to save information
[] Backup postgres information

### Functional
[] Mejorar el registro de asistencias, para que sea más rápido cargar
[] Corregir la hora de las asistencias
[] Renombrar "Entrada" por "Asistencia"
[] Crearle usuarios al Piri, Hacu, Valen y Nico
[] Agregar módulo de pagos
[] Agregar alerta, cuando se registra una entrada de alguien, que no pagó

### Visual
[] Renombrar Gym Manager a Cinaf
[] Agregar logo de Cinaf
[] Mejorar la home

### Next steps - Going to the moon
[] Agregar gráficos de asistencias
[] Agregar cantidad de ingresos estimados
[] Mandarle un whatsapp a un socio, cuando dejó de venir