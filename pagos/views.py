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

def registrar_pago(request):
    socio_id = request.GET.get('socio_id')
    socio = None
    modalidad_actual = None
    monto_sugerido = 20000  # Valor por defecto

    if socio_id:
        socio = Socio.objects.get(id=socio_id)
        modalidad_actual = HistorialModalidad.objects.filter(
            socio=socio, fecha_fin__isnull=True
        ).order_by('-fecha_inicio').first()

        if modalidad_actual:
            monto_sugerido = modalidad_actual.precio_en_el_momento

    # Calcular fecha de vencimiento
    hoy = date.today()
    ultimo_dia_mes = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.socio = socio  # Forzar socio correcto
            pago.monto = monto_sugerido  # Forzar monto correcto
            pago.save()
            return redirect('pagos:listar_pagos')
    else:
        initial_data = {
            'fecha_vencimiento': ultimo_dia_mes,
            'monto': monto_sugerido,
            'socio': socio,
            'modalidad_actual': modalidad_actual.modalidad.nombre if modalidad_actual else 'Sin modalidad'
        }
        form = PagoForm(initial=initial_data)


    return render(request, 'pagos/registrar_pago.html', {'form': form})


def listar_pagos(request):
    pagos = Pago.objects.select_related('socio').order_by('-fecha_pago')
    return render(request, 'pagos/listar_pagos.html', {'pagos': pagos})
