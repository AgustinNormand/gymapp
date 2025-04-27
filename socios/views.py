from django.shortcuts import render, redirect, get_object_or_404
from .forms import SocioForm
from .models import Socio
from django.contrib import messages

def alta_socio(request):
    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Socio creado exitosamente.')
            return redirect('socios:listar_socios')
        else:
            messages.error(request, 'Error al crear el socio. Por favor revisá el formulario.')
    else:
        form = SocioForm()
    return render(request, 'socios/alta_socio.html', {'form': form})


def listar_socios(request):
    socios = Socio.objects.all()
    return render(request, 'socios/listar_socios.html', {'socios': socios})


def eliminar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)
    socio.delete()
    messages.success(request, 'Socio eliminado exitosamente.')
    return redirect('socios:listar_socios')


def editar_socio(request, id):
    socio = get_object_or_404(Socio, id=id)
    if request.method == 'POST':
        form = SocioForm(request.POST, instance=socio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Socio actualizado exitosamente.')
            return redirect('socios:listar_socios')
        else:
            messages.error(request, 'Hubo un error al actualizar el socio. Por favor revisá el formulario.')
    else:
        form = SocioForm(instance=socio)
    return render(request, 'socios/editar_socio.html', {'form': form})
