from django.shortcuts import render, redirect
from django.contrib import messages
from .models import RegistroEntrada
from datetime import date
from django.db.models import Q
import csv
from django.http import HttpResponse
from django.http import JsonResponse
from socios.models import Socio, Observacion
from pagos.models import Pago
from ejercicios.models import RegistroEjercicio
from .models import RegistroEntrada
from django.utils.timezone import now
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from socios.models import Socio
from registros.models import RegistroEntrada
from socios.models import Socio
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.http import JsonResponse
from socios.models import Socio, Observacion
from pagos.models import Pago
from ejercicios.models import RegistroEjercicio
from .models import RegistroEntrada
from django.db.models import Q
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from socios.models import Socio, Observacion
from pagos.models import Pago
from ejercicios.models import RegistroEjercicio
from registros.models import RegistroEntrada
from django.utils.timezone import now
import json

def vista_registrar_asistencia(request):
    return render(request, 'registros/registrar_asistencia.html')


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

def buscar_socios(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    socios = Socio.objects.filter(
        Q(nombre__icontains=query) | Q(apellido__icontains=query)
    ).order_by('apellido')[:10]

    resultados = [
        {
            'id': socio.id,
            'nombre_completo': f"{socio.apellido} {socio.nombre}",
        }
        for socio in socios
    ]
    return JsonResponse(resultados, safe=False)

@csrf_exempt
def registrar_asistencia_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        socio_id = data.get('id')

        socio = Socio.objects.get(id=socio_id)

        # 🛠️ Crear el registro de asistencia y guardar el ID
        registro = RegistroEntrada.objects.create(socio=socio)

        # Estado de cuota
        pagos = Pago.objects.filter(socio=socio).order_by('-fecha_vencimiento')
        cuota = "Sin pagos" if not pagos else (
            "Al día" if pagos.first().fecha_vencimiento >= now().date() else "Vencida"
        )

        # Observaciones activas
        obs_activas = socio.observaciones.filter(
            fecha_fin__isnull=True
        ).values_list('descripcion', flat=True)

        # Pesos cargados
        ejercicios = RegistroEjercicio.objects.filter(socio=socio).order_by('ejercicio__nombre')
        pesos = {
            reg.ejercicio.nombre: float(reg.peso)
            for reg in ejercicios
        }

        return JsonResponse({
            'socio': f"{socio.apellido} {socio.nombre}",
            'cuota': cuota,
            'observaciones': list(obs_activas),
            'pesos': pesos,
            'registro_id': registro.id  # 👈🔥 ACÁ DEVOLVEMOS EL ID DEL REGISTRO
        })

    except Socio.DoesNotExist:
        return JsonResponse({'error': 'Socio no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  # (Idealmente, después mejoramos seguridad con CSRF Token también)
@require_POST
def borrar_asistencia_ajax(request):
    try:
        data = json.loads(request.body)
        registro_id = data.get('registro_id')

        registro = RegistroEntrada.objects.get(id=registro_id)
        registro.delete()

        return JsonResponse({'status': 'ok'})
    except RegistroEntrada.DoesNotExist:
        return JsonResponse({'error': 'Asistencia no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



