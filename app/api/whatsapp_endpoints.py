from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
import re
import base64
from app.services.whatsapp_service import WhatsAppService
from app.services.whatsapp_service_alternative import WhatsAppServiceAlternative
from app.services.whatsapp_supabase_service import WhatsAppSupabaseService
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

# Dependencia para obtener el servicio WhatsApp + Supabase
def get_whatsapp_supabase_service():
    try:
        return WhatsAppSupabaseService()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error de configuración: {str(e)}")

# 🔧 FUNCIONES DE DEBUGGING Y VALIDACIÓN

def formatear_telefono_colombia(telefono: str) -> str:
    """
    Formatear teléfono colombiano automáticamente
    """
    # Remover espacios, guiones, paréntesis
    telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
    
    logger.info(f"📱 Teléfono original: {telefono}")
    logger.info(f"📱 Teléfono limpio: {telefono_limpio}")
    
    # Si empieza con 57, agregar +
    if telefono_limpio.startswith('57') and len(telefono_limpio) == 12:
        resultado = f"+{telefono_limpio}"
        logger.info(f"📱 Formato 57XXXXXXXXXX: {resultado}")
        return resultado
    
    # Si empieza con +57, mantener
    if telefono_limpio.startswith('+57') and len(telefono_limpio) == 13:
        resultado = telefono_limpio
        logger.info(f"📱 Formato +57XXXXXXXXXX: {resultado}")
        return resultado
    
    # Si empieza con 3, agregar +57
    if telefono_limpio.startswith('3') and len(telefono_limpio) == 10:
        resultado = f"+57{telefono_limpio}"
        logger.info(f"📱 Formato 3XXXXXXXXX: {resultado}")
        return resultado
    
    # Si es de 10 dígitos, agregar +57
    if len(telefono_limpio) == 10 and telefono_limpio.isdigit():
        resultado = f"+57{telefono_limpio}"
        logger.info(f"📱 Formato XXXXXXXXXX: {resultado}")
        return resultado
    
    error_msg = f"Formato de teléfono inválido: {telefono} (limpio: {telefono_limpio})"
    logger.error(f"❌ {error_msg}")
    raise ValueError(error_msg)

def validar_pdf_robusto(pdf_base64: str) -> Dict[str, Any]:
    """
    Validar PDF de manera robusta
    """
    try:
        logger.info(f"🔍 Validando PDF: {len(pdf_base64)} caracteres base64")
        
        # Decodificar base64
        pdf_bytes = base64.b64decode(pdf_base64)
        logger.info(f"📄 PDF decodificado: {len(pdf_bytes)} bytes")
        
        # Validar header PDF
        header = pdf_bytes[:10]
        logger.info(f"📄 Header PDF: {header}")
        
        if not pdf_bytes.startswith(b'%PDF-'):
            return {
                "valido": False,
                "error": "No es un PDF válido (header incorrecto)",
                "header": header.decode('utf-8', errors='ignore'),
                "tamaño_bytes": len(pdf_bytes)
            }
        
        # Validar tamaño
        size_mb = len(pdf_bytes) / (1024 * 1024)
        logger.info(f"📏 Tamaño PDF: {size_mb:.2f}MB")
        
        if size_mb > 10:
            return {
                "valido": False,
                "error": f"PDF demasiado grande: {size_mb:.2f}MB",
                "tamaño_mb": size_mb,
                "tamaño_bytes": len(pdf_bytes)
            }
        
        # Validar que tenga contenido mínimo
        if len(pdf_bytes) < 100:
            return {
                "valido": False,
                "error": "PDF demasiado pequeño",
                "tamaño_bytes": len(pdf_bytes)
            }
        
        logger.info(f"✅ PDF válido: {size_mb:.2f}MB")
        
        return {
            "valido": True,
            "tamaño_mb": round(size_mb, 2),
            "tamaño_bytes": len(pdf_bytes),
            "header": header.decode('utf-8', errors='ignore')
        }
        
    except Exception as e:
        error_msg = f"Error validando PDF: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "valido": False,
            "error": error_msg
        }

def log_solicitud_pdf(request: PDFRequest):
    """
    Logging detallado de la solicitud
    """
    logger.info("=" * 80)
    logger.info("📄 NUEVA SOLICITUD DE ENVÍO DE PDF")
    logger.info("=" * 80)
    logger.info(f"📱 Teléfono original: {request.numero_telefono}")
    logger.info(f"📄 Archivo: {request.nombre_archivo}")
    logger.info(f"📊 Tamaño base64: {len(request.pdf_base64)} caracteres")
    logger.info(f"📋 Metadata: {request.metadata}")
    
    # Validar PDF
    validacion = validar_pdf_robusto(request.pdf_base64)
    if validacion["valido"]:
        logger.info(f"✅ PDF válido: {validacion['tamaño_mb']}MB")
    else:
        logger.error(f"❌ PDF inválido: {validacion['error']}")
    
    # Formatear teléfono
    try:
        telefono_formateado = formatear_telefono_colombia(request.numero_telefono)
        logger.info(f"📱 Teléfono formateado: {telefono_formateado}")
    except Exception as e:
        logger.error(f"❌ Error formateando teléfono: {e}")

def crear_pdf_prueba() -> bytes:
    """
    Crear un PDF de prueba mínimo
    """
    pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000368 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
465
%%EOF"""
    
    return pdf_content.encode('utf-8')

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
    whatsapp_supabase_service: WhatsAppSupabaseService = Depends(get_whatsapp_supabase_service)
):
    """
    Endpoint principal para enviar PDF con Supabase Storage automático
    
    Flujo:
    1. Recibe PDF del frontend
    2. Sube a Supabase Storage
    3. Obtiene URL pública
    4. Envía por WhatsApp
    5. Retorna respuesta al frontend
    
    Endpoint: POST /whatsapp/enviar-pdf
    """
    try:
        # 🔍 LOGGING DETALLADO
        log_solicitud_pdf(request)
        
        # ✅ FORMATEAR TELÉFONO
        try:
            telefono_formateado = formatear_telefono_colombia(request.numero_telefono)
            logger.info(f"📱 Teléfono formateado: {telefono_formateado}")
        except Exception as e:
            error_msg = f"Error formateando teléfono: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ VALIDAR PDF
        validacion = validar_pdf_robusto(request.pdf_base64)
        if not validacion["valido"]:
            error_msg = f"PDF inválido: {validacion['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"✅ PDF válido: {validacion['tamaño_mb']}MB")
        
        # ✅ CREAR MENSAJE PERSONALIZADO
        mensaje_personalizado = crear_mensaje_pdf(request.metadata, request.nombre_archivo)
        logger.info(f"💬 Mensaje: {mensaje_personalizado}")
        
        # ✅ ENVIAR CON SUPABASE (AUTOMÁTICO)
        logger.info("🚀 Enviando con Supabase Storage...")
        resultado = whatsapp_supabase_service.enviar_pdf_con_supabase(
            telefono_formateado,
            request.pdf_base64,
            request.nombre_archivo,
            mensaje_personalizado,
            request.metadata
        )
        
        # 📊 RESPUESTA
        logger.info(f"📨 Resultado: {resultado}")
        
        if "error" in resultado:
            error_msg = f"Error enviando PDF: {resultado['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ ÉXITO
        logger.info(f"✅ PDF enviado exitosamente con Supabase a {telefono_formateado}")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "message": "PDF enviado exitosamente",
            "numero_telefono": telefono_formateado,
            "archivo": request.nombre_archivo,
            "tamaño_mb": validacion["tamaño_mb"],
            "url_supabase": resultado.get("url_supabase"),
            "metadata": request.metadata,
            "whapi_response": resultado.get("whatsapp_result")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        logger.error(f"💥 {error_msg}")
        logger.error("=" * 80)
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
        
        # Configuración Supabase
        try:
            from app.services.supabase_storage import SupabaseStorageService
            supabase_service = SupabaseStorageService()
            supabase_config = {
                "supabase_url": supabase_service.supabase_url,
                "supabase_key_configurado": bool(supabase_service.supabase_key),
                "supabase_key_preview": supabase_service.supabase_key[:10] + "..." if supabase_service.supabase_key else "No configurado",
                "bucket_name": supabase_service.bucket_name,
                "bucket_accesible": supabase_service.verificar_bucket_existe()
            }
        except Exception as e:
            supabase_config = {
                "error": str(e),
                "status": "failed"
            }
        
        return {
            "status": "success",
            "message": "Configuración de WHAPI y Supabase",
            "whapi": config_info,
            "supabase": supabase_config
        }
        
    except Exception as e:
        logger.error(f"Error en debug config: {str(e)}")
        return {
            "status": "error",
            "message": f"Error obteniendo configuración: {str(e)}"
        }

@router.post("/test-pdf")
async def test_pdf_endpoint():
    """
    Endpoint para probar la funcionalidad de PDF
    """
    try:
        # Crear PDF de prueba
        pdf_prueba = crear_pdf_prueba()
        pdf_base64 = base64.b64encode(pdf_prueba).decode('utf-8')
        
        # Validar el PDF creado
        validacion = validar_pdf_robusto(pdf_base64)
        
        return {
            "message": "PDF de prueba creado",
            "tamaño_bytes": len(pdf_prueba),
            "tamaño_base64": len(pdf_base64),
            "header": pdf_prueba[:10].decode('utf-8', errors='ignore'),
            "validacion": validacion,
            "pdf_base64_preview": pdf_base64[:100] + "..."
        }
        
    except Exception as e:
        logger.error(f"Error creando PDF de prueba: {str(e)}")
        return {
            "error": f"Error creando PDF de prueba: {str(e)}"
        }

@router.post("/test-telefono")
async def test_telefono_endpoint(telefono: str):
    """
    Endpoint para probar formateo de teléfono
    """
    try:
        telefono_formateado = formatear_telefono_colombia(telefono)
        return {
            "original": telefono,
            "formateado": telefono_formateado,
            "valido": True
        }
    except Exception as e:
        return {
            "original": telefono,
            "error": str(e),
            "valido": False
        }

@router.post("/test-pdf-completo")
async def test_pdf_completo():
    """
    Endpoint para probar envío completo de PDF
    """
    try:
        # Crear PDF de prueba
        pdf_prueba = crear_pdf_prueba()
        pdf_base64 = base64.b64encode(pdf_prueba).decode('utf-8')
        
        # Crear request de prueba
        request_prueba = PDFRequest(
            numero_telefono="573172288329",  # Sin +57
            pdf_base64=pdf_base64,
            nombre_archivo="test_recibo_123_2025-01-18.pdf",
            metadata={
                "numero_recibo": 123,
                "empresa": "SOCOMAC",
                "cliente": "David Cuellar",
                "valor": "10000",
                "concepto": "Mercancia nacional",
                "fecha": "2025-01-18"
            }
        )
        
        # Probar formateo de teléfono
        telefono_formateado = formatear_telefono_colombia(request_prueba.numero_telefono)
        
        # Probar validación de PDF
        validacion = validar_pdf_robusto(request_prueba.pdf_base64)
        
        # Crear mensaje
        mensaje = crear_mensaje_pdf(request_prueba.metadata, request_prueba.nombre_archivo)
        
        return {
            "message": "Prueba completa realizada",
            "telefono_original": request_prueba.numero_telefono,
            "telefono_formateado": telefono_formateado,
            "pdf_validacion": validacion,
            "mensaje_generado": mensaje,
            "metadata": request_prueba.metadata
        }
        
    except Exception as e:
        logger.error(f"Error en prueba completa: {str(e)}")
        return {
            "error": f"Error en prueba completa: {str(e)}"
        }

@router.post("/test-upload-documento")
async def test_upload_documento():
    """
    Endpoint para probar solo el upload de documento
    """
    try:
        # Crear PDF de prueba
        pdf_prueba = crear_pdf_prueba()
        pdf_base64 = base64.b64encode(pdf_prueba).decode('utf-8')
        
        # Obtener servicio
        whatsapp_service = WhatsAppService()
        
        # Probar upload
        logger.info("🧪 Probando upload de documento...")
        upload_result = whatsapp_service.subir_documento(pdf_base64, "test_upload.pdf")
        
        return {
            "message": "Prueba de upload realizada",
            "pdf_tamaño": len(pdf_prueba),
            "pdf_base64_tamaño": len(pdf_base64),
            "upload_result": upload_result
        }
        
    except Exception as e:
        logger.error(f"Error en prueba de upload: {str(e)}")
        return {
            "error": f"Error en prueba de upload: {str(e)}"
        }

@router.post("/enviar-pdf-supabase")
async def enviar_pdf_supabase(
    request: PDFRequest,
    whatsapp_supabase_service: WhatsAppSupabaseService = Depends(get_whatsapp_supabase_service)
):
    """
    Endpoint para enviar PDF usando Supabase Storage + WHAPI
    
    Flujo:
    1. Subir PDF a Supabase Storage
    2. Obtener URL pública
    3. Enviar por WhatsApp usando la URL
    """
    try:
        # 🔍 LOGGING DETALLADO
        log_solicitud_pdf(request)
        
        # ✅ FORMATEAR TELÉFONO
        try:
            telefono_formateado = formatear_telefono_colombia(request.numero_telefono)
            logger.info(f"📱 Teléfono formateado: {telefono_formateado}")
        except Exception as e:
            error_msg = f"Error formateando teléfono: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ VALIDAR PDF
        validacion = validar_pdf_robusto(request.pdf_base64)
        if not validacion["valido"]:
            error_msg = f"PDF inválido: {validacion['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"✅ PDF válido: {validacion['tamaño_mb']}MB")
        
        # ✅ CREAR MENSAJE PERSONALIZADO
        mensaje_personalizado = crear_mensaje_pdf(request.metadata, request.nombre_archivo)
        logger.info(f"💬 Mensaje: {mensaje_personalizado}")
        
        # ✅ ENVIAR CON SUPABASE
        logger.info("🚀 Enviando con Supabase Storage...")
        resultado = whatsapp_supabase_service.enviar_pdf_con_supabase(
            telefono_formateado,
            request.pdf_base64,
            request.nombre_archivo,
            mensaje_personalizado,
            request.metadata
        )
        
        # 📊 RESPUESTA
        logger.info(f"📨 Resultado: {resultado}")
        
        if "error" in resultado:
            error_msg = f"Error enviando PDF: {resultado['error']}"
            logger.error(f"❌ {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ✅ ÉXITO
        logger.info(f"✅ PDF enviado exitosamente con Supabase a {telefono_formateado}")
        logger.info("=" * 80)
        
        return {
            "success": True,
            "message": "PDF enviado exitosamente (Supabase Storage)",
            "numero_telefono": telefono_formateado,
            "archivo": request.nombre_archivo,
            "tamaño_mb": validacion["tamaño_mb"],
            "url_supabase": resultado.get("url_supabase"),
            "metadata": request.metadata,
            "supabase_result": resultado.get("supabase_result"),
            "whatsapp_result": resultado.get("whatsapp_result")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        logger.error(f"💥 {error_msg}")
        logger.error("=" * 80)
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/documentos-supabase")
async def listar_documentos_supabase(
    limite: int = 50,
    whatsapp_supabase_service: WhatsAppSupabaseService = Depends(get_whatsapp_supabase_service)
):
    """
    Listar documentos en Supabase Storage
    """
    try:
        resultado = whatsapp_supabase_service.listar_documentos(limite)
        return resultado
    except Exception as e:
        logger.error(f"Error listando documentos: {str(e)}")
        return {"error": f"Error listando documentos: {str(e)}"}

@router.delete("/documentos-supabase/{nombre_archivo}")
async def eliminar_documento_supabase(
    nombre_archivo: str,
    whatsapp_supabase_service: WhatsAppSupabaseService = Depends(get_whatsapp_supabase_service)
):
    """
    Eliminar documento de Supabase Storage
    """
    try:
        resultado = whatsapp_supabase_service.eliminar_documento(nombre_archivo)
        return {
            "success": resultado,
            "message": f"Documento {nombre_archivo} {'eliminado' if resultado else 'no eliminado'}"
        }
    except Exception as e:
        logger.error(f"Error eliminando documento: {str(e)}")
        return {"error": f"Error eliminando documento: {str(e)}"}

@router.post("/test-supabase-url")
async def test_supabase_url():
    """
    Endpoint para probar solo la extracción de URL de Supabase
    """
    try:
        # Crear PDF de prueba
        pdf_prueba = crear_pdf_prueba()
        pdf_base64 = base64.b64encode(pdf_prueba).decode('utf-8')
        
        # Obtener servicio Supabase
        from app.services.supabase_storage import SupabaseStorageService
        supabase_service = SupabaseStorageService()
        
        # Probar upload y extracción de URL
        logger.info("🧪 Probando extracción de URL de Supabase...")
        upload_result = supabase_service.subir_pdf(
            pdf_base64, 
            "test_url_extraction.pdf",
            {"test": "url_extraction"}
        )
        
        if "error" in upload_result:
            return {
                "error": upload_result["error"],
                "status": "failed"
            }
        
        # Extraer URL directamente
        url_publica = upload_result["url_publica"]
        
        return {
            "message": "URL extraída exitosamente",
            "pdf_tamaño": len(pdf_prueba),
            "pdf_base64_tamaño": len(pdf_base64),
            "url_publica": url_publica,
            "archivo_nombre": upload_result["archivo_nombre"],
            "tamaño_bytes": upload_result["tamaño_bytes"],
            "metadata": upload_result["metadata"],
            "upload_result": upload_result
        }
        
    except Exception as e:
        logger.error(f"Error en prueba de URL: {str(e)}")
        return {
            "error": f"Error en prueba de URL: {str(e)}"
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
