from django.db import migrations
import os

def cargar_socios(apps, schema_editor):
    Socio = apps.get_model('socios', 'Socio')

    raw_users = os.getenv('RAW_USERNAMES')

    socios_list = raw_users.split(',')

    socios_crear = []

    socios_vistos = set()  # Para evitar duplicados

    for user in socios_list:
        user = user.strip()
        if not user or user.lower() in socios_vistos:
            continue
        socios_vistos.add(user.lower())

        parts = user.split(' ', 1)
        if len(parts) == 2:
            apellido, nombre = parts
        else:
            apellido, nombre = parts[0], ''

        socios_crear.append(
            Socio(
                nombre=nombre.strip().capitalize(), 
                apellido=apellido.strip().capitalize(),
                dni=None,
                email=None,
                telefono=None
            )
        )

    Socio.objects.bulk_create(socios_crear)

class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0002_alter_socio_dni_alter_socio_email_and_more'),
    ]

    operations = [
        migrations.RunPython(cargar_socios),
    ]
