#!/usr/bin/env python3
"""
Script para probar la conexión completa del sistema WhatsApp
"""
import requests
import json
import time
from datetime import datetime

# Configuración
BACKEND_URL = "https://tu-backend-render.onrender.com"  # Reemplaza con tu URL real
FRONTEND_URL = "https://tu-app-vercel.vercel.app"  # Reemplaza con tu URL real

def test_backend_health():
    """Test 1: Verificar que el backend esté funcionando"""
    print("🔍 Test 1: Verificando salud del backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend funcionando correctamente")
            print(f"   Versión: {data.get('version')}")
            print(f"   Endpoints: {data.get('endpoints')}")
            return True
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_whatsapp_status():
    """Test 2: Verificar estado de WhatsApp"""
    print("\n🔍 Test 2: Verificando estado de WhatsApp...")
    try:
        response = requests.get(f"{BACKEND_URL}/whatsapp/status", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print("✅ WhatsApp conectado correctamente")
                return True
            else:
                print(f"❌ WhatsApp no conectado: {data.get('message')}")
                return False
        else:
            print(f"❌ Error verificando WhatsApp: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error verificando WhatsApp: {e}")
        return False

def test_send_message(numero_prueba="573001234567"):
    """Test 3: Probar envío de mensaje"""
    print(f"\n🔍 Test 3: Probando envío de mensaje a {numero_prueba}...")
    
    payload = {
        "numero_telefono": numero_prueba,
        "mensaje": f"🧪 Mensaje de prueba - {datetime.now().strftime('%H:%M:%S')}"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/whatsapp/enviar-mensaje",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Mensaje enviado correctamente")
            print(f"   Message ID: {data.get('data', {}).get('message_id')}")
            return True
        else:
            error_data = response.json()
            print(f"❌ Error enviando mensaje: {error_data.get('detail', 'Error desconocido')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error enviando mensaje: {e}")
        return False

def test_cors_headers():
    """Test 4: Verificar headers CORS"""
    print("\n🔍 Test 4: Verificando headers CORS...")
    try:
        # Simular petición desde el frontend
        headers = {
            "Origin": FRONTEND_URL,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = requests.options(f"{BACKEND_URL}/whatsapp/enviar-mensaje", headers=headers)
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
        }
        
        print("📋 Headers CORS encontrados:")
        for header, value in cors_headers.items():
            if value:
                print(f"   ✅ {header}: {value}")
            else:
                print(f"   ❌ {header}: No encontrado")
        
        return bool(cors_headers["Access-Control-Allow-Origin"])
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error verificando CORS: {e}")
        return False

def test_frontend_connection():
    """Test 5: Simular conexión desde frontend"""
    print("\n🔍 Test 5: Simulando conexión desde frontend...")
    
    # Simular la petición que haría tu frontend
    payload = {
        "numero_telefono": "573001234567",
        "mensaje": "Recibo listo"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": FRONTEND_URL
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/whatsapp/recibo-listo",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Conexión frontend-backend exitosa")
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Error en conexión frontend: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en conexión frontend: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 Iniciando tests de conexión WhatsApp...")
    print(f"📡 Backend: {BACKEND_URL}")
    print(f"🌐 Frontend: {FRONTEND_URL}")
    print("=" * 60)
    
    tests = [
        ("Salud del Backend", test_backend_health),
        ("Estado de WhatsApp", test_whatsapp_status),
        ("Envío de Mensaje", test_send_message),
        ("Headers CORS", test_cors_headers),
        ("Conexión Frontend", test_frontend_connection)
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error ejecutando {nombre}: {e}")
            resultados.append((nombre, False))
        
        time.sleep(1)  # Pausa entre tests
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS:")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Tests exitosos: {exitosos}/{len(resultados)}")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todos los tests pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisa la configuración.")
    
    return exitosos == len(resultados)

if __name__ == "__main__":
    main()
