from django.urls import path
from . import views

urlpatterns = [
    path('entradas/', views.listar_entradas, name='listar_entradas'),
    path('registrar/', views.registrar_entrada, name='registrar_entrada'),
    path('alta_entrada/', views.alta_entrada, name='alta_entrada'),
    path('entrada/<int:id>/eliminar/', views.eliminar_entrada, name='eliminar_entrada'),
    path('estadisticas/', views.estadisticas_asistencias, name='estadisticas_asistencias'),
]
