"""
Generador de PDFs para facturas electrónicas

Este módulo se encarga de generar PDFs para las facturas electrónicas
utilizando la biblioteca FPDF.
"""
import os
from datetime import datetime
from fpdf import FPDF
from django.conf import settings

class FacturaPDF(FPDF):
    """
    Clase para generar PDFs de facturas utilizando FPDF
    """
    def __init__(self, factura, datos_emisor):
        """
        Inicializa el generador de PDF
        
        Args:
            factura: Instancia del modelo Factura
            datos_emisor: Datos del emisor (ConfiguracionFacturacion)
        """
        super().__init__(orientation='P', unit='mm', format='A4')
        self.factura = factura
        self.datos_emisor = datos_emisor
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        
    def header(self):
        """Cabecera del documento"""
        # Logo (si existe)
        logo_path = os.path.join(settings.STATIC_ROOT, 'img/logo.png')
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
            
        # Título de la factura
        tipo_factura = dict(self.factura.TIPOS_COMPROBANTE).get(self.factura.tipo_comprobante, 'Factura')
        self.set_font('Arial', 'B', 18)
        self.cell(0, 10, f"{tipo_factura}", 0, 1, 'C')
        
        # Línea y espacio
        self.line(10, 25, 200, 25)
        self.ln(5)
        
    def footer(self):
        """Pie de página del documento"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')
        self.cell(0, 10, 'Documento generado electrónicamente', 0, 0, 'R')
        
    def add_datos_emisor(self):
        """Agregar datos del emisor"""
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'DATOS DEL EMISOR:', 0, 1)
        
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Razón Social: {self.datos_emisor.razon_social}', 0, 1)
        self.cell(0, 5, f'CUIT: {self.datos_emisor.cuit}', 0, 1)
        self.cell(0, 5, f'Domicilio: {self.datos_emisor.domicilio_fiscal}', 0, 1)
        
        condicion_iva = {
            'RI': 'Responsable Inscripto',
            'MT': 'Monotributista',
            'EX': 'Exento'
        }.get(self.datos_emisor.condicion_iva, self.datos_emisor.condicion_iva)
        
        self.cell(0, 5, f'Condición frente al IVA: {condicion_iva}', 0, 1)
        self.cell(0, 5, f'Ingresos Brutos: {self.datos_emisor.ingresos_brutos}', 0, 1)
        self.cell(0, 5, f'Inicio de Actividades: {self.datos_emisor.inicio_actividades.strftime("%d/%m/%Y")}', 0, 1)
        
        # Línea divisoria
        self.ln(2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        
    def add_datos_comprobante(self):
        """Agregar datos del comprobante"""
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'COMPROBANTE:', 0, 1)
        
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Número: {self.factura.punto_venta:04d}-{self.factura.numero_comprobante:08d}', 0, 1)
        self.cell(0, 5, f'Fecha de Emisión: {self.factura.fecha_emision.strftime("%d/%m/%Y")}', 0, 1)
        self.cell(0, 5, f'CAE: {self.factura.cae}', 0, 1)
        self.cell(0, 5, f'Vencimiento CAE: {self.factura.vencimiento_cae.strftime("%d/%m/%Y")}', 0, 1)
        
        # Línea divisoria
        self.ln(2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        
    def add_datos_cliente(self):
        """Agregar datos del cliente"""
        # Obtener datos fiscales del socio
        socio = self.factura.pago.socio
        datos_fiscales = None
        
        try:
            datos_fiscales = socio.datos_fiscales
        except:
            pass
            
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'DATOS DEL CLIENTE:', 0, 1)
        
        self.set_font('Arial', '', 10)
        self.cell(0, 5, f'Nombre: {socio.nombre} {socio.apellido}', 0, 1)
        
        if datos_fiscales:
            # Tipo de documento
            tipo_doc = {
                '80': 'CUIT',
                '86': 'CUIL',
                '96': 'DNI',
            }.get(datos_fiscales.tipo_documento, 'DNI')
            
            self.cell(0, 5, f'{tipo_doc}: {datos_fiscales.numero_documento}', 0, 1)
            
            # Condición frente al IVA
            condicion_iva = {
                'CF': 'Consumidor Final',
                'RI': 'Responsable Inscripto',
                'MT': 'Monotributista',
                'EX': 'Exento',
            }.get(datos_fiscales.condicion_iva, datos_fiscales.condicion_iva)
            
            self.cell(0, 5, f'Condición frente al IVA: {condicion_iva}', 0, 1)
            
            # Domicilio si está disponible
            if datos_fiscales.domicilio:
                self.cell(0, 5, f'Domicilio: {datos_fiscales.domicilio}', 0, 1)
        else:
            # Datos mínimos
            self.cell(0, 5, 'Condición frente al IVA: Consumidor Final', 0, 1)
            self.cell(0, 5, f'DNI: {socio.dni}', 0, 1)
            
        # Línea divisoria
        self.ln(2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)
        
    def add_detalle_factura(self):
        """Agregar detalle de la factura"""
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, 'DETALLE:', 0, 1)
        
        # Encabezados de la tabla
        self.set_fill_color(230, 230, 230)
        self.set_font('Arial', 'B', 9)
        self.cell(100, 6, 'Descripción', 1, 0, 'C', True)
        self.cell(30, 6, 'Cantidad', 1, 0, 'C', True)
        self.cell(30, 6, 'Precio Unitario', 1, 0, 'C', True)
        self.cell(30, 6, 'Importe', 1, 1, 'C', True)
        
        # Detalle (en este caso, solo la cuota)
        self.set_font('Arial', '', 9)
        pago = self.factura.pago
        
        # Intentar obtener la modalidad del socio
        descripcion = "Servicio de gimnasio"
        try:
            historial_modalidad = pago.socio.modalidad_actual()
            if historial_modalidad:
                descripcion = f"Cuota {historial_modalidad.modalidad.nombre}"
        except:
            pass
            
        # Agregar el ítem
        self.cell(100, 6, descripcion, 1, 0)
        self.cell(30, 6, '1', 1, 0, 'C')
        self.cell(30, 6, f'${pago.monto:.2f}', 1, 0, 'R')
        self.cell(30, 6, f'${pago.monto:.2f}', 1, 1, 'R')
        
        # Total
        self.set_font('Arial', 'B', 10)
        self.cell(160, 8, 'Total:', 0, 0, 'R')
        self.cell(30, 8, f'${pago.monto:.2f}', 1, 1, 'R')
        
    def add_notas_adicionales(self):
        """Agregar notas adicionales"""
        self.ln(10)
        self.set_font('Arial', '', 8)
        self.multi_cell(0, 4, 'Esta factura fue generada en un entorno automatizado y es válida sin firma manuscrita según RG AFIP 1415/03.')
        
    def add_codigo_barras(self):
        """Agregar código de barras con información del CAE"""
        # En una implementación real, aquí se generaría un código de barras
        # con la información del CAE, según especificaciones de AFIP
        pass
        
    def generar(self):
        """
        Generar el PDF completo de la factura
        
        Returns:
            str: Ruta al archivo PDF generado
        """
        # Datos del emisor
        self.add_datos_emisor()
        
        # Datos del comprobante
        self.add_datos_comprobante()
        
        # Datos del cliente
        self.add_datos_cliente()
        
        # Detalle de la factura
        self.add_detalle_factura()
        
        # Notas adicionales
        self.add_notas_adicionales()
        
        # Código de barras (opcional)
        self.add_codigo_barras()
        
        # Guardar el archivo
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'facturas'), exist_ok=True)
        filename = self.factura.get_pdf_filename()
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'facturas', filename)
        
        self.output(pdf_path)
        return os.path.join('facturas', filename)

def generar_pdf_factura(factura):
    """
    Función principal para generar el PDF de una factura
    
    Args:
        factura: Instancia del modelo Factura
        
    Returns:
        str: Ruta relativa al archivo PDF generado
    """
    from facturacion.models import ConfiguracionFacturacion
    
    # Obtener la configuración de facturación
    try:
        config = ConfiguracionFacturacion.objects.first()
        if not config:
            raise Exception("No se encontró la configuración de facturación")
    except Exception as e:
        # Manejar el error o crear una configuración por defecto
        raise e
    
    # Generar el PDF
    generator = FacturaPDF(factura, config)
    return generator.generar()
