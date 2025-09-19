#!/usr/bin/env python3
"""
Script para probar el envío del PDF específico de Supabase
"""
import requests
import json

def probar_pdf_prueba():
    """
    Probar el endpoint de PDF de prueba
    """
    print("🧪 PRUEBA: Enviando PDF específico de Supabase")
    print("=" * 80)
    
    # URL del endpoint
    url = "https://socomac.onrender.com/whatsapp/enviar-pdf-prueba"
    
    # Datos de prueba
    payload = {
        "numero_telefono": "+573172288329",  # Tu número de prueba
        "pdf_base64": "dummy",  # No se usa en este endpoint
        "nombre_archivo": "test.pdf",  # No se usa en este endpoint
        "metadata": {
            "test": True,
            "empresa": "SOCOMAC",
            "tipo": "recibo_prueba"
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"🔗 URL: {url}")
    print(f"📱 Teléfono: {payload['numero_telefono']}")
    print(f"📄 PDF: Recibo_Caja_81_2025-09-18.pdf")
    print(f"🔗 URL Supabase: https://rixvqufnzasolxxklaue.supabase.co/storage/v1/object/public/receipt/Recibo_Caja_81_2025-09-18.pdf")
    
    try:
        print("\n🚀 Enviando solicitud...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ÉXITO!")
            print(f"📨 Respuesta: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print("❌ ERROR!")
            print(f"📄 Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La solicitud tardó demasiado")
    except requests.exceptions.ConnectionError:
        print("🔌 Error de conexión")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")
    
    print("\n" + "=" * 80)
    print("📊 PRUEBA COMPLETADA")
    print("=" * 80)

def verificar_pdf_supabase():
    """
    Verificar que el PDF existe en Supabase
    """
    print("\n🔍 Verificando PDF en Supabase...")
    print("=" * 60)
    
    pdf_url = "https://rixvqufnzasolxxklaue.supabase.co/storage/v1/object/public/receipt/Recibo_Caja_81_2025-09-18.pdf"
    
    try:
        response = requests.head(pdf_url, timeout=10)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ PDF accesible en Supabase")
            print(f"📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"📏 Content-Length: {response.headers.get('content-length', 'N/A')} bytes")
        else:
            print("❌ PDF no accesible")
            
    except Exception as e:
        print(f"❌ Error verificando PDF: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA COMPLETA DE PDF DE SUPABASE")
    print("=" * 80)
    
    # Verificar que el PDF existe
    verificar_pdf_supabase()
    
    # Probar envío
    probar_pdf_prueba()
    
    print("\n" + "=" * 80)
    print("📊 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
