from django.urls import path
from . import views

app_name = 'modalidades'

urlpatterns = [
    path('cambiar-modalidad/<int:socio_id>/', views.cambiar_modalidad, name='cambiar_modalidad'),
]


