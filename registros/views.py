from django.shortcuts import render, redirect
from .forms import RegistroEntradaForm
from django.contrib import messages
from .models import RegistroEntrada
from datetime import date
from django.db.models import Q
import csv
from django.http import HttpResponse


def registrar_entrada(request):
    if request.method == 'POST':
        form = RegistroEntradaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrada registrada correctamente.')
            return redirect('registrar_entrada')
    else:
        form = RegistroEntradaForm()
    return render(request, 'registros/registrar_entrada.html', {'form': form})


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


def exportar_entradas_csv(request):
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

    # Crear el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="entradas.csv"'

    writer = csv.writer(response)
    writer.writerow(['Socio', 'Fecha', 'Hora'])

    for entrada in entradas:
        writer.writerow([
            f"{entrada.socio.nombre} {entrada.socio.apellido}",
            entrada.fecha_hora.strftime('%d/%m/%Y'),
            entrada.fecha_hora.strftime('%H:%M')
        ])

    return response

