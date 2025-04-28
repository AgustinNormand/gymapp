from django.contrib import admin
from .models import Pago
from .models import Pago, ConfiguracionPago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('socio', 'fecha_pago', 'monto', 'fecha_vencimiento')
    search_fields = ('socio__nombre', 'socio__apellido')
    list_filter = ('fecha_pago', 'fecha_vencimiento')

@admin.register(ConfiguracionPago)
class ConfiguracionPagoAdmin(admin.ModelAdmin):
    list_display = ('monto_sugerido',)
