#!/usr/bin/env python3
"""
Script para probar la herramienta limpiar_memoria
"""

import os
import sys
from dotenv import load_dotenv

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app.core.tools import limpiar_memoria
from app.db.mongo import MongoChatMessageHistory

def test_limpiar_memoria():
    """Prueba la herramienta limpiar_memoria"""
    
    # Número de teléfono de prueba
    test_phone = "573195792747"
    
    print("🧪 Probando herramienta limpiar_memoria...")
    print(f"📱 Teléfono de prueba: {test_phone}")
    
    # Verificar memoria antes de limpiar
    print("\n📊 Verificando memoria antes de limpiar...")
    memory_before = MongoChatMessageHistory(phone=test_phone)
    messages_before = memory_before.messages
    print(f"📝 Mensajes en memoria antes: {len(messages_before)}")
    
    # Ejecutar la herramienta
    print("\n🧹 Ejecutando limpiar_memoria...")
    result = limpiar_memoria(test_phone)
    print(f"✅ Resultado: {result}")
    
    # Verificar memoria después de limpiar
    print("\n📊 Verificando memoria después de limpiar...")
    memory_after = MongoChatMessageHistory(phone=test_phone)
    messages_after = memory_after.messages
    print(f"📝 Mensajes en memoria después: {len(messages_after)}")
    
    # Verificar que se limpió correctamente
    if len(messages_after) == 0:
        print("✅ ¡Éxito! La memoria se limpió correctamente.")
    else:
        print("❌ Error: La memoria no se limpió completamente.")
    
    print("\n🏁 Prueba completada")

if __name__ == "__main__":
    test_limpiar_memoria() 