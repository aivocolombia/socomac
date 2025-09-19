"""
Servicio alternativo de WhatsApp con múltiples endpoints
"""
import requests
import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppServiceAlternative:
    def __init__(self):
        self.whapi_token = os.getenv('WHAPI_TOKEN')
        self.base_url = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')
        
        if not self.whapi_token:
            raise ValueError("WHAPI_TOKEN no está configurado")
    
    def enviar_documento_base64(self, numero_telefono: str, documento_base64: str, 
                               nombre_archivo: str, mensaje: str = "") -> Dict[str, Any]:
        """
        Envía documento probando diferentes endpoints
        """
        logger.info(f"Enviando documento base64 a {numero_telefono}: {nombre_archivo}")
        
        base_url = self.base_url.rstrip('/')
        
        # Lista de endpoints a probar
        endpoints = [
            f"{base_url}/messages/document",
            f"{base_url}/messages/documents",
            f"{base_url}/messages",
            f"{base_url}/messages/media",
            f"{base_url}/media/upload"
        ]
        
        payload = {
            "to": numero_telefono,
            "type": "document",
            "document": {
                "filename": nombre_archivo,
                "data": documento_base64,
                "mime_type": "application/pdf"
            },
            "caption": mensaje
        }
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}",
            "Content-Type": "application/json"
        }
        
        # Probar cada endpoint
        for i, url in enumerate(endpoints, 1):
            logger.info(f"Probando endpoint {i}/{len(endpoints)}: {url}")
            
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                logger.info(f"Response status: {response.status_code}")
                logger.info(f"Response content: {response.text[:200]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Éxito con endpoint: {url}")
                    return {
                        "status": "success",
                        "message_id": result.get("id"),
                        "timestamp": datetime.now().isoformat(),
                        "endpoint_used": url,
                        "whatsapp_response": result
                    }
                elif response.status_code == 400:
                    logger.warning(f"⚠️ Bad Request en {url}: {response.text}")
                    continue
                elif response.status_code == 404:
                    logger.warning(f"⚠️ Not Found en {url}")
                    continue
                else:
                    logger.warning(f"⚠️ Status {response.status_code} en {url}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error en {url}: {e}")
                continue
        
        # Si llegamos aquí, ningún endpoint funcionó
        return {
            "error": "Todos los endpoints fallaron",
            "status": "failed",
            "endpoints_tested": endpoints
        }
    
    def enviar_mensaje_texto(self, numero_telefono: str, mensaje: str) -> Dict[str, Any]:
        """
        Envía mensaje de texto
        """
        logger.info(f"Enviando mensaje a {numero_telefono}: {mensaje}")
        
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
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando mensaje: {e}")
            return {"error": f"Error enviando mensaje: {e}", "status": "failed"}
    
    def verificar_conexion(self) -> Dict[str, Any]:
        """
        Verifica la conexión con WHAPI
        """
        try:
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
            logger.error(f"Error verificando conexión: {e}")
            return {"status": "disconnected", "error": str(e)}
