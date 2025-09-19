#!/usr/bin/env python3
"""
Script para probar WHAPI directamente
"""
import requests
import json

def probar_whapi_directo():
    """
    Probar WHAPI directamente
    """
    print("🧪 PROBANDO WHAPI DIRECTO")
    print("=" * 60)
    
    # Configuración WHAPI
    whapi_url = "https://gate.whapi.cloud/messages/document"
    whapi_token = "7IX1zKt6zN..."  # Token real del servidor
    
    # Datos del PDF
    pdf_url = "https://rixvqufnzasolxxklaue.supabase.co/storage/v1/object/public/receipt/Recibo_Caja_81_2025-09-18.pdf"
    numero_telefono = "+573172288329"
    
    # Payload según documentación WHAPI
    payload = {
        "to": numero_telefono,
        "type": "document",
        "document": {
            "link": pdf_url,
            "filename": "Recibo_Caja_81_2025-09-18.pdf",
            "caption": "📄 Recibo de Caja SOCOMAC\n\nArchivo: Recibo_Caja_81_2025-09-18.pdf",
            "mime_type": "application/pdf"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {whapi_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔗 URL: {whapi_url}")
    print(f"📄 PDF: {pdf_url}")
    print(f"📱 Teléfono: {numero_telefono}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(whapi_url, headers=headers, json=payload, timeout=30)
        
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ PDF enviado exitosamente")
        else:
            print(f"❌ Error HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_status_whapi():
    """
    Probar status de WHAPI
    """
    print("\n🔍 PROBANDO STATUS WHAPI")
    print("=" * 60)
    
    whapi_url = "https://gate.whapi.cloud/status"
    whapi_token = "7IX1zKt6zN..."  # Token real del servidor
    
    headers = {
        "Authorization": f"Bearer {whapi_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(whapi_url, headers=headers, timeout=30)
        print(f"📊 Status: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA DE WHAPI DIRECTO")
    print("=" * 80)
    
    # Probar status
    probar_status_whapi()
    
    # Probar envío
    probar_whapi_directo()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
