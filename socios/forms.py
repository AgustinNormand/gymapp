from django import forms
from .models import Socio
from modalidades.models import Modalidad

class SocioForm(forms.ModelForm):
    modalidad = forms.ModelChoiceField(
        queryset=Modalidad.objects.all(),
        required=True,
        label="Modalidad",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'dni', 'email', 'telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }
