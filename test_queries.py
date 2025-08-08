#!/usr/bin/env python3
"""
Script para probar las consultas específicas de las herramientas
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_queries():
    """Prueba las consultas específicas de las herramientas"""
    print("🔍 Probando consultas específicas...")
    
    # Credenciales de conexión
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
        
        patron_busqueda = "%johan%"
        print(f"Buscando: '{patron_busqueda}'")
        
        cursor.execute(query_cliente, (patron_busqueda, 0, 10))
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
        
        patron_empresa = "%%"  # Buscar todas
        print(f"Buscando empresas: '{patron_empresa}'")
        
        cursor.execute(query_empresa, (patron_empresa, 0, 10))
        resultados_empresa = cursor.fetchall()
        
        print(f"✅ Encontradas {len(resultados_empresa)} empresas:")
        for id_empresa, nombre_empresa in resultados_empresa:
            print(f"  - ID: {id_empresa} | Empresa: {nombre_empresa}")
        
        # Probar consulta de leads
        print("\n🧪 Probando consulta de leads...")
        query_leads = "SELECT name, email FROM public.leads WHERE phone = %s"
        
        phone_test = "573195792747"
        print(f"Buscando lead con teléfono: '{phone_test}'")
        
        cursor.execute(query_leads, (phone_test,))
        resultado_leads = cursor.fetchone()
        
        if resultado_leads:
            name, email = resultado_leads
            print(f"✅ Lead encontrado: {name} - {email}")
        else:
            print("❌ No se encontró lead con ese teléfono")
        
        conn.close()
        print("\n✅ Todas las pruebas completadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        print(f"Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    test_queries() 