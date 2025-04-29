import os
import sys
import csv
import django
from decimal import Decimal, InvalidOperation
from django.utils.timezone import now

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')  # Ajustá si tu proyecto se llama distinto
django.setup()

from socios.models import Socio
from ejercicios.models import Ejercicio, RegistroEjercicio

def cargar_socios_ejercicios(csv_path):
    hoy = now().date()
    registros_creados = 0
    registros_invalidos = 0

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [campo.strip().upper() for campo in reader.fieldnames]

        for row in reader:
            nombre_completo = row.get('NOMBRE', '').strip()

            if not nombre_completo:
                continue

            partes = nombre_completo.split(' ', 1)
            if len(partes) == 2:
                apellido, nombre = partes
            else:
                apellido, nombre = partes[0], ''

            apellido = apellido.strip().capitalize()
            nombre = nombre.strip().capitalize()

            try:
                socio = Socio.objects.get(nombre__iexact=nombre, apellido__iexact=apellido)
            except Socio.DoesNotExist:
                print(f"⚠️ No se encontró el socio: '{apellido} {nombre}'")
                continue

            for ejercicio_nombre in reader.fieldnames[1:]:  # Ignorar la columna "NOMBRE"
                peso_raw = row.get(ejercicio_nombre, '').strip()

                if not peso_raw or peso_raw == "-":
                    continue

                try:
                    peso_str = str(peso_raw).lower().replace("kg", "").replace(",", ".").strip()
                    peso = Decimal(peso_str)
                except (InvalidOperation, ValueError):
                    print(f"⚠️ Peso inválido para {socio}: '{peso_raw}' en ejercicio '{ejercicio_nombre}'")
                    registros_invalidos += 1
                    continue

                try:
                    ejercicio = Ejercicio.objects.get(nombre__iexact=ejercicio_nombre.strip())
                except Ejercicio.DoesNotExist:
                    print(f"⚠️ Ejercicio no encontrado: '{ejercicio_nombre}'")
                    continue

                RegistroEjercicio.objects.create(
                    socio=socio,
                    ejercicio=ejercicio,
                    fecha=hoy,
                    peso=peso
                )
                registros_creados += 1
                print(f"✔️ Registro creado: {socio} - {ejercicio} - {peso} kg")

    print(f"\nResumen:")
    print(f"Registros creados: {registros_creados}")
    print(f"Registros inválidos (peso no válido): {registros_invalidos}")

if __name__ == '__main__':
    ruta_csv = os.path.join(BASE_DIR, 'data', 'Socios_Ejercicios.csv')
    cargar_socios_ejercicios(ruta_csv)
