from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.vista_registrar_asistencia, name='registrar_entrada'),  # 👈 Cambiado
    path('buscar_socios/', views.buscar_socios, name='buscar_socios'),
    path('registrar_asistencia_ajax/', views.registrar_asistencia_ajax, name='registrar_asistencia_ajax'),
    path('entradas/', views.listar_entradas, name='listar_entradas'),
    path('borrar_asistencia_ajax/', views.borrar_asistencia_ajax, name='borrar_asistencia_ajax'),  # <<< 🔥
]
