import requests
import os

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