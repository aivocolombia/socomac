#!/usr/bin/env python3
"""
Script para debuggear la URL de WHAPI
"""
import os

def debug_whapi_url():
    """
    Debuggear la configuración de URL de WHAPI
    """
    print("🔍 Debugging URL de WHAPI...")
    print("=" * 50)
    
    # Simular la configuración del servicio
    base_url = os.getenv('WHAPI_BASE_URL', 'https://gate.whapi.cloud')
    
    print(f"📋 WHAPI_BASE_URL: {base_url}")
    print(f"📏 Longitud: {len(base_url)}")
    print(f"🔚 Termina con '/': {base_url.endswith('/')}")
    
    # Probar diferentes combinaciones
    print("\n🧪 Probando diferentes URLs:")
    
    # URL original
    url1 = f"{base_url}/messages"
    print(f"1. {base_url}/messages = {url1}")
    
    # URL con rstrip
    base_url_limpia = base_url.rstrip('/')
    url2 = f"{base_url_limpia}/messages"
    print(f"2. {base_url_limpia}/messages = {url2}")
    
    # URL con doble slash (problema)
    url3 = f"{base_url}//messages"
    print(f"3. {base_url}//messages = {url3}")
    
    # Verificar si hay doble slash
    if '//' in url1:
        print("❌ PROBLEMA: URL contiene doble slash")
    else:
        print("✅ URL correcta")
    
    print("\n📊 URLs de prueba:")
    urls_prueba = [
        "https://gate.whapi.cloud/messages",
        "https://gate.whapi.cloud//messages",
        "https://gate.whapi.cloud/messages/",
        "https://gate.whapi.cloud//messages/"
    ]
    
    for i, url in enumerate(urls_prueba, 1):
        print(f"{i}. {url}")
        if '//' in url:
            print("   ❌ Contiene doble slash")
        else:
            print("   ✅ URL correcta")
    
    print("\n🔧 Solución recomendada:")
    print("base_url = self.base_url.rstrip('/')")
    print("url = f'{base_url}/messages'")
    
    return base_url_limpia

def probar_conexion_whapi():
    """
    Probar conexión directa a WHAPI
    """
    import requests
    
    print("\n🌐 Probando conexión a WHAPI...")
    
    # URLs a probar
    urls = [
        "https://gate.whapi.cloud/messages",
        "https://gate.whapi.cloud/status",
        "https://gate.whapi.cloud/"
    ]
    
    for url in urls:
        try:
            print(f"📡 Probando: {url}")
            response = requests.get(url, timeout=5)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado: {e}")

def main():
    """
    Ejecutar debug completo
    """
    print("🚀 Iniciando debug de URL de WHAPI...")
    print("=" * 60)
    
    # Debug de URL
    base_url_limpia = debug_whapi_url()
    
    # Probar conexión
    probar_conexion_whapi()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print("=" * 60)
    print("✅ Usar: base_url.rstrip('/') + '/messages'")
    print("❌ Evitar: base_url + '/messages' (puede crear doble slash)")
    print("🔧 Verificar: que WHAPI_BASE_URL no termine con '/'")
    
    return base_url_limpia

if __name__ == "__main__":
    main()
