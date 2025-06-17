from .models import RegistroEntrada
from datetime import date
from django.db.models import Q
from django.http import JsonResponse
from socios.models import Socio
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Prefetch, Count, Avg, F, Q
from django.db.models.functions import TruncWeek, TruncMonth
from socios.models import Observacion, Socio
from modalidades.models import Modalidad
from django.shortcuts import get_object_or_404
from ejercicios.models import Ejercicio
from datetime import datetime, timedelta
from django.utils.timezone import now
from decimal import Decimal


def evolucion_semanal(request):
    # Obtener el mes actual y el anterior
    hoy = now().date()
    primer_dia_mes_actual = hoy.replace(day=1)
    ultimo_dia_mes_anterior = primer_dia_mes_actual - timedelta(days=1)
    primer_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
    
    # Obtener todas las modalidades ordenadas por días por semana (de menor a mayor)
    modalidades = Modalidad.objects.all().order_by('dias_por_semana')
    
    # Obtener todos los socios activos (que tengan al menos un pago vigente o hayan asistido en los últimos 30 días)
    socios = Socio.objects.filter(
        Q(pagos__fecha_vencimiento__gte=hoy) | 
        Q(registroentrada__fecha_hora__date__gte=hoy-timedelta(days=30))
    ).distinct()
    
    # Preparar datos para cada socio
    estadisticas = []
    
    for socio in socios:
        # Obtener modalidad actual
        modalidad_actual = socio.modalidad_actual()
        
        # Obtener modalidad del mes anterior
        modalidad_mes_anterior = socio.historial_modalidades.filter(
            fecha_inicio__lte=ultimo_dia_mes_anterior,
        ).order_by('-fecha_inicio').first()
        
        # Calcular asistencias por semana del mes actual
        asistencias_mes_actual = socio.registroentrada_set.filter(
            fecha_hora__date__range=(primer_dia_mes_actual, hoy)
        ).annotate(
            semana=TruncWeek('fecha_hora')
        ).values('semana').annotate(
            total=Count('id')
        ).aggregate(
            promedio=Avg('total')
        )['promedio'] or 0
        
        # Calcular asistencias por semana del mes anterior
        asistencias_mes_anterior = socio.registroentrada_set.filter(
            fecha_hora__date__range=(primer_dia_mes_anterior, ultimo_dia_mes_anterior)
        ).annotate(
            semana=TruncWeek('fecha_hora')
        ).values('semana').annotate(
            total=Count('id')
        ).aggregate(
            promedio=Avg('total')
        )['promedio'] or 0
        
        # Calcular diferencia de promedios
        diferencia = round(asistencias_mes_actual, 1) - (round(asistencias_mes_anterior, 1) if asistencias_mes_anterior else 0)
        
        # Inicializar variables
        mejor_modalidad = None
        ahorro_posible = Decimal('0.00')
        
        # Si no hay asistencias en el mes actual, no mostrar recomendación
        if asistencias_mes_actual == 0:
            mejor_modalidad = None
            ahorro_posible = Decimal('0.00')
        elif modalidad_actual and modalidad_actual.modalidad:
            promedio_redondeado = round(asistencias_mes_actual)
            
            # Obtener todas las modalidades que cubran el promedio
            # y tengan MENOS días que la actual (para no sugerir cambios laterales)
            modalidades_validas = [
                m for m in modalidades 
                if m.dias_por_semana >= promedio_redondeado and 
                   m.dias_por_semana < modalidad_actual.modalidad.dias_por_semana
            ]
            
            # Ordenar por precio (más barata primero) y luego por ID para consistencia
            modalidades_validas.sort(key=lambda x: (x.precio, x.id))
            
            # Si hay modalidades válidas, tomar la más barata
            if modalidades_validas:
                mejor_modalidad_candidata = modalidades_validas[0]
                
                # Solo sugerir cambio si hay un ahorro real
                # y la modalidad candidata tiene MENOS días que la actual
                if (mejor_modalidad_candidata.precio < modalidad_actual.modalidad.precio and 
                    mejor_modalidad_candidata.dias_por_semana < modalidad_actual.modalidad.dias_por_semana):
                    mejor_modalidad = mejor_modalidad_candidata
                    ahorro_posible = modalidad_actual.modalidad.precio - mejor_modalidad.precio
                else:
                    mejor_modalidad = modalidad_actual.modalidad
                    ahorro_posible = Decimal('0.00')
            else:
                # Si no hay modalidades que cubran el promedio con menos días, mantener la actual
                mejor_modalidad = modalidad_actual.modalidad
                ahorro_posible = Decimal('0.00')
        
        estadisticas.append({
            'socio': socio,
            'modalidad_actual': modalidad_actual.modalidad if modalidad_actual else None,
            'modalidad_mes_anterior': modalidad_mes_anterior.modalidad if modalidad_mes_anterior else None,
            'promedio_semanal_actual': round(asistencias_mes_actual, 1),
            'promedio_semanal_anterior': round(asistencias_mes_anterior, 1) if asistencias_mes_anterior else 0,
            'diferencia': round(diferencia, 1),
            'mejor_modalidad': mejor_modalidad,
            'ahorro_posible': ahorro_posible if ahorro_posible > 0 else Decimal('0.00'),
            'puede_ahorrar': ahorro_posible > 0
        })
    
    # Ordenar por nombre de socio
    estadisticas = sorted(estadisticas, key=lambda x: (x['socio'].apellido, x['socio'].nombre))
    
    # Diccionario de meses en español
    meses_espanol = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    mes_actual_str = f"{meses_espanol[primer_dia_mes_actual.month]} {primer_dia_mes_actual.year}"
    mes_anterior_str = f"{meses_espanol[primer_dia_mes_anterior.month]} {primer_dia_mes_anterior.year}"
    
    return render(request, 'registros/evolucion_semanal.html', {
        'estadisticas': estadisticas,
        'mes_actual': mes_actual_str,
        'mes_anterior': mes_anterior_str,
    })

############ ABM de Entradas ############

@require_POST
def alta_entrada(request):
    # Este método se encarga de confirmar la entrada de un socio al gimnasio.
    # Se recibe el ID del socio desde el formulario y se busca en la base de datos.
    # Si se encuentra, se crea un nuevo registro de entrada y se redirige a la vista de registro de entrada.
    # Si no se encuentra, se muestra un mensaje de error.
    # Se utiliza el decorador @require_POST para asegurarse de que solo se acepten solicitudes POST.

    socio_id = request.POST.get('socio_id')
    if socio_id:
        socio = Socio.objects.filter(id=socio_id).first()
        if socio:
            # Verificar si ya existe un registro para este socio en la hora actual
            ahora = now()
            inicio_hora = ahora.replace(minute=0, second=0, microsecond=0)
            fin_hora = ahora.replace(minute=59, second=59, microsecond=999999)
            
            # Buscar si ya existe un registro para este socio en la hora actual
            registro_existente = RegistroEntrada.objects.filter(
                socio=socio,
                fecha_hora__range=(inicio_hora, fin_hora)
            ).exists()
            
            if registro_existente:
                messages.warning(request, f'Ya existe un registro de entrada para {socio.nombre} {socio.apellido} en esta hora.')
            else:
                RegistroEntrada.objects.create(socio=socio)
                messages.success(request, f'Entrada registrada para {socio.nombre} {socio.apellido}.')
        else:
            messages.error(request, 'Socio no encontrado.')
    else:
        messages.error(request, 'No se proporcionó un ID de socio.')
    
    # Si se registró correctamente la asistencia, redirigir con el ID del socio como parámetro
    from django.urls import reverse
    if socio_id and socio:
        url = reverse('registrar_entrada')
        return redirect(f'{url}?registrado={socio_id}')
    else:
        return redirect('registrar_entrada')

def eliminar_entrada(request, id):
    # Este método se encarga de eliminar la entrada de un socio al gimnasio.
    # Se recibe el ID de la entrada a eliminar y se busca en la base de datos.
    # Si se encuentra, se elimina y se redirige a la vista de registro de entrada.
    # Si no se encuentra, se muestra un mensaje de error.

    entrada = get_object_or_404(RegistroEntrada, id=id)
    entrada.delete()

    messages.success(request, f"Asistencia de {entrada.socio} eliminada correctamente.")
    #return redirect('registrar_entrada')
    return redirect(request.META.get('HTTP_REFERER', '/'))

# No se permiten modificaciones a las entradas ya registradas, por fuera del admin

############ Otros métodos ############

def registrar_entrada(request):
    # Este método se encarga de registrar la entrada de un socio al gimnasio.

    ahora = now()
    inicio_hora = ahora.replace(minute=0, second=0, microsecond=0)
    fin_hora = ahora.replace(minute=59, second=59, microsecond=999999)
    
    # Calcular inicio y fin de la semana actual (lunes a domingo)
    hoy = ahora.date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)

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

    # Verificar si algún socio de las entradas registradas cumple años esta semana
    socios_cumpleanos = []
    for entrada in entradas_hoy:
        socio = entrada.socio
        if socio.fecha_nacimiento:
            fecha_cumple_este_anio = socio.fecha_nacimiento.replace(year=hoy.year)
            if inicio_semana <= fecha_cumple_este_anio <= fin_semana:
                socios_cumpleanos.append({
                    'id': socio.id,
                    'nombre': socio.nombre,
                    'apellido': socio.apellido,
                    'fecha_cumple': fecha_cumple_este_anio
                })

    ejercicios = Ejercicio.objects.all().order_by('nombre')

    return render(request, 'registros/registrar_entrada.html', {
        'entradas_hora': entradas_hoy,
        'ejercicios': ejercicios,
        'socios_cumpleanos': socios_cumpleanos,
    })

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







