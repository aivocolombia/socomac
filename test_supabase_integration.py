#!/usr/bin/env python3
"""
Script para probar la integración con Supabase Storage
"""
import requests
import base64
import json
import time

def test_supabase_endpoint():
    """
    Probar endpoint de Supabase
    """
    print("🧪 Probando endpoint con Supabase Storage...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
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
(Test PDF Supabase) Tj
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
    
    payload = {
        "numero_telefono": "573172288329",  # Sin +57
        "pdf_base64": pdf_base64,
        "nombre_archivo": "test_supabase_123_2025-01-18.pdf",
        "metadata": {
            "numero_recibo": 123,
            "empresa": "SOCOMAC",
            "cliente": "David Cuellar",
            "valor": "10000",
            "concepto": "Mercancia nacional",
            "fecha": "2025-01-18",
            "metodo": "supabase_storage"
        }
    }
    
    try:
        print(f"📱 Enviando a: {payload['numero_telefono']}")
        print(f"📄 Archivo: {payload['nombre_archivo']}")
        print(f"📊 PDF: {len(pdf_bytes)} bytes")
        print(f"📋 Metadata: {payload['metadata']}")
        
        response = requests.post(
            f"{backend_url}/whatsapp/enviar-pdf-supabase",
            json=payload,
            timeout=60  # Más tiempo para Supabase + WHAPI
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ¡PDF enviado exitosamente con Supabase!")
            print(f"📱 Teléfono: {result['numero_telefono']}")
            print(f"📄 Archivo: {result['archivo']}")
            print(f"📏 Tamaño: {result['tamaño_mb']}MB")
            print(f"🔗 URL Supabase: {result.get('url_supabase', 'N/A')}")
            print(f"📤 Supabase result: {result.get('supabase_result', {})}")
            print(f"📨 WhatsApp result: {result.get('whatsapp_result', {})}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📄 Error detail: {error_detail}")
            except:
                print(f"📄 Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def test_listar_documentos():
    """
    Probar listado de documentos
    """
    print("\n📋 Probando listado de documentos...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    try:
        response = requests.get(f"{backend_url}/whatsapp/documentos-supabase?limite=10", timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Documentos listados:")
            print(f"📊 Total: {result.get('total', 0)}")
            print(f"📄 Archivos: {result.get('archivos', [])}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_configuracion():
    """
    Probar configuración
    """
    print("\n🔍 Probando configuración...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    try:
        response = requests.get(f"{backend_url}/whatsapp/debug-config", timeout=10)
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Configuración obtenida:")
            print(f"🌐 Base URL: {config['config']['whapi_base_url']}")
            print(f"🔑 Token: {config['config']['whapi_token_configurado']}")
            print(f"🌐 URLs: {config['config']['urls_generadas']}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE SUPABASE STORAGE")
    print("=" * 80)
    
    # Test 1: Configuración
    test_configuracion()
    
    # Test 2: Listar documentos
    test_listar_documentos()
    
    # Test 3: Envío con Supabase
    print("\n" + "=" * 80)
    print("🤔 ¿Quieres probar el envío con Supabase? (s/n)")
    print("=" * 80)
    
    # Para testing automático, descomenta esta línea:
    # test_supabase_endpoint()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)
    print("✅ Revisa los logs en Render para más detalles")
    print("🔍 El método Supabase usa: Storage + URL + WHAPI")

if __name__ == "__main__":
    main()
