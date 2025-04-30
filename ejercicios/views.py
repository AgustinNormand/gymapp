from django.shortcuts import render, get_object_or_404, redirect
from socios.models import Socio
from .models import Ejercicio, RegistroEjercicio
from datetime import date
from django.contrib import messages

def gestionar_registros(request, socio_id):
    socio = get_object_or_404(Socio, id=socio_id)
    ejercicios = Ejercicio.objects.all()
    registros = RegistroEjercicio.objects.filter(socio=socio).order_by('ejercicio__nombre', 'fecha')

    if request.method == 'POST':
        ejercicio_id = request.POST.get('ejercicio')
        peso = request.POST.get('peso')

        if ejercicio_id and peso:
            ejercicio = get_object_or_404(Ejercicio, id=ejercicio_id)
            hoy = date.today()

            # Verificamos si ya existe un registro para ese socio, ejercicio y día
            existe = RegistroEjercicio.objects.filter(
                socio=socio,
                ejercicio=ejercicio,
                fecha=hoy
            ).exists()

            if existe:
                messages.warning(request, f"Ya hay un registro de hoy para el ejercicio {ejercicio.nombre}.")
            else:
                RegistroEjercicio.objects.create(
                    socio=socio,
                    ejercicio=ejercicio,
                    fecha=hoy,
                    peso=peso
                )
                messages.success(request, f"Registro agregado correctamente para {ejercicio.nombre}.")

            return redirect('ejercicios:gestionar_registros', socio_id=socio.id)


    return render(request, 'ejercicios/gestionar_registros.html', {
        'socio': socio,
        'ejercicios': ejercicios,
        'registros': registros,
    })

def editar_registro(request, registro_id):
    registro = get_object_or_404(RegistroEjercicio, id=registro_id)
    socio = registro.socio  # Para volver después

    if request.method == 'POST':
        peso = request.POST.get('peso')
        fecha = request.POST.get('fecha')

        if peso and fecha:
            registro.peso = peso
            registro.fecha = fecha
            registro.save()
            return redirect('ejercicios:gestionar_registros', socio_id=socio.id)

    ejercicios = Ejercicio.objects.all()

    return render(request, 'ejercicios/editar_registro.html', {
        'registro': registro,
        'ejercicios': ejercicios,
    })

def borrar_registro(request, registro_id):
    registro = get_object_or_404(RegistroEjercicio, id=registro_id)
    socio_id = registro.socio.id
    registro.delete()
    return redirect('ejercicios:gestionar_registros', socio_id=socio_id)
