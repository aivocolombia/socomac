#!/usr/bin/env python3
"""
Script para probar el acceso al bucket 'receipt' de Supabase
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def probar_bucket_receipt():
    """
    Probar acceso al bucket 'receipt'
    """
    print("🧪 Probando acceso al bucket 'receipt'...")
    print("=" * 60)
    
    try:
        from app.services.supabase_storage import SupabaseStorageService
        
        # Crear servicio
        service = SupabaseStorageService()
        print(f"✅ Servicio creado con bucket: {service.bucket_name}")
        
        # Verificar bucket
        if service.verificar_bucket_existe():
            print("✅ Bucket 'receipt' accesible")
            
            # Listar archivos existentes
            print("\n📋 Listando archivos en el bucket...")
            resultado = service.listar_archivos(limite=5)
            
            if resultado.get("status") == "success":
                archivos = resultado.get("archivos", [])
                print(f"📁 Total de archivos: {len(archivos)}")
                
                for archivo in archivos[:3]:  # Mostrar solo los primeros 3
                    print(f"  - {archivo.get('name', 'N/A')}")
            else:
                print(f"❌ Error listando archivos: {resultado.get('error')}")
                
        else:
            print("❌ No se pudo acceder al bucket 'receipt'")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def probar_subida_pdf():
    """
    Probar subida de un PDF de prueba
    """
    print("\n🧪 Probando subida de PDF...")
    print("=" * 60)
    
    try:
        from app.services.supabase_storage import SupabaseStorageService
        
        # Crear servicio
        service = SupabaseStorageService()
        
        # Crear PDF de prueba (muy simple)
        pdf_base64 = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCjIgMCBvYmoKPDwKL1R5cGUgL1BhZ2VzCi9LaWRzIFszIDAgUl0KL0NvdW50IDEKPD4KZW5kb2JqCjMgMCBvYmoKPDwKL1R5cGUgL1BhZ2UKL1BhcmVudCAyIDAgUgovTWVkaWFCb3ggWzAgMCA2MTIgNzkyXQovUmVzb3VyY2VzIDw8Ci9Gb250IDw8Ci9GMSA0IDAgUgo+Pgo+PgovQ29udGVudHMgNSAwIFIKPj4KZW5kb2JqCjQgMCBvYmoKPDwKL1R5cGUgL0ZvbnQKL1N1YnR5cGUgL1R5cGUxCi9CYXNlRm9udCAvSGVsdmV0aWNhCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9MZW5ndGggNDQKPj4Kc3RyZWFtCkJUCi9GMSAxMiBUZgoyNTAgNzAwIFRkCihUZXN0IFBERikgVGoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYKMDAwMDAwMDAwOSAwMDAwMCBuCjAwMDAwMDAwNTggMDAwMDAgbgowMDAwMDAwMTE1IDAwMDAwIG4KMDAwMDAwMDI2NCAwMDAwMCBuCjAwMDAwMDAzNDEgMDAwMDAgbgp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjQzNQolJUVPRgo="
        
        # Metadatos de prueba
        metadata = {
            "test": True,
            "empresa": "SOCOMAC",
            "tipo": "recibo_prueba"
        }
        
        # Subir PDF
        resultado = service.subir_pdf(
            pdf_base64,
            "test_recibo.pdf",
            metadata
        )
        
        if resultado.get("status") == "success":
            print("✅ PDF subido exitosamente")
            print(f"📁 Archivo: {resultado.get('archivo_nombre')}")
            print(f"🔗 URL: {resultado.get('url_publica')}")
            print(f"📊 Tamaño: {resultado.get('tamaño_bytes')} bytes")
        else:
            print(f"❌ Error subiendo PDF: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """
    Ejecutar todas las pruebas
    """
    print("🚀 PRUEBA DE BUCKET SUPABASE")
    print("=" * 80)
    
    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Variables de entorno no configuradas")
        print("💡 Configura SUPABASE_URL y SUPABASE_KEY en tu archivo .env")
        return
    
    print(f"✅ SUPABASE_URL: {supabase_url[:20]}...")
    print(f"✅ SUPABASE_KEY: {supabase_key[:10]}...")
    
    # Probar bucket
    probar_bucket_receipt()
    
    # Probar subida
    probar_subida_pdf()
    
    print("\n" + "=" * 80)
    print("📊 PRUEBAS COMPLETADAS")
    print("=" * 80)

if __name__ == "__main__":
    main()
