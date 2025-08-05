from fastapi import APIRouter, Request
from app.core.agent import get_agent
from app.services.sender import send_whatsapp_message, download_whapi_audio_from_link
from app.core.format_message import TextNormalizer
import os
from app.services.sender import send_image_message

from pydantic import BaseModel, Field
from app.services.telegram import send_telegram_message, download_file
from app.services.audio_processor import audio_processor
#TODO averiguar logging typing 
from typing import List, Optional
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


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    print("Webhook received:", body)

    try:
        message_data = body.get("messages", [])[0]
        phone = message_data.get("from", "")
        
        # Verificar si es el número autorizado
        if phone != "573195792747":
            return {"reply": "ok"}
            
        channel_id = body.get("channel_id", "")
        
        # Detectar tipo de mensaje
        message_type = message_data.get("type", "")
        message_text = ""
        
        if message_type == "text":
            # Mensaje de texto - lógica actual
            message_text = message_data.get("text", {}).get("body", "")
            print(f"📝 Mensaje de texto recibido: {message_text}")
            
        elif message_type == "voice":
            # Mensaje de voz - transcribir y procesar
            print("🎵 Mensaje de voz recibido")
            voice_data = message_data.get("voice", {})
            audio_link = voice_data.get("link")
            
            if audio_link:
                print(f"🔗 Link de audio: {audio_link}")
                # Descargar el audio usando el link directo
                audio_file_path = download_whapi_audio_from_link(audio_link)
                
                if audio_file_path:
                    print(f"🎯 Iniciando transcripción del archivo: {audio_file_path}")
                    # Transcribir el audio
                    success, transcription = audio_processor.transcribe_audio(audio_file_path, language="es")
                    
                    if success:
                        message_text = transcription
                        print(f"✅ Transcripción exitosa: '{message_text}'")
                        print(f"📊 Longitud del texto transcrito: {len(message_text)} caracteres")
                    else:
                        print(f"❌ Error en transcripción: {transcription}")
                        # Limpiar archivo temporal
                        audio_processor.cleanup_temp_files(audio_file_path)
                        return {"reply": "No pude entender el mensaje de voz. Por favor, intenta de nuevo o envía un mensaje de texto."}
                    
                    # Limpiar archivo temporal
                    audio_processor.cleanup_temp_files(audio_file_path)
                    print("🧹 Archivo temporal eliminado")
                else:
                    return {"reply": "Error al descargar el mensaje de voz. Por favor, intenta de nuevo."}
            else:
                print("❌ No se encontró link de audio en el mensaje")
                return {"reply": "No se pudo obtener el link del mensaje de voz."}
                
        elif message_type == "audio":
            # Mensaje de audio (no voz) - transcribir y procesar
            print("🎵 Mensaje de audio recibido")
            audio_data = message_data.get("audio", {})
            audio_link = audio_data.get("link")
            
            if audio_link:
                print(f"🔗 Link de audio: {audio_link}")
                # Descargar el audio usando el link directo
                audio_file_path = download_whapi_audio_from_link(audio_link)
                
                if audio_file_path:
                    print(f"🎯 Iniciando transcripción del archivo: {audio_file_path}")
                    # Transcribir el audio
                    success, transcription = audio_processor.transcribe_audio(audio_file_path, language="es")
                    
                    if success:
                        message_text = transcription
                        print(f"✅ Transcripción exitosa: '{message_text}'")
                        print(f"📊 Longitud del texto transcrito: {len(message_text)} caracteres")
                    else:
                        print(f"❌ Error en transcripción: {transcription}")
                        # Limpiar archivo temporal
                        audio_processor.cleanup_temp_files(audio_file_path)
                        return {"reply": "No pude entender el audio. Por favor, intenta de nuevo o envía un mensaje de texto."}
                    
                    # Limpiar archivo temporal
                    audio_processor.cleanup_temp_files(audio_file_path)
                    print("🧹 Archivo temporal eliminado")
                else:
                    return {"reply": "Error al descargar el audio. Por favor, intenta de nuevo."}
            else:
                print("❌ No se encontró link de audio en el mensaje")
                return {"reply": "No se pudo obtener el link del audio."}
                
        else:
            # Otros tipos de mensaje (imagen, documento, etc.)
            print(f"❌ Tipo de mensaje no soportado: {message_type}")
            return {"reply": "Solo puedo procesar mensajes de texto, voz y audio por ahora."}
            
    except (IndexError, AttributeError, TypeError) as e:
        print(f"❌ Error procesando mensaje: {e}")
        return {"reply": "Formato de mensaje inválido"}

    if not message_text or not phone or not channel_id:
        return {"reply": "Faltan datos en el mensaje"}

    print(f"🤖 Procesando con agente de IA: '{message_text}'")
    # Procesar con el agente de IA
    agent = get_agent(phone)
    response = agent.run(message_text)
    if not response:
        response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
        
    print(f"🤖 Respuesta del agente: '{response}'")
    response_dict = TextNormalizer().formatear_json(response)
    respuestas = response_dict.get("json", [])
    print("📤 Respuestas formateadas:", respuestas)
    for item in respuestas:
        message = item["message"]
        image_url = item["image"]
        if message and  image_url:
            send_image_message(phone=phone, image_url=image_url, caption=message, channel_id=channel_id)
        else:
            if message:
                send_whatsapp_message(phone=phone, message=message, channel_id=channel_id)
            if image_url:
                send_image_message(phone=phone, image_url=image_url, caption="", channel_id=channel_id)
    return {"reply": response}
