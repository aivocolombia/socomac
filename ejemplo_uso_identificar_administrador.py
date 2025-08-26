#!/usr/bin/env python3
"""
Ejemplo de uso de la herramienta identificar_administrador
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio app al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.tools import identificar_administrador

def ejemplo_uso_herramienta():
    """Ejemplo de cómo usar la herramienta identificar_administrador"""
    
    print("🚀 EJEMPLO DE USO: Identificación de Administrador")
    print("=" * 60)
    
    # Ejemplo 1: Verificar si un teléfono es de administrador
    print("\n📞 Ejemplo 1: Verificar administrador")
    phone_example = "573195792747"
    result = identificar_administrador(phone_example)
    print(f"Resultado: {result}")
    
    # Ejemplo 2: Verificar teléfono que no es administrador
    print("\n📞 Ejemplo 2: Verificar no administrador")
    phone_example2 = "573172288329"
    result2 = identificar_administrador(phone_example2)
    print(f"Resultado: {result2}")
    
    # Ejemplo 3: Formato de teléfono con espacios
    print("\n📞 Ejemplo 3: Teléfono con formato")
    phone_example3 = "573 195 792 747"
    result3 = identificar_administrador(phone_example3)
    print(f"Resultado: {result3}")

def ejemplo_integracion_agente():
    """Ejemplo de cómo integrar la herramienta en el flujo del agente"""
    
    print("\n🤖 EJEMPLO DE INTEGRACIÓN CON EL AGENTE")
    print("=" * 60)
    
    # Simular el flujo del webhook
    def simular_webhook(phone: str, message: str):
        """Simula el procesamiento de un webhook"""
        print(f"\n📱 Mensaje recibido de: {phone}")
        print(f"💬 Contenido: {message}")
        
        # Verificar si es administrador antes de procesar
        admin_check = identificar_administrador(phone)
        
        if "ADMINISTRADOR IDENTIFICADO" in admin_check:
            print("✅ Usuario identificado como ADMINISTRADOR")
            print("🔓 Acceso completo a todas las funcionalidades")
            # Aquí el agente tendría acceso completo a todas las herramientas
            return "Procesando como administrador con acceso completo..."
        else:
            print("❌ Usuario NO es administrador")
            print("🔒 Acceso limitado a funcionalidades básicas")
            # Aquí el agente tendría acceso limitado
            return "Procesando como usuario regular con acceso limitado..."
    
    # Ejemplos de uso
    print("\n🔍 Caso 1: Administrador envía mensaje")
    simular_webhook("573195792747", "Necesito ver todos los clientes")
    
    print("\n🔍 Caso 2: Usuario regular envía mensaje")
    simular_webhook("573172288329", "Hola, ¿cómo estás?")

if __name__ == "__main__":
    ejemplo_uso_herramienta()
    ejemplo_integracion_agente()
    
    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES PARA EL AGENTE:")
    print("1. Usar identificar_administrador(phone) para verificar permisos")
    print("2. Si es administrador: acceso completo a todas las herramientas")
    print("3. Si no es administrador: acceso limitado a funcionalidades básicas")
    print("4. La herramienta valida automáticamente el formato del teléfono")
    print("5. Consulta la tabla user_agent en Supabase con type='Administrador'")
