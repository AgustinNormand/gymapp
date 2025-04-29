import os
import sys
import csv
import django
from django.utils.timezone import now

# Agregar /app al sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Inicializar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Cambialo si tu settings está en otra carpeta
django.setup()

from socios.models import Socio, Observacion

def cargar_observaciones_desde_csv(csv_path):
    hoy = now().date()
    observaciones_creadas = 0
    observaciones_omitidas = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            nombre_completo = row['NOMBRE Y APELLIDO'].strip()
            descripcion = row['OBSERVACION'].strip()

            # Ignorar observaciones vacías o "-"
            if not descripcion or descripcion == "-":
                observaciones_omitidas += 1
                continue

            parts = nombre_completo.split(' ', 1)
            if len(parts) == 2:
                apellido, nombre = parts
            else:
                apellido, nombre = parts[0], ''

            apellido = apellido.strip().capitalize()
            nombre = nombre.strip().capitalize()

            try:
                socio = Socio.objects.get(nombre__iexact=nombre, apellido__iexact=apellido)
                Observacion.objects.create(
                    socio=socio,
                    descripcion=descripcion,
                    fecha_inicio=hoy,
                    fecha_fin=None
                )
                print(f"✔️ Observación creada para {apellido} {nombre}: {descripcion}")
                observaciones_creadas += 1
            except Socio.DoesNotExist:
                print(f"⚠️ No se encontró el socio: '{apellido} {nombre}'")
            except Exception as e:
                print(f"❌ Error creando observación para '{apellido} {nombre}': {e}")

    print(f"\nResumen:")
    print(f"Observaciones creadas: {observaciones_creadas}")
    print(f"Observaciones omitidas (vacías o '-'): {observaciones_omitidas}")

if __name__ == '__main__':
    ruta_csv = os.path.join(BASE_DIR, 'data', 'Socios_Observaciones.csv')
    cargar_observaciones_desde_csv(ruta_csv)
