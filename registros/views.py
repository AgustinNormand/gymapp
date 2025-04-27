from django.shortcuts import render, redirect
from .forms import RegistroEntradaForm
from django.contrib import messages

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
