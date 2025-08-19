import requests
import os
import tempfile

WHAPI_API_KEY = os.getenv("WHAPI_API_KEY")

def send_whatsapp_message(phone: str, message: str, channel_id: str):
    url = f"https://gate.whapi.cloud/messages/text"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHAPI_API_KEY}"
    }
    payload = {
        "to": phone,
        "body": message
    }

    response = requests.post(url, headers=headers, json=payload)
    print("Whapi response:", response.status_code, response.text)
    return response.status_code == 200


def send_image_message(phone: str, image_url: str, caption: str, channel_id: str = ""):
    url = f"https://gate.whapi.cloud/messages/image"
    payload = {
        "to": phone,
        "caption": caption,
        "media": image_url
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHAPI_API_KEY}"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print(f"[❌] Error enviando imagen a {phone}: {response.status_code} - {response.text}")
    else:
        print(f"[✅] Imagen enviada a {phone}: {response.json()}")


def download_whapi_audio(media_id: str) -> str:
    """
    Descarga un archivo de audio desde Whapi y retorna la ruta del archivo descargado
    """
    try:
        # Obtener información del archivo
        url = f"https://gate.whapi.cloud/media/{media_id}"
        headers = {
            "Authorization": f"Bearer {WHAPI_API_KEY}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"[❌] Error obteniendo información del audio: {response.status_code} - {response.text}")
            return None
        
        # Crear archivo temporal
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"audio_{media_id}.ogg")
        
        # Descargar el archivo
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        print(f"[✅] Audio descargado: {temp_file}")
        return temp_file
        
    except Exception as e:
        print(f"[❌] Error descargando audio: {e}")
        return None


def download_whapi_audio_from_link(audio_link: str) -> str:
    """
    Descarga un archivo de audio usando el link directo de Whapi
    """
    try:
        print(f"[📥] Descargando audio desde: {audio_link}")
        
        # Crear archivo temporal
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"audio_{os.path.basename(audio_link)}")
        
        # Descargar el archivo directamente desde el link
        response = requests.get(audio_link)
        
        if response.status_code != 200:
            print(f"[❌] Error descargando audio: {response.status_code} - {response.text}")
            return None
        
        # Guardar el archivo
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        print(f"[✅] Audio descargado exitosamente: {temp_file}")
        print(f"[📊] Tamaño del archivo: {len(response.content)} bytes")
        return temp_file
        
    except Exception as e:
        print(f"[❌] Error descargando audio desde link: {e}")
        return None