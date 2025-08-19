
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    try:
        return psycopg2.connect(
            user="postgres.hcyxhuvyqvtlvfsnrhjw",
            password="3627765Camilo",
            host="aws-0-us-east-2.pooler.supabase.com",
            port=6543,
            dbname="postgres",
            client_encoding='utf8'
        )
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        raise


