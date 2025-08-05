#!/usr/bin/env python3
"""
Script simple para probar el webhook con JSON válido
"""

import requests
import json

# URL del webhook local
WEBHOOK_URL = "http://localhost:8000/webhook"

def test_simple_text():
    """Prueba simple con mensaje de texto"""
    payload = {
        "messages": [
            {
                "id": "test_123",
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
    
    print("🧪 Probando mensaje de texto simple...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def test_voice_message():
    """Prueba con mensaje de voz (formato real)"""
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
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 50)

def test_image_message():
    """Prueba con mensaje de imagen (formato exacto que proporcionaste)"""
    payload = {
        "messages": [
            {
                "id": "OjI5zPXtkQlm6g-gOWFdSGxaw",
                "from_me": False,
                "type": "image",
                "chat_id": "573195792747@s.whatsapp.net",
                "timestamp": 1754416293,
                "source": "mobile",
                "image": {
                    "id": "jpeg-3a3239ccf5ed910966ea-80e5857521b16b",
                    "mime_type": "image/jpeg",
                    "file_size": 46793,
                    "sha256": "4o5LVrenal7p1KpDxgcmUGPb4Y1KsyKurUuihOqR9WA=",
                    "link": "https://s3.eu-central-1.wasabisys.com/in-files/573027367797/jpeg-3a3239ccf5ed910966ea-80e5857521b16b.jpeg",
                    "width": 724,
                    "height": 1280,
                    "preview": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABsSFBcUERsXFhceHBsgKEIrKCUlKFE6PTBCYFVlZF9VXVtqeJmBanGQc1tdhbWGkJ6jq62rZ4C8ybqmx5moq6T/2wBDARweHigjKE4rK06kbl1upKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKSkpKT/wgARCABIACkDASIAAhEBAxEB/8QAGQAAAwEBAQAAAAAAAAAAAAAAAAIDAQQF/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAH/2gAMAwEAAhADEAAAAPGxrFeO4kDcVmdia0URaTKutCQ8wm6FHAQ0FSkx8AADFA//xAAUEQEAAAAAAAAAAAAAAAAAAAAw/9oACAECAQE/AH//xAAXEQEAAwAAAAAAAAAAAAAAAAABABEw/9oACAEDAQE/AIFbf//EACYQAAICAgEDAgcAAAAAAAAAAAECAAMREhAhMVEEkSAiIzJBUlP/2gAIAQEAAT8A4rq9MfRl2b6nwKQGBIyIHQ9RUJsv8h7zZQOtQ947Bmyq6jxwtbMMgQV2DsIUs8Qo57w1kDPFJfXCxmsXucQ3P5m5hc4I4qR2XKmGmw9zmGsg4Jmh8woQM54p6r9xE1P7mHX8uczYwsccVq5X5e0K3GFGz1mjQowGeKNtejYhtcEgNmbmbmFjjhLCg6GbCbCbCFhjj//+AAMA/9k="
                },
                "context": {
                    "forwarded": True,
                    "forwarding_score": 3
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
    
    print("🖼️ Probando mensaje de imagen con formato exacto...")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
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
    test_simple_text()
    test_voice_message()
    test_image_message()
    
    print("✅ Pruebas completadas") 