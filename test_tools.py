#!/usr/bin/env python3
"""
Script para probar las herramientas nombre_cliente y nombre_empresa
"""

from app.core.tools import nombre_cliente, nombre_empresa

def test_tools():
    """Prueba las herramientas directamente"""
    print("🧪 Probando herramienta nombre_cliente...")
    
    # Probar búsqueda de cliente específico
    print("\n1. Buscando cliente 'johan':")
    try:
        resultado = nombre_cliente.invoke({"nombre": "johan"})
        print(f"✅ Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar búsqueda de todos los clientes
    print("\n2. Buscando todos los clientes:")
    try:
        resultado = nombre_cliente.invoke({"nombre": ""})
        print(f"✅ Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("🧪 Probando herramienta nombre_empresa...")
    
    # Probar búsqueda de empresa específica
    print("\n3. Buscando empresa 'SAS':")
    try:
        resultado = nombre_empresa.invoke({"nombre": "SAS"})
        print(f"✅ Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Probar búsqueda de todas las empresas
    print("\n4. Buscando todas las empresas:")
    try:
        resultado = nombre_empresa.invoke({"nombre": ""})
        print(f"✅ Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    test_tools() 