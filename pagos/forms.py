from django import forms
from .models import Pago
from datetime import date
from django.db.models import Q
import locale
from calendar import month_name

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['socio', 'monto', 'fecha_vencimiento']  # Solo campos del modelo
        widgets = {
            'socio': forms.Select(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'format': 'yyyy-mm-dd'}),
        }

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        socio = self.cleaned_data.get('socio')
        
        # Validar que la fecha no sea anterior a hoy
        if fecha_vencimiento and fecha_vencimiento < date.today():
            raise forms.ValidationError("La fecha de vencimiento no puede ser anterior a hoy.")
        
        # Validar que no exista otro pago para el mismo socio con vencimiento en el mismo mes
        if socio and fecha_vencimiento:
            # Si estamos editando un pago existente, excluirlo de la validación
            instance_id = self.instance.id if self.instance and self.instance.pk else None
            
            # Buscar pagos del mismo socio con vencimiento en el mismo mes y año
            mismo_mes_pagos = Pago.objects.filter(
                Q(socio=socio) &
                Q(fecha_vencimiento__year=fecha_vencimiento.year) &
                Q(fecha_vencimiento__month=fecha_vencimiento.month)
            )
            
            # Si estamos editando, excluir el pago actual
            if instance_id:
                mismo_mes_pagos = mismo_mes_pagos.exclude(id=instance_id)
            
            if mismo_mes_pagos.exists():
                # Nombres de los meses en español
                meses_es = {
                    1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
                    5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
                    9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
                }
                
                # Obtener el nombre del mes en español
                mes_es = meses_es[fecha_vencimiento.month]
                
                raise forms.ValidationError(
                    f"Ya existe un pago para {socio} con vencimiento en {mes_es} {fecha_vencimiento.year}."
                )
                
        return fecha_vencimiento
