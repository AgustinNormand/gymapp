from django.shortcuts import render, redirect
from .models import Pago
from socios.models import Socio
from .forms import PagoForm
from calendar import monthrange
from datetime import date
from .models import Pago
from socios.models import Socio
from datetime import date
from calendar import monthrange

from pagos.models import Pago
from socios.models import Socio
from modalidades.models import HistorialModalidad
from calendar import monthrange
from datetime import date
from django.contrib import messages

def registrar_pago(request):
    socio_id = request.GET.get('socio_id')
    socio = None
    modalidad_actual = None
    monto_sugerido = 20000  # Default por si no hay modalidad

    if socio_id:
        socio = Socio.objects.get(id=socio_id)
        modalidad_actual = HistorialModalidad.objects.filter(
            socio=socio, fecha_fin__isnull=True
        ).order_by('-fecha_inicio').first()

        if modalidad_actual:
            monto_sugerido = modalidad_actual.precio_en_el_momento
        else:
            # 🚨 No tiene modalidad activa
            messages.error(request, "El socio no tiene una modalidad activa asignada. No se puede registrar el pago.")
            return redirect('socios:listar_socios') 
    else:
        # 🚨 No se envió el ID de socio
        messages.error(request, "No se ha proporcionado un ID de socio válido.")
        return redirect('socios:listar_socios') 

    hoy = date.today()
    ultimo_dia_mes = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.socio = socio
            pago.monto = monto_sugerido
            pago.save()

            messages.success(request, f"Pago registrado correctamente para {socio.nombre} {socio.apellido}.")

            return redirect('pagos:listar_pagos')
    else:
        initial_data = {
            'fecha_vencimiento': ultimo_dia_mes,
            'socio': socio.id if socio else None,
            'monto': monto_sugerido,
        }
        form = PagoForm(initial=initial_data)


    return render(request, 'pagos/registrar_pago.html', {
        'form': form,
        'socio': socio,
        'modalidad_actual': modalidad_actual,
        'monto_sugerido': monto_sugerido,
    })


def listar_pagos(request):
    pagos = Pago.objects.select_related('socio').order_by('-fecha_pago')
    return render(request, 'pagos/listar_pagos.html', {'pagos': pagos})
