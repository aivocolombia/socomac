#!/usr/bin/env python3
"""
Script para probar envío directo del PDF existente
"""
import requests
import json

def probar_pdf_directo():
    """
    Probar envío directo del PDF
    """
    print("🧪 PROBANDO PDF DIRECTO")
    print("=" * 60)
    
    # URL del PDF que ya existe
    pdf_url = "https://rixvqufnzasolxxklaue.supabase.co/storage/v1/object/public/receipt/Recibo_Caja_81_2025-09-18.pdf"
    
    # Datos para enviar
    data = {
        "numero_telefono": "+573172288329",
        "documento_url": pdf_url,
        "nombre_archivo": "Recibo_Caja_81_2025-09-18.pdf",
        "mensaje": "📄 Recibo de Caja SOCOMAC\n\nArchivo: Recibo_Caja_81_2025-09-18.pdf\n\nEste es un recibo de prueba enviado desde el sistema."
    }
    
    # URL del endpoint
    url = "https://socomac.onrender.com/whatsapp/enviar-documento"
    
    print(f"🔗 Llamando a: {url}")
    print(f"📄 PDF: {pdf_url}")
    print(f"📱 Teléfono: {data['numero_telefono']}")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PDF enviado exitosamente:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error HTTP {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar prueba
    """
    print("🚀 PRUEBA DE PDF DIRECTO")
    print("=" * 80)
    
    probar_pdf_directo()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBA COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    main()
