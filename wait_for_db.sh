#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "⏳ Esperando base de datos en $host..."
  sleep 2
done

>&2 echo "✅ Base de datos $host está disponible. Continuando..."
exec $cmd
