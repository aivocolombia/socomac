#!/usr/bin/env python3
"""
Script para probar endpoints de WHAPI
"""
import requests
import os

def probar_endpoints_whapi():
    """
    Probar diferentes endpoints de WHAPI para encontrar el correcto
    """
    print("🔍 Probando endpoints de WHAPI...")
    print("=" * 60)
    
    # Token de WHAPI (debe estar configurado)
    token = os.getenv('WHAPI_TOKEN')
    if not token:
        print("❌ WHAPI_TOKEN no configurado")
        return
    
    base_url = "https://gate.whapi.cloud"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Endpoints a probar
    endpoints = [
        "/",
        "/status",
        "/messages",
        "/messages/text",
        "/messages/documents",
        "/messages/media",
        "/chats",
        "/contacts",
        "/groups"
    ]
    
    print(f"📡 Base URL: {base_url}")
    print(f"🔑 Token: {token[:10]}...")
    print()
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        print(f"🧪 Probando: {url}")
        
        try:
            # Probar GET
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   GET  - Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ GET funciona")
            elif response.status_code == 404:
                print(f"   ❌ GET - Endpoint no encontrado")
            elif response.status_code == 405:
                print(f"   ⚠️ GET - Método no permitido")
            else:
                print(f"   ⚠️ GET - Status inesperado")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ GET - Error: {e}")
        
        # Probar POST para endpoints de mensajes
        if "messages" in endpoint:
            try:
                test_payload = {
                    "to": "573172288329",
                    "type": "text",
                    "body": "Test message"
                }
                
                response = requests.post(url, headers=headers, json=test_payload, timeout=10)
                print(f"   POST - Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ POST funciona")
                elif response.status_code == 400:
                    print(f"   ⚠️ POST - Bad Request (puede ser normal)")
                elif response.status_code == 404:
                    print(f"   ❌ POST - Endpoint no encontrado")
                else:
                    print(f"   ⚠️ POST - Status inesperado")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ POST - Error: {e}")
        
        print()

def probar_documento_whapi():
    """
    Probar envío de documento con diferentes endpoints
    """
    print("📄 Probando envío de documento...")
    print("=" * 60)
    
    token = os.getenv('WHAPI_TOKEN')
    if not token:
        print("❌ WHAPI_TOKEN no configurado")
        return
    
    base_url = "https://gate.whapi.cloud"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # PDF de prueba (mínimo)
    pdf_base64 = """JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDMgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDYgMCBSCj4+Cj4+Ci9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCi9Db250ZW50cyA3IDAgUgo+PgplbmRvYmoKNiAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjcyIDcyMCBUZAooVGVzdCBQREYpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzUgMCBSXQovQ291bnQgMQo+PgplbmRvYmoKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMyAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL01ldGFkYXRhCi9Qcm9kdWNlciAoUERGKQo+PgplbmRvYmoKeHJlZgowIDgKMDAwMDAwMDAwMCA2NTUzNSBmIAowMDAwMDAwMDA5IDAwMDAwIG4gCjAwMDAwMDAwNzQgMDAwMDAwIG4gCjAwMDAwMDAxMjkgMDAwMDAwIG4gCjAwMDAwMDAyODQgMDAwMDAwIG4gCjAwMDAwMDAzNjkgMDAwMDAwIG4gCjAwMDAwMDA0NjQgMDAwMDAwIG4gCjAwMDAwMDA1NzkgMDAwMDAwIG4gCnRyYWlsZXIKPDwKL1NpemUgOAovUm9vdCAxIDAgUgo+PgpzdGFydHhyZWYKNjc5CiUlRU9G"""
    
    # Endpoints para documentos
    endpoints_documentos = [
        "/messages",
        "/messages/documents",
        "/messages/media",
        "/media/upload"
    ]
    
    for endpoint in endpoints_documentos:
        url = f"{base_url}{endpoint}"
        print(f"🧪 Probando documento en: {url}")
        
        # Payload para documento
        payload = {
            "to": "573172288329",
            "type": "document",
            "document": {
                "filename": "test.pdf",
                "data": pdf_base64,
                "mime_type": "application/pdf"
            },
            "caption": "Test PDF"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"   ✅ ¡ÉXITO! Endpoint correcto encontrado")
                return endpoint
            elif response.status_code == 400:
                print(f"   ⚠️ Bad Request - Puede ser formato incorrecto")
            elif response.status_code == 404:
                print(f"   ❌ Not Found - Endpoint no existe")
            else:
                print(f"   ⚠️ Status inesperado")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    return None

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 Iniciando pruebas de WHAPI...")
    print("=" * 60)
    
    # Test 1: Probar endpoints
    probar_endpoints_whapi()
    
    print("\n" + "=" * 60)
    print("📄 Probando envío de documentos...")
    print("=" * 60)
    
    # Test 2: Probar documentos
    endpoint_correcto = probar_documento_whapi()
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN:")
    print("=" * 60)
    
    if endpoint_correcto:
        print(f"✅ Endpoint correcto encontrado: {endpoint_correcto}")
    else:
        print("❌ No se encontró endpoint correcto para documentos")
        print("💡 Posibles soluciones:")
        print("   1. Verificar token de WHAPI")
        print("   2. Verificar documentación de WHAPI")
        print("   3. Contactar soporte de WHAPI")

if __name__ == "__main__":
    main()
