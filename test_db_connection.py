#!/usr/bin/env python3
"""
Script para probar la conexión a la base de datos PostgreSQL y verificar el esquema
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_db_connection():
    """Prueba la conexión a la base de datos"""
    print("🔍 Probando conexión a la base de datos...")
    
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
        print("📡 Intentando conectar...")
        conn = psycopg2.connect(**connection_params)
        print("✅ Conexión exitosa!")
        
        cursor = conn.cursor()
        
        # Verificar el esquema actual
        print("\n📋 Verificando esquema actual...")
        cursor.execute("SELECT current_schema();")
        current_schema = cursor.fetchone()[0]
        print(f"Esquema actual: {current_schema}")
        
        # Listar todos los esquemas disponibles
        print("\n📋 Esquemas disponibles:")
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = cursor.fetchall()
        for schema in schemas:
            print(f"  - {schema[0]}")
        
        # Listar todas las tablas en el esquema public
        print("\n📋 Tablas en esquema 'public':")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("  ❌ No se encontraron tablas en el esquema 'public'")
        
        # Verificar si existe la tabla 'clients'
        print("\n🔍 Verificando tabla 'clients':")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = 'clients';
        """)
        clients_table = cursor.fetchone()
        
        if clients_table:
            print("✅ Tabla 'clients' encontrada en esquema 'public'")
            
            # Verificar columnas de la tabla clients
            print("\n📋 Columnas de la tabla 'clients':")
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 'clients'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            for column in columns:
                print(f"  - {column[0]} ({column[1]})")
                
        else:
            print("❌ Tabla 'clients' NO encontrada en esquema 'public'")
            
            # Buscar tablas que contengan 'client' en el nombre
            print("\n🔍 Buscando tablas que contengan 'client':")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name ILIKE '%client%'
                ORDER BY table_name;
            """)
            client_tables = cursor.fetchall()
            
            if client_tables:
                print("Tablas encontradas:")
                for table in client_tables:
                    print(f"  - {table[0]}")
            else:
                print("  ❌ No se encontraron tablas con 'client' en el nombre")
        
        # Probar una consulta simple
        print("\n🧪 Probando consulta simple...")
        try:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            print(f"✅ Consulta simple exitosa: {result}")
        except Exception as e:
            print(f"❌ Error en consulta simple: {e}")
        
        conn.close()
        print("\n✅ Prueba completada exitosamente")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print(f"Tipo de error: {type(e).__name__}")

if __name__ == "__main__":
    test_db_connection() 