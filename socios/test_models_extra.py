from datetime import timedelta, date
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from unittest.mock import MagicMock

from socios.models import Socio, Observacion
from ejercicios.models import Ejercicio, RegistroEjercicio
from registros.models import RegistroEntrada


class SocioModelExtraCoverageTest(TestCase):
    """Pruebas adicionales para alcanzar 100 % de coverage en socios/models.py"""

    def setUp(self):
        # Crear socio completo
        self.socio = Socio.objects.create(
            nombre="Ana",
            apellido="Martínez",
            email="ana.martinez@example.com",
            telefono="123456789",
            fecha_nacimiento=date(1995, 6, 15),
        )

        # Crear dos ejercicios para los registros de prueba
        self.ejercicio_1 = Ejercicio.objects.create(nombre="Press Banca")
        self.ejercicio_2 = Ejercicio.objects.create(nombre="Sentadilla")

        # Crear registros de ejercicio (dos fechas distintas para mismo ejercicio)
        r1 = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio_1,
            peso=70,
        )
        # Uno más reciente, debe ser tomado por la propiedad
        r2 = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio_1,
            peso=72,
        )
        # Segundo ejercicio
        r3 = RegistroEjercicio.objects.create(
            socio=self.socio,
            ejercicio=self.ejercicio_2,
            peso=80,
        )
        # Ajustar fechas manualmente para asegurar orden
        today = timezone.now().date()
        r1.fecha = today - timedelta(days=5)
        r1.save(update_fields=["fecha"])
        r2.fecha = today - timedelta(days=1)
        r2.save(update_fields=["fecha"])
        r3.fecha = today - timedelta(days=3)
        r3.save(update_fields=["fecha"])

    def test_pesos_por_ejercicio_cached(self):
        """Verifica que pesos_por_ejercicio devuelve último peso por ejercicio y usa caché."""
        data = self.socio.pesos_por_ejercicio
        # Ejercicio 1 debe tener 72 (más reciente)
        self.assertEqual(data[self.ejercicio_1.id], Decimal("72"))
        # Ejercicio 2 debe tener 80
        self.assertEqual(data[self.ejercicio_2.id], Decimal("80"))

        # Llamada nuevamente debe usar caché y devolver mismo resultado
        self.assertIs(self.socio.pesos_por_ejercicio, data)

    def test_pesos_con_fechas_por_ejercicio(self):
        """Verifica estructura y datos de pesos_con_fechas_por_ejercicio."""
        data = self.socio.pesos_con_fechas_por_ejercicio
        info_e1 = data[self.ejercicio_1.id]
        self.assertEqual(info_e1["peso"], Decimal("72"))
        expected_e1_fecha = timezone.now().date() - timedelta(days=1)
        self.assertEqual(info_e1["fecha"], expected_e1_fecha)

        info_e2 = data[self.ejercicio_2.id]
        self.assertEqual(info_e2["peso"], Decimal("80"))
        expected_e2_fecha = timezone.now().date() - timedelta(days=3)
        self.assertEqual(info_e2["fecha"], expected_e2_fecha)

        # Caché
        self.assertIs(self.socio.pesos_con_fechas_por_ejercicio, data)

    def test_observaciones_activas_y_pasadas(self):
        """Valida filtrado de observaciones activas y pasadas."""
        hoy = timezone.now().date()
        # Activa: sin fecha_fin
        obs_activa = Observacion.objects.create(
            socio=self.socio,
            descripcion="Lesión hombro",
            fecha_inicio=hoy - timedelta(days=1),
        )
        # Pasada: fecha_fin <= hoy
        obs_pasada = Observacion.objects.create(
            socio=self.socio,
            descripcion="Molestia rodilla",
            fecha_inicio=hoy - timedelta(days=10),
            fecha_fin=hoy - timedelta(days=5),
        )

        # Primera llamada (sin caché en atributo), debe filtrar correctamente
        activas = list(self.socio.get_observaciones_activas())
        pasadas = list(self.socio.get_observaciones_pasadas())

        self.assertIn(obs_activa, activas)
        self.assertNotIn(obs_activa, pasadas)
        self.assertIn(obs_pasada, pasadas)
        self.assertNotIn(obs_pasada, activas)

        # Guardar resultados en atributos para forzar la otra rama
        self.socio.observaciones_activas = activas
        self.socio.observaciones_pasadas = pasadas

        # Segunda llamada: debe devolver directamente los atributos (cubre líneas 53 y 59)
        self.assertIs(self.socio.get_observaciones_activas(), activas)
        self.assertIs(self.socio.get_observaciones_pasadas(), pasadas)

    def test_estado_cuota_sin_ultimo_pago(self):
        """Cubre rama donde existen pagos pero .first() devuelve None."""
        from unittest.mock import PropertyMock, patch

        mock_pagos_qs = MagicMock()
        mock_pagos_qs.exists.return_value = True
        mock_ordered = MagicMock()
        mock_ordered.first.return_value = None  # Fuerza rama donde no hay ultimo_pago
        mock_pagos_qs.order_by.return_value = mock_ordered

        with patch("socios.models.Socio.pagos", new_callable=PropertyMock) as mock_prop:
            mock_prop.return_value = mock_pagos_qs
            self.assertEqual(self.socio.estado_cuota(), "vencida")

    def test_excedio_asistencias_semanales_sin_modalidad(self):
        """Debe devolver True cuando el socio no tiene modalidad."""
        socio_sin_modalidad = Socio.objects.create(nombre="Luis", apellido="Suarez")
        self.assertTrue(socio_sin_modalidad.excedio_asistencias_semanales())

    def test_dias_sin_asistir(self):
        """Verifica cálculo de días sin asistir."""
        # Sin asistencias debería devolver "-"
        self.assertEqual(self.socio.dias_sin_asistir(), "-")

        # Crear asistencia hace 4 días
        entrada = RegistroEntrada.objects.create(socio=self.socio)
        entrada.fecha_hora = timezone.now() - timedelta(days=4)
        entrada.save(update_fields=["fecha_hora"])

        self.assertEqual(self.socio.dias_sin_asistir(), 4)
