from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.registrar_entrada, name='registrar_entrada'),
    path('entradas/', views.listar_entradas, name='listar_entradas'),
    path('entradas/exportar/', views.exportar_entradas_csv, name='exportar_entradas'),  # <- ESTE FALTABA
]
