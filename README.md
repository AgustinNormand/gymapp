# CINAF Management APP

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

## Legacy Data Migration

Based in Sheets of actual CINAF management, extract CSVs in desired format, and run:

docker-compose exec web bash
python3 legacy_data_migration/scripts/cargar_todo.py

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

## Pending Tasks
### Infra
[] Add Nginx to production scope
[] Add volume to Postgres to save information
[] Backup postgres information, to avoid SPOF
[] Add .env.example file and add to .gitignore .env file

### Functional
[] Ver de crear distintos usuarios, con roles diferentes, para los distintos profes
[] Mostrar una alerta cuando se carga una asistencia, de alguien que no pagó
[] Mostrar una alerta cuando se carga una asistencia, que ya vino más de lo que podía, por semana

### Visual
[] Agregar logo de Cinaf

### Dash
[] Agregar info de, usuarios no pagos, ausentes
[] Agregar info de, usuarios pagos, ausentes
[] Agregar info de, usuarios pagos, presentes
[] Agregar info de, usuarios no pagos, presentes
[] Agregar gráficos de cantidad de usuarios mensuales

### Next steps - Going to the moon
[] Agregar cantidad de ingresos estimados
[] Mandarle un whatsapp a un socio, cuando dejó de venir
[] Cargar foto de cada socio, para usar en reconocimiento facial






[] Script que periodicamente pullea el repo en la rama main, y si hay cambios, hace un "docker-compose up", y hace un backup de la base de datos
[] Deploy de la solución en GCP, en la capa Free Tier
[] En la vista de socios, a medida voy escribiendo, ir mostrando los resultados
[] Si el socio no tiene modalidad asignada, que me permita asignarle una, y luego registrar el pago, de forma más simple
[] Unificar los íconos de acciones que se pueden hacer sobre socios, a lo largo de la app, para estandarizar. Y disponibilizar estas acciones, en todas las vistas donde se muestra información de socios, incluso, en la vista de detalle de un socio

