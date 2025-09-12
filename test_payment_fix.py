#!/usr/bin/env python3
"""
Script de prueba para verificar que la corrección de payment_method funciona correctamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.tools import registrar_pago_directo_orden

def test_payment_fix():
    """Prueba la función registrar_pago_directo_orden con los parámetros que fallaron."""
    
    print("🧪 Probando la corrección de registrar_pago_directo_orden...")
    
    # Parámetros del caso que falló
    params = {
        'id_sales_orders': 30,
        'amount': 500,
        'metodo_pago': 'efectivo',
        'id_client': 3
    }
    
    print(f"📋 Parámetros de prueba: {params}")
    
    try:
        result = registrar_pago_directo_orden(**params)
        print(f"✅ Resultado: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_payment_fix()
    if success:
        print("\n🎉 ¡La corrección funciona correctamente!")
    else:
        print("\n💥 La corrección aún tiene problemas.")
