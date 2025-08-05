#!/bin/bash

# Script para probar el webhook de Telegram con diferentes tipos de contenido

echo "Probando el endpoint de salud..."
curl -X GET http://localhost:8000/health

echo -e "\n\nProbando el webhook con mensaje de texto..."
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {
        "id": 123456789
      },
      "text": "Hola, quiero ver el menú"
    }
  }'

echo -e "\n\nProbando el webhook con imagen..."
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {
        "id": 123456789
      },
      "photo": [
        {
          "file_id": "test_photo_id",
          "file_unique_id": "unique_photo_id",
          "width": 800,
          "height": 600,
          "file_size": 102400
        }
      ]
    }
  }'

echo -e "\n\nProbando el webhook con archivo de audio..."
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {
        "id": 123456789
      },
      "audio": {
        "file_id": "test_audio_id",
        "file_unique_id": "unique_audio_id",
        "duration": 30,
        "file_name": "audio_message.mp3",
        "mime_type": "audio/mpeg",
        "file_size": 512000
      }
    }
  }'

echo -e "\n\nProbando el webhook con mensaje de voz grabado en la app..."
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {
        "id": 123456789
      },
      "voice": {
        "file_id": "test_voice_id",
        "file_unique_id": "unique_voice_id",
        "duration": 15,
        "mime_type": "audio/ogg",
        "file_size": 256000
      }
    }
  }'

echo -e "\n\nProbando el webhook con saludo simple..."
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "from": {
        "id": 123456789
      },
      "text": "Hola"
    }
  }'

echo -e "\n\nPruebas completadas!" 