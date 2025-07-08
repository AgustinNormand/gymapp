from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
from decimal import Decimal
from datetime import date, timedelta

from .models import Modalidad, HistorialModalidad
from socios.models import Socio


class ModalidadModelTest(TestCase):
    """Tests para el modelo Modalidad"""
    
    def setUp(self):
        # Crear una modalidad para pruebas
        self.modalidad = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
    
    def test_modalidad_creation(self):
        """Test para verificar la creación correcta de una modalidad"""
        self.assertEqual(self.modalidad.nombre, 'Full')
        self.assertEqual(self.modalidad.precio, Decimal('1000.00'))
        self.assertEqual(self.modalidad.dias_por_semana, 3)
    
    def test_modalidad_str(self):
        """Test para verificar la representación en cadena de una modalidad"""
        expected_str = "Full ($1000.00) - 3 días/semana"
        self.assertEqual(str(self.modalidad), expected_str)


class HistorialModalidadModelTest(TestCase):
    """Tests para el modelo HistorialModalidad"""
    
    def setUp(self):
        # Crear un socio
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Crear modalidades
        self.modalidad1 = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
        self.modalidad2 = Modalidad.objects.create(
            nombre='Básica',
            precio=Decimal('800.00'),
            dias_por_semana=2
        )
        
        # Crear historial de modalidad
        self.historial = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad1,
            precio_en_el_momento=self.modalidad1.precio,
            fecha_inicio=date.today() - timedelta(days=30)  # Hace 30 días
        )
    
    def test_historial_modalidad_creation(self):
        """Test para verificar la creación correcta de un historial de modalidad"""
        self.assertEqual(self.historial.socio, self.socio)
        self.assertEqual(self.historial.modalidad, self.modalidad1)
        self.assertEqual(self.historial.precio_en_el_momento, Decimal('1000.00'))
        self.assertEqual(self.historial.fecha_inicio, date.today() - timedelta(days=30))
        self.assertIsNone(self.historial.fecha_fin)  # Por defecto debería ser None (modalidad activa)
    
    def test_historial_modalidad_str(self):
        """Test para verificar la representación en cadena de un historial de modalidad"""
        expected_str = f"{self.socio} - {self.modalidad1.nombre} - ${self.modalidad1.precio} ({self.historial.fecha_inicio} - Actual)"
        self.assertEqual(str(self.historial), expected_str)
        
        # Probamos también con una modalidad finalizada
        self.historial.fecha_fin = date.today()
        self.historial.save()
        expected_str = f"{self.socio} - {self.modalidad1.nombre} - ${self.modalidad1.precio} ({self.historial.fecha_inicio} - {self.historial.fecha_fin})"
        self.assertEqual(str(self.historial), expected_str)
    
    def test_multiple_historiales_por_socio(self):
        """Test para verificar que un socio pueda tener múltiples historiales de modalidad"""
        # Cerramos el historial actual
        self.historial.fecha_fin = date.today() - timedelta(days=1)  # Ayer
        self.historial.save()
        
        # Crear un nuevo historial con otra modalidad
        nuevo_historial = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad2,
            precio_en_el_momento=self.modalidad2.precio,
            fecha_inicio=date.today()
        )
        
        # Verificar que ambos historiales pertenecen al socio
        historiales_socio = HistorialModalidad.objects.filter(socio=self.socio)
        self.assertEqual(historiales_socio.count(), 2)
        self.assertIn(self.historial, historiales_socio)
        self.assertIn(nuevo_historial, historiales_socio)


class ModalidadViewsTest(TestCase):
    """Tests para las vistas de la aplicación modalidades"""
    
    def setUp(self):
        self.client = Client()
        
        # Crear un socio
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Crear modalidades
        self.modalidad1 = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
        self.modalidad2 = Modalidad.objects.create(
            nombre='Básica',
            precio=Decimal('800.00'),
            dias_por_semana=2
        )
        
        # Crear historial de modalidad
        self.historial = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad1,
            precio_en_el_momento=self.modalidad1.precio,
            fecha_inicio=date.today() - timedelta(days=30)  # Hace 30 días
        )
    
    def test_cambiar_modalidad_get(self):
        """Test para la vista de cambiar modalidad (GET)"""
        url = reverse('modalidades:cambiar_modalidad', args=[self.socio.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'modalidades/cambiar_modalidad.html')
        self.assertEqual(response.context['socio'], self.socio)
        self.assertIn(self.modalidad1, response.context['modalidades'])
        self.assertIn(self.modalidad2, response.context['modalidades'])
        self.assertEqual(response.context['modalidad_actual'], self.modalidad1)
        self.assertEqual(response.context['historial_modalidad'], self.historial)
    
    def test_cambiar_modalidad_post_same_modalidad(self):
        """Test para verificar que no se puede cambiar a la misma modalidad"""
        url = reverse('modalidades:cambiar_modalidad', args=[self.socio.id])
        data = {
            'modalidad': self.modalidad1.id
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "La modalidad seleccionada es la misma que la actual.")
        
        # Verificar que no se creó un nuevo historial
        self.assertEqual(HistorialModalidad.objects.filter(socio=self.socio).count(), 1)
    
    def test_cambiar_modalidad_post_new_modalidad(self):
        """Test para la vista de cambiar modalidad (POST con modalidad diferente)"""
        url = reverse('modalidades:cambiar_modalidad', args=[self.socio.id])
        data = {
            'modalidad': self.modalidad2.id
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('socios:listar_socios'))
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), f"Modalidad cambiada a {self.modalidad2.nombre} para el socio {self.socio.nombre} {self.socio.apellido}.")
        
        # Verificar que se cerró el historial anterior
        historial_anterior = HistorialModalidad.objects.get(id=self.historial.id)
        self.assertIsNotNone(historial_anterior.fecha_fin)
        
        # Verificar que se creó un nuevo historial
        nuevo_historial = HistorialModalidad.objects.filter(
            socio=self.socio, 
            modalidad=self.modalidad2, 
            fecha_fin__isnull=True
        ).first()
        self.assertIsNotNone(nuevo_historial)
        self.assertEqual(nuevo_historial.precio_en_el_momento, self.modalidad2.precio)
    
    def test_cambiar_modalidad_sin_modalidad_previa(self):
        """Test para cambiar modalidad cuando no hay una modalidad previa"""
        # Eliminar el historial actual
        HistorialModalidad.objects.all().delete()
        
        url = reverse('modalidades:cambiar_modalidad', args=[self.socio.id])
        data = {
            'modalidad': self.modalidad1.id
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó un nuevo historial
        nuevo_historial = HistorialModalidad.objects.filter(
            socio=self.socio, 
            modalidad=self.modalidad1, 
            fecha_fin__isnull=True
        ).first()
        self.assertIsNotNone(nuevo_historial)
        self.assertEqual(nuevo_historial.precio_en_el_momento, self.modalidad1.precio)
