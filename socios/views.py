from django.shortcuts import render, redirect, get_object_or_404
from registros.models import RegistroEntrada
from .forms import SocioForm, SocioEditForm, ObservacionForm
from .models import Socio, Observacion
from django.contrib import messages
from pagos.models import Pago
from datetime import date, timedelta
from modalidades.models import Modalidad, HistorialModalidad
from django.utils import timezone
from django.db.models import BooleanField, Case, When, Value
from django.db import models
from ejercicios.models import Ejercicio, RegistroEjercicio
from django.db.models import Q
from django.http import JsonResponse


############ ABM de Socios ############
def alta_socio(request):
    # Este método se encarga de crear un nuevo socio.
    # Si el método es GET, se muestra el formulario vacío.
    # Si el método es POST, significa que se está enviando el formulario, por ende, se procesa.
    # Si el formulario es válido, se guarda el nuevo socio y se redirige a la lista de socios.
    # Si el formulario no es válido, se muestra un mensaje de error.

    if request.method == 'POST':
        form = SocioForm(request.POST)
        if form.is_valid():
            socio = form.save()

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
            return render(request, 'socios/alta_socio.html', {'form': form})
    else:
        form = SocioForm()
        return render(request, 'socios/alta_socio.html', {'form': form})

def eliminar_socio(request, id):
    # Este método se encarga de eliminar un socio.
    # Se busca el socio por su ID y se elimina.
    # Si el socio no existe, se lanza un error 404.
    # Luego se redirige a la lista de socios y se muestra un mensaje de éxito.

    socio = get_object_or_404(Socio, id=id)
    socio.delete()

    messages.success(request, 'Socio eliminado exitosamente.')
    return redirect('socios:listar_socios')

def editar_socio(request, id):
    # Este método se encarga de editar un socio existente.
    # Se busca el socio por su ID y se carga el formulario con los datos actuales.
    # Si no se encuentra el socio, se lanza un error 404.
    # Si el método es POST, se procesa el formulario.
    # Si el formulario es válido, se guarda el socio y se redirige a la lista de socios.
    # Si el formulario no es válido, se muestra un mensaje de error.

    socio = get_object_or_404(Socio, id=id)

    if request.method == 'POST':
        form = SocioEditForm(request.POST, instance=socio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Socio actualizado exitosamente.')
            return redirect('socios:listar_socios')
        else:
            messages.error(request, 'Hubo un error al actualizar el socio. Por favor revisá el formulario.')
            form = SocioEditForm(instance=socio)
            return render(request, 'socios/editar_socio.html', {'form': form})
    else:
        form = SocioEditForm(instance=socio)
        return render(request, 'socios/editar_socio.html', {'form': form})
    
############ ABM de Observaciones ############

def alta_observacion(request, socio_id):
    # Este método se encarga de crear una nueva observación para un socio.
    # Se busca el socio por su ID y se carga el formulario vacío.
    # Si el método es POST, se procesa el formulario.
    # Si el formulario es válido, se guarda la observación y se redirige a la lista de observaciones del socio.
    # Si el formulario no es válido, se muestra un mensaje de error.
    # Si el socio no existe, se lanza un error 404.
    # Si el método no es POST, se muestra el formulario vacío.

    socio = get_object_or_404(Socio, id=socio_id)

    if request.method == 'POST':
        form = ObservacionForm(request.POST)
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.socio = socio
            observacion.save()
            return redirect('socios:gestionar_observaciones', socio_id=socio.id)
        else:
            messages.error(request, 'Error al crear la observación. Por favor revisá el formulario.')
            form = ObservacionForm()
            return render(request, 'socios/crear_editar_observacion.html', {'form': form, 'socio': socio, 'es_edicion': False})

    else:
        form = ObservacionForm()
        return render(request, 'socios/crear_editar_observacion.html', {'form': form, 'socio': socio, 'es_edicion': False})

def eliminar_observacion(request, observacion_id):
    # Este método se encarga de eliminar una observación.
    # Se busca la observación por su ID y se elimina.
    # Si la observación no existe, se lanza un error 404.
    # Luego se redirige a la lista de observaciones del socio y se muestra un mensaje de éxito.


    observacion = get_object_or_404(Observacion, id=observacion_id)
    socio_id = observacion.socio.id

    observacion.delete()
    return redirect('socios:gestionar_observaciones', socio_id=socio_id)

def editar_observacion(request, observacion_id):
    # Este método se encarga de editar una observación existente.
    # Se busca la observación por su ID y se carga el formulario con los datos actuales.
    # Si no se encuentra la observación, se lanza un error 404.
    # Si el método es POST, se procesa el formulario.
    # Si el formulario es válido, se guarda la observación y se redirige a la lista de observaciones del socio.
    # Si el formulario no es válido, se muestra un mensaje de error.
    # Si el método no es POST, se muestra el formulario con los datos actuales.


    observacion = get_object_or_404(Observacion, id=observacion_id)
    socio = observacion.socio

    if request.method == 'POST':
        form = ObservacionForm(request.POST, instance=observacion)
        if form.is_valid():
            form.save()
            return redirect('socios:gestionar_observaciones', socio_id=socio.id)
        else:
            messages.error(request, 'Error al editar la observación. Por favor revisá el formulario.')
            form = ObservacionForm(instance=observacion)
            return render(request, 'socios/crear_editar_observacion.html', {'form': form, 'socio': socio, 'es_edicion': True})
    else:
        form = ObservacionForm(instance=observacion)
        return render(request, 'socios/crear_editar_observacion.html', {'form': form, 'socio': socio, 'es_edicion': True})


############ Otros métodos ############

def detalle_socio(request, id):
    # Este método se encarga de mostrar el detalle de un socio.
    # Se busca el socio por su ID y se carga la información de pagos, modalidad, observaciones y ejercicios.
    # Si el socio no existe, se lanza un error 404.
    # TODO: Me parece que podríamos reducir la carga lógica de este méoodo, delegandola en los modelos

    socio = get_object_or_404(Socio, id=id)
    pagos = Pago.objects.filter(socio=socio).order_by('-fecha_pago')

    estado_cuota = 'Sin pagos registrados'
    color_cuota = 'secondary'

    if pagos.exists():
        pagos = Pago.objects.filter(socio=socio).order_by('-fecha_vencimiento')
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

    # Modalidad e historial de modalidades
    modalidad_actual = HistorialModalidad.objects.filter(
        socio=socio, fecha_fin__isnull=True
    ).order_by('-fecha_inicio').first()

    historial_modalidades = socio.historial_modalidades.annotate(
        es_actual=Case(
            When(fecha_fin__isnull=True, then=Value(True)),
            default=Value(False),
            output_field=BooleanField(),
        )
    ).order_by('-es_actual', '-fecha_inicio')


    # Observaciones de los usuarios
    hoy = timezone.now().date()

    observaciones = socio.observaciones.annotate(
        activa=Case(
            When(models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=hoy), then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('-fecha_inicio')

    ## Ejercicios y los pesos del usuario
    ejercicios = Ejercicio.objects.all()
    ejercicio_id = request.GET.get('ejercicio_id')

    registros_ejercicio = None
    ejercicio_seleccionado = None

    if ejercicio_id:
        try:
            ejercicio_seleccionado = Ejercicio.objects.get(id=ejercicio_id)
            registros_ejercicio = RegistroEjercicio.objects.filter(
                socio=socio,
                ejercicio=ejercicio_seleccionado
            ).order_by('-fecha')
        except Ejercicio.DoesNotExist:
            registros_ejercicio = None

    # Asistencias
    asistencias = RegistroEntrada.objects.filter(socio=socio).order_by('-fecha_hora')

    # Método llamado desde AJAX, devolvemos JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        ejercicios_pesos = [
            {
                'nombre': reg.ejercicio.nombre,
                'peso': str(reg.peso)
            }
            for reg in RegistroEjercicio.objects.filter(socio=socio)
        ]

        data = {
            'nombre_completo': f"{socio.apellido} {socio.nombre}",
            'estado_cuota': estado_cuota,
            'color_cuota': color_cuota,
            'observaciones': observaciones,
            'ejercicios': ejercicios_pesos,
        }
        return JsonResponse(data)

    # Si no es AJAX, seguimos devolviendo el HTML como siempre
    return render(request, 'socios/detalle_socio.html', {
        'socio': socio,
        'pagos': pagos,
        'estado_cuota': estado_cuota,
        'color_cuota': color_cuota,
        'modalidad_actual': modalidad_actual,
        'historial_modalidades': historial_modalidades,
        'observaciones': observaciones,
        'ejercicios': ejercicios,
        'registros_ejercicio': registros_ejercicio,
        'ejercicio_seleccionado': ejercicio_seleccionado,
        'asistencias': asistencias,
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



def listar_socios(request):
    query = request.GET.get('q') or ''

    socios = Socio.objects.all()

    if query:
        socios = socios.filter(
            Q(nombre__icontains=query) | Q(apellido__icontains=query)
        )

    socios_info = []
    hoy = date.today()

    for socio in socios:
        pagos = Pago.objects.filter(socio=socio).order_by('-fecha_vencimiento')

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

    return render(request, 'socios/listar_socios.html', {
        'socios_info': socios_info,
        'query': query,  # 👈 Le pasamos el query al template también
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


def gestionar_observaciones(request, socio_id):
    # Este método se encarga de gestionar las observaciones de un socio.
    # Se busca el socio por su ID y se carga la lista de observaciones.
    # Si el socio no existe, se lanza un error 404.
    
    socio = get_object_or_404(Socio, id=socio_id)
    observaciones = socio.observaciones.all()

    return render(request, 'socios/gestionar_observaciones.html', {
        'socio': socio,
        'observaciones': observaciones,
    })



def tabla_socios_parcial(request):
    query = request.GET.get('q', '')
    socios = Socio.objects.all()

    if query:
        socios = socios.filter(Q(nombre__icontains=query) | Q(apellido__icontains=query))

    socios_info = []
    hoy = date.today()

    for socio in socios:
        pagos = Pago.objects.filter(socio=socio).order_by('-fecha_vencimiento')
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

    return render(request, 'socios/tabla_socios.html', {'socios_info': socios_info})
