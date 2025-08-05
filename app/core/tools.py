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


@tool
def get_next_question(input: str) -> str:
    """Devuelve la siguiente pregunta pendiente para completar el flujo."""
    for field, question in question_list:
        if not user_state.get(field):
            return question
    return "¡Gracias! Ya tenemos toda la información necesaria. Un asesor te contactará pronto."


@tool
def buscar_nombre_cliente(input: str) -> str:
    """Busca clientes en Supabase por coincidencia parcial en el nombre (full_name) y muestra nombre, email y teléfono. Si hay varios resultados, pide al usuario que elija uno."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("clients").select("full_name, email, phone").ilike("full_name", f"%{input}%").execute()
        if response.data and len(response.data) > 0:
            if len(response.data) == 1:
                cliente = response.data[0]
                nombre = cliente.get("full_name", "Sin nombre")
                email = cliente.get("email", "Sin email")
                phone = cliente.get("phone", "Sin teléfono")
                return f"Nombre: {nombre}\nEmail: {email}\nTeléfono: {phone}"
            else:
                lista = []
                for idx, cliente in enumerate(response.data, 1):
                    nombre = cliente.get("full_name", "Sin nombre")
                    email = cliente.get("email", "Sin email")
                    phone = cliente.get("phone", "Sin teléfono")
                    lista.append(f"{idx}. {nombre} | {email} | {phone}")
                return "Se encontraron varios clientes con ese nombre. Por favor, indica el número del cliente que deseas ver:\n\n" + "\n".join(lista)
        return "No se encontró ningún cliente con ese nombre."
    except Exception as e:
        return f"Error al buscar el cliente en Supabase: {e}"


@tool
def buscar_cliente_por_cedula(cedula: str) -> str:
    """Busca un cliente en la tabla clients por su cédula (unique_id) y devuelve nombre, email y teléfono."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("clients").select("full_name, email, phone, unique_id").eq("unique_id", cedula).execute()
        if response.data and len(response.data) > 0:
            cliente = response.data[0]
            nombre = cliente.get("full_name", "Sin nombre")
            email = cliente.get("email", "Sin email")
            phone = cliente.get("phone", "Sin teléfono")
            unique_id = cliente.get("unique_id", "Sin cédula")
            return f"Nombre: {nombre}\nEmail: {email}\nTeléfono: {phone}\nCédula: {unique_id}"
        return "No se encontró ningún cliente con esa cédula."
    except Exception as e:
        return f"Error al buscar el cliente por cédula en Supabase: {e}"

@tool
def buscar_ordenes_por_cliente(id_cliente: str) -> str:
    """Busca todas las órdenes de compra en la tabla sales_orders asociadas a un id_client y devuelve una lista de las órdenes encontradas."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("sales_orders").select("id_sales_orders, id_client, order_date, status, outstading_balance").eq("id_client", id_cliente).execute()
        if response.data and len(response.data) > 0:
            ordenes = []
            for orden in response.data:
                id_orden = orden.get("id", "Sin id")
                fecha = orden.get("Order_date", "Sin order_date")
                status = orden.get("status", "Sin estado")
                outstanding_balance = orden.get("outstanding_balance", "Sin outstanding_balance")
                ordenes.append(f"Orden: {id_orden} | Fecha: {fecha} | Estado: {status} | outstanding_balance: {outstanding_balance}")
            return "Órdenes encontradas para el cliente:\n" + "\n".join(ordenes)
        return "No se encontraron órdenes para este cliente."
    except Exception as e:
        return f"Error al buscar las órdenes en Supabase: {e}"
    
    

