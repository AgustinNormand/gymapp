import os
import sys
import csv
import django

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Ajustalo si tu settings.py está en otra carpeta
django.setup()

from modalidades.models import Modalidad

def cargar_modalidades_desde_csv(csv_path):
    modalidades_creadas = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [campo.strip().upper() for campo in reader.fieldnames]

        for row in reader:
            nombre = row.get('NOMBRE', '').strip()
            precio = row.get('PRECIO', '').strip()

            if not nombre or not precio:
                continue

            modalidad, created = Modalidad.objects.get_or_create(
                nombre=nombre,
                defaults={'precio': int(precio)}
            )

            if created:
                print(f"✔️ Modalidad creada: {nombre} - ${precio}")
                modalidades_creadas += 1
            else:
                print(f"ℹ️ Modalidad ya existente: {nombre}")

    print(f"\nResumen: {modalidades_creadas} modalidades creadas.")

if __name__ == '__main__':
    ruta_csv = os.path.join(BASE_DIR, 'data', 'Modalidades.csv')
    cargar_modalidades_desde_csv(ruta_csv)
