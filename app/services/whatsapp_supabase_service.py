"""
Servicio híbrido: Supabase Storage + WHAPI
"""
import logging
from typing import Dict, Any
from datetime import datetime
from app.services.whatsapp_service import WhatsAppService
from app.services.supabase_storage import SupabaseStorageService

logger = logging.getLogger(__name__)

class WhatsAppSupabaseService:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.supabase_service = SupabaseStorageService()
    
    def enviar_pdf_con_supabase(self, numero_telefono: str, pdf_base64: str, 
                               nombre_archivo: str, mensaje: str = "", 
                               metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Envía PDF usando Supabase Storage + WHAPI
        
        Flujo:
        1. Subir PDF a Supabase Storage
        2. Obtener URL pública
        3. Enviar por WhatsApp usando la URL
        
        Args:
            numero_telefono: Número de teléfono destino
            pdf_base64: PDF en base64
            nombre_archivo: Nombre del archivo
            mensaje: Mensaje personalizado
            metadata: Metadatos adicionales
            
        Returns:
            Dict con resultado del envío
        """
        try:
            logger.info(f"🚀 Iniciando envío con Supabase Storage: {nombre_archivo}")
            
            # Paso 1: Subir a Supabase Storage
            logger.info("📤 Paso 1: Subiendo a Supabase Storage...")
            upload_result = self.supabase_service.subir_pdf(
                pdf_base64, 
                nombre_archivo, 
                metadata
            )
            
            if "error" in upload_result:
                logger.error(f"❌ Error subiendo a Supabase: {upload_result['error']}")
                return upload_result
            
            url_publica = upload_result["url_publica"]
            logger.info(f"✅ PDF subido a Supabase: {url_publica}")
            
            # Paso 2: Enviar por WhatsApp usando URL
            logger.info("📱 Paso 2: Enviando por WhatsApp...")
            whatsapp_result = self.whatsapp_service.enviar_documento(
                numero_telefono,
                url_publica,
                nombre_archivo,
                mensaje
            )
            
            if "error" in whatsapp_result:
                logger.error(f"❌ Error enviando por WhatsApp: {whatsapp_result['error']}")
                return whatsapp_result
            
            logger.info(f"✅ PDF enviado exitosamente por WhatsApp")
            
            # Paso 3: Eliminar el archivo de Supabase tras el envío exitoso
            eliminado = False
            try:
                archivo_subido = upload_result.get("archivo_nombre")
                if archivo_subido:
                    eliminado = self.supabase_service.eliminar_archivo(archivo_subido)
                    logger.info(f"🗑️ Eliminación de archivo en Supabase ({archivo_subido}): {eliminado}")
                else:
                    logger.warning("⚠️ No se encontró 'archivo_nombre' para eliminar")
            except Exception as del_err:
                logger.error(f"⚠️ No se pudo eliminar el archivo subido: {del_err}")

            return {
                "status": "success",
                "message": "PDF enviado exitosamente (Supabase + WHAPI)",
                "numero_telefono": numero_telefono,
                "archivo": nombre_archivo,
                "url_supabase": url_publica,
                "supabase_result": upload_result,
                "whatsapp_result": whatsapp_result,
                "archivo_eliminado": eliminado,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error inesperado: {str(e)}")
            return {"error": f"Error inesperado: {str(e)}", "status": "failed"}
    
    def enviar_pdf_directo(self, numero_telefono: str, pdf_base64: str, 
                          nombre_archivo: str, mensaje: str = "") -> Dict[str, Any]:
        """
        Envía PDF directamente sin Supabase (método anterior)
        """
        logger.info(f"📤 Enviando PDF directo: {nombre_archivo}")
        return self.whatsapp_service.enviar_documento_base64(
            numero_telefono, pdf_base64, nombre_archivo, mensaje
        )
    
    def listar_documentos(self, limite: int = 50) -> Dict[str, Any]:
        """
        Listar documentos en Supabase Storage
        """
        return self.supabase_service.listar_archivos(limite)
    
    def eliminar_documento(self, nombre_archivo: str) -> bool:
        """
        Eliminar documento de Supabase Storage
        """
        return self.supabase_service.eliminar_archivo(nombre_archivo)
