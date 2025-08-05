# Socomac - AI Agent con Soporte de Audio e Imágenes

Socomac es un agente de inteligencia artificial que puede procesar mensajes de texto, audio e imágenes a través de WhatsApp Business API (Whapi).

## 🚀 Características

- **Procesamiento de Texto**: Maneja mensajes de texto normales
- **Procesamiento de Audio**: Transcribe mensajes de voz usando OpenAI Whisper
- **Procesamiento de Imágenes**: Extrae texto de imágenes usando OpenAI Vision API
- **Integración con Whapi**: Conecta con WhatsApp Business API
- **Agente de IA**: Procesa mensajes con un agente de inteligencia artificial
- **Respuestas Inteligentes**: Genera respuestas contextuales y relevantes

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web para la API
- **OpenAI Whisper**: Transcripción de audio
- **OpenAI Vision API**: Extracción de texto de imágenes
- **Whapi**: API de WhatsApp Business
- **LangChain**: Framework para agentes de IA
- **MongoDB**: Base de datos (opcional)
- **Supabase**: Base de datos (opcional)

## 📋 Requisitos

- Python 3.8+
- OpenAI API Key
- Whapi API Key
- FFmpeg (para procesamiento de audio)

## 🔧 Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/aivocolombia/socomac.git
cd socomac
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**:
```bash
# Crear archivo .env
OPENAI_API_KEY=tu_openai_api_key
WHAPI_API_KEY=tu_whapi_api_key
TELEGRAM_KEY=tu_telegram_bot_token  # Opcional
```

4. **Instalar FFmpeg** (para procesamiento de audio):
   - **Windows**: Descargar desde https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## 🚀 Uso

1. **Iniciar el servidor**:
```bash
uvicorn app.main:app --reload
```

2. **Configurar webhook en Whapi**:
   - URL: `https://tu-dominio.com/webhook`
   - Método: POST

3. **Probar la funcionalidad**:
```bash
python test_webhook_simple.py
```

## 📁 Estructura del Proyecto

```
socomac/
├── app/
│   ├── api/
│   │   └── webhook.py          # Endpoint del webhook
│   ├── core/
│   │   ├── agent.py            # Agente de IA
│   │   ├── format_message.py   # Formateo de mensajes
│   │   ├── memory.py           # Gestión de memoria
│   │   ├── prompts.py          # Prompts del agente
│   │   └── tools.py            # Herramientas del agente
│   ├── services/
│   │   ├── audio_processor.py  # Procesamiento de audio
│   │   ├── image_processor.py  # Procesamiento de imágenes
│   │   ├── sender.py           # Envío de mensajes
│   │   └── telegram.py         # Integración con Telegram
│   └── main.py                 # Aplicación principal
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔄 Flujo de Procesamiento

### Mensajes de Texto
1. Recibe mensaje de texto desde Whapi
2. Procesa con el agente de IA
3. Envía respuesta formateada

### Mensajes de Audio/Voz
1. Recibe mensaje de audio desde Whapi
2. Descarga el archivo de audio
3. Transcribe usando OpenAI Whisper
4. Procesa el texto con el agente de IA
5. Envía respuesta formateada

### Mensajes de Imagen
1. Recibe mensaje de imagen desde Whapi
2. Descarga la imagen
3. Extrae texto usando OpenAI Vision API
4. Procesa el texto con el agente de IA
5. Envía respuesta formateada

## 🧪 Pruebas

### Probar con PowerShell
```powershell
# Probar mensaje de imagen
powershell -ExecutionPolicy Bypass -File test_image_powershell.ps1
```

### Probar con Python
```bash
# Probar todos los tipos de mensajes
python test_webhook_simple.py
```

## 🔧 Configuración del Webhook

El webhook acepta los siguientes tipos de mensajes:

- **text**: Mensajes de texto normales
- **voice**: Mensajes de voz (audio/ogg)
- **audio**: Mensajes de audio (otros formatos)
- **image**: Mensajes de imagen (JPEG, PNG, etc.)

### Formato de Respuesta
```json
{
  "reply": "ok"
}
```

## 🐳 Docker

Para ejecutar con Docker:

```bash
docker build -t socomac .
docker run -p 8000:8000 socomac
```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.
