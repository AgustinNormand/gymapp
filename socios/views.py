from django.shortcuts import render, redirect, get_object_or_404
from .forms import SocioForm
from .models import Socio
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from .models import Socio
from pagos.models import Pago
from datetime import date, timedelta
from modalidades.models import Modalidad, HistorialModalidad
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

def alta_socio(request):
    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save()

            # Nueva parte: guardar el historial de modalidad
            modalidad = form.cleaned_data['modalidad']
            hoy = timezone.now().date()

            HistorialModalidad.objects.create(
                socio=socio,
                modalidad=modalidad,
                precio_en_el_momento=modalidad.precio,
                fecha_inicio=hoy
            )

            messages.success(request, 'Socio creado exitosamente.')
            return redirect('socios:listar_socios')
        else:
            messages.error(request, 'Error al crear el socio. Por favor revisá el formulario.')
    else:
        form = SocioForm()
    return render(request, 'socios/alta_socio.html', {'form': form})



def listar_socios(request):
    socios = Socio.objects.all()

    socios_info = []
    hoy = date.today()

    for socio in socios:
        pagos = Pago.objects.filter(socio=socio).order_by('-fecha_pago')

        estado_cuota = 'Sin pagos'
        color_cuota = 'secondary'

        if pagos.exists():
            ultimo_pago = pagos.first()
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

        socios_info.append({
            'socio': socio,
            'estado_cuota': estado_cuota,
            'color_cuota': color_cuota,
        })

    return render(request, 'socios/listar_socios.html', {'socios_info': socios_info})


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

    # Modalidad actual
    modalidad_actual = HistorialModalidad.objects.filter(
        socio=socio, fecha_fin__isnull=True
    ).order_by('-fecha_inicio').first()

    # Historial de modalidades
    historial_modalidades = HistorialModalidad.objects.filter(socio=socio).order_by('-fecha_inicio')

    return render(request, 'socios/detalle_socio.html', {
        'socio': socio,
        'pagos': pagos,
        'estado_cuota': estado_cuota,
        'color_cuota': color_cuota,
        'modalidad_actual': modalidad_actual,
        'historial_modalidades': historial_modalidades,
    })





def cambiar_modalidad(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)
    modalidades = Modalidad.objects.all()

    if request.method == 'POST':
        nueva_modalidad_id = request.POST.get('modalidad')
        nueva_modalidad = Modalidad.objects.get(id=nueva_modalidad_id)

        hoy = timezone.now().date()

        # Cerrar historial anterior
        historial_actual = HistorialModalidad.objects.filter(socio=socio, fecha_fin__isnull=True).first()
        if historial_actual:
            historial_actual.fecha_fin = hoy
            historial_actual.save()

        # Crear nuevo historial
        HistorialModalidad.objects.create(
            socio=socio,
            modalidad=nueva_modalidad,
            precio_en_el_momento=nueva_modalidad.precio,
            fecha_inicio=hoy,
            fecha_fin=None
        )


        return redirect('socios:listar_socios')  # Volvemos a la lista de socios

    return render(request, 'socios/cambiar_modalidad.html', {'socio': socio, 'modalidades': modalidades})


