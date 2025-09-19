"""
Endpoint de prueba para enviar PDF fijo
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/test-pdf-fijo")
async def test_pdf_fijo():
    """
    Probar envío del PDF fijo que ya existe en Supabase
    """
    try:
        from app.services.whatsapp_service import WhatsAppService
        
        # URL del PDF que ya existe
        pdf_url = "https://rixvqufnzasolxxklaue.supabase.co/storage/v1/object/public/receipt/Recibo_Caja_81_2025-09-18.pdf"
        
        # Número de teléfono de prueba (cambia por el tuyo)
        numero_telefono = "+573172288329"
        
        # Mensaje personalizado
        mensaje = "📄 Recibo de Caja SOCOMAC\n\nArchivo: Recibo_Caja_81_2025-09-18.pdf\n\nEste es un recibo de prueba enviado desde el sistema."
        
        # Crear servicio WhatsApp
        whatsapp_service = WhatsAppService()
        
        # Enviar documento por URL
        resultado = whatsapp_service.enviar_documento(
            numero_telefono,
            pdf_url,
            "Recibo_Caja_81_2025-09-18.pdf",
            mensaje
        )
        
        if "error" in resultado:
            return {
                "status": "error",
                "error": resultado["error"],
                "mensaje": "Error enviando PDF"
            }
        
        return {
            "status": "success",
            "mensaje": "PDF enviado exitosamente",
            "numero_telefono": numero_telefono,
            "archivo": "Recibo_Caja_81_2025-09-18.pdf",
            "url_pdf": pdf_url,
            "whapi_response": resultado
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "mensaje": "Error en prueba de PDF fijo"
        }
