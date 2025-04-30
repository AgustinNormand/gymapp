from django.db import models
from datetime import date

class Modalidad(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    dias_por_semana = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} (${self.precio}) - {self.dias_por_semana} días/semana"

class HistorialModalidad(models.Model):
    socio = models.ForeignKey('socios.Socio', on_delete=models.CASCADE, related_name='historial_modalidades')
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE)
    precio_en_el_momento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_inicio = models.DateField(default=date.today)
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.socio} - {self.modalidad.nombre} - ${self.precio_en_el_momento} ({self.fecha_inicio} - {self.fecha_fin or 'Actual'})"
