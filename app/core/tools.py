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
    Devuelve las cuotas pendientes de un plan de pago específico.

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
                pi.installment_number,
                pi.id_payment_installment,
                pi.id_payment_plan,
                pi.amount,
                COALESCE(pi.pay_amount, 0),
                TO_CHAR(pi.due_date, 'DD/MM/YYYY'),
                pi.status
            FROM public.payment_installment AS pi
            WHERE pi.id_payment_plan = %s
              AND pi.status = 'Pendiente'
            ORDER BY pi.installment_number ASC;
        """
        cursor.execute(query, (id_payment_plan,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron cuotas pendientes para el plan {id_payment_plan}."

        # mapa global para convertir número mostrado → id real
        global cuotas_map
        cuotas_map = {}

        lines = []
        for num_installment, id_real, id_plan, amount, pay_amount, due_date, status in rows:
            cuotas_map[num_installment] = {
                "id_payment_installment": id_real,
                "id_payment_plan": id_plan
            }
            lines.append(
                f"Nro: {num_installment} | 🆔 ID real (id_payment_installment): {id_real} "
                f"| 🪙 ID plan: {id_plan} | 💰 Monto total: {amount} | "
                f"💵 Pagado: {pay_amount} | 📅 Vence: {due_date} | Estado: {status}"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Error al consultar cuotas pendientes: {str(e)}"


from decimal import Decimal

@tool
def obtener_id_sales_orders_por_plan(id_payment_plan: int) -> str:
    """
    Obtiene el id_sales_orders asociado a un plan de pago específico.

    Args:
        id_payment_plan (int): ID del plan de pago.

    Returns:
        str: El id_sales_orders asociado al plan o mensaje de error.
    """
    try:
        if not isinstance(id_payment_plan, int) or id_payment_plan <= 0:
            return "El ID del plan de pago debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT id_sales_orders
            FROM public.payment_plan
            WHERE id_payment_plan = %s;
        """
        cursor.execute(query, (id_payment_plan,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return f"No se encontró el plan de pago con ID {id_payment_plan}."

        id_sales_orders = result[0]
        return f"ID de orden de venta: {id_sales_orders}"

    except Exception as e:
        return f"❌ Error al obtener id_sales_orders: {str(e)}"


@tool
def registrar_pago(
    id_sales_orders: int,
    id_payment_installment: int,
    amount: float,
    metodo_pago: str,
    proof_number: str = None,
    emission_bank: str = None,
    emission_date: str = None,
    destiny_bank: str = None,
    observations: str = None,
    cheque_number: str = None,
    bank: str = None,
    emision_date: str = None,
    stimate_collection_date: str = None,
    cheque_value: float = None
) -> str:
    """
    Registra un pago en la base de datos. 
    Dependiendo del método, inserta en payments y en la tabla correspondiente:
    - Efectivo → payments
    - Transferencia → payments + transfers (trans_value = amount, destino validado)
    - Cheque → payments + cheques (amount = cheque_value)
    Actualiza el acumulado pagado en la cuota.
    
    Args:
        id_sales_orders (int): ID de la orden de venta
        id_payment_installment (int): ID de la cuota de pago
        amount (float): Monto del pago
        metodo_pago (str): Método de pago (efectivo, transferencia, cheque)
        proof_number (str, optional): Número de comprobante para transferencias
        emission_bank (str, optional): Banco de emisión para transferencias
        emission_date (str, optional): Fecha de emisión para transferencias
        destiny_bank (str, optional): Banco de destino para transferencias
        observations (str, optional): Observaciones adicionales
        cheque_number (str, optional): Número de cheque
        bank (str, optional): Banco del cheque
        emision_date (str, optional): Fecha de emisión del cheque
        stimate_collection_date (str, optional): Fecha estimada de cobro del cheque
        cheque_value (float, optional): Valor del cheque
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        metodo_pago = metodo_pago.strip().lower()

        # === Normalizar y validar destino en transferencias ===
        if metodo_pago == "transferencia":
            # Solo validar banco de destino (destiny_bank)
            bancos_validos = {
                "bancolombia": "Bancolombia",
                "davivienda": "Davivienda"
            }
            if not destiny_bank:
                return "❌ Debes indicar el banco destino."
            destiny_bank_normalizado = destiny_bank.strip().lower()
            if destiny_bank_normalizado not in bancos_validos:
                return "❌ Banco destino inválido. Solo se permite 'Bancolombia' o 'Davivienda'."
            destiny_bank = bancos_validos[destiny_bank_normalizado]
            # El banco de emisión (emission_bank) puede ser cualquier banco, no se valida
            trans_value = amount  # Copiar automáticamente

        # === Ajustar amount en caso de cheque ===
        if metodo_pago == "cheque":
            if cheque_value is None:
                return "❌ Debes indicar el valor del cheque."
            amount = cheque_value

        # === Insertar en payments ===
        cursor.execute("""
            INSERT INTO payments (id_sales_orders, id_payment_installment, amount, payment_method, payment_date, destiny_bank)
            VALUES (%s, %s, %s, %s, CURRENT_DATE, %s)
            RETURNING id_payment;
        """, (
            id_sales_orders, id_payment_installment, amount, metodo_pago.capitalize(), destiny_bank
        ))
        id_payment = cursor.fetchone()[0]

        # === Insertar en tabla específica según método ===
        if metodo_pago == "transferencia":
            cursor.execute("""
                INSERT INTO transfers (id_payment, proof_number, emission_bank, emission_date, trans_value, destiny_bank, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, proof_number, emission_bank, emission_date, trans_value, destiny_bank, observations
            ))

        elif metodo_pago == "cheque":
            cursor.execute("""
                INSERT INTO cheques (id_payment, cheque_number, bank, emision_date, stimate_collection_date, cheque_value, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, cheque_number, bank, emision_date, stimate_collection_date, cheque_value, observations
            ))

        # === Actualizar pay_amount en la cuota ===
        cursor.execute("""
            UPDATE payment_installment
            SET pay_amount = COALESCE(pay_amount, 0) + %s
            WHERE id_payment_installment = %s;
        """, (amount, id_payment_installment))

        conn.commit()
        conn.close()

        return (
            f"✅ Pago registrado correctamente.\n"
            f"ID Payment: {id_payment}\n"
            f"Nuevo acumulado en la cuota: {amount}"
        )

    except Exception as e:
        return f"❌ Error al registrar el pago: {str(e)}"
