from django.shortcuts import render, redirect
from .forms import RegistroEntradaForm
from django.contrib import messages
from .models import RegistroEntrada

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
    entradas = RegistroEntrada.objects.all().order_by('-fecha_hora')
    return render(request, 'registros/listar_entradas.html', {'entradas': entradas})
