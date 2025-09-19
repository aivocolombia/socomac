#!/usr/bin/env python3
"""
Script para probar el endpoint de envío de PDF
"""
import requests
import base64
import json
import os

def crear_pdf_prueba():
    """
    Crear un PDF de prueba mínimo
    """
    # PDF mínimo válido
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
(Test PDF) Tj
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
    
    return pdf_content.encode('utf-8')

def test_endpoint_pdf():
    """
    Probar el endpoint de envío de PDF
    """
    print("🧪 Probando endpoint de envío de PDF...")
    print("=" * 60)
    
    # Crear PDF de prueba
    pdf_bytes = crear_pdf_prueba()
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    print(f"📄 PDF creado: {len(pdf_bytes)} bytes")
    print(f"📊 Base64: {len(pdf_base64)} caracteres")
    
    # URL del backend (cambiar por tu URL real)
    backend_url = "https://socomac.onrender.com"
    endpoint = f"{backend_url}/whatsapp/enviar-pdf"
    
    # Payload de prueba
    payload = {
        "numero_telefono": "+573172288329",
        "pdf_base64": pdf_base64,
        "nombre_archivo": "test_recibo_123_2025-01-18.pdf",
        "metadata": {
            "numero_recibo": 123,
            "empresa": "SOCOMAC",
            "cliente": "David Cuellar",
            "valor": "10000",
            "concepto": "Mercancia nacional",
            "fecha": "2025-01-18"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"🌐 URL: {endpoint}")
    print(f"📱 Teléfono: {payload['numero_telefono']}")
    print(f"📄 Archivo: {payload['nombre_archivo']}")
    print(f"📋 Metadata: {payload['metadata']}")
    print()
    
    try:
        print("🚀 Enviando solicitud...")
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📨 Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"📄 Response JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
        except:
            print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ ¡ÉXITO! PDF enviado correctamente")
        else:
            print("❌ Error en la respuesta")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_debug_config():
    """
    Probar el endpoint de debug de configuración
    """
    print("\n🔍 Probando endpoint de debug...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    endpoint = f"{backend_url}/whatsapp/debug-config"
    
    try:
        response = requests.get(endpoint, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Configuración obtenida:")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_whapi_connection():
    """
    Probar la conexión directa con WHAPI
    """
    print("\n🌐 Probando conexión directa con WHAPI...")
    print("=" * 60)
    
    token = os.getenv('WHAPI_TOKEN')
    if not token:
        print("❌ WHAPI_TOKEN no configurado")
        return
    
    base_url = "https://gate.whapi.cloud"
    url = f"{base_url}/status"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Conexión con WHAPI exitosa")
        else:
            print("❌ Error en la conexión con WHAPI")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DEL ENDPOINT DE PDF")
    print("=" * 60)
    
    # Test 1: Debug config
    test_debug_config()
    
    # Test 2: Conexión WHAPI
    test_whapi_connection()
    
    # Test 3: Endpoint PDF
    test_endpoint_pdf()
    
    print("\n" + "=" * 60)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    main()