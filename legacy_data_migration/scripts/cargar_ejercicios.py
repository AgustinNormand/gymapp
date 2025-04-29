import os
import sys
import csv
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Ajustá si tu proyecto se llama distinto
django.setup()

from ejercicios.models import Ejercicio

def cargar_ejercicios_desde_csv(csv_path):
    ejercicios_creados = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [campo.strip().upper() for campo in reader.fieldnames]

        for row in reader:
            nombre = row.get('NOMBRE', '').strip()

            if not nombre:
                continue

            ejercicio, creado = Ejercicio.objects.get_or_create(nombre=nombre)

            if creado:
                print(f"✔️ Ejercicio creado: {nombre}")
                ejercicios_creados += 1
            else:
                print(f"ℹ️ Ejercicio ya existente: {nombre}")

    print(f"\nResumen: {ejercicios_creados} ejercicios creados.")

if __name__ == '__main__':
    ruta_csv = os.path.join(BASE_DIR, 'data', 'Ejercicios.csv')
    cargar_ejercicios_desde_csv(ruta_csv)
