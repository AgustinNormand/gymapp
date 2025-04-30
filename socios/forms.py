from django import forms
from .models import Socio, Observacion
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
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['telefono'].required = False
        self.fields['fecha_nacimiento'].required = False


class SocioEditForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'apellido', 'email', 'telefono', 'fecha_nacimiento']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['telefono'].required = False
        self.fields['fecha_nacimiento'].required = False


class ObservacionForm(forms.ModelForm):
    class Meta:
        model = Observacion
        fields = ['descripcion', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_fin'].required = False  # (por si acaso aseguramos que no sea requerido)
        self.fields['fecha_fin'].label = 'Fecha de Fin (opcional)'
