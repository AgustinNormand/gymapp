from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_entrada, name='registrar_entrada'),
    path('entradas/', views.listar_entradas, name='listar_entradas'),
]
