from django.shortcuts import render
from socios.models import Socio
from registros.models import RegistroEntrada
from pagos.models import Pago
from datetime import date
from django.db.models.functions import ExtractHour
from django.db.models import Count

from django.db.models.functions import ExtractHour
from django.db.models import Count
from django.utils.timezone import now
from datetime import date, timedelta

def home(request):
    hoy = date.today()

    filtro = request.GET.get('filtro', 'hoy')  # valor por defecto: hoy

    total_socios = Socio.objects.filter().count()
    asistencias_hoy = RegistroEntrada.objects.filter(fecha_hora__date=hoy).count()
    pagos_mes = Pago.objects.filter(
        fecha_pago__year=hoy.year,
        fecha_pago__month=hoy.month
    )

    total_pagos_mes = sum(pago.monto for pago in pagos_mes)

    # 📊 Asistencias filtradas
    asistencias = RegistroEntrada.objects.all()

    if filtro == 'hoy':
        asistencias = asistencias.filter(fecha_hora__date=hoy)
    elif filtro == 'semana':
        hace_7_dias = hoy - timedelta(days=7)
        asistencias = asistencias.filter(fecha_hora__date__gte=hace_7_dias)
    elif filtro == 'mes':
        asistencias = asistencias.filter(
            fecha_hora__year=hoy.year,
            fecha_hora__month=hoy.month
        )

    asistencias_por_hora = (
        asistencias
        .annotate(hora=ExtractHour('fecha_hora'))
        .values('hora')
        .annotate(cantidad=Count('id'))
        .order_by('hora')
    )

    horas = [registro['hora'] for registro in asistencias_por_hora]
    cantidades = [registro['cantidad'] for registro in asistencias_por_hora]

    context = {
        'total_socios': total_socios,
        'asistencias_hoy': asistencias_hoy,
        'total_pagos_mes': total_pagos_mes,
        'horas': horas,
        'cantidades': cantidades,
        'filtro': filtro,  # para mantener el select correcto
    }
    return render(request, 'home.html', context)

