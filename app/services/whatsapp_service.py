import requests
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.whapi_token = os.getenv('WHAPI_TOKEN')
        self.base_url = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')
        
        # Logging de configuración
        logger.info(f"WHAPI_BASE_URL configurado: {self.base_url}")
        logger.info(f"WHAPI_TOKEN configurado: {'Sí' if self.whapi_token else 'No'}")
        
        if not self.whapi_token:
            raise ValueError("WHAPI_TOKEN no está configurado en las variables de entorno")
    
    def enviar_mensaje(self, numero_telefono: str, mensaje: str) -> Dict[str, Any]:
        """
        Envía un mensaje de texto a WhatsApp
        
        Args:
            numero_telefono: Número en formato internacional (ej: 573001234567)
            mensaje: Texto del mensaje a enviar
            
        Returns:
            Dict con respuesta de la API
        """
        logger.info(f"Enviando mensaje a {numero_telefono}: {mensaje}")
        
        # ✅ URL CORREGIDA - Verificar si base_url ya tiene barra
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/messages/text"
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": numero_telefono,
            "body": mensaje
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Mensaje enviado exitosamente: {result}")
            
            return {
                "status": "success",
                "message_id": result.get("id"),
                "timestamp": datetime.now().isoformat(),
                "whatsapp_response": result
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout al enviar mensaje")
            return {"error": "Timeout al conectar con Whapi", "status": "failed"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {str(e)}")
            return {"error": f"Error de conexión: {str(e)}", "status": "failed"}
            
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}", "status": "failed"}
    
    def enviar_documento(self, numero_telefono: str, documento_url: str, 
                        nombre_archivo: str = "documento.pdf", 
                        mensaje: str = "") -> Dict[str, Any]:
        """
        Envía un documento (PDF) a WhatsApp
        
        Args:
            numero_telefono: Número en formato internacional
            documento_url: URL pública del documento
            nombre_archivo: Nombre del archivo
            mensaje: Mensaje opcional que acompaña el documento
            
        Returns:
            Dict con respuesta de la API
        """
        logger.info(f"Enviando documento a {numero_telefono}: {documento_url}")
        
        # ✅ URL CORREGIDA - Endpoint correcto para documentos
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/messages/document"
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": numero_telefono,
            "type": "document",
            "document": {
                "link": documento_url,
                "filename": nombre_archivo,
                "caption": mensaje
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Documento enviado exitosamente: {result}")
            
            return {
                "status": "success",
                "message_id": result.get("id"),
                "timestamp": datetime.now().isoformat(),
                "whatsapp_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar documento: {str(e)}")
            return {"error": f"Error al enviar documento: {str(e)}", "status": "failed"}
            
        except Exception as e:
            logger.error(f"Error inesperado al enviar documento: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}", "status": "failed"}
    
    def subir_documento(self, documento_base64: str, nombre_archivo: str) -> Dict[str, Any]:
        """
        Subir documento a WHAPI y obtener ID
        
        Args:
            documento_base64: Documento en base64
            nombre_archivo: Nombre del archivo
            
        Returns:
            Dict con ID del documento subido
        """
        logger.info(f"Subiendo documento: {nombre_archivo}")
        
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/media/upload"
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "type": "document",
            "data": documento_base64,
            "filename": nombre_archivo,
            "mime_type": "application/pdf"
        }
        
        try:
            logger.info(f"Subiendo a WHAPI: {url}")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            logger.info(f"Upload response status: {response.status_code}")
            logger.info(f"Upload response content: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Documento subido exitosamente: {result}")
            return {
                "status": "success",
                "document_id": result.get("id"),
                "whatsapp_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error subiendo documento: {str(e)}")
            return {"error": f"Error subiendo documento: {str(e)}", "status": "failed"}
            
        except Exception as e:
            logger.error(f"Error inesperado subiendo documento: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}", "status": "failed"}

    def enviar_documento_base64(self, numero_telefono: str, documento_base64: str, 
                               nombre_archivo: str, mensaje: str = "") -> Dict[str, Any]:
        """
        Envía documento usando el método correcto: Upload + Send
        
        Args:
            numero_telefono: Número en formato internacional
            documento_base64: Documento en formato base64
            nombre_archivo: Nombre del archivo
            mensaje: Mensaje opcional que acompaña el documento
            
        Returns:
            Dict con respuesta de la API
        """
        logger.info(f"Enviando documento a {numero_telefono}: {nombre_archivo}")
        
        # Paso 1: Subir documento
        logger.info("📤 Paso 1: Subiendo documento...")
        upload_result = self.subir_documento(documento_base64, nombre_archivo)
        
        if "error" in upload_result:
            logger.error(f"Error en upload: {upload_result['error']}")
            return upload_result
        
        document_id = upload_result.get("document_id")
        if not document_id:
            logger.error("No se obtuvo ID del documento")
            return {"error": "No se obtuvo ID del documento", "status": "failed"}
        
        logger.info(f"✅ Documento subido con ID: {document_id}")
        
        # Paso 2: Enviar mensaje con documento
        logger.info("📤 Paso 2: Enviando mensaje con documento...")
        base_url = self.base_url.rstrip('/')
        url = f"{base_url}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "to": numero_telefono,
            "type": "document",
            "document": {
                "id": document_id,
                "caption": mensaje
            }
        }
        
        try:
            logger.info(f"Enviando mensaje a WHAPI: {url}")
            logger.info(f"Payload: {payload}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response content: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Documento enviado exitosamente: {result}")
            
            return {
                "status": "success",
                "message_id": result.get("id"),
                "document_id": document_id,
                "timestamp": datetime.now().isoformat(),
                "whatsapp_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            logger.error(f"Response status: {getattr(e.response, 'status_code', 'N/A')}")
            logger.error(f"Response text: {getattr(e.response, 'text', 'N/A')}")
            return {"error": f"Error al enviar mensaje: {str(e)}", "status": "failed"}
            
        except Exception as e:
            logger.error(f"Error inesperado enviando mensaje: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}", "status": "failed"}

    def verificar_conexion(self) -> Dict[str, Any]:
        """
        Verifica la conexión con Whapi
        
        Returns:
            Dict con el estado de la conexión
        """
        try:
            # ✅ URL CORREGIDA - Verificar si base_url ya tiene barra
            base_url = self.base_url.rstrip('/')
            url = f"{base_url}/status"
            headers = {"Authorization": f"Bearer {self.whapi_token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return {
                "status": "connected",
                "whapi_response": response.json()
            }
            
        except Exception as e:
            logger.error(f"Error verificando conexión: {str(e)}")
            return {"status": "disconnected", "error": str(e)}
