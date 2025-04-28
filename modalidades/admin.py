from django.contrib import admin
from .models import Modalidad, HistorialModalidad

@admin.register(Modalidad)
class ModalidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio')

@admin.register(HistorialModalidad)
class HistorialModalidadAdmin(admin.ModelAdmin):
    list_display = ('socio', 'modalidad', 'precio_en_el_momento', 'fecha_inicio', 'fecha_fin')
    list_filter = ('modalidad',)
    search_fields = ('socio__nombre', 'socio__apellido')

