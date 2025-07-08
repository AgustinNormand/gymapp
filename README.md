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
[] [Other] [Easy] Algunas tablas no están 100% centradas
[] [Other] [Easy] Centrar los filtros, en la vista de "Pagos Realizados", "Asistencias Registradas"
[] [Other] [Easy] Cuando selecciono un ejercicio, en la vista de detalle de socio, quiero que scrolee para abajo
[] [Other] [Easy] Revisar el gráfico de estadisticas de asistencias de la home, a veces da valores raros, pero capaz están bien
[] [Other] [Easy] Acomodar la vista de "Detalle de Socio"
[] [Other] [Easy] Revisar los formularios de "Gestionar Ejercicios", "Gestionar Pagos" ...
[] [Other] [Easy] Cuando una persona puede ahorrar plata, agregar un ícono cuando le paso asistencia (Que al presionarlo, me redirija, a la vista de "Evolución Semanal")
[] [Other] [Easy] Permitir que se pueda cargar una asistencia de un momento pasado
[] [Other] [Hard] Eliminar los casos donde se cambió la modalidad de un socio, a la misma modalidad
[] [Functional] [Medium] Crear distintos usuarios, con roles diferentes, para los distintos profes
[] [Infra] [Medium] Add volume to Postgres to save information
[] [Infra] [Medium] Add Nginx to production scope
[] [Other] [Medium] Script que periodicamente pullea el repo en la rama main, y si hay cambios, hace un "docker-compose up"
[] [Other] [Medium] Script que hace un backup de la base de datos
[] [Other] [Hard] Deploy de la solución en GCP, en la capa Free Tier

### Next steps - Going to the moon
[] Agregar cantidad de ingresos estimados para meses siguientes
[] Mandarle un whatsapp a un socio de forma automática, cuando dejó de venir
[] Cargar foto de cada socio, para usar en reconocimiento facial