from django.urls import path
from . import views

urlpatterns = [
    path('entradas/', views.listar_entradas, name='listar_entradas'),
    path('registrar/', views.registrar_entrada, name='registrar_entrada'),
    path('buscar_socios/', views.buscar_socios, name='buscar_socios'),
    path('confirmar_entrada/', views.confirmar_entrada, name='confirmar_entrada'),
    path('entrada/<int:id>/eliminar/', views.eliminar_entrada, name='eliminar_entrada'),
]
