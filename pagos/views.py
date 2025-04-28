from django.shortcuts import render, redirect
from .models import Pago
from socios.models import Socio
from .forms import PagoForm

def registrar_pago(request):
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pagos:listar_pagos')
    else:
        form = PagoForm()
    return render(request, 'pagos/registrar_pago.html', {'form': form})

def listar_pagos(request):
    pagos = Pago.objects.select_related('socio').order_by('-fecha_pago')
    return render(request, 'pagos/listar_pagos.html', {'pagos': pagos})
