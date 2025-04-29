import os
import django
import csv
import sys

# Agregar /app al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from socios.models import Socio

def cargar_socios_desde_csv(csv_path):
    socios_crear = []
    socios_vistos = set()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            nombre_completo = row['NOMBRE Y APELLIDO'].strip()

            if not nombre_completo or nombre_completo.lower() in socios_vistos:
                continue
            socios_vistos.add(nombre_completo.lower())

            parts = nombre_completo.split(' ', 1)
            if len(parts) == 2:
                apellido, nombre = parts
            else:
                apellido, nombre = parts[0], ''

            socio = Socio(
                nombre=nombre.strip().capitalize(),
                apellido=apellido.strip().capitalize(),
                dni=None,
                email=None,
                telefono=None
            )
            socios_crear.append(socio)

    Socio.objects.bulk_create(socios_crear)
    print(f"Se cargaron {len(socios_crear)} socios.")

if __name__ == '__main__':
    ruta_csv = os.path.join(BASE_DIR, 'data', 'Socios.csv')
    cargar_socios_desde_csv(ruta_csv)
