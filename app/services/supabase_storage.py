"""
Servicio para manejar archivos en Supabase Storage
"""
import os
import base64
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    logging.warning("Supabase no está instalado. Ejecuta: pip install supabase")

logger = logging.getLogger(__name__)

class SupabaseStorageService:
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ValueError("Supabase no está disponible. Instala con: pip install supabase")
        
        self.supabase_url = os.getenv('SUPABASE_URL')
        # Usar la misma variable que ya tienes configurada
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = "receipt"  # Usar el bucket existente
    
    def verificar_bucket_existe(self) -> bool:
        """
        Verificar si el bucket existe y está disponible
        """
        try:
            logger.info(f"🔍 Verificando bucket: {self.bucket_name}")
            logger.info(f"🔗 Supabase URL: {self.supabase_url}")
            logger.info(f"🔑 Supabase Key: {self.supabase_key[:10]}...")
            
            # Método 1: Intentar obtener el bucket
            try:
                bucket_info = self.supabase.storage.get_bucket(self.bucket_name)
                logger.info(f"✅ Bucket '{self.bucket_name}' existe y está disponible")
                logger.info(f"📊 Bucket info: {bucket_info}")
                return True
            except Exception as e1:
                logger.warning(f"⚠️ Método 1 falló: {e1}")
                
                # Método 2: Intentar listar archivos directamente
                try:
                    files = self.supabase.storage.from_(self.bucket_name).list()
                    logger.info(f"✅ Bucket '{self.bucket_name}' accesible via listado")
                    logger.info(f"📁 Archivos encontrados: {len(files)}")
                    return True
                except Exception as e2:
                    logger.warning(f"⚠️ Método 2 falló: {e2}")
                    return False
            
        except Exception as e:
            logger.error(f"❌ Error general accediendo al bucket '{self.bucket_name}': {e}")
            logger.error(f"🔍 Tipo de error: {type(e).__name__}")
            return False
    
    def subir_pdf(self, pdf_base64: str, nombre_archivo: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Subir PDF a Supabase Storage
        
        Args:
            pdf_base64: PDF en base64
            nombre_archivo: Nombre del archivo
            metadata: Metadatos adicionales
            
        Returns:
            Dict con información del archivo subido
        """
        try:
            logger.info(f"📤 Subiendo PDF a Supabase: {nombre_archivo}")
            
            # Verificar que el bucket existe
            if not self.verificar_bucket_existe():
                return {"error": "No se pudo acceder al bucket", "status": "failed"}
            
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            nombre_unico = f"{timestamp}_{unique_id}_{nombre_archivo}"
            
            # Decodificar base64
            pdf_bytes = base64.b64decode(pdf_base64)
            
            # Subir archivo
            result = self.supabase.storage.from_(self.bucket_name).upload(
                nombre_unico,
                pdf_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "cache-control": "3600"
                }
            )
            
            # Manejar posibles errores del UploadResponse (objeto, no dict)
            upload_error = None
            try:
                if hasattr(result, "error") and result.error:
                    upload_error = str(result.error)
            except Exception:
                pass
            if upload_error:
                logger.error(f"❌ Error subiendo archivo: {upload_error}")
                return {"error": f"Error subiendo archivo: {upload_error}", "status": "failed"}
            
            # Obtener URL pública (puede ser str o dict dependiendo de la versión del SDK)
            public_url_resp = self.supabase.storage.from_(self.bucket_name).get_public_url(nombre_unico)
            public_url = None
            if isinstance(public_url_resp, str):
                public_url = public_url_resp
            elif isinstance(public_url_resp, dict):
                public_url = (
                    public_url_resp.get("publicURL")
                    or public_url_resp.get("public_url")
                    or (public_url_resp.get("data") or {}).get("publicUrl")
                )
            if not public_url:
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{nombre_unico}"
            
            # Guardar metadatos en base de datos (opcional) - DESHABILITADO por RLS
            # if metadata:
            #     self._guardar_metadatos(nombre_unico, metadata, public_url)
            
            logger.info(f"✅ PDF subido exitosamente: {public_url}")
            
            return {
                "status": "success",
                "archivo_nombre": nombre_unico,
                "url_publica": public_url,
                "tamaño_bytes": len(pdf_bytes),
                "metadata": metadata,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo PDF: {str(e)}")
            return {"error": f"Error subiendo PDF: {str(e)}", "status": "failed"}
    
    def _guardar_metadatos(self, nombre_archivo: str, metadata: Dict[str, Any], url_publica: str):
        """
        Guardar metadatos en la tabla de documentos - DESHABILITADO por RLS
        """
        # DESHABILITADO: No guardar metadatos para evitar problemas de RLS
        logger.info(f"📊 Metadatos deshabilitados por RLS: {nombre_archivo}")
        return
    
    def obtener_url_publica(self, nombre_archivo: str) -> Optional[str]:
        """
        Obtener URL pública de un archivo
        """
        try:
            return self.supabase.storage.from_(self.bucket_name).get_public_url(nombre_archivo)
        except Exception as e:
            logger.error(f"❌ Error obteniendo URL: {e}")
            return None
    
    def eliminar_archivo(self, nombre_archivo: str) -> bool:
        """
        Eliminar archivo del storage
        """
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([nombre_archivo])
            logger.info(f"🗑️ Archivo eliminado: {result}")
            return True
        except Exception as e:
            logger.error(f"❌ Error eliminando archivo: {e}")
            return False
    
    def subir_pdf_solo_storage(self, pdf_base64: str, nombre_archivo: str) -> Dict[str, Any]:
        """
        Subir PDF solo al storage de Supabase (sin base de datos)
        
        Args:
            pdf_base64: PDF en base64
            nombre_archivo: Nombre del archivo
            
        Returns:
            Dict con información del archivo subido
        """
        try:
            logger.info(f"📤 Subiendo PDF solo al storage: {nombre_archivo}")
            
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            nombre_unico = f"{timestamp}_{unique_id}_{nombre_archivo}"
            
            # Decodificar base64
            pdf_bytes = base64.b64decode(pdf_base64)
            
            # Subir archivo directamente al storage
            result = self.supabase.storage.from_(self.bucket_name).upload(
                nombre_unico,
                pdf_bytes,
                file_options={
                    "content-type": "application/pdf",
                    "cache-control": "3600"
                }
            )
            
            # Manejar posibles errores del UploadResponse
            upload_error = None
            try:
                if hasattr(result, "error") and result.error:
                    upload_error = str(result.error)
            except Exception:
                pass
            if upload_error:
                logger.error(f"❌ Error subiendo archivo: {upload_error}")
                return {"error": f"Error subiendo archivo: {upload_error}", "status": "failed"}
            
            # Obtener URL pública (str o dict)
            public_url_resp = self.supabase.storage.from_(self.bucket_name).get_public_url(nombre_unico)
            public_url = None
            if isinstance(public_url_resp, str):
                public_url = public_url_resp
            elif isinstance(public_url_resp, dict):
                public_url = (
                    public_url_resp.get("publicURL")
                    or public_url_resp.get("public_url")
                    or (public_url_resp.get("data") or {}).get("publicUrl")
                )
            if not public_url:
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{nombre_unico}"
            
            logger.info(f"✅ PDF subido exitosamente: {public_url}")
            
            return {
                "status": "success",
                "archivo_nombre": nombre_unico,
                "url_publica": public_url,
                "tamaño_bytes": len(pdf_bytes),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo PDF: {str(e)}")
            return {"error": f"Error subiendo PDF: {str(e)}", "status": "failed"}

    def listar_archivos(self, limite: int = 50) -> Dict[str, Any]:
        """
        Listar archivos en el bucket
        """
        try:
            # Corregir: list() no acepta parámetro limit
            result = self.supabase.storage.from_(self.bucket_name).list()
            
            # Aplicar límite manualmente si es necesario
            if limite and len(result) > limite:
                result = result[:limite]
            
            return {
                "status": "success",
                "archivos": result,
                "total": len(result)
            }
        except Exception as e:
            logger.error(f"❌ Error listando archivos: {e}")
            return {"error": f"Error listando archivos: {e}", "status": "failed"}
