import psycopg2

def test_final_queries():
    """Prueba las consultas finales actualizadas"""
    print("🔍 Probando consultas finales...")
    
    conn = psycopg2.connect(
        user="postgres.jhgvhzxcxyxaiixnqprj",
        password="Omnion2025_",
        host="aws-0-us-east-2.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        client_encoding='utf8'
    )
    
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
    
    cursor.execute(query_cliente, ("%johan%", 0, 10))
    resultados = cursor.fetchall()
    print(f"✅ Encontrados {len(resultados)} clientes:")
    for id_cliente, nombre_cliente in resultados:
        print(f"  - ID: {id_cliente} | Nombre: {nombre_cliente}")
    
    # Probar consulta de users
    print("\n🧪 Probando consulta de users...")
    query_users = "SELECT full_name, email FROM public.users WHERE phone = %s"
    
    phone_test = "573195792747"
    cursor.execute(query_users, (phone_test,))
    resultado_users = cursor.fetchone()
    
    if resultado_users:
        full_name, email = resultado_users
        print(f"✅ Usuario encontrado: {full_name} - {email}")
    else:
        print("❌ No se encontró usuario con ese teléfono")
    
    conn.close()
    print("\n✅ Todas las pruebas completadas exitosamente")

if __name__ == "__main__":
    test_final_queries() 