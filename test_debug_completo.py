#!/usr/bin/env python3
"""
Script para probar la configuración completa
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def probar_configuracion():
    """
    Probar configuración completa
    """
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN COMPLETA")
    print("=" * 80)
    
    # Variables requeridas
    variables = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'WHAPI_TOKEN': os.getenv('WHAPI_TOKEN'),
        'WHAPI_BASE_URL': os.getenv('WHAPI_BASE_URL')
    }
    
    print("📋 Variables de entorno:")
    for var, value in variables.items():
        if value:
            preview = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {preview}")
        else:
            print(f"❌ {var}: No configurado")
    
    print("\n" + "=" * 60)
    
    # Probar servicios
    try:
        print("🧪 Probando servicios...")
        
        # Probar WhatsApp Service
        from app.services.whatsapp_service import WhatsAppService
        whatsapp_service = WhatsAppService()
        print(f"✅ WhatsApp Service: {whatsapp_service.base_url}")
        
        # Probar Supabase Service
        from app.services.supabase_storage import SupabaseStorageService
        supabase_service = SupabaseStorageService()
        print(f"✅ Supabase Service: {supabase_service.bucket_name}")
        
        # Probar bucket
        if supabase_service.verificar_bucket_existe():
            print("✅ Bucket 'receipt' accesible")
        else:
            print("❌ Bucket 'receipt' no accesible")
        
        # Probar WhatsApp Supabase Service
        from app.services.whatsapp_supabase_service import WhatsAppSupabaseService
        whatsapp_supabase_service = WhatsAppSupabaseService()
        print("✅ WhatsApp Supabase Service creado")
        
    except Exception as e:
        print(f"❌ Error creando servicios: {e}")
    
    print("\n" + "=" * 80)
    print("📊 VERIFICACIÓN COMPLETADA")
    print("=" * 80)

def probar_endpoint_debug():
    """
    Probar endpoint de debug
    """
    print("\n🧪 Probando endpoint de debug...")
    print("=" * 60)
    
    try:
        import requests
        
        # URL del endpoint de debug
        debug_url = "https://socomac.onrender.com/whatsapp/debug-config"
        
        print(f"🔗 Llamando a: {debug_url}")
        
        response = requests.get(debug_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint de debug funcionando")
            print(f"📊 Respuesta: {data}")
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA COMPLETA DE CONFIGURACIÓN")
    print("=" * 80)
    
    # Verificar configuración local
    probar_configuracion()
    
    # Probar endpoint remoto
    probar_endpoint_debug()
    
    print("\n" + "=" * 80)
    print("📊 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
