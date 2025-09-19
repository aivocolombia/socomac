#!/usr/bin/env python3
"""
Script para probar los endpoints corregidos
"""
import requests
import json

def probar_status():
    """
    Probar endpoint de status
    """
    print("🔍 Probando endpoint de status...")
    print("=" * 60)
    
    url = "https://socomac.onrender.com/whatsapp/status"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Status funcionando")
            print(f"📨 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ Error en status")
            print(f"📄 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_mensaje():
    """
    Probar envío de mensaje
    """
    print("\n📱 Probando envío de mensaje...")
    print("=" * 60)
    
    url = "https://socomac.onrender.com/whatsapp/enviar-mensaje"
    payload = {
        "numero_telefono": "+573172288329",
        "mensaje": "🧪 Prueba de WhatsApp corregido desde Postman"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Mensaje enviado exitosamente")
            print(f"📨 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ Error enviando mensaje")
            print(f"📄 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_debug_config():
    """
    Probar configuración de debug
    """
    print("\n🔧 Probando configuración de debug...")
    print("=" * 60)
    
    url = "https://socomac.onrender.com/whatsapp/debug-config"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Debug config funcionando")
            print(f"📨 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ Error en debug config")
            print(f"📄 Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA DE ENDPOINTS CORREGIDOS")
    print("=" * 80)
    
    # Probar status
    probar_status()
    
    # Probar mensaje
    probar_mensaje()
    
    # Probar debug config
    probar_debug_config()
    
    print("\n" + "=" * 80)
    print("📊 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
