#!/usr/bin/env python3
"""
Script para probar el envío del PDF fijo que ya existe en Supabase
"""
import requests
import json

def probar_pdf_fijo():
    """
    Probar envío del PDF fijo
    """
    print("🧪 PROBANDO PDF FIJO DE SUPABASE")
    print("=" * 60)
    
    # URL del endpoint
    url = "https://socomac.onrender.com/whatsapp/test-pdf-fijo"
    
    print(f"🔗 Llamando a: {url}")
    
    try:
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Respuesta exitosa:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_debug_config():
    """
    Probar configuración de debug
    """
    print("\n🔍 PROBANDO CONFIGURACIÓN DE DEBUG")
    print("=" * 60)
    
    url = "https://socomac.onrender.com/whatsapp/debug-config"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Configuración obtenida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA DE PDF FIJO")
    print("=" * 80)
    
    # Probar configuración
    probar_debug_config()
    
    # Probar PDF fijo
    probar_pdf_fijo()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
