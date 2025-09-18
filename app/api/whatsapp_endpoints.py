from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import Optional
import re
from app.services.whatsapp_service import WhatsAppService
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

class MensajeRequest(BaseModel):
    numero_telefono: str
    mensaje: str
    
    @validator('numero_telefono')
    def validar_numero_telefono(cls, v):
        # Remover espacios y caracteres especiales
        numero_limpio = re.sub(r'[^\d]', '', v)
        
        # Validar que sea un número válido
        if not numero_limpio.isdigit():
            raise ValueError('El número de teléfono debe contener solo dígitos')
        
        # Validar longitud mínima
        if len(numero_limpio) < 10:
            raise ValueError('El número de teléfono es muy corto')
        
        # Validar longitud máxima
        if len(numero_limpio) > 15:
            raise ValueError('El número de teléfono es muy largo')
        
        return numero_limpio
    
    @validator('mensaje')
    def validar_mensaje(cls, v):
        if not v or not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        
        if len(v) > 1000:
            raise ValueError('El mensaje es muy largo (máximo 1000 caracteres)')
        
        return v.strip()

class DocumentoRequest(BaseModel):
    numero_telefono: str
    documento_url: str
    nombre_archivo: Optional[str] = "documento.pdf"
    mensaje: Optional[str] = ""
    
    @validator('numero_telefono')
    def validar_numero_telefono(cls, v):
        numero_limpio = re.sub(r'[^\d]', '', v)
        if not numero_limpio.isdigit() or len(numero_limpio) < 10 or len(numero_limpio) > 15:
            raise ValueError('Número de teléfono inválido')
        return numero_limpio
    
    @validator('documento_url')
    def validar_url_documento(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('La URL del documento debe comenzar con http:// o https://')
        return v
    
    @validator('mensaje')
    def validar_mensaje(cls, v):
        if v and len(v) > 500:
            raise ValueError('El mensaje es muy largo (máximo 500 caracteres)')
        return v

class ReciboListoRequest(BaseModel):
    numero_telefono: str
    mensaje: Optional[str] = "Recibo listo"
    
    @validator('numero_telefono')
    def validar_numero_telefono(cls, v):
        numero_limpio = re.sub(r'[^\d]', '', v)
        if not numero_limpio.isdigit() or len(numero_limpio) < 10 or len(numero_limpio) > 15:
            raise ValueError('Número de teléfono inválido')
        return numero_limpio

# Dependencia para obtener el servicio WhatsApp
def get_whatsapp_service():
    try:
        return WhatsAppService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error de configuración: {str(e)}")

@router.post("/enviar-mensaje")
async def enviar_mensaje_whatsapp(
    request: MensajeRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para enviar mensaje de texto a WhatsApp
    """
    try:
        logger.info(f"Recibida solicitud para enviar mensaje a {request.numero_telefono}")
        
        resultado = whatsapp_service.enviar_mensaje(
            request.numero_telefono, 
            request.mensaje
        )
        
        if "error" in resultado:
            logger.error(f"Error al enviar mensaje: {resultado['error']}")
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        logger.info(f"Mensaje enviado exitosamente a {request.numero_telefono}")
        
        return {
            "status": "success",
            "message": "Mensaje enviado correctamente",
            "data": {
                "numero_telefono": request.numero_telefono,
                "mensaje": request.mensaje,
                "message_id": resultado.get("message_id"),
                "timestamp": resultado.get("timestamp")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/enviar-documento")
async def enviar_documento_whatsapp(
    request: DocumentoRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para enviar documento a WhatsApp
    """
    try:
        logger.info(f"Recibida solicitud para enviar documento a {request.numero_telefono}")
        
        resultado = whatsapp_service.enviar_documento(
            request.numero_telefono,
            request.documento_url,
            request.nombre_archivo,
            request.mensaje
        )
        
        if "error" in resultado:
            logger.error(f"Error al enviar documento: {resultado['error']}")
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        logger.info(f"Documento enviado exitosamente a {request.numero_telefono}")
        
        return {
            "status": "success",
            "message": "Documento enviado correctamente",
            "data": {
                "numero_telefono": request.numero_telefono,
                "documento_url": request.documento_url,
                "nombre_archivo": request.nombre_archivo,
                "mensaje": request.mensaje,
                "message_id": resultado.get("message_id"),
                "timestamp": resultado.get("timestamp")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.post("/recibo-listo")
async def notificar_recibo_listo(
    request: ReciboListoRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint específico para notificar que el recibo está listo
    """
    try:
        logger.info(f"Recibida solicitud de recibo listo para {request.numero_telefono}")
        
        resultado = whatsapp_service.enviar_mensaje(
            request.numero_telefono, 
            request.mensaje
        )
        
        if "error" in resultado:
            logger.error(f"Error al enviar notificación de recibo: {resultado['error']}")
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        logger.info(f"Notificación de recibo enviada exitosamente a {request.numero_telefono}")
        
        return {
            "status": "success",
            "message": "Notificación de recibo enviada",
            "data": {
                "numero_telefono": request.numero_telefono,
                "mensaje": request.mensaje,
                "message_id": resultado.get("message_id"),
                "timestamp": resultado.get("timestamp")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/status")
async def verificar_estado_whatsapp(
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para verificar el estado de la conexión con WhatsApp
    """
    try:
        resultado = whatsapp_service.verificar_conexion()
        
        if resultado["status"] == "connected":
            return {
                "status": "success",
                "message": "Conexión con WhatsApp activa",
                "data": resultado
            }
        else:
            return {
                "status": "error",
                "message": "Conexión con WhatsApp inactiva",
                "data": resultado
            }
            
    except Exception as e:
        logger.error(f"Error verificando estado: {str(e)}")
        raise HTTPException(status_code=500, detail="Error verificando estado de WhatsApp")
