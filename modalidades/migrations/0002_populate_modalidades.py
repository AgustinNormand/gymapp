from django.db import migrations

def crear_modalidades(apps, schema_editor):
    Modalidad = apps.get_model('modalidades', 'Modalidad')

    modalidades = [
        ("Hasta 3 por semana", 25000),
        ("Libre", 30000),
        ("Libre+Nutri", 35000),
    ]

    for nombre, precio in modalidades:
        Modalidad.objects.create(nombre=nombre, precio=precio)

class Migration(migrations.Migration):

    dependencies = [
        ('modalidades', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(crear_modalidades),
    ]
