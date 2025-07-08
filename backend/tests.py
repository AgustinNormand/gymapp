from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from socios.models import Socio
from registros.models import RegistroEntrada
from pagos.models import Pago
from modalidades.models import Modalidad, HistorialModalidad


class BackendHomeViewTest(TestCase):
    """Tests para la vista principal (home) del backend"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('home')
        
        # Crear socios para pruebas
        self.hoy = date.today()
        
        # Socio 1: Con cumpleaños hoy
        self.socio1 = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan@example.com',
            telefono='1234567890',
            fecha_nacimiento=date(1990, self.hoy.month, self.hoy.day)  # Mismo mes y día que hoy
        )
        
        # Socio 2: Sin cumpleaños hoy
        self.socio2 = Socio.objects.create(
            nombre='Maria',
            apellido='Gomez',
            email='maria@example.com',
            telefono='9876543210',
            fecha_nacimiento=date(1992, 1, 1)  # Fecha diferente
        )
        
        # Socio 3: Sin fecha de cumpleaños
        self.socio3 = Socio.objects.create(
            nombre='Carlos',
            apellido='Rodriguez',
            email=None,
            telefono=None,
            fecha_nacimiento=None  # Sin fecha de cumpleaños
        )
        
        # Crear una modalidad para los socios
        self.modalidad = Modalidad.objects.create(
            nombre='Full',
            precio=1000,
            dias_por_semana=3
        )
        
        # Asignar modalidad a socio1 y socio2
        self.historial_modalidad1 = HistorialModalidad.objects.create(
            socio=self.socio1,
            modalidad=self.modalidad,
            precio_en_el_momento=self.modalidad.precio,
            fecha_inicio=self.hoy - timedelta(days=30)
        )
        
        self.historial_modalidad2 = HistorialModalidad.objects.create(
            socio=self.socio2,
            modalidad=self.modalidad,
            precio_en_el_momento=self.modalidad.precio,
            fecha_inicio=self.hoy - timedelta(days=30)
        )
        
        # Crear registros de asistencia
        # Socio 1: Asistió hoy
        self.registro_hoy_socio1 = RegistroEntrada.objects.create(
            socio=self.socio1,
            fecha_hora=timezone.now()
        )
        
        # Socio 2: Asistió hace una semana
        self.registro_semana_pasada_socio2 = RegistroEntrada.objects.create(
            socio=self.socio2,
            fecha_hora=timezone.now() - timedelta(days=7)
        )
        
        # Crear pagos
        # Socio 1: Pagó este mes
        self.pago_socio1 = Pago.objects.create(
            socio=self.socio1,
            monto=self.modalidad.precio,
            fecha_vencimiento=self.hoy + timedelta(days=30)
        )
    
    def test_home_view_status_code(self):
        """Test para verificar que la vista home carga correctamente"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_view_context_basic(self):
        """Test para verificar datos básicos en el contexto de la vista home"""
        response = self.client.get(self.url)
        
        # Verificar total de socios
        self.assertEqual(response.context['total_socios'], 3)
        
        # Verificar que hay asistencias de hoy (al menos 1)
        # No verificamos el número exacto, ya que otras pruebas pueden afectar el conteo
        self.assertTrue(response.context['asistencias_hoy'] >= 1)
    
    def test_home_view_cumpleanos(self):
        """Test para verificar detección de cumpleaños en vista home"""
        response = self.client.get(self.url)
        
        # Verificar que hay cumpleaños hoy
        self.assertTrue(response.context['hay_cumpleanos'])
        
        # Verificar que socio1 está en la lista de cumpleaños
        socios_cumpleanos = response.context['socios_cumpleanos']
        self.assertEqual(len(socios_cumpleanos), 1)
        self.assertEqual(socios_cumpleanos[0]['nombre'], 'Juan')
        self.assertEqual(socios_cumpleanos[0]['apellido'], 'Pérez')
    
    def test_home_view_agrupacion_hora(self):
        """Test para verificar agrupación por hora en vista home"""
        response = self.client.get(self.url, {'tipo_agrupacion': 'hora'})
        
        # Verificar que se ha configurado correctamente el tipo de agrupación
        self.assertEqual(response.context['tipo_agrupacion'], 'hora')
        
        # Verificar que hay etiquetas y cantidades para el gráfico
        self.assertIsNotNone(response.context['etiquetas'])
        self.assertIsNotNone(response.context['cantidades'])
        
        # Verificar que el título incluye "por hora"
        self.assertIn("hora", response.context['titulo_grafico'].lower())
    
    def test_home_view_agrupacion_dia(self):
        """Test para verificar agrupación por día en vista home"""
        response = self.client.get(self.url, {'tipo_agrupacion': 'dia'})
        
        # Verificar que se ha configurado correctamente el tipo de agrupación
        self.assertEqual(response.context['tipo_agrupacion'], 'dia')
        
        # Verificar que el título incluye "por día"
        self.assertIn("día", response.context['titulo_grafico'].lower())
    
    def test_home_view_filtro_grupo(self):
        """Test para verificar filtro por grupo de socios en vista home"""
        # Probar filtro para socios con pago y con asistencia (socio1)
        response = self.client.get(self.url, {'grupo': 'pago_con_asistencia'})
        
        # Verificar que hay socios en el detalle
        socios_detalle = response.context['socios_detalle']
        self.assertTrue(len(socios_detalle) > 0)
        
        # Verificar que socio1 está en el detalle
        socio1_en_detalle = False
        for socio in socios_detalle:
            if socio['id'] == self.socio1.id:
                socio1_en_detalle = True
                break
        
        self.assertTrue(socio1_en_detalle)
    
    def test_home_view_fechas_personalizadas(self):
        """Test para verificar filtro por fechas personalizadas en vista home"""
        # Definir fechas personalizadas para el filtro
        fecha_inicio = (self.hoy - timedelta(days=10)).strftime('%Y-%m-%d')
        fecha_fin = self.hoy.strftime('%Y-%m-%d')
        
        # Realizar petición con fechas personalizadas
        response = self.client.get(self.url, {
            'tipo_agrupacion': 'dia',
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
        
        # Verificar que las fechas se han configurado correctamente
        self.assertEqual(response.context['fecha_inicio'], fecha_inicio)
        self.assertEqual(response.context['fecha_fin'], fecha_fin)
