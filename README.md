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

## Backupear la base
docker exec -t gymapp-db-1 pg_dump -U gymuser -F c -b -v -f /tmp/backup_gymdb.backup gymdb

docker cp gymapp-db-1:/tmp/backup_gymdb.backup /home/nicolas/Backups/gymapp_backups/

### Restaurar la base, desde un backup
docker cp backup_gymdb.backup gymapp-db-1:/tmp/

docker exec -it gymapp-db-1 pg_restore -U gymuser -d gymdb --clean --if-exists -v /tmp/backup_gymdb.backup

## Pending Tasks - Sorted by priority
[] [Functional] [Easy] Agregar un ícono distintivo, cuando falta cargarle algún dato a un socio (Email, Teléfono, cumpleaños, etc)
[] [Functional] [Easy] Armar un ranking, ordenado por cantidad de días sin venir, de usuarios pagos, que vinieron algúna vez al més
[] [Functional] [Easy] Levantar un warning, cuando una persona, hace un més, no modifica el peso de sus ejercicios
[] [Infra] [Easy] Make another backup of postgres information, to avoid SPOF
[] [Other] [Easy] Agregar un tooltip a las acciones, para que quede claro que hace cada una
[] [Dash] [Easy] Agregar gráficos de cantidad de usuarios mensuales
[] [Dash] [Easy] Agregar gráfico de la evolución de los pesos de un socio
[] [Dash] [Easy] Agregar gráfico de las asistencias semanales de los socios
[] [Functional] [Medium] Ver de crear distintos usuarios, con roles diferentes, para los distintos profes
[] [Infra] [Medium] Add volume to Postgres to save information
[] [Infra] [Medium] Add Nginx to production scope
[] [Other] [Medium] Script que periodicamente pullea el repo en la rama main, y si hay cambios, hace un "docker-compose up"
[] [Other] [Medium] Script que hace un backup de la base de datos
[] [Other] [Hard] Deploy de la solución en GCP, en la capa Free Tier

### Next steps - Going to the moon
[] Agregar cantidad de ingresos estimados
[] Mandarle un whatsapp a un socio, cuando dejó de venir
[] Cargar foto de cada socio, para usar en reconocimiento facial