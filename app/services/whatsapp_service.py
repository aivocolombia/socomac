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
        
        url = f"{self.base_url}/messages/text"
        
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
        
        url = f"{self.base_url}/messages/documents"
        
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
    
    def verificar_conexion(self) -> Dict[str, Any]:
        """
        Verifica la conexión con Whapi
        
        Returns:
            Dict con el estado de la conexión
        """
        try:
            url = f"{self.base_url}/status"
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
