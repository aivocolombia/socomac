
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional

load_dotenv()


def get_db_connection():
    return psycopg2.connect(
        user="postgres.jhgvhzxcxyxaiixnqprj",
        password="Omnion2025_",
        host="aws-0-us-east-2.pooler.supabase.com",
        port=6543,
        dbname="postgres.jhgvhzxcxyxaiixnqprj"
    )

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
