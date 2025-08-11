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


from decimal import Decimal

@tool
def cuotas_pendientes_por_plan(id_payment_plan: int) -> str:
    """
    Devuelve las cuotas con estado 'Pendiente' de un plan de pago específico.
    Corrige el orden de columnas y devuelve el id_payment_installment real primero.
    """
    try:
        if not isinstance(id_payment_plan, int) or id_payment_plan <= 0:
            return "El ID del plan de pago debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                pi.id_payment_installment,
                pi.installment_number AS nro_mostrado,
                pi.id_payment_plan,
                pi.amount AS monto_total,
                COALESCE(pi.pay_amount, 0) AS monto_pagado,
                TO_CHAR(pi.due_date, 'DD/MM/YYYY') AS fecha_vencimiento,
                pi.status AS estado,
                COALESCE(pi.daysoverdue, 0) AS dias_mora,
                COALESCE(pi.early_payment_discount, 0) AS descuento_pronto_pago
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

        # Construir mapa interno: número mostrado -> id real
        mapa_cuotas = {}
        lines = []
        for (
            id_real_installment,
            installment_number,
            id_plan,
            amount,
            pay_amount,
            fecha_vencimiento,
            status,
            dias_mora,
            descuento_pronto_pago
        ) in rows:
            # Guardamos el mapeo para uso posterior (pagar cuota X -> id real)
            mapa_cuotas[str(installment_number)] = id_real_installment

            # Formateo de montos
            try:
                monto_total_fmt = f"{Decimal(amount):,.2f}"
            except Exception:
                monto_total_fmt = str(amount)
            try:
                monto_pagado_fmt = f"{Decimal(pay_amount):,.2f}"
            except Exception:
                monto_pagado_fmt = str(pay_amount)

            lines.append(
                f"Nro: {installment_number} | 🆔 ID real (id_payment_installment): {id_real_installment} | 🪙 ID plan: {id_plan} | "
                f"💰 Monto total: {monto_total_fmt} | 💵 Pagado: {monto_pagado_fmt} | 📅 Vence: {fecha_vencimiento} | Estado: {status} | "
                f"Días mora: {dias_mora} | Descuento pronto pago: {descuento_pronto_pago}"
            )

        # Opcional: si quieres devolver también el mapa, podrías retornarlo o almacenarlo en contexto.
        return "\n".join(lines)

    except Exception as e:
        error_msg = f"Error al consultar cuotas pendientes: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"

from decimal import Decimal, InvalidOperation
from datetime import datetime

from decimal import Decimal, InvalidOperation
from datetime import datetime

@tool
def registrar_pago(
    id_payment_installment: int = None,
    installment_number: int = None,
    id_payment_plan: int = None,
    id_sales_orders: int = None,
    id_client: int = None,
    amount: float = None,
    payment_method: str = None,
    # Transferencia
    proof_number: str = None,
    emission_bank: str = None,
    emission_date: str = None,
    trans_value: float = None,
    destiny_bank: str = None,
    observations: str = None,
    # Cheque
    cheque_number: str = None,
    bank: str = None,
    emision_date_cheque: str = None,
    stimate_collection_date: str = None,
    cheque_value: float = None,
    notes: str = ""
) -> str:
    """
    Registra un pago; asume:
      - payments.id_payment es PK (se obtiene con RETURNING).
      - payments.id_sales_orders es FK a sales_orders.
      - transfers.cheques referencian payments.id_payment.
    """

    # Validaciones básicas
    if id_payment_installment is None and installment_number is None:
        return "Proporciona id_payment_installment o installment_number (con id_payment_plan si corresponde)."

    if amount is None:
        return "Necesito el monto a pagar."

    try:
        monto_a_pagar = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        return "El monto no es válido."

    if monto_a_pagar <= 0:
        return "El monto debe ser mayor a 0."

    if payment_method not in (None, "Efectivo", "Transferencia", "Cheque"):
        return "Método inválido."

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Si nos dieron installment_number, mapear al id real dentro del plan
        if id_payment_installment is None and installment_number is not None:
            if id_payment_plan is None:
                return "Cuando usas installment_number, también proporciona id_payment_plan."
            cur.execute(
                "SELECT id_payment_installment FROM public.payment_installment WHERE id_payment_plan = %s AND installment_number = %s LIMIT 1;",
                (id_payment_plan, installment_number)
            )
            r = cur.fetchone()
            if not r:
                cur.close(); conn.close()
                return f"No se encontró la cuota {installment_number} en el plan {id_payment_plan}."
            id_payment_installment = r[0]

        # Bloqueamos la fila para evitar race conditions y obtenemos ids relacionados
        cur.execute(
            """
            SELECT pi.id_payment_installment, pi.id_payment_plan, pp.id_sales_orders, so.id_client,
                   COALESCE(pi.pay_amount,0) AS pay_amount, pi.amount AS cuota_amount
            FROM public.payment_installment pi
            JOIN public.payment_plan pp ON pp.id_payment_plan = pi.id_payment_plan
            JOIN public.sales_orders so ON so.id_sales_orders = pp.id_sales_orders
            WHERE pi.id_payment_installment = %s
            FOR UPDATE;
            """,
            (id_payment_installment,)
        )
        fila = cur.fetchone()
        if not fila:
            cur.close(); conn.close()
            return f"No existe la cuota con id_payment_installment = {id_payment_installment}."

        db_id_pay_installment, db_id_plan, db_id_sales_orders, db_id_client, db_pay_amount, db_cuota_amount = fila

        # Autocompletar si faltan
        if id_payment_plan is None:
            id_payment_plan = db_id_plan
        if id_sales_orders is None:
            id_sales_orders = db_id_sales_orders
        if id_client is None:
            id_client = db_id_client

        # Validaciones: si el usuario pasó ids, que coincidan
        if db_id_plan != id_payment_plan:
            cur.close(); conn.close()
            return "El id_payment_installment no pertenece al id_payment_plan indicado."
        if db_id_sales_orders != id_sales_orders:
            cur.close(); conn.close()
            return "El id_sales_orders no coincide con la orden asociada al plan/cuota."
        if db_id_client != id_client:
            cur.close(); conn.close()
            return "El id_client no coincide con la orden asociada al plan/cuota."

        # --- Insert en payments: IMPORTANT -> RETURNING id_payment (PK) ---
        cur.execute(
            """
            INSERT INTO public.payments
                (id_sales_orders, id_payment_plan, id_client, id_payment_installment,
                 payment_method, amount, notes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id_payment;
            """,
            (id_sales_orders, id_payment_plan, id_client, id_payment_installment,
             payment_method or "Efectivo", float(monto_a_pagar), notes)
        )
        row = cur.fetchone()
        if not row:
            conn.rollback(); cur.close(); conn.close()
            return "Error al insertar el pago en la tabla payments."
        id_payment = row[0]  # <-- este es el PK que usaremos en transfers/cheques

        # --- Insert en tablas auxiliares usando id_payment (PK) ---
        if payment_method == "Transferencia":
            if not all([proof_number, emission_bank, emission_date, trans_value, destiny_bank]):
                conn.rollback(); cur.close(); conn.close()
                return "Faltan campos para Transferencia."
            cur.execute(
                """
                INSERT INTO public.transfers
                    (id_payment, id_payment_installment, proof_number, emission_bank, emission_date, trans_value, destiny_bank, observations, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
                """,
                (id_payment, id_payment_installment, proof_number, emission_bank, emission_date,
                 float(trans_value), destiny_bank, observations)
            )
        elif payment_method == "Cheque":
            if not all([cheque_number, bank, emision_date_cheque, cheque_value]):
                conn.rollback(); cur.close(); conn.close()
                return "Faltan campos para Cheque."
            cur.execute(
                """
                INSERT INTO public.cheques
                    (id_payment, id_payment_installment, cheque_number, bank, emision_date, stimate_collection_date, cheque_value, observations, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
                """,
                (id_payment, id_payment_installment, cheque_number, bank, emision_date_cheque,
                 stimate_collection_date, float(cheque_value), observations)
            )

        # --- Actualizar pay_amount y obtener nuevo acumulado ---
        cur.execute(
            """
            UPDATE public.payment_installment
            SET pay_amount = COALESCE(pay_amount, 0) + %s,
                status = CASE WHEN COALESCE(pay_amount, 0) + %s >= amount THEN 'Pagado' ELSE 'Pendiente' END
            WHERE id_payment_installment = %s
            RETURNING COALESCE(pay_amount,0) AS nuevo_acumulado, amount;
            """,
            (float(monto_a_pagar), float(monto_a_pagar), id_payment_installment)
        )
        nuevo_acumulado, cuota_total = cur.fetchone()

        conn.commit()
        cur.close()
        conn.close()

        return (
            f"✅ Pago registrado correctamente.\n"
            f"ID Payment (PK): {id_payment}\n"
            f"Cuota ID: {id_payment_installment}\n"
            f"Nuevo acumulado: {Decimal(str(nuevo_acumulado)):,.2f} / {Decimal(str(cuota_total)):,.2f}"
        )

    except Exception as e:
        if conn:
            try:
                conn.rollback(); conn.close()
            except:
                pass
        return f"❌ Error al registrar el pago: {str(e)}"
