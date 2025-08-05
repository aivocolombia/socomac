import requests
import os   
BOT_TOKEN =  os.getenv("TELEGRAM_KEY")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_telegram_message(chat_id: int, text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

   # print(f"[DEBUG] Enviando a chat_id={chat_id} el texto: {texto}")
  #  print(f"[DEBUG] URL: {url}")
   # print(f"[DEBUG] Payload: {payload}")

    response = requests.post(url, json=payload)

    if not response.ok:
        print(f"[ERROR] No se pudo enviar el mensaje a Telegram: {response.text}")
    
    return response.json()
#TODO nuevas 2 funciónes

def get_file_info(file_id: str):
    """
    Obtiene información detallada de un archivo de Telegram
    """
    url = f"{BASE_URL}/getFile"
    payload = {
        "file_id": file_id
    }
    
    response = requests.post(url, json=payload)
    
    if response.ok:
        return response.json()
    else:
        print(f"[ERROR] No se pudo obtener información del archivo: {response.text}")
        return None

def download_file(file_id: str, save_path: str = None):
    """
    Descarga un archivo de Telegram
    """
    file_info = get_file_info(file_id)
    
    if not file_info or not file_info.get("ok"):
        return None
    
    file_path = file_info["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    
    response = requests.get(file_url)
    
    if response.ok:
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        return response.content
    else:
        print(f"[ERROR] No se pudo descargar el archivo: {response.text}")
        return None
