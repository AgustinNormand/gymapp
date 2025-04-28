from django.shortcuts import render
from socios.models import Socio
from registros.models import RegistroEntrada
from pagos.models import Pago
from datetime import date

def home(request):
    hoy = date.today()

    total_socios = Socio.objects.filter().count()
    asistencias_hoy = RegistroEntrada.objects.filter(fecha_hora__date=hoy).count()
    pagos_mes = Pago.objects.filter(
        fecha_pago__year=hoy.year,
        fecha_pago__month=hoy.month
    )

    total_pagos_mes = sum(pago.monto for pago in pagos_mes)

    context = {
        'total_socios': total_socios,
        'asistencias_hoy': asistencias_hoy,
        'total_pagos_mes': total_pagos_mes,
    }
    return render(request, 'home.html', context)
