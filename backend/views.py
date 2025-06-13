from django.shortcuts import render
from socios.models import Socio
from registros.models import RegistroEntrada
from pagos.models import Pago
from datetime import date, datetime, timedelta
from django.db.models.functions import ExtractHour, ExtractMonth, ExtractYear
from django.db.models import Count, Q
from django.utils.timezone import now

def home(request):
    hoy = date.today()
    grupo = request.GET.get('grupo', '')  # Obtener el parámetro 'grupo' de la URL, vacío por defecto
    primer_dia_mes = hoy.replace(day=1)  # Definir al inicio para usarlo en todo el contexto
    total_socios = Socio.objects.filter().count()
    asistencias_hoy = RegistroEntrada.objects.filter(fecha_hora__date=hoy).count()
    
    # --- Gráfico de asistencias por mes ---
    # Obtener parámetros de fechas para el gráfico mensual
    fecha_inicio_mes = request.GET.get('fecha_inicio_mes')
    fecha_fin_mes = request.GET.get('fecha_fin_mes')
    
    # Validar y establecer fechas por defecto para el gráfico mensual (últimos 12 meses)
    try:
        if fecha_inicio_mes and fecha_fin_mes:
            fecha_inicio_mes = datetime.strptime(fecha_inicio_mes, '%Y-%m-%d').date()
            fecha_fin_mes = datetime.strptime(fecha_fin_mes, '%Y-%m-%d').date()
        else:
            fecha_fin_mes = hoy
            fecha_inicio_mes = fecha_fin_mes - timedelta(days=365)  # Últimos 12 meses por defecto
    except (ValueError, TypeError):
        fecha_fin_mes = hoy
        fecha_inicio_mes = fecha_fin_mes - timedelta(days=365)  # Últimos 12 meses por defecto
    
    # Asegurarse de que la fecha de inicio sea menor que la de fin
    if fecha_inicio_mes >= fecha_fin_mes:
        fecha_inicio_mes = fecha_fin_mes - timedelta(days=30)  # Mostrar al menos 1 mes

    # Obtener datos para el gráfico de asistencias por mes
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_etiquetas = []
    cantidades_mes = []
    
    # Generar lista de meses en el rango seleccionado
    current_date = date(fecha_inicio_mes.year, fecha_inicio_mes.month, 1)
    end_date = date(fecha_fin_mes.year, fecha_fin_mes.month, 1)
    
    while current_date <= end_date:
        # Obtener el primer y último día del mes
        primer_dia = current_date
        if current_date.month == 12:
            ultimo_dia = date(current_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            ultimo_dia = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
        
        # Ajustar fechas según el rango seleccionado
        if primer_dia < fecha_inicio_mes:
            primer_dia = fecha_inicio_mes
        if ultimo_dia > fecha_fin_mes:
            ultimo_dia = fecha_fin_mes
        
        # Contar asistencias de socios únicos para este mes
        try:
            # Asegurarse de que las fechas sean válidas
            if primer_dia > ultimo_dia:
                total_asistencias = 0
            else:
                total_asistencias = RegistroEntrada.objects.filter(
                    fecha_hora__date__range=(primer_dia, ultimo_dia)
                ).values('socio').distinct().count()
            
            # Formatear la etiqueta del mes
            etiqueta_mes = f"{meses_nombres[current_date.month-1]}/{str(current_date.year)[2:]}"
            
            # Agregar a las listas
            meses_etiquetas.append(etiqueta_mes)
            cantidades_mes.append(total_asistencias)
            
        except Exception:
            etiqueta_mes = f"{meses_nombres[current_date.month-1]}/{str(current_date.year)[2:]}"
            meses_etiquetas.append(etiqueta_mes)
            cantidades_mes.append(0)
        
        # Pasar al primer día del siguiente mes
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    # --- Gráfico de asistencias por hora ---
    # Obtener parámetros de fechas para el gráfico de horas
    fecha_inicio_hora = request.GET.get('fecha_inicio_hora')
    fecha_fin_hora = request.GET.get('fecha_fin_hora')
    
    # Validar y establecer fechas por defecto para el gráfico de horas
    try:
        if fecha_inicio_hora and fecha_fin_hora:
            fecha_inicio_hora = datetime.strptime(fecha_inicio_hora, '%Y-%m-%d').date()
            fecha_fin_hora = datetime.strptime(fecha_fin_hora, '%Y-%m-%d').date()
            
            # Asegurarse de que la fecha de inicio sea menor o igual que la de fin
            if fecha_inicio_hora > fecha_fin_hora:
                fecha_inicio_hora, fecha_fin_hora = fecha_fin_hora, fecha_inicio_hora
        else:
            # Por defecto, mostrar solo el día actual
            fecha_inicio_hora = hoy
            fecha_fin_hora = hoy
    except (ValueError, TypeError):
        # En caso de error, mostrar solo el día actual
        fecha_inicio_hora = hoy
        fecha_fin_hora = hoy
        
    # Obtener parámetros de fechas para el gráfico de meses
    fecha_inicio_mes = request.GET.get('fecha_inicio')
    fecha_fin_mes = request.GET.get('fecha_fin')
    
    # Validar y establecer fechas por defecto para el gráfico de meses
    try:
        if fecha_inicio_mes and fecha_fin_mes:
            fecha_inicio_mes = datetime.strptime(fecha_inicio_mes, '%Y-%m-%d').date()
            fecha_fin_mes = datetime.strptime(fecha_fin_mes, '%Y-%m-%d').date()
        else:
            # Por defecto, mostrar los últimos 12 meses completos
            # Establecer la fecha de fin al último día del mes actual
            primer_dia_prox_mes = date(hoy.year + (hoy.month == 12), (hoy.month % 12) + 1, 1)
            fecha_fin_mes = primer_dia_prox_mes - timedelta(days=1)  # Último día del mes actual
            
            # Establecer la fecha de inicio al primer día del mes hace 11 meses
            primer_dia_mes_actual = hoy.replace(day=1)
            if primer_dia_mes_actual.month <= 11:
                fecha_inicio_mes = date(primer_dia_mes_actual.year - 1, 13 - primer_dia_mes_actual.month, 1)
            else:
                fecha_inicio_mes = date(primer_dia_mes_actual.year - 1, primer_dia_mes_actual.month - 11, 1)
    except (ValueError, TypeError):
        # En caso de error, usar el rango por defecto de 12 meses
        primer_dia_prox_mes = date(hoy.year + (hoy.month == 12), (hoy.month % 12) + 1, 1)
        fecha_fin_mes = primer_dia_prox_mes - timedelta(days=1)
        fecha_inicio_mes = date(fecha_fin_mes.year - 1, fecha_fin_mes.month, 1)
        
    # Determinar si es un solo día o un rango para el gráfico de horas
    es_un_solo_dia = (fecha_inicio_hora == fecha_fin_hora)
    
    # Obtener datos para el gráfico de asistencias por hora
    asistencias_por_hora = RegistroEntrada.objects.filter(
        fecha_hora__date__range=(fecha_inicio_hora, fecha_fin_hora)
    ).annotate(
        hora=ExtractHour('fecha_hora')
    ).values('hora').annotate(
        total_asistencias=Count('id')
    ).order_by('hora')
    
    # Crear lista completa de horas (0-23)
    horas_completas = [{'hora': h, 'cantidad': 0} for h in range(24)]
    
    # Procesar los resultados según si es un día o rango
    if es_un_solo_dia:
        # Para un solo día, mostrar el conteo exacto (números enteros)
        for registro in asistencias_por_hora:
            hora = registro['hora']
            if 0 <= hora <= 23:
                valor = int(registro['total_asistencias'])
                horas_completas[hora]['cantidad'] = valor
    else:
        # Para rango de días, calcular el promedio diario
        dias_rango = (fecha_fin_hora - fecha_inicio_hora).days + 1
        if dias_rango < 1:
            dias_rango = 1
            
        for registro in asistencias_por_hora:
            hora = registro['hora']
            if 0 <= hora <= 23:
                # Calcular el promedio redondeado a 1 decimal
                promedio = round(registro['total_asistencias'] / dias_rango, 1)
                horas_completas[hora]['cantidad'] = promedio
    
    # Ordenar por hora y preparar datos para el template
    horas_completas.sort(key=lambda x: x['hora'])
    horas = [f"{registro['hora']:02d}:00" for registro in horas_completas]
    cantidades = [float(registro['cantidad']) for registro in horas_completas]  # Asegurar que sean números flotantes
    
    # --- Lista de asistencias (filtro simple) ---
    filtro = request.GET.get('filtro', 'hoy')  # valor por defecto: hoy
    asistencias = RegistroEntrada.objects.all()
    
    if filtro == 'hoy':
        asistencias = asistencias.filter(fecha_hora__date=hoy)
    elif filtro == 'semana':
        hace_7_dias = hoy - timedelta(days=7)
        asistencias = asistencias.filter(fecha_hora__date__gte=hace_7_dias)
    elif filtro == 'mes':
        asistencias = asistencias.filter(fecha_hora__date__gte=primer_dia_mes)

    asistencias_por_hora = (
        asistencias
        .annotate(hora=ExtractHour('fecha_hora'))
        .values('hora')
        .annotate(cantidad=Count('id'))
        .order_by('hora')
    )

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

    # Preparar datos para los gráficos
    import json
    from django.utils.safestring import mark_safe
    
    # Depuración: Imprimir datos antes de la serialización
    print("Datos para gráfico de meses antes de serializar:")
    print("Meses etiquetas:", meses_etiquetas)
    print("Cantidades mes:", cantidades_mes)
    print("Tipo de meses_etiquetas:", type(meses_etiquetas))
    print("Tipo de cantidades_mes:", type(cantidades_mes))
    
    # Asegurarse de que los datos sean serializables
    try:
        # Convertir a listas de Python
        if not isinstance(meses_etiquetas, list):
            meses_etiquetas = list(meses_etiquetas)
        if not isinstance(cantidades_mes, list):
            cantidades_mes = [int(x) for x in cantidades_mes]
        
        # Asegurarse de que las cantidades sean números
        cantidades_mes = [int(x) if x is not None else 0 for x in cantidades_mes]
        
        # Serializar a JSON
        horas_json = mark_safe(json.dumps(horas))
        cantidades_json = mark_safe(json.dumps([float(x) for x in cantidades]))
        meses_etiquetas_json = mark_safe(json.dumps(meses_etiquetas, ensure_ascii=False))
        cantidades_mes_json = mark_safe(json.dumps(cantidades_mes))
        
        # Depuración: Imprimir datos después de la serialización
        print("Datos para gráfico de meses después de serializar:")
        print("meses_etiquetas_json:", meses_etiquetas_json)
        print("cantidades_mes_json:", cantidades_mes_json)
        
    except Exception as e:
        print(f"Error al serializar datos para los gráficos: {str(e)}")
        # Asignar valores por defecto en caso de error
        horas_json = mark_safe(json.dumps([]))
        cantidades_json = mark_safe(json.dumps([]))
        meses_etiquetas_json = mark_safe(json.dumps([], ensure_ascii=False))
        cantidades_mes_json = mark_safe(json.dumps([]))
    
    context = {
        'total_socios': total_socios,
        'asistencias_hoy': asistencias_hoy,
        'horas': horas_json,
        'cantidades': cantidades_json,
        'filtro': filtro,
        'grupo': grupo,
        'titulo_detalle': titulo_detalle,
        'socios_detalle': socios_detalle,
        'socios_no_pago_sin_asistencia': socios_no_pago_sin_asistencia,
        'socios_no_pago_con_asistencia': socios_no_pago_con_asistencia,
        'socios_con_pago_sin_asistencia': socios_con_pago_sin_asistencia,
        'socios_con_pago_con_asistencia': socios_con_pago_con_asistencia,
        'meses_etiquetas': meses_etiquetas_json,
        'cantidades_mes': cantidades_mes_json,
    }
    return render(request, 'home.html', context)
