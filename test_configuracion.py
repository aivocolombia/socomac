#!/usr/bin/env python3
"""
Script para verificar la configuración de Supabase
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def verificar_configuracion():
    """
    Verificar configuración de Supabase
    """
    print("🔍 Verificando configuración de Supabase...")
    print("=" * 60)
    
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
            # Mostrar solo los primeros 10 caracteres por seguridad
            preview = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {preview}")
        else:
            print(f"❌ {var}: No configurado")
    
    print("\n" + "=" * 60)
    
    # Verificar Supabase
    if variables['SUPABASE_URL'] and variables['SUPABASE_KEY']:
        print("✅ Supabase configurado correctamente")
        try:
            from app.services.supabase_storage import SupabaseStorageService
            service = SupabaseStorageService()
            print("✅ Servicio Supabase Storage creado exitosamente")
        except Exception as e:
            print(f"❌ Error creando servicio Supabase: {e}")
    else:
        print("❌ Supabase no configurado")
        print("💡 Configura SUPABASE_URL y SUPABASE_KEY en tu archivo .env")
    
    # Verificar WHAPI
    if variables['WHAPI_TOKEN'] and variables['WHAPI_BASE_URL']:
        print("✅ WHAPI configurado correctamente")
    else:
        print("❌ WHAPI no configurado")
        print("💡 Configura WHAPI_TOKEN y WHAPI_BASE_URL en tu archivo .env")
    
    print("\n" + "=" * 60)
    print("📝 Variables requeridas:")
    print("SUPABASE_URL=https://tu-proyecto.supabase.co")
    print("SUPABASE_KEY=tu_supabase_key_aqui")
    print("WHAPI_TOKEN=tu_token_whapi_aqui")
    print("WHAPI_BASE_URL=https://gate.whapi.cloud")

def probar_conexion_supabase():
    """
    Probar conexión con Supabase
    """
    print("\n🧪 Probando conexión con Supabase...")
    print("=" * 60)
    
    try:
        from app.services.supabase_storage import SupabaseStorageService
        service = SupabaseStorageService()
        
        # Probar listar archivos
        resultado = service.listar_archivos(limite=5)
        print(f"📋 Resultado: {resultado}")
        
        if resultado.get("status") == "success":
            print("✅ Conexión con Supabase exitosa")
        else:
            print("❌ Error en conexión con Supabase")
            
    except Exception as e:
        print(f"❌ Error probando Supabase: {e}")

def main():
    """
    Ejecutar todas las verificaciones
    """
    print("🚀 VERIFICACIÓN DE CONFIGURACIÓN")
    print("=" * 80)
    
    verificar_configuracion()
    
    # Solo probar conexión si está configurado
    if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY'):
        probar_conexion_supabase()
    
    print("\n" + "=" * 80)
    print("📊 VERIFICACIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()
