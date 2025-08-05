# Socomac - AI Agent con Soporte de Audio

Socomac es un agente de inteligencia artificial que puede procesar mensajes de texto y audio a través de WhatsApp Business API (Whapi).

## 🚀 Características

- **Procesamiento de Texto**: Maneja mensajes de texto normales
- **Procesamiento de Audio**: Transcribe mensajes de voz usando OpenAI Whisper
- **Integración con Whapi**: Conecta con WhatsApp Business API
- **Agente de IA**: Procesa mensajes con un agente de inteligencia artificial
- **Respuestas Inteligentes**: Genera respuestas contextuales y relevantes

## 🛠️ Tecnologías Utilizadas

- **FastAPI**: Framework web para la API
- **OpenAI Whisper**: Transcripción de audio
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
python test_audio_webhook.py
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
│   │   ├── sender.py           # Envío de mensajes
│   │   └── telegram.py         # Integración con Telegram
│   └── main.py                 # Aplicación principal
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🎵 Funcionalidad de Audio

### Procesamiento de Mensajes de Voz

El sistema puede procesar mensajes de voz y audio de WhatsApp:

1. **Recepción**: El webhook recibe mensajes de voz/audio desde Whapi
2. **Detección**: Identifica si es mensaje de voz (`voice`) o audio (`audio`)
3. **Descarga**: Descarga el archivo de audio temporalmente
4. **Transcripción**: Usa OpenAI Whisper para transcribir el audio a texto
5. **Procesamiento**: Envía el texto transcrito al agente de IA
6. **Respuesta**: Genera y envía la respuesta al usuario
7. **Limpieza**: Elimina archivos temporales

### Formatos Soportados

- **Audio**: OGG, MP3, WAV, M4A, FLAC, WEBM
- **Idioma**: Español (configurable)
- **Duración**: Hasta 25MB (límite de Whisper)

## 🔧 Configuración

### Variables de Entorno

```bash
# Requeridas
OPENAI_API_KEY=sk-...
WHAPI_API_KEY=tu_whapi_key

# Opcionales
TELEGRAM_KEY=tu_telegram_bot_token
```

### Configuración del Webhook

El webhook maneja diferentes tipos de mensajes:

- **Texto**: `type: "text"`
- **Voz**: `type: "voice"` (mensajes de voz de WhatsApp)
- **Audio**: `type: "audio"` (archivos de audio)
- **Imagen**: `type: "image"` (no soportado actualmente)

## 🧪 Pruebas

Ejecuta las pruebas del webhook:

```bash
python test_audio_webhook.py
```

## 📝 Logs

El sistema registra logs detallados para:

- Recepción de mensajes
- Procesamiento de audio
- Transcripciones
- Errores y excepciones

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa los logs del servidor
2. Verifica la configuración de las variables de entorno
3. Asegúrate de que FFmpeg esté instalado correctamente
4. Abre un issue en GitHub

## 🔄 Roadmap

- [ ] Soporte para imágenes
- [ ] Soporte para documentos
- [ ] Múltiples idiomas
- [ ] Cache de transcripciones
- [ ] Métricas y analytics
- [ ] Dashboard de administración
