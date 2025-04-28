FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar curl, psql y limpiar
RUN apt-get update && apt-get install -y curl postgresql-client && apt-get clean

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Asegurar permisos de los scripts
RUN chmod +x /app/entrypoint.sh /app/wait_for_db.sh

# EntryPoint
CMD ["./entrypoint.sh"]
