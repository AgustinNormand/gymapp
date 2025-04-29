# socios/urls.py
from django.urls import path
from . import views

app_name = 'socios'

urlpatterns = [
    path('', views.listar_socios, name='listar_socios'),
    path('alta/', views.alta_socio, name='alta_socio'),
    path('editar/<int:id>/', views.editar_socio, name='editar_socio'),
    path('eliminar/<int:id>/', views.eliminar_socio, name='eliminar_socio'),
    path('detalle/<int:id>/', views.detalle_socio, name='detalle_socio'),
    path('cambiar-modalidad/<int:socio_id>/', views.cambiar_modalidad, name='cambiar_modalidad'),
    path('socio/<int:socio_id>/observaciones/', views.gestionar_observaciones, name='gestionar_observaciones'),
    path('socio/<int:socio_id>/observacion/nueva/', views.crear_observacion, name='crear_observacion'),
    path('observacion/<int:observacion_id>/editar/', views.editar_observacion, name='editar_observacion'),
    path('observacion/<int:observacion_id>/borrar/', views.borrar_observacion, name='borrar_observacion'),
]
