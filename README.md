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

## Backups

Los backups son **automáticos** vía dos servicios sidecar en `docker-compose`
(idénticos en Linux y Windows):

- `db-backup` (`prodrigestivill/postgres-backup-local:15`): corre `pg_dump` **diario**
  con rotación **7 diarios + 4 semanales**. Deja los dumps (`.sql.gz`) en la carpeta
  `./backups/{last,daily,weekly,monthly}/` del host.
- `db-backup-offsite` (`rclone/rclone`): replica `./backups` a Google Drive 1×/día.

### Setup one-time de Google Drive (rclone)
Se hace **una vez** en una máquina con navegador y se copia el `rclone.conf` a cada gym:

1. Instalar rclone y crear el remote:
   `rclone config` → `n` (new) → nombre `gdrive` → backend `drive` → autorizar en el
   navegador. Genera `~/.config/rclone/rclone.conf`.
2. Copiar ese `rclone.conf` a la **raíz del proyecto** en cada gym
   (`C:\gymapp\rclone.conf` en Windows, `.../gymapp/rclone.conf` en Linux). No se versiona.
3. En el `.env` de cada gym, setear `RCLONE_REMOTE` con un subfolder distinto por gym
   (ej. `gdrive:gym-backups/cinaf` y `gdrive:gym-backups/gym2`).
4. Levantar los servicios: `docker compose up -d db-backup db-backup-offsite`

### Forzar un backup manual ahora
docker compose exec db-backup /backup.sh

### Restaurar la base, desde un backup
Los dumps son SQL plano gzippeado. Recrear la base y cargar el dump elegido:

docker exec -i gymapp-db-1 psql -U gymuser -d postgres -c "DROP DATABASE IF EXISTS gymdb;" -c "CREATE DATABASE gymdb OWNER gymuser;"

gunzip -c backups/daily/gymdb-YYYYMMDD.sql.gz | docker exec -i gymapp-db-1 psql -U gymuser -d gymdb

Para restaurar desde el offsite, bajar primero el archivo:
docker compose exec db-backup-offsite rclone copy ${RCLONE_REMOTE}/daily/gymdb-YYYYMMDD.sql.gz /data/restore/

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
[x] [Other] [Medium] Script que hace un backup de la base de datos (backups automáticos diarios local + offsite, ver sección "Backups")
[] [Other] [Hard] Deploy de la solución en GCP, en la capa Free Tier

### Next steps - Going to the moon
[] Agregar cantidad de ingresos estimados para meses siguientes
[] Mandarle un whatsapp a un socio de forma automática, cuando dejó de venir
[] Cargar foto de cada socio, para usar en reconocimiento facial