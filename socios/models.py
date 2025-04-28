from django.db import models

class Socio(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    fecha_alta = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} (DNI: {self.dni})"

class Pago(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return f"Pago de {self.socio.nombre} {self.socio.apellido} - {self.monto} - {self.fecha_pago.strftime('%d/%m/%Y')}"
