#!/usr/bin/env python3
"""
Script de prueba completo para debugging del endpoint de PDF
"""
import requests
import base64
import json
import time

def test_formateo_telefono():
    """
    Probar formateo de teléfono
    """
    print("🧪 Probando formateo de teléfono...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    telefonos_prueba = [
        "573172288329",
        "+573172288329", 
        "3172288329",
        "3172288329",
        "573172288329",
        "573172288329",
        "573172288329"
    ]
    
    for telefono in telefonos_prueba:
        try:
            response = requests.post(
                f"{backend_url}/whatsapp/test-telefono",
                json={"telefono": telefono},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                status = "✅" if result.get("valido") else "❌"
                print(f"{status} {telefono} -> {result.get('formateado', 'ERROR')}")
            else:
                print(f"❌ {telefono} -> Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {telefono} -> Error: {e}")

def test_pdf_endpoint():
    """
    Probar endpoint de PDF
    """
    print("\n🧪 Probando endpoint de PDF...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    try:
        # Test 1: Crear PDF de prueba
        print("📄 Creando PDF de prueba...")
        response = requests.post(f"{backend_url}/whatsapp/test-pdf", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PDF creado: {result['tamaño_bytes']} bytes")
            print(f"📊 Base64: {result['tamaño_base64']} caracteres")
            print(f"📄 Header: {result['header']}")
            print(f"✅ Validación: {result['validacion']['valido']}")
        else:
            print(f"❌ Error creando PDF: {response.status_code}")
            return
        
        # Test 2: Prueba completa
        print("\n🔍 Ejecutando prueba completa...")
        response = requests.post(f"{backend_url}/whatsapp/test-pdf-completo", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prueba completa exitosa")
            print(f"📱 Teléfono: {result['telefono_original']} -> {result['telefono_formateado']}")
            print(f"📄 PDF válido: {result['pdf_validacion']['valido']}")
            print(f"💬 Mensaje: {result['mensaje_generado'][:100]}...")
        else:
            print(f"❌ Error en prueba completa: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_debug_config():
    """
    Probar configuración de debug
    """
    print("\n🔍 Probando configuración de debug...")
    print("=" * 60)
    
    backend_url = "https://socomac.onrender.com"
    
    try:
        response = requests.get(f"{backend_url}/whatsapp/debug-config", timeout=10)
        
        if response.status_code == 200:
            config = response.json()
            print("✅ Configuración obtenida:")
            print(f"🌐 Base URL: {config['config']['whapi_base_url']}")
            print(f"🔑 Token configurado: {config['config']['whapi_token_configurado']}")
            print(f"🔑 Token preview: {config['config']['whapi_token_preview']}")
            print(f"🌐 URLs generadas:")
            for key, url in config['config']['urls_generadas'].items():
                print(f"   {key}: {url}")
        else:
            print(f"❌ Error obteniendo configuración: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_envio_real():
    """
    Probar envío real de PDF
    """
    print("\n🚀 Probando envío real de PDF...")
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
    
    pdf_bytes = pdf_content.encode('utf-8')
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    
    payload = {
        "numero_telefono": "573172288329",  # Sin +57
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
    
    try:
        print(f"📱 Enviando a: {payload['numero_telefono']}")
        print(f"📄 Archivo: {payload['nombre_archivo']}")
        print(f"📊 PDF: {len(pdf_bytes)} bytes")
        
        response = requests.post(
            f"{backend_url}/whatsapp/enviar-pdf",
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ¡PDF enviado exitosamente!")
            print(f"📱 Teléfono: {result['numero_telefono']}")
            print(f"📄 Archivo: {result['archivo']}")
            print(f"📏 Tamaño: {result['tamaño_mb']}MB")
            print(f"📨 Respuesta WHAPI: {result.get('whapi_response', {})}")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"📄 Error detail: {error_detail}")
            except:
                print(f"📄 Error text: {response.text}")
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 INICIANDO PRUEBAS DE DEBUGGING COMPLETO")
    print("=" * 80)
    
    # Test 1: Configuración
    test_debug_config()
    
    # Test 2: Formateo de teléfono
    test_formateo_telefono()
    
    # Test 3: PDF endpoint
    test_pdf_endpoint()
    
    # Test 4: Envío real (opcional)
    print("\n" + "=" * 80)
    print("🤔 ¿Quieres probar el envío real? (s/n)")
    print("=" * 80)
    
    # Para testing automático, comentar esta línea
    # test_envio_real()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)
    print("✅ Revisa los logs en Render para más detalles")
    print("🔍 Usa los endpoints de debug para troubleshooting")

if __name__ == "__main__":
    main()
