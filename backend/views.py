from django.shortcuts import render
from socios.models import Socio
from registros.models import RegistroEntrada
from pagos.models import Pago
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractHour, ExtractMonth, ExtractYear
from django.db.models import Count, Q, F
from django.utils.timezone import now

def home(request):
    hoy = date.today()
    grupo = request.GET.get('grupo', '')  # Obtener el parámetro 'grupo' de la URL, vacío por defecto
    total_socios = Socio.objects.filter().count()
    asistencias_hoy = RegistroEntrada.objects.filter(fecha_hora__date=hoy).count()
    
    # Calcular el inicio y fin de la semana actual (lunes a domingo)
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    
    # Buscar socios que cumplen años esta semana
    socios_cumpleanos = []
    
    # Para depuración: imprimir fechas
    print(f"Fecha actual: {hoy}")
    print(f"Inicio de semana: {inicio_semana}")
    print(f"Fin de semana: {fin_semana}")
    
    # Obtener todos los socios con fecha de nacimiento
    socios_con_fecha = Socio.objects.filter(fecha_nacimiento__isnull=False)
    print(f"Total socios con fecha de nacimiento: {socios_con_fecha.count()}")
    
    for socio in socios_con_fecha:
        if socio.fecha_nacimiento:
            # Verificar si el cumpleaños cae en esta semana (ignorando el año)
            fecha_cumple_este_anio = socio.fecha_nacimiento.replace(year=hoy.year)
            print(f"Socio: {socio.nombre} {socio.apellido}, Cumpleaños este año: {fecha_cumple_este_anio}")
            
            if inicio_semana <= fecha_cumple_este_anio <= fin_semana:
                print(f"¡CUMPLE ESTA SEMANA! {socio.nombre} {socio.apellido}")
                # Agregar a la lista con la fecha del cumpleaños
                socios_cumpleanos.append({
                    'nombre': socio.nombre,
                    'apellido': socio.apellido,
                    'fecha_cumple': fecha_cumple_este_anio
                })
    
    print(f"Total socios que cumplen esta semana: {len(socios_cumpleanos)}")
    
    # Ordenar por fecha de cumpleaños
    socios_cumpleanos.sort(key=lambda x: x['fecha_cumple'])
    
    # --- Configuración de fechas y agrupación ---
    tipo_agrupacion = request.GET.get('tipo_agrupacion', 'hora')  # Por defecto agrupar por hora
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Validar y establecer fechas por defecto según el tipo de agrupación
    try:
        if fecha_inicio and fecha_fin:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            
            # Asegurar que la fecha de inicio sea menor o igual que la de fin
            if fecha_inicio > fecha_fin:
                fecha_inicio, fecha_fin = fecha_fin, fecha_inicio
        else:
            # Valores por defecto según el tipo de agrupación
            if tipo_agrupacion == 'hora':
                fecha_inicio = hoy
                fecha_fin = hoy
            elif tipo_agrupacion == 'dia':
                fecha_fin = hoy
                fecha_inicio = hoy - timedelta(days=30)  # Últimos 30 días
            elif tipo_agrupacion == 'semana':
                fecha_fin = hoy
                fecha_inicio = hoy - timedelta(weeks=12)  # Últimas 12 semanas
            elif tipo_agrupacion == 'mes':
                fecha_fin = hoy
                fecha_inicio = hoy.replace(day=1) - relativedelta(months=11)  # Últimos 12 meses completos
                fecha_inicio = fecha_inicio.replace(day=1)  # Asegurar que sea el primer día del mes
            else:  # anual
                fecha_fin = hoy
                fecha_inicio = hoy.replace(month=1, day=1, year=hoy.year-4)  # Últimos 5 años
    except (ValueError, TypeError) as e:
        # En caso de error, usar valores por defecto
        fecha_inicio = hoy
        fecha_fin = hoy
        
    # --- Procesar datos según el tipo de agrupación ---
    etiquetas = []
    cantidades = []
    tipo_eje_x = ''
    
    if tipo_agrupacion == 'hora':
        # Agrupar por hora del día (socios únicos)
        asistencias = RegistroEntrada.objects.filter(
            fecha_hora__date__range=(fecha_inicio, fecha_fin)
        ).annotate(
            hora=ExtractHour('fecha_hora')
        ).values('hora', 'socio_id').distinct()
        
        # Contar socios únicos por hora
        socios_por_hora = {h: set() for h in range(24)}
        
        for registro in asistencias:
            hora = registro['hora']
            if 0 <= hora <= 23:
                socios_por_hora[hora].add(registro['socio_id'])
        
        # Calcular promedio diario si es un rango de fechas
        dias_rango = (fecha_fin - fecha_inicio).days + 1
        if dias_rango < 1:
            dias_rango = 1
            
        # Preparar datos para el template
        etiquetas = [f"{h:02d}:00" for h in range(24)]
        if dias_rango > 1:
            cantidades = [round(len(socios) / dias_rango, 1) for socios in socios_por_hora.values()]
            titulo_grafico = f"Promedio diario de socios únicos por hora\n({fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')})"
        else:
            cantidades = [len(socios) for socios in socios_por_hora.values()]
            titulo_grafico = f"Socios Únicos por Hora del Día ({fecha_inicio.strftime('%d/%m/%Y')})"
        tipo_eje_x = 'Hora del día'
        
    elif tipo_agrupacion == 'dia':
        # Agrupar por día
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            total = RegistroEntrada.objects.filter(
                fecha_hora__date=current_date
            ).values('socio_id').distinct().count()
            
            etiquetas.append(current_date.strftime('%d/%m/%Y'))
            cantidades.append(total)
            current_date += timedelta(days=1)
            
        titulo_grafico = f'Asistencias por Día ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})'
        tipo_eje_x = 'Fecha'
        
    elif tipo_agrupacion == 'semana':
        # Agrupar por semana
        current_date = fecha_inicio
        while current_date <= fecha_fin:
            # Obtener el lunes de la semana actual
            start_of_week = current_date - timedelta(days=current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            
            # Ajustar fechas al rango seleccionado
            if start_of_week < fecha_inicio:
                start_of_week = fecha_inicio
            if end_of_week > fecha_fin:
                end_of_week = fecha_fin
                
            total = RegistroEntrada.objects.filter(
                fecha_hora__date__range=(start_of_week, end_of_week)
            ).values('socio_id').distinct().count()
            
            # Formato más compacto para las etiquetas
            if start_of_week.month == end_of_week.month:
                etiqueta = f"{start_of_week.day}-{end_of_week.day} {start_of_week.strftime('%b %Y')}"
            else:
                etiqueta = f"{start_of_week.day} {start_of_week.strftime('%b')}-{end_of_week.day} {end_of_week.strftime('%b %Y')}"
                
            etiquetas.append(etiqueta)
            cantidades.append(total)
            
            # Mover al lunes de la siguiente semana
            current_date = end_of_week + timedelta(days=1)
            
        titulo_grafico = f'Asistencias por Semana ({fecha_inicio.strftime("%d/%m/%Y")} - {fecha_fin.strftime("%d/%m/%Y")})'
        tipo_eje_x = 'Semana'
        
    elif tipo_agrupacion == 'mes':
        # Agrupar por mes
        current_date = date(fecha_inicio.year, fecha_inicio.month, 1)
        meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                        'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        
        while current_date <= fecha_fin:
            # Obtener el primer y último día del mes
            primer_dia = current_date
            if current_date.month == 12:
                ultimo_dia = date(current_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                ultimo_dia = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
            
            # Ajustar fechas según el rango seleccionado
            if primer_dia < fecha_inicio:
                primer_dia = fecha_inicio
            if ultimo_dia > fecha_fin:
                ultimo_dia = fecha_fin
                
            # Contar asistencias para el mes
            if primer_dia <= ultimo_dia:
                total = RegistroEntrada.objects.filter(
                    fecha_hora__date__range=(primer_dia, ultimo_dia)
                ).values('socio_id').distinct().count()
                
                etiqueta = f"{meses_nombres[current_date.month-1]} {current_date.year}"
                etiquetas.append(etiqueta)
                cantidades.append(total)
            
            # Mover al primer día del siguiente mes
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
                
        titulo_grafico = f'Asistencias por Mes ({fecha_inicio.strftime("%b %Y")} - {fecha_fin.strftime("%b %Y")})'
        tipo_eje_x = 'Mes'
        
    else:  # tipo_agrupacion == 'anio'
        # Agrupar por año
        current_year = fecha_inicio.year
        end_year = fecha_fin.year
        
        for year in range(current_year, end_year + 1):
            # Determinar el rango de fechas para el año
            start_date = max(date(year, 1, 1), fecha_inicio)
            end_date = min(date(year, 12, 31), fecha_fin)
            
            total = RegistroEntrada.objects.filter(
                fecha_hora__date__range=(start_date, end_date)
            ).values('socio_id').distinct().count()
            
            etiquetas.append(str(year))
            cantidades.append(total)
            
        titulo_grafico = f'Asistencias por Año ({fecha_inicio.year} - {fecha_fin.year})'
        tipo_eje_x = 'Año'
    
    # Obtener los últimos registros de asistencia para la tabla
    ultimas_asistencias = RegistroEntrada.objects.select_related('socio').order_by('-fecha_hora')[:10]
    
    # Aplicar filtro de búsqueda si existe
    filtro = request.GET.get('filtro', '')
    if filtro:
        ultimas_asistencias = ultimas_asistencias.filter(
            Q(socio__nombre__icontains=filtro) |
            Q(socio__apellido__icontains=filtro) |
            Q(socio__documento__icontains=filtro)
        )
    
    # Preparar el título del detalle
    titulo_detalle = "Últimas asistencias"
    if filtro:
        titulo_detalle += f" - Filtro: {filtro}"
    
    # Importar json y mark_safe al inicio del archivo
    import json
    from django.utils.safestring import mark_safe
    
    # Asegurarse de que las cantidades sean números
    cantidades = [float(x) if x is not None else 0 for x in cantidades]
    
    # Serializar datos para el gráfico
    try:
        etiquetas_json = mark_safe(json.dumps(etiquetas, ensure_ascii=False))
        cantidades_json = mark_safe(json.dumps(cantidades))
    except Exception as e:
        print(f"Error al serializar datos para el gráfico: {str(e)}")
        etiquetas_json = mark_safe(json.dumps([], ensure_ascii=False))
        cantidades_json = mark_safe(json.dumps([]))
    
    # Calcular datos para la sección "Actividad mensual de Socios"
    mes_actual = date.today().replace(day=1)
    mes_siguiente = (mes_actual.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    # Obtener todos los socios activos
    socios_activos = Socio.objects.all()
    
    # Calcular socios con pago vigente para el mes actual
    # Un pago está vigente si su fecha de vencimiento es igual o posterior a la fecha actual
    fecha_actual = date.today()
    socios_con_pago = set(Pago.objects.filter(
        fecha_vencimiento__gte=fecha_actual
    ).values_list('socio_id', flat=True))
    
    # Calcular socios con asistencia en el mes actual
    socios_con_asistencia = set(RegistroEntrada.objects.filter(
        fecha_hora__gte=mes_actual, 
        fecha_hora__lt=mes_siguiente
    ).values_list('socio_id', flat=True))
    
    # Inicializar listas para cada categoría
    socios_no_pago_sin_asistencia = 0
    socios_no_pago_con_asistencia = 0
    socios_con_pago_sin_asistencia = 0
    socios_con_pago_con_asistencia = 0
    socios_detalle = []
    titulo_detalle = "Últimas asistencias"
    
    # Contar socios en cada categoría
    for socio in socios_activos:
        tiene_pago = socio.id in socios_con_pago
        tiene_asistencia = socio.id in socios_con_asistencia
        
        if not tiene_pago and not tiene_asistencia:
            socios_no_pago_sin_asistencia += 1
        elif not tiene_pago and tiene_asistencia:
            socios_no_pago_con_asistencia += 1
        elif tiene_pago and not tiene_asistencia:
            socios_con_pago_sin_asistencia += 1
        else:  # tiene_pago and tiene_asistencia
            socios_con_pago_con_asistencia += 1
    
    # Si se ha seleccionado un grupo, filtrar los socios correspondientes
    if grupo:
        # Determinar qué socios mostrar según el grupo seleccionado
        if grupo == 'no_pago_sin_asistencia':
            titulo_detalle = "No pago, sin asistencias"
            socios_filtrados = [s for s in socios_activos if s.id not in socios_con_pago and s.id not in socios_con_asistencia]
        elif grupo == 'no_pago_con_asistencia':
            titulo_detalle = "No pago, con asistencias"
            socios_filtrados = [s for s in socios_activos if s.id not in socios_con_pago and s.id in socios_con_asistencia]
        elif grupo == 'pago_sin_asistencia':
            titulo_detalle = "Pago, sin asistencias"
            socios_filtrados = [s for s in socios_activos if s.id in socios_con_pago and s.id not in socios_con_asistencia]
        elif grupo == 'pago_con_asistencia':
            titulo_detalle = "Pago, con asistencias"
            socios_filtrados = [s for s in socios_activos if s.id in socios_con_pago and s.id in socios_con_asistencia]
        else:
            socios_filtrados = []
        
        # Calcular días sin asistir para cada socio
        for socio in socios_filtrados:
            # Obtener la última asistencia del socio
            ultima_asistencia = RegistroEntrada.objects.filter(socio=socio).order_by('-fecha_hora').first()
            dias_sin_asistir = 0
            if ultima_asistencia:
                dias_sin_asistir = (date.today() - ultima_asistencia.fecha_hora.date()).days
            
            # Verificar si el socio tiene todos los datos opcionales
            has_all_data = bool(socio.telefono and socio.email and socio.fecha_nacimiento)
            
            # Añadir socio a la lista con información adicional
            socios_detalle.append({
                'id': socio.id,
                'nombre': socio.nombre,
                'apellido': socio.apellido,
                'telefono': socio.telefono,
                'dias_sin_asistir': dias_sin_asistir,
                'has_all_data': has_all_data
            })
        
        # Si hay un filtro, aplicarlo también a los socios detalle
        if filtro:
            socios_detalle = [s for s in socios_detalle if 
                              filtro.lower() in s['nombre'].lower() or 
                              filtro.lower() in s['apellido'].lower()]
            titulo_detalle += f" - Filtro: {filtro}"
    
    # Preparar el contexto para la plantilla
    # Asegurarse de que hay_cumpleanos sea correcto
    hay_cumpleanos = len(socios_cumpleanos) > 0
    print(f"¿Hay cumpleaños esta semana?: {hay_cumpleanos}")
    
    return render(request, 'home.html', {
        'total_socios': total_socios,
        'asistencias_hoy': asistencias_hoy,
        'etiquetas': etiquetas_json,
        'cantidades': cantidades_json,
        'titulo_grafico': titulo_grafico,
        'tipo_eje_x': tipo_eje_x,
        'fecha_inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fecha_fin': fecha_fin.strftime('%Y-%m-%d'),
        'tipo_agrupacion': tipo_agrupacion,
        'ultimas_asistencias': ultimas_asistencias,
        'titulo_detalle': titulo_detalle,
        'filtro': filtro,
        'grupo': grupo,
        'socios_no_pago_sin_asistencia': socios_no_pago_sin_asistencia,
        'socios_no_pago_con_asistencia': socios_no_pago_con_asistencia,
        'socios_con_pago_sin_asistencia': socios_con_pago_sin_asistencia,
        'socios_con_pago_con_asistencia': socios_con_pago_con_asistencia,
        'socios_detalle': socios_detalle,
        'socios_cumpleanos': socios_cumpleanos,
        'hay_cumpleanos': hay_cumpleanos
    })
