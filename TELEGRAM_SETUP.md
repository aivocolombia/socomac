
### Estructura de Datos

El webhook ahora maneja la siguiente estructura de datos de Telegram:

```json
{
  "message": {
    "from": {
      "id": 123456789
    },
    "text": "Mensaje de texto opcional",
    "photo": [
      {
        "file_id": "id_del_archivo",
        "file_unique_id": "id_unico",
        "width": 800,
        "height": 600,
        "file_size": 102400
      }
    ],
    "audio": {
      "file_id": "id_del_audio",
      "file_unique_id": "id_unico_audio",
      "duration": 30,
      "file_name": "cancion.mp3",
      "mime_type": "audio/mpeg",
      "file_size": 512000
    },
    "voice": {
      "file_id": "id_del_voice",
      "file_unique_id": "id_unico_voice",
      "duration": 15,
      "mime_type": "audio/ogg",
      "file_size": 256000
    }
  }
}
```
## Logging

La aplicación incluye logging detallado para debugging:

- Información sobre el tipo de contenido recibido
- Detalles de archivos (IDs, tamaños, duración)
- Respuestas del agente
- Errores de procesamiento

## Funciones Adicionales

### Descarga de Archivos

El servicio de Telegram incluye funciones para:
- Obtener información de archivos
- Descargar archivos de Telegram

```python
from app.services.telegram import get_file_info, download_file

# Obtener información de un archivo
file_info = get_file_info("file_id")

# Descargar un archivo
file_content = download_file("file_id", "ruta_guardado.jpg")
```

## Próximas Mejoras

- [ ] Soporte para videos
- [ ] Soporte para documentos
- [ ] Análisis de contenido de imágenes con IA
- [ ] Transcripción de audios y mensajes de voz
- [ ] Respuestas más contextuales basadas en el contenido multimedia 