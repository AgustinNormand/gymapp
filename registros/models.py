from django.db import models
from socios.models import Socio

class RegistroEntrada(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.socio.nombre} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"
