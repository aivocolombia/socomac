#!/usr/bin/env python3
"""
Script para probar que el agente puede usar la herramienta limpiar_memoria
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.core.agent import get_agent

def test_agente_limpiar_memoria():
    """Prueba que el agente puede usar la herramienta limpiar_memoria"""
    
    # Número de teléfono de prueba
    test_phone = "573195792747"
    
    print("🧪 Probando agente con herramienta limpiar_memoria...")
    print(f"📱 Teléfono de prueba: {test_phone}")
    
    # Crear el agente
    agent = get_agent(test_phone)
    
    # Mensaje de prueba para limpiar memoria
    test_message = "Por favor, limpia la memoria de nuestra conversación"
    
    print(f"\n💬 Mensaje de prueba: '{test_message}'")
    print("\n🤖 Ejecutando agente...")
    
    try:
        # Ejecutar el agente
        response = agent.run(test_message)
        print(f"\n✅ Respuesta del agente: {response}")
        
    except Exception as e:
        print(f"\n❌ Error ejecutando agente: {e}")
    
    print("\n🏁 Prueba completada")

if __name__ == "__main__":
    test_agente_limpiar_memoria() 