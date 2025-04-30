from django.db import models
from django.utils import timezone

class Socio(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    
class Observacion(models.Model):
    socio = models.ForeignKey('Socio', on_delete=models.CASCADE, related_name='observaciones')
    descripcion = models.TextField()
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)

    def esta_activa(self):
        """Devuelve True si la observación sigue vigente"""
        return self.fecha_fin is None or self.fecha_fin > timezone.now().date()

    def __str__(self):
        estado = "Activa" if self.esta_activa() else "Finalizada"
        return f"{self.descripcion[:30]} ({estado})"

