# app/core/tools.py

from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import get_db_connection
from app.db.mongo import MongoChatMessageHistory



@tool
def limpiar_memoria(phone: str) -> str:
    """Limpia toda la memoria de conversación de un usuario específico usando su número de teléfono. Esta herramienta borra todos los mensajes almacenados en MongoDB para el número de teléfono proporcionado."""
    try:
        print(f"🧹 Iniciando limpieza de memoria para el teléfono: {phone}")
        
        memory = MongoChatMessageHistory(phone=phone)
        
        memory.clear()
        
        print(f"✅ Memoria limpiada exitosamente para el teléfono: {phone}")
        return f"Memoria de conversación limpiada exitosamente para el número {phone}. La conversación anterior ha sido borrada."
        
    except Exception as e:
        error_msg = f"Error al limpiar la memoria: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def validar_cliente(telefono: str) -> str:
    """
    Valida si un cliente existe en la tabla public.clientes usando el teléfono.
    
    Args:
        telefono (str): Teléfono del cliente a buscar.

    Returns:
        str: Información del cliente si existe o mensaje de no encontrado.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, nombre, telefono, direccion, created_at
            FROM public.clientes
            WHERE telefono = %s
            LIMIT 1;
        """, (telefono,))
        cliente = cur.fetchone()
        conn.close()

        if cliente:
            return (f"🆔 ID: {cliente[0]} | 👤 {cliente[1]} | 📱 {cliente[2]} "
                    f"| 📍 {cliente[3] or 'N/A'} | 📅 Creado: {cliente[4]}")
        else:
            return f"❌ No se encontró cliente con teléfono {telefono}."

    except Exception as e:
        return f"❌ Error al validar cliente: {str(e)}"


@tool
def insertar_cliente(nombre: str, telefono: str, direccion: str = "") -> str:
    """
    Inserta un cliente en la tabla public.clientes si no existe (usando el teléfono como referencia).
    
    Args:
        nombre (str): Nombre del cliente.
        telefono (str): Teléfono del cliente (único).
        direccion (str, opcional): Dirección del cliente.

    Returns:
        str: Mensaje de confirmación o error.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM public.clientes WHERE telefono = %s
        """, (telefono,))
        existe = cur.fetchone()

        if existe:
            conn.close()
            return f"⚠️ El cliente con teléfono {telefono} ya existe."

        cur.execute("""
            INSERT INTO public.clientes (nombre, telefono, direccion, updated_at, created_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            RETURNING id, nombre, telefono, direccion;
        """, (nombre, telefono, direccion))
        nuevo = cur.fetchone()
        conn.commit()
        conn.close()

        return f"✅ Cliente creado: ID {nuevo[0]} | {nuevo[1]} ({nuevo[2]})"

    except Exception as e:
        return f"❌ Error al insertar cliente: {str(e)}"
