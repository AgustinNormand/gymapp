from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('registrar/', views.registrar_pago, name='registrar_pago'),
    path('listar/', views.listar_pagos, name='listar_pagos'),
]
