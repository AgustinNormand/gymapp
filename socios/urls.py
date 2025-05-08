# socios/urls.py
from django.urls import path
from . import views

app_name = 'socios'

urlpatterns = [
    # URLs de ABM de Socios
    path('alta/', views.alta_socio, name='alta_socio'),
    path('editar/<int:id>/', views.editar_socio, name='editar_socio'),
    path('eliminar/<int:id>/', views.eliminar_socio, name='eliminar_socio'),

    # URLs para la gestión de socios
    path('', views.listar_socios, name='listar_socios'),
    path('detalle/<int:id>/', views.detalle_socio, name='detalle_socio'),
    path('buscar_socios/', views.buscar_socios, name='buscar_socios'),
    path('ajax/tabla_socios/', views.tabla_socios_parcial, name='tabla_socios_parcial'),
    
    # URLs para ABM de Observaciones
    path('socio/<int:socio_id>/observacion/nueva/', views.alta_observacion, name='alta_observacion'),
    path('observacion/<int:observacion_id>/editar/', views.editar_observacion, name='editar_observacion'),
    path('observacion/<int:observacion_id>/borrar/', views.eliminar_observacion, name='eliminar_observacion'),

    # URLs para la gestión de observaciones
    path('socio/<int:socio_id>/observaciones/', views.gestionar_observaciones, name='gestionar_observaciones'),

    # Otras URLs
    path('cambiar-modalidad/<int:socio_id>/', views.cambiar_modalidad, name='cambiar_modalidad'),
    
]
