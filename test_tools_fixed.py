#!/usr/bin/env python3
"""
Script para probar las herramientas con credenciales hardcodeadas
"""

import psycopg2

def test_tools_with_fixed_credentials():
    """Prueba las consultas con credenciales hardcodeadas"""
    print("🧪 Probando consultas con credenciales fijas...")
    
    # Credenciales que funcionan
    connection_params = {
        "user": "postgres.jhgvhzxcxyxaiixnqprj",
        "password": "Omnion2025_",
        "host": "aws-0-us-east-2.pooler.supabase.com",
        "port": 6543,
        "dbname": "postgres",
        "client_encoding": 'utf8'
    }
    
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        
        # Probar consulta de nombre_cliente
        print("\n🧪 Probando consulta de nombre_cliente...")
        query_cliente = """
            SELECT DISTINCT
                c.id_client AS id,
                c.full_name AS nombre
            FROM public.clients c
            WHERE COALESCE(NULLIF(c.full_name, ''), '') <> ''
              AND c.full_name ILIKE %s
            ORDER BY nombre
            OFFSET %s
            LIMIT %s
        """
        
        # Buscar cliente específico
        print("1. Buscando cliente 'johan':")
        cursor.execute(query_cliente, ("%johan%", 0, 10))
        resultados = cursor.fetchall()
        print(f"✅ Encontrados {len(resultados)} clientes:")
        for id_cliente, nombre_cliente in resultados:
            print(f"  - ID: {id_cliente} | Nombre: {nombre_cliente}")
        
        # Buscar todos los clientes
        print("\n2. Buscando todos los clientes:")
        cursor.execute(query_cliente, ("%%", 0, 10))
        resultados = cursor.fetchall()
        print(f"✅ Encontrados {len(resultados)} clientes:")
        for id_cliente, nombre_cliente in resultados:
            print(f"  - ID: {id_cliente} | Nombre: {nombre_cliente}")
        
        # Probar consulta de nombre_empresa
        print("\n🧪 Probando consulta de nombre_empresa...")
        query_empresa = """
            SELECT DISTINCT
                c.id_client AS id,
                c.company   AS nombre
            FROM public.clients c
            WHERE COALESCE(NULLIF(c.company, ''), '') <> ''
              AND c.company ILIKE %s
            ORDER BY nombre
            OFFSET %s
            LIMIT %s
        """
        
        # Buscar empresa específica
        print("3. Buscando empresa 'SAS':")
        cursor.execute(query_empresa, ("%SAS%", 0, 10))
        resultados_empresa = cursor.fetchall()
        print(f"✅ Encontradas {len(resultados_empresa)} empresas:")
        for id_empresa, nombre_empresa in resultados_empresa:
            print(f"  - ID: {id_empresa} | Empresa: {nombre_empresa}")
        
        # Buscar todas las empresas
        print("\n4. Buscando todas las empresas:")
        cursor.execute(query_empresa, ("%%", 0, 10))
        resultados_empresa = cursor.fetchall()
        print(f"✅ Encontradas {len(resultados_empresa)} empresas:")
        for id_empresa, nombre_empresa in resultados_empresa:
            print(f"  - ID: {id_empresa} | Empresa: {nombre_empresa}")
        
        conn.close()
        print("\n✅ Todas las pruebas completadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        print(f"Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    test_tools_with_fixed_credentials() 