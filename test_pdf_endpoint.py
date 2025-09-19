#!/usr/bin/env python3
"""
Script para probar el endpoint de envío de PDF
"""
import requests
import base64
import json
from datetime import datetime

# Configuración
BACKEND_URL = "https://tu-backend-render.onrender.com"  # Reemplaza con tu URL real
NUMERO_PRUEBA = "573172288329"  # Reemplaza con tu número de prueba

def crear_pdf_prueba():
    """
    Crear un PDF simple para pruebas
    """
    # PDF mínimo válido en base64
    pdf_base64 = """JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDYgMCBSCj4+Cj4+Ci9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCi9Db250ZW50cyA3IDAgUgo+PgplbmRvYmoKNiAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooVGVzdCBQREYpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzUgMCBSXQovQ291bnQgMQo+PgplbmRvYmoKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL01ldGFkYXRhCi9Qcm9kdWNlciAoUERGKQo+PgplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAwIG4gCjAwMDAwMDAxMjkgMDAwMDAwIG4gCjAwMDAwMDAyODQgMDAwMDAwIG4gCjAwMDAwMDAzNjkgMDAwMDAwIG4gCjAwMDAwMDA0NjQgMDAwMDAwIG4gCjAwMDAwMDA1NzkgMDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgOAovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNjc5CiUlRU9G"""
    
    return pdf_base64

def probar_endpoint_pdf():
    """
    Probar el endpoint de envío de PDF
    """
    print("🧪 Probando endpoint de envío de PDF...")
    
    # Crear PDF de prueba
    pdf_base64 = crear_pdf_prueba()
    
    # Datos de la solicitud
    payload = {
        "numero_telefono": NUMERO_PRUEBA,
        "pdf_base64": pdf_base64,
        "nombre_archivo": f"test_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        "metadata": {
            "numero_recibo": 999,
            "empresa": "SOCOMAC",
            "cliente": "Cliente de Prueba",
            "valor": "50000",
            "concepto": "Prueba de sistema",
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    try:
        print(f"📤 Enviando solicitud a: {BACKEND_URL}/whatsapp/enviar-pdf")
        print(f"📱 Número: {NUMERO_PRUEBA}")
        print(f"📄 Archivo: {payload['nombre_archivo']}")
        print(f"📊 Tamaño PDF: {len(pdf_base64)} caracteres base64")
        
        response = requests.post(
            f"{BACKEND_URL}/whatsapp/enviar-pdf",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            json=payload,
            timeout=30
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF enviado exitosamente!")
            print(f"📱 Número: {result.get('numero_telefono')}")
            print(f"📄 Archivo: {result.get('archivo')}")
            print(f"📊 Tamaño: {result.get('tamaño_mb')}MB")
            print(f"🆔 Message ID: {result.get('whatsapp_response', {}).get('message_id')}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📋 Error details: {error_data}")
            except:
                print(f"📋 Error text: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout: El servidor tardó demasiado en responder")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión: No se pudo conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def probar_estado_backend():
    """
    Probar el estado del backend
    """
    print("🔍 Verificando estado del backend...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend funcionando")
            print(f"📊 Status: {data.get('status')}")
            print(f"📋 Message: {data.get('message')}")
            print(f"🔗 Endpoints: {data.get('endpoints')}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")
        return False

def probar_whatsapp_status():
    """
    Probar el estado de WhatsApp
    """
    print("📱 Verificando estado de WhatsApp...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/whatsapp/status", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WhatsApp status obtenido")
            print(f"📊 Status: {data.get('status')}")
            print(f"📋 Message: {data.get('message')}")
            return True
        else:
            print(f"❌ WhatsApp status error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando WhatsApp: {e}")
        return False

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 Iniciando pruebas del sistema de PDF...")
    print("=" * 60)
    
    # Test 1: Estado del backend
    backend_ok = probar_estado_backend()
    print()
    
    # Test 2: Estado de WhatsApp
    whatsapp_ok = probar_whatsapp_status()
    print()
    
    # Test 3: Envío de PDF
    if backend_ok and whatsapp_ok:
        pdf_ok = probar_endpoint_pdf()
    else:
        print("⚠️ Saltando prueba de PDF - Backend o WhatsApp no disponible")
        pdf_ok = False
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    print(f"🔧 Backend: {'✅ OK' if backend_ok else '❌ FAIL'}")
    print(f"📱 WhatsApp: {'✅ OK' if whatsapp_ok else '❌ FAIL'}")
    print(f"📄 PDF: {'✅ OK' if pdf_ok else '❌ FAIL'}")
    
    if backend_ok and whatsapp_ok and pdf_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa la configuración.")
    
    return backend_ok and whatsapp_ok and pdf_ok

if __name__ == "__main__":
    main()
