from django.shortcuts import get_object_or_404, render, redirect
from .models import Pago
from .forms import PagoForm
from socios.models import Socio
from modalidades.models import HistorialModalidad
from calendar import monthrange
from datetime import date
from django.contrib import messages

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
    socio = None
    modalidad_actual = None
    monto_sugerido = 20000  # Default por si no hay modalidad

    if socio_id:
        socio = Socio.objects.get(id=socio_id)
        modalidad_actual = HistorialModalidad.objects.filter(
            socio=socio, fecha_fin__isnull=True
        ).order_by('-fecha_inicio').first()

        if modalidad_actual:
            monto_sugerido = modalidad_actual.precio_en_el_momento
        else:
            # 🚨 No tiene modalidad activa
            messages.error(request, "El socio no tiene una modalidad activa asignada. No se puede registrar el pago.")
            return redirect('socios:listar_socios') 
    else:
        # 🚨 No se envió el ID de socio
        messages.error(request, "No se ha proporcionado un ID de socio válido.")
        return redirect('socios:listar_socios') 

    hoy = date.today()
    ultimo_dia_mes = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])

    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.socio = socio
            pago.monto = monto_sugerido
            pago.save()

            messages.success(request, f"Pago registrado correctamente para {socio.nombre} {socio.apellido}.")

            return redirect('pagos:listar_pagos')
    else:
        initial_data = {
            'fecha_vencimiento': ultimo_dia_mes,
            'socio': socio.id if socio else None,
            'monto': monto_sugerido,
        }
        form = PagoForm(initial=initial_data)


    return render(request, 'pagos/alta_pago.html', {
        'form': form,
        'socio': socio,
        'modalidad_actual': modalidad_actual,
        'monto_sugerido': monto_sugerido,
    })

# No es posible eliminar un pago si ya fue registrado
# No es posible modificar un pago si ya fue registrado

############ Otros métodos ############

def listar_pagos(request):
    # Este método se encarga de listar todos los pagos registrados en el sistema.
    # Se utiliza el método select_related para optimizar la consulta de pagos y socios.
    # Se utiliza el método order_by para ordenar los pagos por fecha de pago en orden descendente.

    pagos = Pago.objects.select_related('socio').order_by('-fecha_pago')
    
    return render(request, 'pagos/listar_pagos.html', {'pagos': pagos})
