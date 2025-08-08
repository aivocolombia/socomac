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
    try:
        print(f"🔍 Buscando clientes con nombre: '{nombre}'")
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
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
        
        patron_busqueda = f"%{nombre}%" if nombre else "%%"

        cursor.execute(query, (patron_busqueda, offset, limit))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return "No se encontraron clientes con los criterios especificados."

        respuesta = []
        for id_cliente, nombre_cliente in resultados:
            respuesta.append(f"🆔 ID: {id_cliente} | 👤 Nombre: {nombre_cliente}")

        print(f"✅ Encontrados {len(resultados)} clientes")
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"Error al consultar clientes: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"


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
    try:
        print(f"🏢 Buscando empresas con nombre: '{nombre}'")
        
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
            FROM public.clients c
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
        print(f"✅ Encontradas {len(rows)} empresas")
        return "\n".join(lines)
        
    except Exception as e:
        error_msg = f"Error al consultar empresas: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"


@tool
def planes_pago_pendientes_por_cliente(id_cliente: int) -> str:
    """
    Devuelve los planes de pago con estado 'Pendiente' asociados a un cliente.

    Args:
        id_cliente (int): ID del cliente.

    Returns:
        str: Lista de planes con campos clave o mensaje de no encontrados.
    """
    try:
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            return "El ID de cliente debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                pp.id_payment_plan,
                pp.id_sales_orders,
                pp.num_installments,
                pp.total_amount,
                pp.status,
                pp.pending_amount,
                pp.type_payment_plan
            FROM public.payment_plan pp
            JOIN public.sales_orders so 
                ON so.id_sales_orders = pp.id_sales_orders
            WHERE so.id_client = %s
              AND pp.status = 'Pendiente'
            ORDER BY pp.created_at DESC;
        """

        cursor.execute(query, (id_cliente,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron planes de pago pendientes para el cliente con ID {id_cliente}."

        # Formato de salida
        lines = []
        for rid_plan, rid_order, num_inst, total_amt, status, pending_amt, type_plan in rows:
            lines.append(
                f"📋 Plan: {rid_plan} | 🛒 Orden: {rid_order} | "
                f"Cuotas: {num_inst} | 💰 Total: {total_amt} | "
                f"Estado: {status} | ⏳ Pendiente: {pending_amt} | "
                f"Tipo: {type_plan}"
            )

        return "\n".join(lines)

    except Exception as e:
        error_msg = f"Error al consultar planes de pago: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"


@tool
def montos_a_favor_por_cliente(id_cliente: int) -> str:
    """
    Devuelve los planes de pago 'Pagado' con monto pendiente mayor a 0,
    es decir, montos a favor de un cliente.

    Args:
        id_cliente (int): ID del cliente.

    Returns:
        str: Lista de planes con montos a favor o mensaje de no encontrados.
    """
    try:
        if not isinstance(id_cliente, int) or id_cliente <= 0:
            return "El ID de cliente debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                pp.id_payment_plan,
                pp.id_sales_orders,
                pp.pending_amount
            FROM public.payment_plan pp
            JOIN public.sales_orders so 
                ON so.id_sales_orders = pp.id_sales_orders
            WHERE so.id_client = %s
              AND pp.status = 'Pagado'
              AND pp.pending_amount > 0
            ORDER BY pp.created_at DESC;
        """

        cursor.execute(query, (id_cliente,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron montos a favor para el cliente con ID {id_cliente}."

        # Formato de salida
        lines = []
        for rid_plan, rid_order, pending_amt in rows:
            lines.append(
                f"📋 Plan: {rid_plan} | 🛒 Orden: {rid_order} | 💵 Monto a favor: {pending_amt}"
            )

        return "\n".join(lines)

    except Exception as e:
        error_msg = f"Error al consultar montos a favor: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"


@tool
def cuotas_pendientes_por_plan(id_payment_plan: int) -> str:
    """
    Devuelve las cuotas con estado 'Pendiente' de un plan de pago específico.

    Args:
        id_payment_plan (int): ID del plan de pago.

    Returns:
        str: Lista de cuotas pendientes con detalles o mensaje de no encontradas.
    """
    try:
        if not isinstance(id_payment_plan, int) or id_payment_plan <= 0:
            return "El ID del plan de pago debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                pi.id_payment_installment,
                pi.installment_number,
                pi.due_date,
                pi.amount,
                pi.pay_amount,
                pi.status,
                pi.daysoverdue,
                pi.early_payment_discount
            FROM public.payment_installment pi
            WHERE pi.id_payment_plan = %s
              AND pi.status = 'Pendiente'
            ORDER BY pi.installment_number ASC;
        """

        cursor.execute(query, (id_payment_plan,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron cuotas pendientes para el plan {id_payment_plan}."

        # Formateo de salida
        lines = []
        for (
            id_installment, num_installment, due_date, amount, pay_amount,
            status, days_overdue, early_discount
        ) in rows:
            lines.append(
                f"📌 Cuota #{num_installment} | "
                f"💰 Total: {amount} | 💵 Pagado: {pay_amount} | "
                f"📅 Vence: {due_date} | Estado: {status} | "
                f"Días mora: {days_overdue} | "
                f"Descuento pronto pago: {early_discount}"
            )

        return "\n".join(lines)

    except Exception as e:
        error_msg = f"Error al consultar cuotas pendientes: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"

import psycopg2

def registrar_pago():
    conn = psycopg2.connect(
        host="localhost",
        database="tu_base",
        user="tu_usuario",
        password="tu_password"
    )
    cursor = conn.cursor()

    # Paso 1: Confirmar id_payment_plan
    id_payment_plan = input("Ingrese el ID del plan de pago: ")

    # Paso 2: Mostrar cuotas asociadas
    cursor.execute("""
        SELECT id_payment_installment, installment_number, pay_amount
        FROM payment_installment
        WHERE id_payment_plan = %s
        ORDER BY installment_number;
    """, (id_payment_plan,))
    cuotas = cursor.fetchall()

    if not cuotas:
        print("No se encontraron cuotas para este plan.")
        conn.close()
        return

    print("\nCuotas del plan:")
    for cuota in cuotas:
        id_pi, num, monto = cuota
        print(f"ID: {id_pi} | Cuota N° {num} | Monto actual: {monto or 0}")

    # Paso 3: Usuario elige cuota
    id_payment_installment = input("\nIngrese el ID de la cuota a la que desea afiliar el pago: ")

    # Paso 4: Monto del pago
    try:
        amount = float(input("Ingrese el monto a pagar: "))
    except ValueError:
        print("Monto inválido.")
        conn.close()
        return

    # Paso 5: Obtener monto actual y sumarlo
    cursor.execute("""
        SELECT pay_amount
        FROM payment_installment
        WHERE id_payment_installment = %s;
    """, (id_payment_installment,))
    row = cursor.fetchone()
    if not row:
        print("No se encontró la cuota seleccionada.")
        conn.close()
        return

    pay_amount_actual = float(row[0] or 0)
    nuevo_acumulado = pay_amount_actual + amount

    # Paso 6: Actualizar monto acumulado en la cuota
    cursor.execute("""
        UPDATE payment_installment
        SET pay_amount = %s
        WHERE id_payment_installment = %s;
    """, (nuevo_acumulado, id_payment_installment))

    # Paso 7: Registrar el pago
    cursor.execute("""
        INSERT INTO payments (id_payment_installment, amount)
        VALUES (%s, %s);
    """, (id_payment_installment, amount))

    conn.commit()
    conn.close()
    print(f"\nPago registrado correctamente. Nuevo monto acumulado en la cuota: {nuevo_acumulado}")



