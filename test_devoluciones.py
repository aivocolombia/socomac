#!/usr/bin/env python3
"""
Prueba de la funcionalidad de devoluciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.tools import consultar_detalles_ordenes_cliente, procesar_devolucion

def test_consultar_detalles_cliente():
    """Prueba la consulta de detalles de órdenes de un cliente"""
    
    print("🧪 Probando consulta de detalles de órdenes...")
    
    # ID de cliente de prueba (ajustar según tu base de datos)
    id_cliente_prueba = 1
    
    try:
        resultado = consultar_detalles_ordenes_cliente(id_cliente_prueba)
        print("✅ Resultado de consulta:")
        print(resultado)
        return True
    except Exception as e:
        print(f"❌ Error en consulta: {str(e)}")
        return False

def test_procesar_devolucion():
    """Prueba el procesamiento de una devolución"""
    
    print("\n🧪 Probando procesamiento de devolución...")
    
    # ID de detalle de prueba (ajustar según tu base de datos)
    id_detalle_prueba = 1
    
    try:
        resultado = procesar_devolucion(id_detalle_prueba)
        print("✅ Resultado de devolución:")
        print(resultado)
        return True
    except Exception as e:
        print(f"❌ Error en devolución: {str(e)}")
        return False

def main():
    """Función principal de pruebas"""
    
    print("🚀 Iniciando pruebas de funcionalidad de devoluciones")
    print("=" * 60)
    
    # Prueba 1: Consultar detalles de cliente
    print("\n📋 PRUEBA 1: Consultar detalles de órdenes de cliente")
    test1_exito = test_consultar_detalles_cliente()
    
    # Prueba 2: Procesar devolución
    print("\n🔄 PRUEBA 2: Procesar devolución")
    test2_exito = test_procesar_devolucion()
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"   Consulta de detalles: {'✅ PASÓ' if test1_exito else '❌ FALLÓ'}")
    print(f"   Procesamiento de devolución: {'✅ PASÓ' if test2_exito else '❌ FALLÓ'}")
    
    if test1_exito and test2_exito:
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisar errores arriba.")

if __name__ == "__main__":
    main()

