from django.db import migrations
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def create_roles(apps, schema_editor):
    """Crea grupos de permisos para Admin y Profesor"""
    # Crear o recuperar grupos
    admin_group, _ = Group.objects.get_or_create(name="Admin")
    profesor_group, _ = Group.objects.get_or_create(name="Profesor")

    # Admin obtiene todos los permisos
    all_perms = Permission.objects.all()
    admin_group.permissions.set(all_perms)

    # Permisos para Profesor (socios y registros)
    allowed_apps = {"socios", "registros"}
    profesor_perms = Permission.objects.filter(content_type__app_label__in=allowed_apps)
    profesor_group.permissions.set(profesor_perms)


def remove_roles(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=["Admin", "Profesor"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("socios", "0005_remove_socio_dni_socio_fecha_nacimiento"),
    ]

    operations = [
        migrations.RunPython(create_roles, reverse_code=remove_roles),
    ]
