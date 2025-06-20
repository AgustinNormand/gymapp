from django.shortcuts import get_object_or_404, render, redirect
from .models import Pago
from .forms import PagoForm
from socios.models import Socio
from modalidades.models import HistorialModalidad
from calendar import monthrange
from datetime import date
from django.contrib import messages
from django.urls import reverse

############ ABM de Pagos ############

def alta_pago(request):
    # Este método se encarga de registrar un nuevo pago para un socio.
    # Se espera que el ID del socio se pase como un parámetro GET en la URL.
    # Si el socio no existe, se lanza un error 404.
    # Si el ID del socio no se proporciona, se redirige al usuario a la lista de socios.
    # Si el socio no tiene una modalidad activa, se muestra un mensaje de error y se redirige a la lista de socios.
    # Si el formulario es válido, se guarda el pago y se redirige a la lista de pagos.
    # Si el formulario no es válido, se vuelve a mostrar el formulario con los datos ingresados.
    # Se sugiere un monto basado en la modalidad activa del socio.
    # Si no hay modalidad activa, se sugiere un monto por defecto de 20000.
    # Se establece la fecha de vencimiento del pago como el último día del mes actual.
    # Se utiliza el método select_related para optimizar la consulta de pagos y socios.
    # Se utiliza el método order_by para ordenar los pagos por fecha de pago en orden descendente.


    socio_id = request.GET.get('socio_id')
    socio = get_object_or_404(Socio, id=socio_id)


    historial_modalidad = socio.modalidad_actual()

    if historial_modalidad:
        # Usamos el precio actual de la modalidad, no el guardado en el historial
        modalidad_actual = historial_modalidad.modalidad
        monto_sugerido = modalidad_actual.precio
    else:
        messages.warning(request, "El socio no tiene una modalidad activa asignada. Asigne una modalidad, antes de registrar el pago.")
        return redirect('modalidades:cambiar_modalidad', socio_id=socio.id)

    hoy = date.today()
    ultimo_dia_mes = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])
    # Aseguramos que la fecha esté en formato ISO (yyyy-MM-dd) para el input type="date"

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.socio = socio
            pago.monto = monto_sugerido
            pago.save()
            
            # Actualizamos el historial de modalidad con el precio actual
            if historial_modalidad:
                # Cerramos el historial anterior
                historial_modalidad.fecha_fin = date.today()
                historial_modalidad.save()
                
                # Creamos un nuevo historial con el precio actual
                HistorialModalidad.objects.create(
                    socio=socio,
                    modalidad=modalidad_actual,
                    precio_en_el_momento=modalidad_actual.precio,
                    fecha_inicio=date.today(),
                    fecha_fin=None
                )

            messages.success(request, f"Pago registrado correctamente para {socio.nombre} {socio.apellido}.")
            return redirect('pagos:listar_pagos')
    else:
        # Formateamos la fecha en formato ISO (yyyy-MM-dd) para el input type="date"
        ultimo_dia_mes_iso = ultimo_dia_mes.isoformat()
        
        initial_data = {
            'fecha_vencimiento': ultimo_dia_mes_iso,
            'socio': socio.id if socio else None,
            'monto': monto_sugerido,
        }
        form = PagoForm(initial=initial_data)


    return render(request, 'pagos/alta_pago.html', {
        'form': form,
        'socio': socio,
        'modalidad_actual': modalidad_actual,
        'historial_modalidad': historial_modalidad,
        'monto_sugerido': monto_sugerido,
    })

# No es posible modificar un pago si ya fue registrado

############ Otros métodos ############

def listar_pagos(request):
    # Este método se encarga de listar todos los pagos registrados en el sistema.
    # Se utiliza el método select_related para optimizar la consulta de pagos y socios.
    # Se utiliza el método order_by para ordenar los pagos por fecha de pago en orden descendente.
    # Soporta filtrado por rango de fechas y por nombre/apellido del socio

    # Obtener queryset inicial
    pagos = Pago.objects.select_related('socio').order_by('-fecha_pago')
    
    # Obtener la fecha de hoy
    hoy = date.today()
    hoy_iso = hoy.isoformat()
    
    # Filtros con valores por defecto
    fecha_desde = request.GET.get('fecha_desde') or hoy_iso
    fecha_hasta = request.GET.get('fecha_hasta') or hoy_iso
    socio_query = request.GET.get('socio') or ''
    
    # Aplicar filtros si existen
    if fecha_desde:
        pagos = pagos.filter(fecha_pago__gte=fecha_desde)
    
    if fecha_hasta:
        pagos = pagos.filter(fecha_pago__lte=fecha_hasta)
    
    if socio_query:
        pagos = pagos.filter(
            socio__nombre__icontains=socio_query
        ) | pagos.filter(
            socio__apellido__icontains=socio_query
        )
    
    # Pasar los parámetros de filtro al contexto para mantenerlos en el formulario
    context = {
        'pagos': pagos,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'socio': socio_query,
    }
    
    return render(request, 'pagos/listar_pagos.html', context)


def eliminar_pago(request, pago_id):
    # Este método se encarga de eliminar un pago registrado en el sistema.
    # Se espera que el ID del pago se pase como un parámetro en la URL.
    # Si el pago no existe, se lanza un error 404.
    # Si la solicitud es POST, se elimina el pago y se redirige a la lista de pagos.
    # Si la solicitud no es POST, se muestra una página de confirmación.
    
    pago = get_object_or_404(Pago, id=pago_id)
    
    if request.method == 'POST':
        pago.delete()
        messages.success(request, f"Pago de {pago.socio.nombre} {pago.socio.apellido} eliminado correctamente.")
        return redirect('pagos:listar_pagos')
    
    return render(request, 'pagos/confirmar_eliminar_pago.html', {'pago': pago})
