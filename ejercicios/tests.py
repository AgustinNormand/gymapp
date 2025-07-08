from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import Ejercicio, RegistroEjercicio
from socios.models import Socio
from modalidades.models import Modalidad, HistorialModalidad


class EjercicioModelTest(TestCase):
    """Tests para el modelo Ejercicio"""
    
    def setUp(self):
        # Crear un ejercicio para pruebas
        self.ejercicio = Ejercicio.objects.create(
            nombre='Sentadillas'
        )
    
    def test_ejercicio_creation(self):
        """Test para verificar la creación correcta de un ejercicio"""
        self.assertEqual(self.ejercicio.nombre, 'Sentadillas')
        self.assertEqual(str(self.ejercicio), 'Sentadillas')
    
    def test_ejercicio_unique_nombre(self):
        """Test para verificar que el nombre del ejercicio sea único"""
        # Intentar crear otro ejercicio con el mismo nombre debería fallar
        with self.assertRaises(Exception):
            Ejercicio.objects.create(nombre='Sentadillas')


class RegistroEjercicioModelTest(TestCase):
    """Tests para el modelo RegistroEjercicio"""
    
    def setUp(self):
        # Crear un socio
        self.modalidad = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
        
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Asignar modalidad al socio
        self.historial_modalidad = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad,
            fecha_inicio=timezone.now().date()
        )
        
        # Crear ejercicios
        self.ejercicio1 = Ejercicio.objects.create(nombre='Press de Banca')
        self.ejercicio2 = Ejercicio.objects.create(nombre='Dominadas')
        
        # Crear registros de ejercicio
        self.registro = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio1,
            fecha=date.today(),
            peso=Decimal('70.5')
        )
    
    def test_registro_ejercicio_creation(self):
        """Test para verificar la creación de un registro de ejercicio"""
        self.assertEqual(self.registro.socio, self.socio)
        self.assertEqual(self.registro.ejercicio, self.ejercicio1)
        self.assertEqual(self.registro.fecha, date.today())
        self.assertEqual(self.registro.peso, Decimal('70.5'))
    
    def test_registro_ejercicio_str(self):
        """Test para verificar la representación en cadena de un registro"""
        expected_str = f"{self.socio} - {self.ejercicio1} - {date.today()} - {self.registro.peso} kg"
        self.assertEqual(str(self.registro), expected_str)

    def test_multiple_registros_por_socio(self):
        """Test para verificar que un socio pueda tener múltiples registros"""
        # Crear un segundo registro para el mismo socio pero con otro ejercicio
        registro2 = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio2,
            fecha=date.today() - timedelta(days=1),  # Ayer
            peso=Decimal('15.0')
        )
        
        # Verificar que ambos registros pertenecen al socio
        registros_socio = RegistroEjercicio.objects.filter(socio=self.socio)
        self.assertEqual(registros_socio.count(), 2)
        self.assertIn(self.registro, registros_socio)
        self.assertIn(registro2, registros_socio)

    def test_registro_unique_por_dia_ejercicio_socio(self):
        """Test para verificar que no puede haber dos registros del mismo ejercicio y socio en el mismo día"""
        # Esto es lógica de negocio implementada en la vista pero no en el modelo
        # Verificamos que se pueden crear dos registros tecnicamente, aunque luego la vista lo evite
        registro_duplicado = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio1,
            fecha=date.today(),
            peso=Decimal('80.0')
        )
        
        # Verificar que se puede crear en el modelo (aunque la vista lo restrinja)
        self.assertTrue(RegistroEjercicio.objects.filter(
            socio=self.socio,
            ejercicio=self.ejercicio1,
            fecha=date.today()
        ).count() > 1)


class EjercicioViewsTest(TestCase):
    """Tests para las vistas de la aplicación ejercicios"""
    
    def setUp(self):
        self.client = Client()
        
        # Crear un socio
        self.modalidad = Modalidad.objects.create(
            nombre='Full',
            precio=Decimal('1000.00'),
            dias_por_semana=3
        )
        
        self.socio = Socio.objects.create(
            nombre='Juan',
            apellido='Pérez',
            email='juan.perez@example.com',
            telefono='1234567890',
            fecha_nacimiento='1990-01-01'
        )
        
        # Asignar modalidad al socio
        self.historial_modalidad = HistorialModalidad.objects.create(
            socio=self.socio,
            modalidad=self.modalidad,
            fecha_inicio=timezone.now().date()
        )
        
        # Crear ejercicios
        self.ejercicio1 = Ejercicio.objects.create(nombre='Press de Banca')
        self.ejercicio2 = Ejercicio.objects.create(nombre='Dominadas')
        
        # Crear un registro de ejercicio
        self.registro = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio1,
            fecha=date.today(),
            peso=Decimal('70.5')
        )
    
    def test_gestionar_registros_get(self):
        """Test para la vista de gestionar registros (GET)"""
        url = reverse('ejercicios:gestionar_registros', args=[self.socio.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ejercicios/gestionar_registros.html')
        self.assertEqual(response.context['socio'], self.socio)
        self.assertIn(self.ejercicio1, response.context['ejercicios'])
        self.assertIn(self.ejercicio2, response.context['ejercicios'])
        self.assertIn(self.registro, response.context['registros'])
    
    def test_gestionar_registros_post_valid(self):
        """Test para la vista de gestionar registros (POST válido)"""
        # Eliminar registro previo del mismo ejercicio para evitar duplicados
        RegistroEjercicio.objects.all().delete()
        
        url = reverse('ejercicios:gestionar_registros', args=[self.socio.id])
        data = {
            'ejercicio': self.ejercicio1.id,
            'peso': '75.5'
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el registro
        self.assertTrue(RegistroEjercicio.objects.filter(
            socio=self.socio,
            ejercicio=self.ejercicio1,
            fecha=date.today(),
            peso=Decimal('75.5')
        ).exists())
    
    def test_gestionar_registros_post_duplicate(self):
        """Test para verificar que no se puede crear un registro duplicado en el mismo día"""
        url = reverse('ejercicios:gestionar_registros', args=[self.socio.id])
        data = {
            'ejercicio': self.ejercicio1.id,
            'peso': '80.0'
        }
        
        # Ya existe un registro para este socio, ejercicio y día
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que sigue habiendo solo un registro para este día
        # (la vista debería impedir la creación del duplicado)
        self.assertEqual(
            RegistroEjercicio.objects.filter(
                socio=self.socio,
                ejercicio=self.ejercicio1,
                fecha=date.today()
            ).count(),
            1  # Solo debería existir el registro original
        )
    
    def test_editar_registro_get(self):
        """Test para la vista de editar registro (GET)"""
        url = reverse('ejercicios:editar_registro', args=[self.registro.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ejercicios/editar_registro.html')
        self.assertEqual(response.context['registro'], self.registro)
        self.assertIn(self.ejercicio1, response.context['ejercicios'])
    
    def test_editar_registro_post(self):
        """Test para la vista de editar registro (POST)"""
        url = reverse('ejercicios:editar_registro', args=[self.registro.id])
        new_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')  # Ayer
        data = {
            'peso': '85.0',
            'fecha': new_date
        }
        
        response = self.client.post(url, data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se actualizó el registro
        self.registro.refresh_from_db()
        self.assertEqual(self.registro.peso, Decimal('85.0'))
        self.assertEqual(self.registro.fecha.strftime('%Y-%m-%d'), new_date)
    
    def test_borrar_registro(self):
        """Test para la vista de borrar registro"""
        url = reverse('ejercicios:borrar_registro', args=[self.registro.id])
        response = self.client.get(url)  # En este caso es GET, no POST
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el registro fue eliminado
        self.assertFalse(RegistroEjercicio.objects.filter(id=self.registro.id).exists())
