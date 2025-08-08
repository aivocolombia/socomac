# app/core/tools.py

from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import PostgresDB
from app.db.mongo import MongoChatMessageHistory
import time
import re
import os
from app.db.supabase import get_supabase_client

user_state = {field: None for field, _ in question_list}


@tool
def limpiar_memoria(phone: str) -> str:
    """Limpia toda la memoria de conversación de un usuario específico usando su número de teléfono. Esta herramienta borra todos los mensajes almacenados en MongoDB para el número de teléfono proporcionado."""
    try:
        print(f"🧹 Iniciando limpieza de memoria para el teléfono: {phone}")
        
        # Crear instancia de memoria de MongoDB
        memory = MongoChatMessageHistory(phone=phone)
        
        # Limpiar la memoria
        memory.clear()
        
        print(f"✅ Memoria limpiada exitosamente para el teléfono: {phone}")
        return f"Memoria de conversación limpiada exitosamente para el número {phone}. La conversación anterior ha sido borrada."
        
    except Exception as e:
        error_msg = f"Error al limpiar la memoria: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
