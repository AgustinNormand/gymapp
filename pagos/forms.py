from django import forms
from .models import Pago
from datetime import date

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['socio', 'monto', 'fecha_vencimiento']  # Solo campos del modelo
        widgets = {
            'socio': forms.Select(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control-plaintext', 'readonly': 'readonly'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        if fecha_vencimiento and fecha_vencimiento < date.today():
            raise forms.ValidationError("La fecha de vencimiento no puede ser anterior a hoy.")
        return fecha_vencimiento
