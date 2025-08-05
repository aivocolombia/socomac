import os
import logging
from typing import Optional, Tuple
from pydub import AudioSegment
import tempfile
import requests

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Servicio para procesar y transcribir archivos de audio usando la API de OpenAI Whisper
    """
    
    def __init__(self):
        """Inicializa el procesador de audio (sin modelo local)"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("La clave OPENAI_API_KEY no está configurada en el entorno.")
        self.api_url = "https://api.openai.com/v1/audio/transcriptions"
    
    def convert_audio_format(self, audio_path: str, target_format: str = "wav") -> Optional[str]:
        """
        Convierte un archivo de audio a formato WAV para mejor compatibilidad
        """
        try:
            temp_dir = tempfile.gettempdir()
            filename = os.path.basename(audio_path)
            name_without_ext = os.path.splitext(filename)[0]
            converted_path = os.path.join(temp_dir, f"{name_without_ext}.{target_format}")
            audio = AudioSegment.from_file(audio_path)
            audio.export(converted_path, format=target_format)
            logger.info(f"Audio convertido exitosamente: {audio_path} -> {converted_path}")
            return converted_path
        except Exception as e:
            logger.error(f"Error al convertir audio {audio_path}: {e}")
            return None

    def transcribe_audio(self, audio_path: str, language: str = "es") -> Tuple[bool, str]:
        """
        Transcribe un archivo de audio a texto usando la API de OpenAI Whisper
        """
        if not self.api_key:
            return False, "Error: OPENAI_API_KEY no configurada"
        try:
            logger.info(f"Iniciando transcripción de: {audio_path} usando Whisper API")
            file_extension = os.path.splitext(audio_path)[1].lower()
            if file_extension not in ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.webm']:
                converted_path = self.convert_audio_format(audio_path, target_format="mp3")
                if not converted_path:
                    return False, "Error al convertir el formato de audio"
                audio_path = converted_path
            with open(audio_path, "rb") as audio_file:
                files = {"file": (os.path.basename(audio_path), audio_file, "audio/mpeg")}
                data = {"model": "whisper-1"}
                if language:
                    data["language"] = language
                headers = {"Authorization": f"Bearer {self.api_key}"}
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
                logger.error(f"Error en la API de OpenAI: {response.text}")
                return False, f"Error en la API de OpenAI: {response.text}"
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
#audio_processor = AudioProcessor()
audio_processor = AudioProcessor() 