from django import forms
from .models import RegistroEntrada

class RegistroEntradaForm(forms.ModelForm):
    class Meta:
        model = RegistroEntrada
        fields = ['socio']
