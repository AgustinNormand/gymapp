from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import get_messages
from decimal import Decimal
from datetime import date, timedelta
from calendar import monthrange

from .models import Pago
from .forms import PagoForm
from socios.models import Socio
from modalidades.models import Modalidad, HistorialModalidad


class PagoModelTest(TestCase):
    """Tests para el modelo Pago"""
    
    def setUp(self):
        # Crear un socio
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Crear un pago
        self.pago = Pago.objects.create(
            socio=self.socio,
            monto=Decimal('1000.00'),
            fecha_vencimiento=date.today() + timedelta(days=30)  # Vencimiento en 30 días
        )
    
    def test_pago_creation(self):
        """Test para verificar la creación correcta de un pago"""
        self.assertEqual(self.pago.socio, self.socio)
        self.assertEqual(self.pago.monto, Decimal('1000.00'))
        self.assertEqual(self.pago.fecha_vencimiento, date.today() + timedelta(days=30))
        self.assertEqual(self.pago.fecha_pago, date.today())  # fecha_pago se establece a hoy con auto_now_add
    
    def test_pago_str(self):
        """Test para verificar la representación en cadena de un pago"""
        expected_str = f"Pago de {self.socio.nombre} {self.socio.apellido} - ${self.pago.monto} - {self.pago.fecha_pago.strftime('%d/%m/%Y')}"
        self.assertEqual(str(self.pago), expected_str)
    
    def test_multiple_pagos_por_socio(self):
        """Test para verificar que un socio pueda tener múltiples pagos"""
        # Crear un segundo pago para el mismo socio
        pago2 = Pago.objects.create(
            socio=self.socio,
            monto=Decimal('1500.00'),
            fecha_vencimiento=date.today() + timedelta(days=60)  # Vencimiento en 60 días
        )
        
        # Verificar que ambos pagos pertenecen al socio
        pagos_socio = Pago.objects.filter(socio=self.socio)
        self.assertEqual(pagos_socio.count(), 2)
        self.assertIn(self.pago, pagos_socio)
        self.assertIn(pago2, pagos_socio)


class PagoFormTest(TestCase):
    """Tests para el formulario PagoForm"""
    
    def setUp(self):
        # Crear un socio
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Fecha de vencimiento futura válida
        self.fecha_vencimiento = date.today() + timedelta(days=30)
    
    def test_form_valid(self):
        """Test para verificar que el formulario es válido con datos correctos"""
        form_data = {
            'socio': self.socio.id,
            'monto': Decimal('1000.00'),
            'fecha_vencimiento': self.fecha_vencimiento
        }
        form = PagoForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_fecha_vencimiento_pasada(self):
        """Test para verificar que el formulario no acepta fechas de vencimiento pasadas"""
        form_data = {
            'socio': self.socio.id,
            'monto': Decimal('1000.00'),
            'fecha_vencimiento': date.today() - timedelta(days=1)  # Ayer
        }
        form = PagoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_vencimiento', form.errors)
        self.assertIn('La fecha de vencimiento no puede ser anterior a hoy.', form.errors['fecha_vencimiento'])
    
    def test_form_pago_mismo_mes(self):
        """Test para verificar que el formulario no acepta pagos duplicados en el mismo mes para un socio"""
        # Crear un pago en el mismo mes
        Pago.objects.create(
            socio=self.socio,
            monto=Decimal('1000.00'),
            fecha_vencimiento=self.fecha_vencimiento
        )
        
        # Intentar crear otro pago para el mismo socio en el mismo mes
        # Asegurarse de que la fecha esté en el mismo mes y año que la fecha_vencimiento
        mismo_mes = date(self.fecha_vencimiento.year, self.fecha_vencimiento.month, 15)
        
        form_data = {
            'socio': self.socio.id,
            'monto': Decimal('1500.00'),
            'fecha_vencimiento': mismo_mes
        }
        form = PagoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_vencimiento', form.errors)
        self.assertTrue(any('Ya existe un pago para' in error for error in form.errors['fecha_vencimiento']))


class PagoViewsTest(TestCase):
    """Tests para las vistas de la aplicación pagos"""
    
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
        
        # Crear una modalidad y asignarla al socio
        self.modalidad = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
        
        self.historial_modalidad = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad,
            precio_en_el_momento=self.modalidad.precio,
            fecha_inicio=date.today() - timedelta(days=30)  # Hace 30 días
        )
        
        # Crear un pago para tests de listar y eliminar
        self.pago = Pago.objects.create(
            socio=self.socio,
            monto=Decimal('1000.00'),
            fecha_vencimiento=date.today() + timedelta(days=30)  # Vencimiento en 30 días
        )
    
    def test_alta_pago_get(self):
        """Test para la vista de alta pago (GET)"""
        url = f"{reverse('pagos:alta_pago')}?socio_id={self.socio.id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pagos/alta_pago.html')
        self.assertEqual(response.context['socio'], self.socio)
        self.assertEqual(response.context['modalidad_actual'], self.modalidad)
        self.assertEqual(response.context['monto_sugerido'], self.modalidad.precio)
    
    def test_alta_pago_post(self):
        """Test para la vista de alta pago (POST)"""
        url = f"{reverse('pagos:alta_pago')}?socio_id={self.socio.id}"
        
        # Determinar el último día del mes actual
        hoy = date.today()
        ultimo_dia_mes = date(hoy.year, hoy.month, monthrange(hoy.year, hoy.month)[1])
        
        # Necesitamos incluir el socio_id y el monto para que el formulario sea válido
        data = {
            'socio': self.socio.id,
            'monto': self.modalidad.precio,
            'fecha_vencimiento': ultimo_dia_mes.strftime('%Y-%m-%d')
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pagos:listar_pagos'))
        
        # Verificar que se creó el pago
        self.assertEqual(Pago.objects.filter(socio=self.socio).count(), 2)  # Ya había un pago creado en setUp
        nuevo_pago = Pago.objects.latest('id')
        self.assertEqual(nuevo_pago.socio, self.socio)
        self.assertEqual(nuevo_pago.monto, self.modalidad.precio)
        
        # Verificar que se cerró el historial anterior y se creó uno nuevo
        historial_anterior = HistorialModalidad.objects.get(id=self.historial_modalidad.id)
        self.assertIsNotNone(historial_anterior.fecha_fin)
        
        nuevo_historial = HistorialModalidad.objects.filter(
            socio=self.socio,
            fecha_fin__isnull=True
        ).first()
        self.assertIsNotNone(nuevo_historial)
        self.assertEqual(nuevo_historial.precio_en_el_momento, self.modalidad.precio)
    
    def test_alta_pago_sin_modalidad(self):
        """Test para verificar que no se puede registrar un pago sin modalidad asignada"""
        # Eliminar el historial de modalidad
        self.historial_modalidad.delete()
        
        url = f"{reverse('pagos:alta_pago')}?socio_id={self.socio.id}"
        response = self.client.get(url)
        
        # Verificar redirección a cambiar modalidad
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('modalidades:cambiar_modalidad', args=[self.socio.id]))
        
        # Verificar mensaje de advertencia
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("El socio no tiene una modalidad activa asignada", str(messages[0]))
    
    def test_listar_pagos_get(self):
        """Test para la vista de listar pagos (GET)"""
        url = reverse('pagos:listar_pagos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pagos/listar_pagos.html')
        self.assertIn(self.pago, response.context['pagos'])
    
    def test_listar_pagos_filtros(self):
        """Test para la vista de listar pagos con filtros"""
        # Crear otro pago con fecha diferente y otro socio
        otro_socio = Socio.objects.create(
            nombre='Maria',
            apellido='Gomez',
            email='maria.gomez@example.com',
            telefono='9876543210'
        )
        
        otro_pago = Pago.objects.create(
            socio=otro_socio,
            monto=Decimal('800.00'),
            fecha_vencimiento=date.today() + timedelta(days=45)
        )
        
        # Probar filtro por fecha
        url = f"{reverse('pagos:listar_pagos')}?fecha_desde={date.today().strftime('%Y-%m-%d')}"
        response = self.client.get(url)
        self.assertEqual(len(response.context['pagos']), 2)  # Ambos pagos están en o después de hoy
        
        # Probar filtro por nombre de socio
        url = f"{reverse('pagos:listar_pagos')}?socio=Juan"
        response = self.client.get(url)
        self.assertEqual(len(response.context['pagos']), 1)
        self.assertIn(self.pago, response.context['pagos'])
        self.assertNotIn(otro_pago, response.context['pagos'])
    
    def test_eliminar_pago_get(self):
        """Test para la vista de confirmar eliminación de pago (GET)"""
        url = reverse('pagos:eliminar_pago', args=[self.pago.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pagos/confirmar_eliminar_pago.html')
        self.assertEqual(response.context['pago'], self.pago)
    
    def test_eliminar_pago_post(self):
        """Test para la vista de eliminar pago (POST)"""
        url = reverse('pagos:eliminar_pago', args=[self.pago.id])
        response = self.client.post(url)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('pagos:listar_pagos'))
        
        # Verificar que el pago fue eliminado
        self.assertFalse(Pago.objects.filter(id=self.pago.id).exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn("eliminado correctamente", str(messages[0]))
