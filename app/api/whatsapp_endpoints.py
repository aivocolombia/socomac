from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
import re
import base64
from app.services.whatsapp_service import WhatsAppService
from app.services.whatsapp_service_alternative import WhatsAppServiceAlternative
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

class PDFRequest(BaseModel):
    numero_telefono: str
    pdf_base64: str
    nombre_archivo: str
    metadata: Optional[Dict[str, Any]] = {}
    
    @validator('numero_telefono')
    def validar_numero_telefono(cls, v):
        numero_limpio = re.sub(r'[^\d]', '', v)
        if not numero_limpio.isdigit() or len(numero_limpio) < 10 or len(numero_limpio) > 15:
            raise ValueError('Número de teléfono inválido')
        return numero_limpio
    
    @validator('pdf_base64')
    def validar_pdf_base64(cls, v):
        if not v or not v.strip():
            raise ValueError('PDF base64 no puede estar vacío')
        
        try:
            # Intentar decodificar para validar que sea base64 válido
            pdf_bytes = base64.b64decode(v)
            
            # Validar que sea un PDF válido
            if not pdf_bytes.startswith(b'%PDF-'):
                raise ValueError('El archivo no es un PDF válido')
            
            # Validar tamaño (máximo 10MB)
            size_mb = len(pdf_bytes) / (1024 * 1024)
            if size_mb > 10:
                raise ValueError(f'El PDF es muy grande ({size_mb:.1f}MB). Máximo permitido: 10MB')
            
            return v
            
        except base64.binascii.Error:
            raise ValueError('Base64 inválido')
        except Exception as e:
            raise ValueError(f'Error validando PDF: {str(e)}')
    
    @validator('nombre_archivo')
    def validar_nombre_archivo(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre de archivo no puede estar vacío')
        
        # Validar extensión
        if not v.lower().endswith('.pdf'):
            raise ValueError('El archivo debe tener extensión .pdf')
        
        # Validar longitud
        if len(v) > 100:
            raise ValueError('Nombre de archivo muy largo (máximo 100 caracteres)')
        
        return v.strip()

# Dependencia para obtener el servicio WhatsApp
def get_whatsapp_service():
    try:
        return WhatsAppService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error de configuración: {str(e)}")

# Dependencia para obtener el servicio WhatsApp alternativo
def get_whatsapp_service_alternative():
    try:
        return WhatsAppServiceAlternative()
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

@router.options("/enviar-mensaje")
async def options_enviar_mensaje():
    """
    Endpoint OPTIONS para manejar preflight CORS
    """
    return {"message": "CORS preflight handled"}

@router.options("/recibo-listo")
async def options_recibo_listo():
    """
    Endpoint OPTIONS para manejar preflight CORS
    """
    return {"message": "CORS preflight handled"}

@router.post("/enviar-pdf")
async def enviar_pdf_whatsapp(
    request: PDFRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para enviar PDF por WhatsApp usando WHAPI
    
    Endpoint: POST /whatsapp/enviar-pdf
    URL WHAPI: https://gate.whapi.cloud/messages/document
    """
    try:
        # 🔍 LOGGING DETALLADO - Inicio de la solicitud
        logger.info("=" * 60)
        logger.info("📄 NUEVA SOLICITUD DE ENVÍO DE PDF")
        logger.info("=" * 60)
        logger.info(f"📱 Teléfono destino: {request.numero_telefono}")
        logger.info(f"📄 Archivo: {request.nombre_archivo}")
        logger.info(f"📊 Tamaño base64: {len(request.pdf_base64)} caracteres")
        logger.info(f"📋 Metadata: {request.metadata}")
        
        # Decodificar PDF para obtener información adicional
        pdf_bytes = base64.b64decode(request.pdf_base64)
        size_mb = len(pdf_bytes) / (1024 * 1024)
        
        logger.info(f"📏 Tamaño real del PDF: {size_mb:.2f}MB")
        
        # ✅ VALIDACIONES ADICIONALES
        if size_mb > 10:
            error_msg = f"PDF demasiado grande: {size_mb:.2f}MB. Máximo permitido: 10MB"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Validar que sea un PDF válido
        if not pdf_bytes.startswith(b'%PDF-'):
            error_msg = "El archivo no es un PDF válido"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Crear mensaje personalizado basado en metadata
        mensaje_personalizado = crear_mensaje_pdf(request.metadata, request.nombre_archivo)
        logger.info(f"💬 Mensaje personalizado: {mensaje_personalizado}")
        
        # 🔧 CONFIGURACIÓN WHAPI
        whapi_url = f"{whatsapp_service.base_url.rstrip('/')}/messages/document"
        logger.info(f"🌐 URL WHAPI: {whapi_url}")
        logger.info(f"🔑 Token configurado: {'Sí' if whatsapp_service.whapi_token else 'No'}")
        
        # 📤 ENVÍO A WHAPI
        logger.info("🚀 Enviando PDF a WHAPI...")
        resultado = whatsapp_service.enviar_documento_base64(
            request.numero_telefono,
            request.pdf_base64,
            request.nombre_archivo,
            mensaje_personalizado
        )
        
        # 📊 RESPUESTA DE WHAPI
        logger.info(f"📨 Respuesta WHAPI: {resultado}")
        
        if "error" in resultado:
            error_msg = f"Error al enviar PDF: {resultado['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        # ✅ ÉXITO
        logger.info(f"✅ PDF enviado exitosamente a {request.numero_telefono}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            "message": "PDF enviado exitosamente",
            "numero_telefono": request.numero_telefono,
            "archivo": request.nombre_archivo,
            "tamaño_mb": round(size_mb, 2),
            "metadata": request.metadata,
            "whapi_response": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error inesperado enviando PDF: {str(e)}"
        logger.error(f"💥 {error_msg}")
        logger.error("=" * 60)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.options("/enviar-pdf")
async def options_enviar_pdf():
    """
    Endpoint OPTIONS para manejar preflight CORS
    """
    return {"message": "CORS preflight handled"}

@router.get("/debug-config")
async def debug_config():
    """
    Endpoint para debuggear la configuración de WHAPI
    """
    try:
        whatsapp_service = WhatsAppService()
        
        # Información de configuración
        config_info = {
            "whapi_base_url": whatsapp_service.base_url,
            "whapi_base_url_limpia": whatsapp_service.base_url.rstrip('/'),
            "whapi_token_configurado": bool(whatsapp_service.whapi_token),
            "whapi_token_preview": whatsapp_service.whapi_token[:10] + "..." if whatsapp_service.whapi_token else "No configurado",
            "urls_generadas": {
                "mensaje": f"{whatsapp_service.base_url.rstrip('/')}/messages/text",
                "documento": f"{whatsapp_service.base_url.rstrip('/')}/messages/document",
                "status": f"{whatsapp_service.base_url.rstrip('/')}/status"
            }
        }
        
        return {
            "status": "success",
            "message": "Configuración de WHAPI",
            "config": config_info
        }
        
    except Exception as e:
        logger.error(f"Error en debug config: {str(e)}")
        return {
            "status": "error",
            "message": f"Error obteniendo configuración: {str(e)}"
        }

@router.post("/enviar-pdf-alternativo")
async def enviar_pdf_whatsapp_alternativo(
    request: PDFRequest,
    whatsapp_service: WhatsAppServiceAlternative = Depends(get_whatsapp_service_alternative)
):
    """
    Endpoint alternativo para enviar PDF probando múltiples endpoints
    """
    try:
        logger.info(f"Recibida solicitud alternativa para enviar PDF a {request.numero_telefono}")
        logger.info(f"Archivo: {request.nombre_archivo}")
        
        # Decodificar PDF para obtener información adicional
        pdf_bytes = base64.b64decode(request.pdf_base64)
        size_mb = len(pdf_bytes) / (1024 * 1024)
        
        logger.info(f"Tamaño real del PDF: {size_mb:.2f}MB")
        
        # Validaciones adicionales
        if size_mb > 10:
            raise HTTPException(status_code=400, detail=f"PDF demasiado grande: {size_mb:.2f}MB. Máximo permitido: 10MB")
        
        # Validar que sea un PDF válido
        if not pdf_bytes.startswith(b'%PDF-'):
            raise HTTPException(status_code=400, detail="El archivo no es un PDF válido")
        
        # Crear mensaje personalizado basado en metadata
        mensaje_personalizado = crear_mensaje_pdf(request.metadata, request.nombre_archivo)
        
        logger.info(f"Enviando PDF con servicio alternativo...")
        
        # Enviar PDF usando el servicio alternativo
        resultado = whatsapp_service.enviar_documento_base64(
            request.numero_telefono,
            request.pdf_base64,
            request.nombre_archivo,
            mensaje_personalizado
        )
        
        if "error" in resultado:
            logger.error(f"Error al enviar PDF: {resultado['error']}")
            raise HTTPException(status_code=400, detail=resultado["error"])
        
        logger.info(f"PDF enviado exitosamente a {request.numero_telefono}")
        
        return {
            "success": True,
            "message": "PDF enviado exitosamente (método alternativo)",
            "numero_telefono": request.numero_telefono,
            "archivo": request.nombre_archivo,
            "tamaño_mb": round(size_mb, 2),
            "metadata": request.metadata,
            "endpoint_used": resultado.get("endpoint_used"),
            "whatsapp_response": resultado
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado enviando PDF alternativo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

def crear_mensaje_pdf(metadata: Dict[str, Any], nombre_archivo: str) -> str:
    """
    Crear mensaje personalizado para el PDF basado en metadata
    """
    mensaje = f"📄 *Recibo de Caja SOCOMAC*\n\n"
    mensaje += f"📋 *Archivo:* {nombre_archivo}\n"
    
    if metadata:
        if metadata.get("numero_recibo"):
            mensaje += f"🔢 *Número de recibo:* {metadata['numero_recibo']}\n"
        
        if metadata.get("empresa"):
            mensaje += f"🏢 *Empresa:* {metadata['empresa']}\n"
        
        if metadata.get("cliente"):
            mensaje += f"👤 *Cliente:* {metadata['cliente']}\n"
        
        if metadata.get("valor"):
            valor_formateado = f"${int(metadata['valor']):,}"
            mensaje += f"💰 *Valor:* {valor_formateado}\n"
        
        if metadata.get("concepto"):
            mensaje += f"📝 *Concepto:* {metadata['concepto']}\n"
        
        if metadata.get("fecha"):
            mensaje += f"📅 *Fecha:* {metadata['fecha']}\n"
    
    mensaje += f"\nEste es un recibo generado automáticamente."
    
    return mensaje

@router.post("/enviar-documento-completo")
async def enviar_documento_completo(
    request: DocumentoRequest,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para enviar documento completo con URL de Supabase
    """
    try:
        logger.info(f"Recibida solicitud para enviar documento a {request.numero_telefono}")
        
        # Validar que la URL sea de Supabase
        if not request.documento_url.startswith('https://'):
            raise HTTPException(status_code=400, detail="URL del documento inválida")
        
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
