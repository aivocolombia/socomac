from fastapi import APIRouter, Request
from app.core.agent import get_agent
from app.services.sender import send_whatsapp_message
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
        message = message_data.get("text", {}).get("body", "")
        phone = message_data.get("from", "")
        if phone != "573195792747":
            return {"reply": "ok"}
        channel_id = body.get("channel_id", "")
    except (IndexError, AttributeError, TypeError):
        return {"reply": "Formato de mensaje inválido"}

    if not message or not phone or not channel_id:
        return {"reply": "Faltan datos en el mensaje"}

    agent = get_agent(phone)
    response = agent.run(message)
    if not response:
        response = "No pude procesar tu mensaje. Por favor, intenta de nuevo más tarde."
        
    response_dict = TextNormalizer().formatear_json(response)
    respuestas = response_dict.get("json", [])
    print("Respuestas formateadas:", respuestas)
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
