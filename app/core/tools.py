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
def nombre_cliente(nombre: str = "", offset: int = 0, limit: int = 10) -> str:
    """
    Devuelve una lista de clientes filtrados por nombre (opcional) con paginación.

    Args:
        nombre (str): Nombre o parte del nombre del cliente a buscar. Puede estar vacío para traer todos.
        offset (int): Posición inicial de los resultados (para paginación).
        limit (int): Número máximo de resultados a devolver.

    Returns:
        str: Lista de clientes encontrados con su ID y nombre.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT
            c.id_client AS id,
            c.full_name AS nombre
        FROM clients c
        WHERE COALESCE(NULLIF(c.full_name, ''), '') <> ''
          AND c.full_name ILIKE %s
        ORDER BY nombre
        OFFSET %s
        LIMIT %s
    """
    
    patron_busqueda = f"%{nombre}%" if nombre else "%%"

    cursor.execute(query, (patron_busqueda, offset, limit))
    resultados = cursor.fetchall()
    conn.close()

    if not resultados:
        return "No se encontraron clientes con los criterios especificados."

    respuesta = []
    for id_cliente, nombre_cliente in resultados:
        respuesta.append(f"🆔 ID: {id_cliente} | 👤 Nombre: {nombre_cliente}")

    return "\n".join(respuesta)


@tool
def nombre_empresa(nombre: str = "", offset: int = 0, limit: int = 10) -> str:
    """
    Devuelve empresas (clients.company) filtradas por nombre con paginación.

    Args:
        nombre (str): Parte del nombre de la empresa a buscar. Vacío = todas.
        offset (int): Desplazamiento inicial (paginación).
        limit (int): Cantidad de registros a devolver.

    Returns:
        str: Lista de empresas con ID y nombre.
    """
    # (Opcional) límites sanos para evitar abusos
    if limit <= 0:
        limit = 10
    if limit > 100:
        limit = 100
    if offset < 0:
        offset = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT
            c.id_client AS id,
            c.company   AS nombre
        FROM clients c
        WHERE COALESCE(NULLIF(c.company, ''), '') <> ''
          AND c.company ILIKE %s
        ORDER BY nombre
        OFFSET %s
        LIMIT %s
    """

    patron = f"%{nombre}%" if nombre else "%%"

    cursor.execute(query, (patron, offset, limit))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "No se encontraron empresas con los criterios especificados."

    lines = [f"🆔 ID: {rid} | 🏢 Empresa: {rnom}" for rid, rnom in rows]
    return "\n".join(lines)
