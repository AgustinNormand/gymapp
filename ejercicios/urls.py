from django.urls import path
from . import views

app_name = 'ejercicios'

urlpatterns = [
    path('socio/<int:socio_id>/gestionar/', views.gestionar_registros, name='gestionar_registros'),
    path('registro/<int:registro_id>/editar/', views.editar_registro, name='editar_registro'),
    path('registro/<int:registro_id>/borrar/', views.borrar_registro, name='borrar_registro'),
]
