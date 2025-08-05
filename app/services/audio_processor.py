import os
import logging
from typing import Optional, Tuple
import tempfile
import requests

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Servicio para procesar y transcribir archivos de audio usando la API de OpenAI Whisper
    """
    
    def __init__(self):
        """Inicializa el procesador de audio"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("La clave OPENAI_API_KEY no está configurada en el entorno.")
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
    
    def transcribe_audio(self, audio_path: str, language: str = "es") -> Tuple[bool, str]:
        """
        Transcribe un archivo de audio a texto usando la API de OpenAI Whisper
        """
        if not self.api_key:
            return False, "Error: OPENAI_API_KEY no configurada"
        try:
            logger.info(f"Iniciando transcripción de: {audio_path} usando Whisper API")
            
            # Verificar si el archivo existe
            if not os.path.exists(audio_path):
                return False, f"Error: El archivo {audio_path} no existe"
            
            # Obtener la extensión del archivo
            file_extension = os.path.splitext(audio_path)[1].lower()
            
            # Determinar el MIME type basado en la extensión
            mime_type_map = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.oga': 'audio/ogg',
                '.m4a': 'audio/mp4',
                '.flac': 'audio/flac',
                '.webm': 'audio/webm'
            }
            
            mime_type = mime_type_map.get(file_extension, 'audio/mpeg')
            
            # Intentar transcribir directamente
            try:
                with open(audio_path, "rb") as audio_file:
                    files = {"file": (os.path.basename(audio_path), audio_file, mime_type)}
                    data = {"model": "whisper-1"}
                    if language:
                        data["language"] = language
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    
                    logger.info(f"Enviando archivo {audio_path} con MIME type {mime_type}")
                    response = requests.post(self.api_url, headers=headers, files=files, data=data)
                
                if response.status_code == 200:
                    transcription = response.json().get("text", "").strip()
                    if transcription:
                        logger.info(f"Transcripción exitosa: '{transcription[:50]}...'")
                        return True, transcription
                    else:
                        logger.warning("Transcripción vacía - posible silencio o audio no reconocible")
                        return False, "No se pudo transcribir el audio (posible silencio o audio no reconocible)"
                else:
                    logger.error(f"Error en la API de OpenAI: {response.status_code} - {response.text}")
                    return False, f"Error en la API de OpenAI: {response.status_code} - {response.text}"
                    
            except Exception as e:
                logger.error(f"Error en transcripción: {e}")
                return False, f"Error en transcripción: {str(e)}"
                    
        except Exception as e:
            error_msg = f"Error en transcripción: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def process_voice_message(self, audio_path: str, user_id: int) -> Tuple[bool, str]:
        logger.info(f"Procesando mensaje de voz para usuario {user_id}: {audio_path}")
        return self.transcribe_audio(audio_path, language="es")

    def process_audio_file(self, audio_path: str, user_id: int) -> Tuple[bool, str]:
        logger.info(f"Procesando archivo de audio para usuario {user_id}: {audio_path}")
        return self.transcribe_audio(audio_path, language=None)

    def cleanup_temp_files(self, file_path: str):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Archivo temporal eliminado: {file_path}")
        except Exception as e:
            logger.warning(f"No se pudo eliminar archivo temporal {file_path}: {e}")

# Instancia global del procesador de audio
audio_processor = AudioProcessor() 