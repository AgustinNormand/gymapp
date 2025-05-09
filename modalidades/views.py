from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from modalidades.models import HistorialModalidad, Modalidad
from socios.models import Socio

def cambiar_modalidad(request, socio_id):
    # Este método permite cambiar la modalidad de un socio.
    # Primero, obtenemos el socio por su ID
    # y luego obtenemos todas las modalidades disponibles.
    # Si no existe el socio, se lanza un error 404.
    # Si el método es POST, se obtiene la nueva modalidad seleccionada
    # y se verifica si es diferente a la actual.
    # Si es la misma, se muestra un mensaje de error.
    # Si es diferente, se cierra el historial anterior y se crea uno nuevo.
    # Finalmente, se redirige al usuario a la lista de socios.
    # Si el método es GET, se renderiza el formulario de cambio de modalidad.

    
    socio = get_object_or_404(Socio, id=socio_id)
    modalidades = Modalidad.objects.all()

    if request.method == 'POST':
        nueva_modalidad_id = request.POST.get('modalidad')
        nueva_modalidad = Modalidad.objects.get(id=nueva_modalidad_id)

        if socio.modalidad_actual() is None:
            modalidad_actual = None
        else:
            modalidad_actual = socio.modalidad_actual().modalidad

        # Si la modalidad es la misma, retornamos un mensaje de error, usando la app de mensajes de Django
        if modalidad_actual == nueva_modalidad:
            messages.error(request, "La modalidad seleccionada es la misma que la actual.")

            # Redirijo al usuario al formulario de cambio de modalidad
            return redirect('modalidades:cambiar_modalidad', socio_id=socio.id)
        else:
            # Si la modalidad es diferente, procedemos a cambiarla
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

            # Mensaje de éxito
            messages.success(request, f"Modalidad cambiada a {nueva_modalidad.nombre} para el socio {socio.nombre} {socio.apellido}.")
            return redirect('socios:listar_socios')

    return render(request, 'modalidades/cambiar_modalidad.html', {'socio': socio, 'modalidades': modalidades})
