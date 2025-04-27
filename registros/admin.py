# registros/admin.py

from django.contrib import admin
from .models import RegistroEntrada

class RegistroEntradaAdmin(admin.ModelAdmin):
    list_display = ('socio', 'fecha_entrada', 'hora_entrada')  # Ahora usamos métodos
    search_fields = ('socio__nombre',)
    list_filter = ('fecha_hora',)

    def fecha_entrada(self, obj):
        return obj.fecha_hora.strftime('%d/%m/%Y')  # Devuelve solo la fecha
    fecha_entrada.short_description = 'Fecha'

    def hora_entrada(self, obj):
        return obj.fecha_hora.strftime('%H:%M')  # Devuelve solo la hora
    hora_entrada.short_description = 'Hora'

admin.site.register(RegistroEntrada, RegistroEntradaAdmin)
