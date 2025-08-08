
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()


def get_db_connection():
    try:
        return psycopg2.connect(
            user=os.getenv("DB_USER", "postgres.jhgvhzxcxyxaiixnqprj"),
            password=os.getenv("DB_PASSWORD", "Omnion2025_"),
            host=os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com"),
            port=int(os.getenv("DB_PORT", "6543")),
            dbname=os.getenv("DB_NAME", "postgres.jhgvhzxcxyxaiixnqprj"),
            client_encoding='utf8'
        )
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        raise

def cargar_estado_desde_postgres(phone: str) -> Optional[dict]:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM leads WHERE phone = %s", (phone,))
        row = cursor.fetchone()
        conn.close()
        if row:
            name, email = row
            onboarding_complete = bool(name and email)
            return {
                "name": name,
                "email": email,
                "onboarding_complete": onboarding_complete,
                "last_intent": None,
                "last_seen": datetime.utcnow().isoformat()
            }
    except Exception as e:
        print(f"[ERROR] Al consultar PostgreSQL para el lead: {e}")
    return None
