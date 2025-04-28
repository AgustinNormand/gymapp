from django.db import models
from socios.models import Socio

class Pago(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='pagos')
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return f"Pago de {self.socio.nombre} {self.socio.apellido} - ${self.monto} - {self.fecha_pago.strftime('%d/%m/%Y')}"


class ConfiguracionPago(models.Model):
    monto_sugerido = models.DecimalField(max_digits=10, decimal_places=2, default=20000)

    def __str__(self):
        return f"Configuración de Pagos - Monto sugerido: ${self.monto_sugerido}"
