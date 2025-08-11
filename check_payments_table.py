#!/usr/bin/env python3
"""
Script para verificar la estructura de la tabla payments
"""

import psycopg2

def check_payments_table():
    """Verifica la estructura de la tabla payments"""
    print("🔍 Verificando estructura de la tabla payments...")
    
    conn = psycopg2.connect(
        user="postgres.jhgvhzxcxyxaiixnqprj",
        password="Omnion2025_",
        host="aws-0-us-east-2.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        client_encoding='utf8'
    )
    
    cursor = conn.cursor()
    
    # Verificar si existe la tabla payments
    print("\n🔍 Verificando si existe la tabla 'payments':")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_name = 'payments';
    """)
    payments_table = cursor.fetchone()
    
    if payments_table:
        print("✅ Tabla 'payments' encontrada en esquema 'public'")
        
        # Verificar columnas de la tabla payments
        print("\n📋 Columnas de la tabla 'payments':")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'payments'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        
        for column in columns:
            nullable = "NULL" if column[2] == "YES" else "NOT NULL"
            print(f"  - {column[0]} ({column[1]}) {nullable}")
            
    else:
        print("❌ Tabla 'payments' NO encontrada en esquema 'public'")
        
        # Buscar tablas que contengan 'payment' en el nombre
        print("\n🔍 Buscando tablas que contengan 'payment':")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name ILIKE '%payment%'
            ORDER BY table_name;
        """)
        payment_tables = cursor.fetchall()
        
        if payment_tables:
            print("Tablas encontradas:")
            for table in payment_tables:
                print(f"  - {table[0]}")
        else:
            print("  ❌ No se encontraron tablas con 'payment' en el nombre")
    
    conn.close()
    print("\n✅ Verificación completada")

if __name__ == "__main__":
    check_payments_table() 