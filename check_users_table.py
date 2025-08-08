import psycopg2

def check_users_table():
    conn = psycopg2.connect(
        user="postgres.jhgvhzxcxyxaiixnqprj",
        password="Omnion2025_",
        host="aws-0-us-east-2.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        client_encoding='utf8'
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'users' 
        ORDER BY ordinal_position;
    """)
    
    columns = cursor.fetchall()
    print("Columnas de la tabla users:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")
    
    conn.close()

if __name__ == "__main__":
    check_users_table() 