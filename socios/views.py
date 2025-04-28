from django.shortcuts import render, redirect, get_object_or_404
from .forms import SocioForm
from .models import Socio
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Socio
from pagos.models import Pago
from datetime import date, timedelta

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

def detalle_socio(request, id):
    socio = get_object_or_404(Socio, id=id)
    pagos = Pago.objects.filter(socio=socio).order_by('-fecha_pago')

    estado_cuota = 'Sin pagos registrados'
    color_cuota = 'secondary'

    if pagos.exists():
        ultimo_pago = pagos.first()
        hoy = date.today()
        fecha_vencimiento = ultimo_pago.fecha_vencimiento

        if fecha_vencimiento >= hoy + timedelta(days=5):
            estado_cuota = 'Al día'
            color_cuota = 'success'
        elif hoy <= fecha_vencimiento < hoy + timedelta(days=5):
            estado_cuota = 'Por vencer'
            color_cuota = 'warning'
        else:
            estado_cuota = 'Vencido'
            color_cuota = 'danger'

    return render(request, 'socios/detalle_socio.html', {
        'socio': socio,
        'pagos': pagos,
        'estado_cuota': estado_cuota,
        'color_cuota': color_cuota,
    })


