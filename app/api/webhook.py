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
        
        # Verificar si es información de transferencia y extraer datos relevantes
        if any(keyword in extracted_text.lower() for keyword in ['transferencia', 'transfer', 'envío', 'envio', 'banco', 'comprobante']):
            print("🏦 Detectada posible información de transferencia")
            processed_text = self._extract_transfer_info(extracted_text)
        else:
            # Procesar el texto extraído para dividir valores grandes entre 1000
            print("💰 Procesando montos monetarios en imagen")
            processed_text = self._process_image_values(extracted_text)
        
        # SIEMPRE mostrar el monto después de analizar la imagen
        if processed_text and processed_text != extracted_text:
            print(f"📝 Texto final procesado: '{processed_text}'")
            return f"IMAGEN RECIBIDA - Procesando imagen...\n\n{processed_text}"
        else:
            print(f"📝 Texto extraído sin cambios: '{extracted_text}'")
            return f"IMAGEN RECIBIDA - Procesando imagen...\n\n{extracted_text}"
    
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
        """Procesa montos de dinero extraídos de imágenes, dividiendo SIEMPRE por 1000"""
        import re
        
        print(f"🔢 Procesando montos de dinero en texto: '{text}'")
        
        # Buscar montos de dinero con signo $ seguido de números de 3 o más dígitos
        def replace_money_amounts(match):
            full_match = match.group(0)  # Captura todo el match incluyendo el $
            number_str = match.group(1)  # Captura solo el número
            
            # Limpiar el número: manejar formato colombiano (punto = miles, coma = decimal)
            # Ejemplo: 1.200.000,00 → 1200000
            clean_number = number_str.replace('.', '')  # Remover puntos de miles
            if ',' in clean_number:
                # Si hay coma decimal, solo tomar la parte entera
                clean_number = clean_number.split(',')[0]
            
            number = int(clean_number)
            
            print(f"🔍 Encontrado monto: ${number_str} → Limpiado: ${number}")
            
            # SIEMPRE dividir por 1000 todos los montos de imágenes
            new_number = number / 1000
            new_amount = f"${int(new_number)}" if new_number.is_integer() else f"${new_number}"
            print(f"💰 Monto procesado: ${number} → Dividido por 1000 = {new_amount}")
            return new_amount
        
        # Aplicar la división por 1000 a TODOS los montos de dinero de imágenes
        # También buscar variaciones como "pesos", "COP", etc.
        processed_text = re.sub(r'\$\s*([\d.]+(?:,\d{2})?)', replace_money_amounts, text)  # $ 1.200.000,00
        processed_text = re.sub(r'\$([\d.]+(?:,\d{2})?)', replace_money_amounts, processed_text)  # $1.200.000,00
        processed_text = re.sub(r'(\d{3,})\s*(?:pesos?|COP|colombianos?)', lambda m: f"{int(m.group(1))/1000} pesos", processed_text)
        processed_text = re.sub(r'(\d{3,})\s*\$', lambda m: f"${int(m.group(1))/1000}", processed_text)
        
        if processed_text != text:
            print(f"✅ Texto procesado: '{text}' → '{processed_text}'")
        else:
            print("ℹ️ No se encontraron montos de dinero grandes para procesar")
        
        return processed_text
    
    def _extract_transfer_info(self, text: str) -> str:
        """Extrae información específica de transferencias y la formatea"""
        import re
        
        print(f"🏦 Analizando texto para información de transferencia: '{text}'")
        
        # Patrones para extraer información de transferencias
        patterns = {
            'monto': r'\$\s*([\d.]+(?:,\d{2})?)',  # $ 1.200.000,00 o $1.200.000,00
            'banco_origen': r'(?:banco|origen|desde|from)[:\s]*([A-Za-z\s]+)',
            'banco_destino': r'(?:destino|hacia|to|para)[:\s]*([A-Za-z\s]+)',
            'comprobante': r'(?:comprobante|referencia|número|numero)[:\s]*(\d+)',
            'fecha': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'cuenta': r'(?:cuenta|account)[:\s]*(\d+)',
            'transferencia': r'(transferencia|transfer|envío|envio)',
        }
        
        extracted_info = {}
        original_monto = None
        
        # Buscar monto y guardarlo en memoria
        monto_match = re.search(patterns['monto'], text)
        if monto_match:
            number_str = monto_match.group(1)
            
            # Limpiar el número: manejar formato colombiano (punto = miles, coma = decimal)
            # Ejemplo: 1.200.000,00 → 1200000
            clean_number = number_str.replace('.', '')  # Remover puntos de miles
            if ',' in clean_number:
                # Si hay coma decimal, solo tomar la parte entera
                clean_number = clean_number.split(',')[0]
            
            original_monto = int(clean_number)
            
            print(f"🔍 Monto de transferencia detectado: ${number_str} → Limpiado: ${original_monto}")
            
            # SIEMPRE dividir por 1000 todos los montos de imágenes
            processed_monto = original_monto / 1000
            extracted_info['monto'] = f"${int(processed_monto)}" if processed_monto.is_integer() else f"${processed_monto}"
            print(f"💰 Monto procesado: ${original_monto} → Guardado en memoria como {extracted_info['monto']}")
        
        # Buscar otros campos
        for field, pattern in patterns.items():
            if field != 'monto':
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted_info[field] = match.group(1).strip()
                    print(f"📋 {field.title()} detectado: {extracted_info[field]}")
        
        # Si se detectó información de transferencia, formatear el mensaje
        if extracted_info:
            transfer_message = "🏦 INFORMACIÓN DE TRANSFERENCIA DETECTADA:\n"
            
            if 'monto' in extracted_info:
                transfer_message += f"💰 Monto: {extracted_info['monto']}\n"
            
            if 'banco_origen' in extracted_info:
                transfer_message += f"🏦 Banco origen: {extracted_info['banco_origen']}\n"
            
            if 'banco_destino' in extracted_info:
                transfer_message += f"🎯 Banco destino: {extracted_info['banco_destino']}\n"
            
            if 'comprobante' in extracted_info:
                transfer_message += f"📄 Comprobante: {extracted_info['comprobante']}\n"
            
            if 'fecha' in extracted_info:
                transfer_message += f"📅 Fecha: {extracted_info['fecha']}\n"
            
            if 'cuenta' in extracted_info:
                transfer_message += f"💳 Cuenta: {extracted_info['cuenta']}\n"
            
            transfer_message += f"\n📝 Texto original extraído: {text}"
            
            print(f"✅ Información de transferencia extraída y formateada")
            return transfer_message
        
        return text
    
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
        self.authorized_phone = ["573172288329"]
    
    def get_authorized_phones(self):
        """Obtiene los números de teléfono autorizados dinámicamente"""
        try:
            # Importar la herramienta aquí para evitar dependencias circulares
#            from app.core.tools import obtener_telefono_usuario_id2
            
            # Obtener todos los usuarios activos
 #           #usuarios_activos = obtener_telefono_usuario_id2("")
            usuarios_activos = [573172288329]
            # Verificar si se obtuvieron usuarios activos
            if usuarios_activos and not usuarios_activos.startswith("❌"):
                # Extraer teléfonos de la respuesta
                lines = usuarios_activos.split('\n')
                authorized_phones = []
                
                for line in lines:
                    if '📱' in line:
                        # Extraer el número de teléfono de la línea
                        phone_part = line.split('📱')[1].split('|')[0].strip()
                        if phone_part.isdigit() and len(phone_part) >= 10:
                            authorized_phones.append(phone_part)
                
                if authorized_phones:
                    print(f"📱 Teléfonos autorizados obtenidos dinámicamente: {authorized_phones}")
                    return authorized_phones
                else:
                    print(f"⚠️ No se pudieron extraer teléfonos válidos de: {usuarios_activos}")
                    return []
            else:
                print(f"⚠️ No se pudieron obtener usuarios activos: {usuarios_activos}")
                return []
                
        except Exception as e:
            print(f"❌ Error obteniendo teléfonos autorizados: {e}")
            return []
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
            
            # Obtener teléfonos autorizados dinámicamente
            authorized_phones = self.get_authorized_phones()
            
            if not authorized_phones:
                print(f"⚠️ No hay teléfonos autorizados configurados")
                return None, None, None, None
            
            if phone not in authorized_phones:
                print(f"🚫 Teléfono no autorizado: {phone}")
                print(f"📱 Teléfonos autorizados: {authorized_phones}")
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
