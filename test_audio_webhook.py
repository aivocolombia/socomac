#!/usr/bin/env python3
"""
Script de prueba para simular webhooks de Whapi con mensajes de voz
"""

import json
import requests
import os

# URL del webhook local
WEBHOOK_URL = "http://localhost:8000/webhook"

def test_text_message():
    """Prueba un mensaje de texto normal"""
    payload = {
        "messages": [
            {
                "id": "text_message_id_123",
                "from_me": False,
                "type": "text",
                "chat_id": "573195792747@s.whatsapp.net",
                "timestamp": 1754413459,
                "source": "mobile",
                "text": {
                    "body": "Hola, ¿cómo estás?"
                },
                "from": "573195792747",
                "from_name": "Camilo Mora"
            }
        ],
        "event": {
            "type": "messages",
            "event": "post"
        },
        "channel_id": "ANTMAN-S5XM6"
    }
    
    print("🧪 Probando mensaje de texto...")
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_voice_message():
    """Prueba un mensaje de voz (formato real de Whapi con link)"""
    payload = {
        "messages": [
            {
                "id": "OqbKEat5yjY7Vw-gHqFdSGxaw",
                "from_me": False,
                "type": "voice",
                "chat_id": "573195792747@s.whatsapp.net",
                "timestamp": 1754413767,
                "source": "mobile",
                "voice": {
                    "id": "oga-3aa6ca11ab79ca363b57-807a857521b16b",
                    "mime_type": "audio/ogg; codecs=opus",
                    "file_size": 9164,
                    "sha256": "IsM2cqdDFMlFw25WQ2R2oyZfFEY+8XJuHPN6gsdFl/c=",
                    "link": "https://s3.eu-central-1.wasabisys.com/in-files/573027367797/oga-3aa6ca11ab79ca363b57-807a857521b16b.oga",
                    "seconds": 3
                },
                "from": "573195792747",
                "from_name": "Camilo Mora"
            }
        ],
        "event": {
            "type": "messages",
            "event": "post"
        },
        "channel_id": "ANTMAN-S5XM6"
    }
    
    print("🎵 Probando mensaje de voz...")
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_audio_message():
    """Prueba un mensaje de audio (no voz) con link"""
    payload = {
        "messages": [
            {
                "id": "audio_message_id_456",
                "from_me": False,
                "type": "audio",
                "chat_id": "573195792747@s.whatsapp.net",
                "timestamp": 1754413459,
                "source": "mobile",
                "audio": {
                    "id": "audio_file_id_789",
                    "mime_type": "audio/mp3",
                    "file_size": 15000,
                    "sha256": "test_sha256_audio",
                    "link": "https://s3.eu-central-1.wasabisys.com/in-files/573027367797/audio_test.mp3",
                    "seconds": 5
                },
                "from": "573195792747",
                "from_name": "Camilo Mora"
            }
        ],
        "event": {
            "type": "messages",
            "event": "post"
        },
        "channel_id": "ANTMAN-S5XM6"
    }
    
    print("🎵 Probando mensaje de audio...")
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

def test_unsupported_message():
    """Prueba un tipo de mensaje no soportado"""
    payload = {
        "messages": [
            {
                "id": "image_message_id_789",
                "from_me": False,
                "type": "image",
                "chat_id": "573195792747@s.whatsapp.net",
                "timestamp": 1754413459,
                "source": "mobile",
                "image": {
                    "id": "image_file_id_123",
                    "mime_type": "image/jpeg",
                    "file_size": 50000,
                    "sha256": "test_sha256_image"
                },
                "from": "573195792747",
                "from_name": "Camilo Mora"
            }
        ],
        "event": {
            "type": "messages",
            "event": "post"
        },
        "channel_id": "ANTMAN-S5XM6"
    }
    
    print("🖼️ Probando mensaje de imagen (no soportado)...")
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del webhook...")
    print("=" * 50)
    
    # Verificar que el servidor esté corriendo
    try:
        health_response = requests.get("http://localhost:8000/health")
        if health_response.status_code == 200:
            print("✅ Servidor está corriendo")
        else:
            print("❌ Servidor no responde correctamente")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en localhost:8000")
        exit(1)
    
    # Ejecutar pruebas
    test_text_message()
    test_voice_message()
    test_audio_message()
    test_unsupported_message()
    
    print("✅ Pruebas completadas") 