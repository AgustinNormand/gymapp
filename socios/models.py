from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.utils.timezone import now

class Socio(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    def has_all_data(self):
        """Verifica si el socio tiene todos los datos completos"""

        if not self.fecha_nacimiento or not self.telefono:
            return False
        return True
        
    
    @property
    def pesos_por_ejercicio(self):
        if hasattr(self, '_cached_pesos'):
            return self._cached_pesos
        registros = self.registros_ejercicio.order_by('ejercicio_id', '-fecha')
        data = {}
        for r in registros:
            if r.ejercicio_id not in data:
                data[r.ejercicio_id] = r.peso
        self._cached_pesos = data
        return data


    def get_observaciones_activas(self):
        hoy = timezone.now().date()
        if hasattr(self, 'observaciones_activas'):
            return self.observaciones_activas
        return self.observaciones.filter(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gt=hoy))

    def get_observaciones_pasadas(self):
        hoy = timezone.now().date()
        if hasattr(self, 'observaciones_pasadas'):
            return self.observaciones_pasadas
        return self.observaciones.filter(fecha_fin__isnull=False, fecha_fin__lte=hoy)
    
    def estado_cuota(self):
        if not self.pagos.exists():
            return 'sin_pagos_registrados'
        
        hoy = timezone.now().date()
        ultimo_pago = self.pagos.order_by('-fecha_vencimiento').first()
        if not ultimo_pago:
            return 'vencida'
        if ultimo_pago.fecha_vencimiento < hoy:
            return 'vencida'
        elif (ultimo_pago.fecha_vencimiento - hoy).days <= 3:
            return 'por_vencer'
        else:
            return 'al_dia'
        
    def modalidad_actual(self):
        # Obtiene la modalidad actual del socio
        
        return self.historial_modalidades.filter(
            fecha_fin__isnull=True
        ).order_by('-fecha_inicio').first()


    def cantidad_asistencias_semana_actual(self):
        inicio_semana = now().date() - timedelta(days=now().weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        return self.registroentrada_set.filter(
            fecha_hora__date__range=(inicio_semana, fin_semana)
        ).count()

    def excedio_asistencias_semanales(self):
        modalidad = self.modalidad_actual()
        if not modalidad:
            return True
        
        limite = modalidad.modalidad.dias_por_semana
        cantidad = self.cantidad_asistencias_semana_actual()
        return cantidad > limite
    
    # Método para saber cuantos días hace que el socio no asiste
    def dias_sin_asistir(self):
        if not self.registroentrada_set.exists():
            return "-"
        ultima_asistencia = self.registroentrada_set.order_by('-fecha_hora').first()
        return (now().date() - ultima_asistencia.fecha_hora.date()).days

    
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

