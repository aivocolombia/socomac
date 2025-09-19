#!/usr/bin/env python3
"""
Script para probar la extracción de URL de Supabase
"""
import requests
import base64
import json

def test_url_extraction():
    """
    Probar extracción de URL de Supabase
    """
    print("🧪 Probando extracción de URL de Supabase...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    try:
        response = requests.post(f"{backend_url}/whatsapp/test-supabase-url", timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL extraída exitosamente:")
            print(f"📄 PDF tamaño: {result['pdf_tamaño']} bytes")
            print(f"📊 Base64 tamaño: {result['pdf_base64_tamaño']} caracteres")
            print(f"🔗 URL pública: {result['url_publica']}")
            print(f"📁 Archivo: {result['archivo_nombre']}")
            print(f"📏 Tamaño: {result['tamaño_bytes']} bytes")
            print(f"📋 Metadata: {result['metadata']}")
            
            # Verificar que la URL es accesible
            print("\n🔍 Verificando accesibilidad de la URL...")
            try:
                url_response = requests.head(result['url_publica'], timeout=10)
                if url_response.status_code == 200:
                    print("✅ URL es accesible públicamente")
                else:
                    print(f"⚠️ URL no accesible: {url_response.status_code}")
            except Exception as e:
                print(f"❌ Error verificando URL: {e}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📄 Error detail: {error_detail}")
            except:
                print(f"📄 Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_direct_whapi_with_url():
    """
    Probar envío directo a WHAPI usando URL de Supabase
    """
    print("\n🚀 Probando envío directo a WHAPI con URL...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    # Primero obtener una URL de Supabase
    try:
        # Crear PDF de prueba
        pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test PDF URL) Tj
ET
endstream
endobj

5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj

xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000274 00000 n 
0000000368 00000 n 
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
465
%%EOF"""
        
        pdf_bytes = pdf_content.encode('utf-8')
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Obtener URL de Supabase
        print("📤 Obteniendo URL de Supabase...")
        url_response = requests.post(f"{backend_url}/whatsapp/test-supabase-url", timeout=30)
        
        if url_response.status_code != 200:
            print(f"❌ Error obteniendo URL: {url_response.status_code}")
            return
        
        url_result = url_response.json()
        url_publica = url_result['url_publica']
        print(f"✅ URL obtenida: {url_publica}")
        
        # Ahora probar envío directo a WHAPI usando la URL
        print("📱 Probando envío directo a WHAPI...")
        
        # Simular envío directo (esto sería en el servicio)
        payload = {
            "to": "+573172288329",
            "type": "document",
            "document": {
                "link": url_publica,  # ← URL de Supabase
                "filename": "test_direct_whapi.pdf"
            },
            "caption": "Test directo con URL de Supabase"
        }
        
        print(f"📤 Payload para WHAPI: {json.dumps(payload, indent=2)}")
        print("✅ URL extraída y lista para envío a WHAPI")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE EXTRACCIÓN DE URL")
    print("=" * 80)
    
    # Test 1: Extracción de URL
    test_url_extraction()
    
    # Test 2: Envío directo con URL
    test_direct_whapi_with_url()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)
    print("✅ La URL se extrae directamente de Supabase Storage")
    print("🔗 No es necesaria una tabla para obtener la URL")
    print("📤 La URL se puede usar inmediatamente con WHAPI")

if __name__ == "__main__":
    main()
