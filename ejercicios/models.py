from django.db import models
from socios.models import Socio

class Ejercicio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class RegistroEjercicio(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='registros_ejercicio')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='registros')
    fecha = models.DateField(auto_now_add=True)
    peso = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.socio} - {self.ejercicio} - {self.fecha} - {self.peso} kg"
