from fastapi import APIRouter, Request
from app.core.agent import get_agent
from app.services.sender import send_whatsapp_message, download_whapi_audio_from_link
from app.core.format_message import TextNormalizer
from app.services.sender import send_image_message
from app.services.telegram import send_telegram_message, download_file
from app.services.audio_processor import audio_processor
from app.services.image_processor import image_processor
from typing import List, Optional, Dict, Any
import logging
import os
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

@router.get("/")
async def health_check():
    return {"status": "ok", "message": "API is running"}


class MessageProcessor:
    """Clase para procesar diferentes tipos de mensajes"""
    
    def __init__(self):
        self.audio_processor = audio_processor
        self.image_processor = image_processor
    
    def process_text_message(self, message_data: Dict[str, Any]) -> str:
        """Procesa mensajes de texto"""
        message_text = message_data.get("text", {}).get("body", "")
        print(f"📝 Mensaje de texto recibido: {message_text}")
        return message_text
    
    def process_voice_message(self, message_data: Dict[str, Any]) -> str:
        """Procesa mensajes de voz"""
        print("🎵 Mensaje de voz recibido")
        voice_data = message_data.get("voice", {})
        audio_link = voice_data.get("link")
        
        if not audio_link:
            print("❌ No se encontró link de audio en el mensaje")
            raise ValueError("No se pudo obtener el link del mensaje de voz.")
        
        print(f"🔗 Link de audio: {audio_link}")
        return self._process_audio_file(audio_link, "voz")
    
    def process_audio_message(self, message_data: Dict[str, Any]) -> str:
        """Procesa mensajes de audio (no voz)"""
        print("🎵 Mensaje de audio recibido")
        audio_data = message_data.get("audio", {})
        audio_link = audio_data.get("link")
        
        if not audio_link:
            print("❌ No se encontró link de audio en el mensaje")
            raise ValueError("No se pudo obtener el link del audio.")
        
        print(f"🔗 Link de audio: {audio_link}")
        return self._process_audio_file(audio_link, "audio")
    
    def process_image_message(self, message_data: Dict[str, Any]) -> str:
        """Procesa mensajes de imagen y extrae texto usando OCR"""
        print("🖼️ IMAGEN RECIBIDA - Procesando imagen...")
        image_data = message_data.get("image", {})
        image_link = image_data.get("link")
        
        if not image_link:
            print("❌ No se encontró link de imagen en el mensaje")
            raise ValueError("No se pudo obtener el link de la imagen.")
        
        print(f"🔗 Link de imagen: {image_link}")
        extracted_text = self._process_image_file(image_link)
        
        # Procesar el texto extraído para dividir valores grandes entre 1000
        processed_text = self._process_image_values(extracted_text)
        
        print(f"📝 Texto final procesado: '{processed_text}'")
        return processed_text
    
    def _process_audio_file(self, audio_link: str, audio_type: str) -> str:
        """Procesa un archivo de audio y retorna la transcripción"""
        # Descargar el audio usando el link directo
        audio_file_path = download_whapi_audio_from_link(audio_link)
        
        if not audio_file_path:
            raise ValueError(f"Error al descargar el {audio_type}. Por favor, intenta de nuevo.")
        
        try:
            print(f"🎯 Iniciando transcripción del archivo: {audio_file_path}")
            # Transcribir el audio
            success, transcription = self.audio_processor.transcribe_audio(audio_file_path, language="es")
            
            if success:
                print(f"✅ Transcripción exitosa: '{transcription}'")
                print(f"📊 Longitud del texto transcrito: {len(transcription)} caracteres")
                return transcription
            else:
                print(f"❌ Error en transcripción: {transcription}")
                raise ValueError(f"No pude entender el {audio_type}. Por favor, intenta de nuevo o envía un mensaje de texto.")
                
        finally:
            # Limpiar archivo temporal
            self.audio_processor.cleanup_temp_files(audio_file_path)
            print("🧹 Archivo temporal eliminado")
    
    def _process_image_file(self, image_link: str) -> str:
        """Procesa un archivo de imagen y extrae texto usando OCR"""
        try:
            print(f"🔍 Iniciando extracción de texto de imagen: {image_link}")
            # Procesar la imagen y extraer texto
            success, extracted_text = self.image_processor.process_image_message(image_link)
            
            if success:
                print(f"✅ Texto extraído exitosamente: '{extracted_text}'")
                print(f"📊 Longitud del texto extraído: {len(extracted_text)} caracteres")
                return extracted_text
            else:
                print(f"❌ Error en extracción de texto: {extracted_text}")
                raise ValueError(f"No pude extraer texto de la imagen. Por favor, intenta con otra imagen o envía un mensaje de texto.")
                
        except Exception as e:
            print(f"❌ Error procesando imagen: {e}")
            raise ValueError(f"Error procesando imagen: {str(e)}")
    
    def _process_image_values(self, text: str) -> str:
        """Procesa montos de dinero extraídos de imágenes, dividiendo por 1000 si son >4 dígitos"""
        import re
        
        print(f"🔢 Procesando montos de dinero en texto: '{text}'")
        
        # Buscar montos de dinero con signo $ seguido de números de 4 o más dígitos
        def replace_money_amounts(match):
            full_match = match.group(0)  # Captura todo el match incluyendo el $
            number_str = match.group(1)  # Captura solo el número
            number = int(number_str)
            
            if number >= 1000:
                new_number = number / 1000
                new_amount = f"${int(new_number)}" if new_number.is_integer() else f"${new_number}"
                print(f"💰 Monto detectado: ${number} → Dividido por 1000 = {new_amount}")
                return new_amount
            return full_match
        
        # Aplicar la división por 1000 solo a montos de dinero ($ seguido de 4+ dígitos)
        processed_text = re.sub(r'\$(\d{4,})', replace_money_amounts, text)
        
        if processed_text != text:
            print(f"✅ Texto procesado: '{text}' → '{processed_text}'")
        else:
            print("ℹ️ No se encontraron montos de dinero grandes para procesar")
        
        return processed_text
    
    def process_unsupported_message(self, message_type: str) -> str:
        """Maneja tipos de mensaje no soportados"""
        print(f"❌ Tipo de mensaje no soportado: {message_type}")
        raise ValueError("Solo puedo procesar mensajes de texto, voz, audio e imágenes por ahora.")


class ResponseSender:
    """Clase para enviar respuestas"""
    
    def send_responses(self, phone: str, channel_id: str, response: str):
        """Envía las respuestas formateadas"""
        print(f"🤖 Procesando con agente de IA: '{response}'")
        
        # Procesar con el agente de IA
        agent = get_agent(phone)
        agent_result = agent.invoke({"input": response})
        agent_response = agent_result.get("output", "")
        
        if not agent_response:
            agent_response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
        
        print(f"🤖 Respuesta del agente: '{agent_response}'")
        
        # Formatear y enviar respuestas
        response_dict = TextNormalizer().formatear_json(agent_response)
        respuestas = response_dict.get("json", [])
        print("📤 Respuestas formateadas:", respuestas)
        
        for item in respuestas:
            message = item["message"]
            if message:
                send_whatsapp_message(phone=phone, message=message, channel_id=channel_id)


class WebhookHandler:
    """Clase principal para manejar webhooks"""
    
    def __init__(self):
        self.message_processor = MessageProcessor()
        self.response_sender = ResponseSender()
        self.authorized_phone = ["573195792747", "573172288329"]
    #TODO verificar numero de telefono del agente de whatsapp, no está tomandolo correctamente.
    def validate_message(self, body: Dict[str, Any]) -> tuple:
        """Valida y extrae datos del mensaje"""
        try:
            # Verificar si es un evento de statuses (ignorar estos eventos)
            if "statuses" in body:
                print("📊 Evento de status ignorado (sent, delivered, read, etc.)")
                return None, None, None, None
            
            # Verificar si hay mensajes
            messages = body.get("messages", [])
            if not messages:
                print("📭 No hay mensajes en el webhook")
                return None, None, None, None
            
            message_data = messages[0]
            phone = message_data.get("from", "")
            
            if phone not in self.authorized_phone:
                print(f"🚫 Teléfono no autorizado: {phone}")
                return None, None, None, None
            
            channel_id = body.get("channel_id", "")
            message_type = message_data.get("type", "")
            
            return message_data, phone, channel_id, message_type
            
        except (IndexError, AttributeError, TypeError) as e:
            print(f"❌ Error procesando mensaje: {e}")
            raise ValueError("Formato de mensaje inválido")
    
    def extract_message_text(self, message_data: Dict[str, Any], message_type: str) -> str:
        """Extrae el texto del mensaje según su tipo"""
        if message_type == "text":
            return self.message_processor.process_text_message(message_data)
        elif message_type == "voice":
            return self.message_processor.process_voice_message(message_data)
        elif message_type == "audio":
            return self.message_processor.process_audio_message(message_data)
        elif message_type == "image":
            return self.message_processor.process_image_message(message_data)
        else:
            return self.message_processor.process_unsupported_message(message_type)
    
    def handle_webhook(self, body: Dict[str, Any]) -> Dict[str, str]:
        """Maneja el webhook completo"""
        try:
            # Validar y extraer datos
            result = self.validate_message(body)
            if result[0] is None:
                return {"reply": "ok"}
            
            message_data, phone, channel_id, message_type = result
            
            # Extraer texto del mensaje
            message_text = self.extract_message_text(message_data, message_type)
            
            if not message_text:
                return {"reply": "Faltan datos en el mensaje"}
            
            # Enviar respuestas
            self.response_sender.send_responses(phone, channel_id, message_text)
            
            return {"reply": "ok"}
            
        except ValueError as e:
            return {"reply": str(e)}
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return {"reply": "Error interno del servidor"}


# Instancia global del manejador de webhooks
webhook_handler = WebhookHandler()


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Endpoint principal del webhook"""
    body = await request.json()
    print("Webhook received:", body)
    
    return webhook_handler.handle_webhook(body)
