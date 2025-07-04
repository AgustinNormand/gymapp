"""
Servicio de Autenticación y Autorización (WSAA) para la AFIP

Este módulo implementa la autenticación con los Web Services de AFIP
para obtener un Ticket de Acceso (TA) que permita utilizar los servicios
de facturación electrónica.
"""
import base64
import datetime
import os
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

import requests
import xmltodict
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from django.conf import settings

# URLs de los servicios web de AFIP
WSAA_URLS = {
    'testing': 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms',
    'produccion': 'https://wsaa.afip.gov.ar/ws/services/LoginCms'
}

class WSAAService:
    """
    Servicio para autenticación con AFIP mediante WSAA
    """
    def __init__(self, cert_path=None, private_key_path=None, ambiente='testing'):
        """
        Inicializa el servicio WSAA
        
        Args:
            cert_path (str): Ruta al certificado .crt
            private_key_path (str): Ruta a la clave privada .key
            ambiente (str): 'testing' o 'produccion'
        """
        self.cert_path = cert_path
        self.private_key_path = private_key_path
        self.ambiente = ambiente
        self.url = WSAA_URLS.get(ambiente)
        
        # Crear carpeta para almacenar tickets de acceso
        os.makedirs(os.path.join(settings.BASE_DIR, 'facturacion', 'tickets'), exist_ok=True)
    
    def _get_ta_path(self, service):
        """Ruta donde se guarda el Ticket de Acceso para un servicio"""
        return os.path.join(settings.BASE_DIR, 'facturacion', 'tickets', f'TA-{service}-{self.ambiente}.xml')
    
    def create_tra(self, service, ttl=24):
        """
        Crear un Ticket de Requerimiento de Acceso (TRA)
        
        Args:
            service (str): Nombre del servicio (ej: 'wsfe')
            ttl (int): Tiempo de vida en horas (por defecto 24)
            
        Returns:
            str: XML del TRA
        """
        # Generar IDs únicos
        unique_id = str(uuid.uuid4())
        
        # Calcular tiempo de generación y expiración
        now = datetime.now()
        gen_time = now.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        exp_time = (now + timedelta(hours=ttl)).strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        # Crear estructura XML para el TRA
        tra = ET.Element('loginTicketRequest')
        tra.set('version', '1.0')
        
        header = ET.SubElement(tra, 'header')
        ET.SubElement(header, 'uniqueId').text = unique_id
        ET.SubElement(header, 'generationTime').text = gen_time
        ET.SubElement(header, 'expirationTime').text = exp_time
        
        ET.SubElement(tra, 'service').text = service
        
        # Convertir a string XML
        tra_xml = ET.tostring(tra, encoding='UTF-8')
        return tra_xml
    
    def sign_tra(self, tra_xml):
        """
        Firmar el TRA con el certificado digital
        
        Args:
            tra_xml (bytes): XML del TRA
            
        Returns:
            str: CMS (PKCS#7) en base64
        """
        # Leer certificado y clave privada
        with open(self.cert_path, 'rb') as cert_file:
            cert_data = cert_file.read()
            cert = load_pem_x509_certificate(cert_data)
        
        with open(self.private_key_path, 'rb') as key_file:
            key_data = key_file.read()
            private_key = serialization.load_pem_private_key(
                key_data, 
                password=None  # Si la clave tiene contraseña, proporcionarla aquí
            )
        
        # Firmar el TRA
        signature = private_key.sign(
            tra_xml,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        
        # Codificar en base64
        return base64.b64encode(signature).decode('utf-8')
    
    def call_wsaa(self, cms):
        """
        Llamar al web service WSAA para autenticar
        
        Args:
            cms (str): CMS en base64
            
        Returns:
            dict: Datos del Ticket de Acceso
        """
        # Crear envelope SOAP
        soap_request = f"""
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsaa="http://wsaa.view.sua.dvadac.desein.afip.gov">
            <soap:Header/>
            <soap:Body>
                <wsaa:loginCms>
                    <wsaa:in0>{cms}</wsaa:in0>
                </wsaa:loginCms>
            </soap:Body>
        </soap:Envelope>
        """
        
        # Configurar headers
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }
        
        # Hacer la petición
        response = requests.post(self.url, data=soap_request, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error al autenticar con WSAA: {response.status_code} - {response.text}")
        
        # Procesar respuesta XML
        try:
            response_dict = xmltodict.parse(response.text)
            login_result = response_dict['soap:Envelope']['soap:Body']['loginCmsResponse']['loginCmsReturn']
            
            # Parsear el resultado para obtener token y sign
            result_dict = xmltodict.parse(login_result)
            return {
                'token': result_dict['loginTicketResponse']['credentials']['token'],
                'sign': result_dict['loginTicketResponse']['credentials']['sign'],
                'expiration': result_dict['loginTicketResponse']['header']['expirationTime']
            }
        except Exception as e:
            raise Exception(f"Error al procesar respuesta WSAA: {str(e)}")
    
    def get_access_ticket(self, service):
        """
        Obtener un Ticket de Acceso para un servicio específico
        Si existe un ticket válido en el caché, lo retorna
        Si no, genera uno nuevo
        
        Args:
            service (str): Nombre del servicio (ej: 'wsfe')
            
        Returns:
            dict: Datos del Ticket de Acceso (token, sign)
        """
        # Verificar si existe un ticket válido
        ta_path = self._get_ta_path(service)
        if os.path.exists(ta_path):
            try:
                with open(ta_path, 'r') as f:
                    ta_xml = f.read()
                    
                # Parsear XML
                ta_dict = xmltodict.parse(ta_xml)
                expiration_str = ta_dict['loginTicketResponse']['header']['expirationTime']
                expiration = datetime.fromisoformat(expiration_str[:-6])  # Eliminar zona horaria
                
                # Si el ticket es válido por al menos una hora más, usarlo
                if expiration > datetime.now() + timedelta(hours=1):
                    return {
                        'token': ta_dict['loginTicketResponse']['credentials']['token'],
                        'sign': ta_dict['loginTicketResponse']['credentials']['sign'],
                        'expiration': expiration_str
                    }
            except Exception:
                # Si hay un error al leer el ticket, generar uno nuevo
                pass
        
        # Si no hay ticket válido, generar uno nuevo
        tra = self.create_tra(service)
        cms = self.sign_tra(tra)
        ta = self.call_wsaa(cms)
        
        # Guardar el nuevo ticket
        ta_xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<loginTicketResponse>
    <header>
        <expirationTime>{ta['expiration']}</expirationTime>
    </header>
    <credentials>
        <token>{ta['token']}</token>
        <sign>{ta['sign']}</sign>
    </credentials>
</loginTicketResponse>
"""
        with open(ta_path, 'w') as f:
            f.write(ta_xml)
        
        return ta
