from django.contrib import admin
from .models import Ejercicio, RegistroEjercicio

@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(RegistroEjercicio)
class RegistroEjercicioAdmin(admin.ModelAdmin):
    list_display = ('socio', 'ejercicio', 'fecha', 'peso')
    list_filter = ('fecha', 'ejercicio')
    search_fields = ('socio__nombre', 'socio__apellido', 'ejercicio__nombre')
