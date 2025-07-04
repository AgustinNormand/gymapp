from django.db import models
from pagos.models import Pago
from socios.models import Socio
from django.core.validators import RegexValidator
import os

class DatosFiscalesSocio(models.Model):
    socio = models.OneToOneField(Socio, on_delete=models.CASCADE, related_name='datos_fiscales')
    tipo_documento = models.CharField(max_length=2, choices=[
        ('80', 'CUIT'),
        ('86', 'CUIL'),
        ('96', 'DNI'),
    ], default='96')
    numero_documento = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[0-9]{8,11}$',
            message='El número de documento debe tener entre 8 y 11 dígitos',
        )]
    )
    condicion_iva = models.CharField(max_length=2, choices=[
        ('CF', 'Consumidor Final'),
        ('RI', 'Responsable Inscripto'),
        ('MT', 'Monotributista'),
        ('EX', 'Exento'),
    ], default='CF')
    domicilio = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return f"Datos fiscales de {self.socio.nombre} {self.socio.apellido}"


class Factura(models.Model):
    TIPOS_COMPROBANTE = [
        ('11', 'Factura C'),  # Común para monotributistas
        ('6', 'Factura B'),   # Para responsables inscriptos a consumidores finales
        ('1', 'Factura A'),   # Entre responsables inscriptos
    ]
    
    ESTADOS = [
        ('emitida', 'Emitida'),
        ('enviada', 'Enviada'),
        ('anulada', 'Anulada'),
        ('error', 'Error'),
    ]
    
    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='factura')
    tipo_comprobante = models.CharField(max_length=2, choices=TIPOS_COMPROBANTE, default='11')
    punto_venta = models.IntegerField(default=1)
    numero_comprobante = models.BigIntegerField()
    cae = models.CharField(max_length=14)
    vencimiento_cae = models.DateField()
    pdf = models.FileField(upload_to='facturas/', null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='emitida')
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        tipo = dict(self.TIPOS_COMPROBANTE).get(self.tipo_comprobante)
        return f"{tipo} {self.punto_venta:0>4}-{self.numero_comprobante:0>8} - {self.pago.socio}"
    
    def get_pdf_filename(self):
        """Generar nombre de archivo estandarizado para el PDF de la factura"""
        return f"Factura-{self.tipo_comprobante}-{self.punto_venta:0>4}-{self.numero_comprobante:0>8}.pdf"


class ConfiguracionFacturacion(models.Model):
    """Modelo para almacenar configuración global de facturación"""
    razon_social = models.CharField(max_length=255)
    cuit = models.CharField(
        max_length=11,
        validators=[RegexValidator(
            regex=r'^[0-9]{11}$',
            message='El CUIT debe tener 11 dígitos',
        )]
    )
    domicilio_fiscal = models.CharField(max_length=255)
    condicion_iva = models.CharField(max_length=2, choices=[
        ('RI', 'Responsable Inscripto'),
        ('MT', 'Monotributista'),
        ('EX', 'Exento'),
    ])
    punto_venta = models.IntegerField(default=1)
    ingresos_brutos = models.CharField(max_length=15, blank=True)
    inicio_actividades = models.DateField()
    
    # Datos del certificado digital
    certificado_path = models.CharField(max_length=255, blank=True)
    clave_privada_path = models.CharField(max_length=255, blank=True)
    
    # Ambiente (testing/produccion)
    ambiente = models.CharField(max_length=10, choices=[
        ('testing', 'Homologación/Testing'),
        ('produccion', 'Producción'),
    ], default='testing')
    
    class Meta:
        verbose_name = "Configuración de facturación"
        verbose_name_plural = "Configuración de facturación"
    
    def __str__(self):
        return f"Configuración de facturación para {self.razon_social}"
