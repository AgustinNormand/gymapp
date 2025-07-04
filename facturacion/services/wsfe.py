"""
Servicio de Facturación Electrónica (WSFE) para la AFIP

Este módulo implementa las funcionalidades para conectarse con el servicio de 
Factura Electrónica de AFIP y generar comprobantes electrónicos.
"""
import datetime
import xml.etree.ElementTree as ET

import requests
import xmltodict

from .wsaa import WSAAService

# URLs de los servicios web de AFIP
WSFE_URLS = {
    'testing': 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx',
    'produccion': 'https://servicios1.afip.gov.ar/wsfev1/service.asmx'
}

class WSFEService:
    """
    Servicio para facturación electrónica con AFIP
    """
    def __init__(self, cert_path=None, private_key_path=None, ambiente='testing', cuit=None):
        """
        Inicializa el servicio WSFE
        
        Args:
            cert_path (str): Ruta al certificado .crt
            private_key_path (str): Ruta a la clave privada .key
            ambiente (str): 'testing' o 'produccion'
            cuit (str): CUIT del emisor
        """
        self.ambiente = ambiente
        self.url = WSFE_URLS.get(ambiente)
        self.cuit = cuit
        
        # Servicio de autenticación
        self.auth_service = WSAAService(cert_path, private_key_path, ambiente)
    
    def _get_auth_header(self):
        """
        Obtener cabecera de autenticación para el servicio WSFE
        
        Returns:
            dict: Información de autenticación (Token, Sign, Cuit)
        """
        # Obtener ticket de acceso
        ta = self.auth_service.get_access_ticket('wsfe')
        
        return {
            'Token': ta['token'],
            'Sign': ta['sign'],
            'Cuit': self.cuit
        }
    
    def _soap_request(self, operation, request_data):
        """
        Realizar una solicitud SOAP al WebService
        
        Args:
            operation (str): Nombre de la operación
            request_data (dict): Datos de la solicitud
            
        Returns:
            dict: Respuesta del servicio
        """
        # Convertir datos a XML
        request_xml = xmltodict.unparse(request_data, pretty=True)
        
        # Construir envelope SOAP
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ar="http://ar.gov.afip.dif.FEV1/">
    <soap:Header/>
    <soap:Body>
        <ar:{operation}>
            {request_xml}
        </ar:{operation}>
    </soap:Body>
</soap:Envelope>"""
        
        # Configurar headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'http://ar.gov.afip.dif.FEV1/{operation}'
        }
        
        # Hacer la petición
        response = requests.post(self.url, data=soap_envelope, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error en WSFE: {response.status_code} - {response.text}")
        
        # Procesar respuesta XML
        try:
            response_dict = xmltodict.parse(response.text)
            return response_dict['soap:Envelope']['soap:Body'][f'{operation}Response'][f'{operation}Result']
        except Exception as e:
            raise Exception(f"Error al procesar respuesta WSFE: {str(e)}")
    
    def get_comp_ultimo(self, punto_vta, tipo_cbte):
        """
        Obtiene el último número de comprobante para un punto de venta y tipo de comprobante
        
        Args:
            punto_vta (int): Número de punto de venta
            tipo_cbte (str): Tipo de comprobante (ej: '1', '6', '11')
            
        Returns:
            int: Último número de comprobante
        """
        request_data = {
            'Auth': self._get_auth_header(),
            'PtoVta': punto_vta,
            'CbteTipo': tipo_cbte
        }
        
        response = self._soap_request('FECompUltimoAutorizado', request_data)
        
        if response.get('Errors'):
            errors = response['Errors']['Err']
            error_msg = errors['Msg'] if isinstance(errors, dict) else ', '.join([e['Msg'] for e in errors])
            raise Exception(f"Error al obtener último comprobante: {error_msg}")
        
        return int(response['CbteNro'])
    
    def get_puntos_venta(self):
        """
        Obtiene los puntos de venta habilitados para el CUIT
        
        Returns:
            list: Lista de puntos de venta
        """
        request_data = {
            'Auth': self._get_auth_header()
        }
        
        response = self._soap_request('FEParamGetPtosVenta', request_data)
        
        if response.get('Errors'):
            errors = response['Errors']['Err']
            error_msg = errors['Msg'] if isinstance(errors, dict) else ', '.join([e['Msg'] for e in errors])
            raise Exception(f"Error al obtener puntos de venta: {error_msg}")
        
        result = []
        ptos_venta = response.get('ResultGet', {}).get('PtoVenta', [])
        
        # Si es un único punto de venta, viene como diccionario
        if isinstance(ptos_venta, dict):
            ptos_venta = [ptos_venta]
            
        for pto in ptos_venta:
            result.append({
                'nro': int(pto['Nro']),
                'emisionTipo': pto['EmisionTipo'],
                'bloqueado': pto['Bloqueado'] == 'S',
                'fechaBaja': pto.get('FchBaja')
            })
        
        return result
    
    def get_tipos_comprobante(self):
        """
        Obtiene los tipos de comprobante disponibles
        
        Returns:
            list: Lista de tipos de comprobante
        """
        request_data = {
            'Auth': self._get_auth_header()
        }
        
        response = self._soap_request('FEParamGetTiposCbte', request_data)
        
        if response.get('Errors'):
            errors = response['Errors']['Err']
            error_msg = errors['Msg'] if isinstance(errors, dict) else ', '.join([e['Msg'] for e in errors])
            raise Exception(f"Error al obtener tipos de comprobante: {error_msg}")
        
        result = []
        tipos = response.get('ResultGet', {}).get('CbteTipo', [])
        
        # Si es un único tipo, viene como diccionario
        if isinstance(tipos, dict):
            tipos = [tipos]
            
        for tipo in tipos:
            result.append({
                'id': tipo['Id'],
                'descripcion': tipo['Desc'],
                'fechaDesde': tipo.get('FchDesde'),
                'fechaHasta': tipo.get('FchHasta')
            })
        
        return result
    
    def solicitar_cae(self, datos_factura):
        """
        Solicita autorización para una factura (CAE)
        
        Args:
            datos_factura (dict): Datos de la factura
                {
                    'tipo_cbte': str,  # Tipo de comprobante ('1', '6', '11', etc.)
                    'punto_vta': int,  # Punto de venta
                    'concepto': int,   # Concepto (1=Productos, 2=Servicios, 3=Productos y Servicios)
                    'tipo_doc': str,   # Tipo de documento del cliente ('80'=CUIT, '96'=DNI, etc.)
                    'nro_doc': str,    # Número de documento del cliente
                    'cbt_desde': int,  # Número de comprobante desde
                    'cbt_hasta': int,  # Número de comprobante hasta (igual a desde)
                    'imp_total': float,  # Importe total
                    'imp_neto': float,   # Importe neto
                    'imp_iva': float,    # Importe IVA
                    'fecha_cbte': str,   # Fecha del comprobante (formato AAAAMMDD)
                    'fecha_serv_desde': str,  # Fecha del servicio desde (formato AAAAMMDD)
                    'fecha_serv_hasta': str,  # Fecha del servicio hasta (formato AAAAMMDD)
                    'fecha_venc_pago': str,   # Fecha de vencimiento del pago (formato AAAAMMDD)
                    'moneda_id': str,         # Moneda ('PES' = Pesos argentinos)
                    'moneda_ctz': float       # Cotización de la moneda
                }
                
        Returns:
            dict: Resultado de la autorización
                {
                    'cae': str,              # CAE obtenido
                    'vencimiento_cae': str,  # Vencimiento del CAE (formato AAAAMMDD)
                    'resultado': str,        # Resultado ('A' = Aprobado, 'R' = Rechazado)
                    'observaciones': list,   # Observaciones
                    'errores': list          # Errores
                }
        """
        # Obtener fecha actual si no se proporciona
        hoy = datetime.datetime.now()
        fecha_cbte = datos_factura.get('fecha_cbte', hoy.strftime('%Y%m%d'))
        
        # Valores por defecto
        defaults = {
            'concepto': 1,  # Productos
            'moneda_id': 'PES',  # Pesos argentinos
            'moneda_ctz': 1.0,  # Cotización 1:1
        }
        
        # Aplicar defaults para valores no proporcionados
        for key, value in defaults.items():
            if key not in datos_factura:
                datos_factura[key] = value
        
        # Si es concepto 2 o 3 (servicios), se requieren fechas adicionales
        if datos_factura['concepto'] in (2, 3):
            if 'fecha_serv_desde' not in datos_factura:
                datos_factura['fecha_serv_desde'] = fecha_cbte
            if 'fecha_serv_hasta' not in datos_factura:
                datos_factura['fecha_serv_hasta'] = fecha_cbte
            if 'fecha_venc_pago' not in datos_factura:
                datos_factura['fecha_venc_pago'] = fecha_cbte
        
        # Construir la solicitud
        comprobante = {
            'CantReg': 1,  # Cantidad de registros
            'PtoVta': datos_factura['punto_vta'],
            'CbteTipo': datos_factura['tipo_cbte']
        }
        
        # Armar cabecera
        request_data = {
            'Auth': self._get_auth_header(),
            'FeCAEReq': {
                'FeCabReq': comprobante,
                'FeDetReq': {
                    'FECAEDetRequest': {
                        'Concepto': datos_factura['concepto'],
                        'DocTipo': datos_factura['tipo_doc'],
                        'DocNro': datos_factura['nro_doc'],
                        'CbteDesde': datos_factura['cbt_desde'],
                        'CbteHasta': datos_factura['cbt_hasta'],
                        'CbteFch': datos_factura['fecha_cbte'],
                        'ImpTotal': datos_factura['imp_total'],
                        'ImpTotConc': 0.0,  # Importe no gravado
                        'ImpNeto': datos_factura['imp_neto'],
                        'ImpOpEx': 0.0,  # Importe exento
                        'ImpIVA': datos_factura['imp_iva'],
                        'ImpTrib': 0.0,  # Importe otros tributos
                        'MonId': datos_factura['moneda_id'],
                        'MonCotiz': datos_factura['moneda_ctz']
                    }
                }
            }
        }
        
        # Si es servicio, agregar fechas adicionales
        if datos_factura['concepto'] in (2, 3):
            request_data['FeCAEReq']['FeDetReq']['FECAEDetRequest'].update({
                'FchServDesde': datos_factura['fecha_serv_desde'],
                'FchServHasta': datos_factura['fecha_serv_hasta'],
                'FchVtoPago': datos_factura['fecha_venc_pago']
            })
        
        # Si hay IVA, agregar detalle
        if datos_factura['imp_iva'] > 0:
            alicuota_iva = [
                {
                    'Id': 5,  # 21%
                    'BaseImp': datos_factura['imp_neto'],
                    'Importe': datos_factura['imp_iva']
                }
            ]
            request_data['FeCAEReq']['FeDetReq']['FECAEDetRequest']['Iva'] = {
                'AlicIva': alicuota_iva
            }
        
        # Realizar solicitud
        try:
            response = self._soap_request('FECAESolicitar', request_data)
            
            # Procesar errores generales
            if response.get('Errors'):
                errors = response['Errors']['Err']
                error_list = []
                if isinstance(errors, dict):
                    error_list.append(errors['Msg'])
                else:
                    error_list = [e['Msg'] for e in errors]
                
                return {
                    'cae': None,
                    'vencimiento_cae': None,
                    'resultado': 'R',
                    'observaciones': [],
                    'errores': error_list
                }
            
            # Obtener resultado del primer comprobante
            comprobante = response['FeDetResp']['FECAEDetResponse']
            
            resultado = {
                'cae': comprobante.get('CAE'),
                'vencimiento_cae': comprobante.get('CAEFchVto'),
                'resultado': comprobante.get('Resultado'),
                'observaciones': [],
                'errores': []
            }
            
            # Procesar observaciones si existen
            if 'Observaciones' in comprobante:
                obs = comprobante['Observaciones'].get('Obs', [])
                if isinstance(obs, dict):
                    resultado['observaciones'].append(obs['Msg'])
                else:
                    resultado['observaciones'] = [o['Msg'] for o in obs]
            
            return resultado
            
        except Exception as e:
            return {
                'cae': None,
                'vencimiento_cae': None,
                'resultado': 'R',
                'observaciones': [],
                'errores': [str(e)]
            }
