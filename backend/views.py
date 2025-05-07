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
from django.db.models import Q

def home(request):
    hoy = date.today()
    primer_dia_mes = hoy.replace(day=1)

    filtro = request.GET.get('filtro', 'hoy')  # valor por defecto: hoy
    grupo = request.GET.get('grupo')  # 👈 nuevo

    total_socios = Socio.objects.filter().count()
    asistencias_hoy = RegistroEntrada.objects.filter(fecha_hora__date=hoy).count()

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

    # Esto debería refactorizarse, hacerse dentro del modelo de socio
    socios = Socio.objects.all()
    socios_con_pago = []
    socios_sin_pago = []
    for socio in socios:
        if socio.estado_cuota() == 'al_dia':
            socios_con_pago.append(socio.id)
        else:
            socios_sin_pago.append(socio.id)

    asistencias_mes = RegistroEntrada.objects.filter(
        fecha_hora__date__gte=primer_dia_mes
    ).values_list('socio_id', flat=True).distinct()

    socios_no_pago_sin_asistencia = Socio.objects.filter(id__in=socios_sin_pago).exclude(id__in=asistencias_mes).count()
    socios_no_pago_con_asistencia = Socio.objects.filter(id__in=socios_sin_pago).filter(id__in=asistencias_mes).count()
    socios_con_pago_sin_asistencia = Socio.objects.filter(id__in=socios_con_pago).exclude(id__in=asistencias_mes).count()
    socios_con_pago_con_asistencia = Socio.objects.filter(id__in=socios_con_pago).filter(id__in=asistencias_mes).count()

    socios_detalle = []
    titulo_detalle = ""

    if grupo:
        if grupo == 'no_pago_sin_asistencia':
            socios_detalle = Socio.objects.filter(id__in=socios_sin_pago).exclude(id__in=asistencias_mes)
            titulo_detalle = "Socios no pagos y sin asistencias en el mes"
        elif grupo == 'no_pago_con_asistencia':
            socios_detalle = Socio.objects.filter(id__in=socios_sin_pago).filter(id__in=asistencias_mes)
            titulo_detalle = "Socios no pagos y con asistencias en el mes"
        elif grupo == 'pago_sin_asistencia':
            socios_detalle = Socio.objects.filter(id__in=socios_con_pago).exclude(id__in=asistencias_mes)
            titulo_detalle = "Socios pagos y sin asistencias en el mes"
        elif grupo == 'pago_con_asistencia':
            socios_detalle = Socio.objects.filter(id__in=socios_con_pago).filter(id__in=asistencias_mes)
            titulo_detalle = "Socios pagos y con asistencias en el mes"

    context = {
        'total_socios': total_socios,
        'asistencias_hoy': asistencias_hoy,
        'horas': horas,
        'cantidades': cantidades,
        'filtro': filtro,
        'grupo': grupo,
        'titulo_detalle': titulo_detalle,
        'socios_detalle': socios_detalle,
        'socios_no_pago_sin_asistencia': socios_no_pago_sin_asistencia,
        'socios_no_pago_con_asistencia': socios_no_pago_con_asistencia,
        'socios_con_pago_sin_asistencia': socios_con_pago_sin_asistencia,
        'socios_con_pago_con_asistencia': socios_con_pago_con_asistencia,
    }
    return render(request, 'home.html', context)
