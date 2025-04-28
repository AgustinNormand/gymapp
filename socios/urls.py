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
]
