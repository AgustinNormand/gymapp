from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    path('registrar/', views.alta_pago, name='alta_pago'),
    path('listar/', views.listar_pagos, name='listar_pagos'),
    path('eliminar/<int:pago_id>/', views.eliminar_pago, name='eliminar_pago'),
]
