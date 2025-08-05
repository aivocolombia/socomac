import os
import logging
import requests
import tempfile
from typing import Tuple, Optional
import base64
import json

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Servicio para procesar imágenes y extraer texto usando OpenAI Vision API
    """
    
    def __init__(self):
        """Inicializa el procesador de imágenes"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY no configurada. No se podrá extraer texto de imágenes.")
    
    def download_image(self, image_link: str) -> Optional[str]:
        """
        Descarga una imagen desde un link y retorna la ruta del archivo
        """
        try:
            print(f"📥 Descargando imagen desde: {image_link}")
            
            # Crear archivo temporal
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"image_{os.path.basename(image_link)}")
            
            # Descargar la imagen
            response = requests.get(image_link)
            
            if response.status_code != 200:
                print(f"❌ Error descargando imagen: {response.status_code} - {response.text}")
                return None
            
            # Guardar la imagen
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Imagen descargada exitosamente: {temp_file}")
            print(f"📊 Tamaño del archivo: {len(response.content)} bytes")
            return temp_file
            
        except Exception as e:
            print(f"❌ Error descargando imagen: {e}")
            return None
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """
        Codifica una imagen a base64 para enviarla a OpenAI Vision API
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error codificando imagen: {e}")
            return None
    
    def extract_text_from_image_openai(self, image_path: str) -> Tuple[bool, str]:
        """
        Extrae texto de una imagen usando OpenAI Vision API
        """
        if not self.api_key:
            return False, "Error: OPENAI_API_KEY no configurada"
        
        try:
            print(f"🔍 Iniciando extracción de texto con OpenAI Vision: {image_path}")
            
            # Verificar si el archivo existe
            if not os.path.exists(image_path):
                return False, f"Error: El archivo {image_path} no existe"
            
            # Codificar imagen a base64
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return False, "Error al codificar la imagen"
            
            # Preparar la solicitud a OpenAI Vision API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extrae todo el texto que veas en esta imagen. Si no hay texto, responde 'No se encontró texto en la imagen'. Responde solo con el texto extraído, sin explicaciones adicionales."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Enviar solicitud a OpenAI
            response = requests.post(self.api_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result["choices"][0]["message"]["content"].strip()
                
                if extracted_text and extracted_text.lower() != "no se encontró texto en la imagen":
                    print(f"✅ Texto extraído exitosamente: '{extracted_text[:100]}...'")
                    print(f"📊 Longitud del texto extraído: {len(extracted_text)} caracteres")
                    return True, extracted_text
                else:
                    print("⚠️ No se encontró texto en la imagen")
                    return False, "No se encontró texto en la imagen"
            else:
                error_msg = f"Error en la API de OpenAI: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error en extracción de texto: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_image_message(self, image_link: str) -> Tuple[bool, str]:
        """
        Procesa un mensaje de imagen completo usando OpenAI Vision
        """
        try:
            # Descargar la imagen
            image_file_path = self.download_image(image_link)
            
            if not image_file_path:
                return False, "Error al descargar la imagen. Por favor, intenta de nuevo."
            
            try:
                # Extraer texto de la imagen usando OpenAI Vision
                success, extracted_text = self.extract_text_from_image_openai(image_file_path)
                return success, extracted_text
                
            finally:
                # Limpiar archivo temporal
                self.cleanup_temp_files(image_file_path)
                print("🧹 Archivo temporal eliminado")
                
        except Exception as e:
            error_msg = f"Error procesando imagen: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def cleanup_temp_files(self, file_path: str):
        """Elimina archivos temporales"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo temporal eliminado: {file_path}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal {file_path}: {e}")

# Instancia global del procesador de imágenes
image_processor = ImageProcessor() 