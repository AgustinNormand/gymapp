# Gym Management APP

## Django 
### Run Migrations for an app
docker-compose run web python manage.py makemigrations socios
docker-compose run web python manage.py migrate

### Run Migrations for all
docker-compose exec web python manage.py makemigrations

### Create Superuser
docker-compose run web python manage.py createsuperuser

### Start/Restart environment
docker-compose down -v --remove-orphans
docker-compose up --build

### Build a new app
docker-compose run web python manage.py startapp pagos

## Info
### Supersuer
Username: admin
Password: admin123

## Pending Tasks
### Infra
[] Add Nginx to production scope
[] Add volume to Postgres to save information
[] Backup postgres information
[] Add .env.example file and add to .gitignore .env file

### Functional
[] Mejorar el registro de asistencias, para que sea más rápido cargar
[] Ver de crear distintos usuarios, con roles diferentes, para los distintos profes
[] Mostrar una alerta cuando se carga una asistencia, de alguien que no pagó
[] Mostrar una alerta cuando se carga una asistencia, que ya vino más de lo que podía, por semana

### Visual
[] Renombrar Gym Manager a Cinaf
[] Agregar logo de Cinaf

### Data
[] Migrar los usuarios de las sheet de Nico, a la DB

### Dash
[] Agregar info de, usuarios no pagos, ausentes
[] Agregar info de, usuarios pagos, ausentes
[] Agregar info de, usuarios pagos, presentes
[] Agregar info de, usuarios no pagos, presentes
[] Agregar gráficos de cantidad de usuarios mensuales
[] Agregar gráficos de cantidad de asistencias por hora

### Next steps - Going to the moon
[] Agregar cantidad de ingresos estimados
[] Mandarle un whatsapp a un socio, cuando dejó de venir




# Documentación

        [docker-compose up]
                ↓
 [DB (Postgres)] [WEB (Django + Gunicorn)]
                           ↓
                   [entrypoint.sh]
                           ↓
                [wait_for_db.sh espera DB]
                           ↓
                   [migrate + superuser]
                           ↓
                 [collectstatic + Gunicorn]
                           ↓
                   [Webserver corriendo]
                           ↓
                  [Healthchecks cada 30s]
