from django.shortcuts import render
from .models import RegistroEntrada
from datetime import date
from django.db.models import Q
from django.http import JsonResponse
from socios.models import Socio
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import RegistroEntrada
from socios.models import Socio
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from socios.models import Observacion
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from ejercicios.models import Ejercicio, RegistroEjercicio

def listar_entradas(request):
    hoy = date.today()

    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    socio = request.GET.get('socio')

    entradas = RegistroEntrada.objects.all()

    if fecha_desde:
        entradas = entradas.filter(fecha_hora__date__gte=fecha_desde)

    if fecha_hasta:
        entradas = entradas.filter(fecha_hora__date__lte=fecha_hasta)

    if socio:
        entradas = entradas.filter(
            Q(socio__nombre__icontains=socio) | 
            Q(socio__apellido__icontains=socio)
        )

    if not fecha_desde and not fecha_hasta and not socio:
        entradas = entradas.filter(fecha_hora__date=hoy)

    entradas = entradas.order_by('-fecha_hora')

    return render(request, 'registros/listar_entradas.html', {
        'entradas': entradas,
        'fecha_desde': fecha_desde or hoy.strftime('%Y-%m-%d'),
        'fecha_hasta': fecha_hasta or hoy.strftime('%Y-%m-%d'),
        'socio': socio or '',
    })

def registrar_entrada(request):
    ahora = now()
    inicio_hora = ahora.replace(minute=0, second=0, microsecond=0)
    fin_hora = ahora.replace(minute=59, second=59, microsecond=999999)

    observaciones_activas = Prefetch(
    'socio__observaciones',
    queryset=Observacion.objects.filter(
        Q(fecha_fin__isnull=True) | Q(fecha_fin__gt=ahora.date())
    ),
    to_attr='observaciones_activas'
    )

    observaciones_pasadas = Prefetch(
        'socio__observaciones',
        queryset=Observacion.objects.filter(
            fecha_fin__isnull=False, fecha_fin__lte=ahora.date()
        ),
        to_attr='observaciones_pasadas'
    )

    entradas_hoy = RegistroEntrada.objects.filter(
        fecha_hora__range=(inicio_hora, fin_hora)
    ).select_related('socio').prefetch_related(
        Prefetch('socio', queryset=Socio.objects.prefetch_related(observaciones_activas, observaciones_pasadas))
    )


    ejercicios = Ejercicio.objects.all().order_by('nombre')

    return render(request, 'registros/registrar_entrada.html', {
        'entradas_hora': entradas_hoy,
        'ejercicios': ejercicios,
    })


def buscar_socios(request):
    q = request.GET.get('q', '')
    socios = Socio.objects.filter(
        Q(nombre__icontains=q) | Q(apellido__icontains=q)
    )[:10]
    resultados = [
        {'id': socio.id, 'nombre_completo': f'{socio.nombre} {socio.apellido}'}
        for socio in socios
    ]
    return JsonResponse(resultados, safe=False)

@require_POST
def confirmar_entrada(request):
    socio_id = request.POST.get('socio_id')
    if socio_id:
        socio = Socio.objects.filter(id=socio_id).first()
        if socio:
            RegistroEntrada.objects.create(socio=socio)
            messages.success(request, f'Entrada registrada para {socio.nombre} {socio.apellido}.')
        else:
            messages.error(request, 'Socio no encontrado.')
    else:
        messages.error(request, 'No se proporcionó un ID de socio.')
    return redirect('registrar_entrada')

def eliminar_entrada(request, id):
    entrada = get_object_or_404(RegistroEntrada, id=id)
    entrada.delete()
    messages.success(request, f"Asistencia de {entrada.socio} eliminada correctamente.")
    return redirect('registrar_entrada')
