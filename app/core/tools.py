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

@tool
def registrar_pago(
    id_sales_orders: int,
    id_payment_plan: int,
    id_client: int,
    amount: float,
    payment_method: str,
    id_payment_installment: int = None,
    installment_number: int = None,
    # Campos transferencia
    proof_number: str = None,
    emission_bank: str = None,
    emission_date: str = None,   # 'YYYY-MM-DD' o None
    trans_value: float = None,
    destiny_bank: str = None,
    observations: str = None,
    # Campos cheque
    cheque_number: str = None,
    bank: str = None,
    emision_date_cheque: str = None,  # 'YYYY-MM-DD' o None
    stimate_collection_date: str = None,
    cheque_value: float = None,
    notes: str = ""
) -> str:
    """
    Registra un pago asociado a una cuota (id_payment_installment) asegurando:
    - Se usa siempre el id_payment_installment real (PK).
    - Soporte para Efectivo / Transferencia / Cheque.
    - Bloqueo FOR UPDATE de la fila de payment_installment para evitar race conditions.
    - Retorna mensaje con ID del payment (insertado) y nuevo acumulado en la cuota.
    """

    # --- validaciones básicas ---
    try:
        # normalizar monto a Decimal
        monto_a_pagar = Decimal(str(amount))
    except (InvalidOperation, TypeError):
        return "El monto ingresado no es válido."

    if monto_a_pagar <= 0:
        return "El monto debe ser mayor a 0."

    if not isinstance(id_sales_orders, int) or id_sales_orders <= 0:
        return "id_sales_orders inválido."

    if not isinstance(id_payment_plan, int) or id_payment_plan <= 0:
        return "id_payment_plan inválido."

    if not isinstance(id_client, int) or id_client <= 0:
        return "id_client inválido."

    if payment_method not in ("Efectivo", "Transferencia", "Cheque"):
        return "Método inválido. Opciones válidas: Efectivo, Transferencia, Cheque."

    if id_payment_installment is None:
        if installment_number is None:
            return "Debes proporcionar id_payment_installment real o installment_number (para mapear internamente)."
        # mapear installment_number -> id_payment_installment (solo dentro del mismo plan)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id_payment_installment
                FROM public.payment_installment
                WHERE id_payment_plan = %s
                  AND installment_number = %s
                LIMIT 1;
                """,
                (id_payment_plan, installment_number)
            )
            row = cur.fetchone()
            if not row:
                conn.close()
                return f"No se encontró la cuota {installment_number} en el plan {id_payment_plan}."
            id_payment_installment = row[0]
            cur.close()
            conn.close()
        except Exception as e:
            return f"Error mapeando installment_number: {str(e)}"

    # --- transacción: verificar existencia y bloquear la fila ---
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        cur = conn.cursor()

        # Verificamos que la cuota exista y pertenezca al plan; además obtenemos datos útiles
        cur.execute(
            """
            SELECT
                pi.id_payment_installment,
                pi.id_payment_plan,
                COALESCE(pi.pay_amount, 0) AS pay_amount,
                pi.amount AS cuota_amount,
                pi.status,
                pp.id_sales_orders,
                so.id_client
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
            conn.rollback()
            cur.close()
            conn.close()
            return f"No existe la cuota con id_payment_installment = {id_payment_installment}."

        (
            db_id_payment_installment,
            db_id_payment_plan,
            db_pay_amount,
            db_cuota_amount,
            db_status,
            db_id_sales_orders,
            db_id_client
        ) = fila

        # Seguridad: validar que IDs pasados coinciden con los relacionados en BD
        if db_id_payment_plan != id_payment_plan:
            conn.rollback()
            cur.close()
            conn.close()
            return "El id_payment_installment no pertenece al id_payment_plan indicado."

        if db_id_sales_orders != id_sales_orders:
            conn.rollback()
            cur.close()
            conn.close()
            return "El id_sales_orders no coincide con el plan/cuota indicada."

        if db_id_client != id_client:
            conn.rollback()
            cur.close()
            conn.close()
            return "El id_client no coincide con la orden asociada al plan."

        # --- insertar en payments (tabla principal) ---
        # Supongo una tabla `payments` con al menos: id_sales_orders, id_payment_plan, id_client,
        # id_payment_installment, payment_method, amount, notes, created_at
        cur.execute(
            """
            INSERT INTO public.payments
                (id_sales_orders, id_payment_plan, id_client, id_payment_installment,
                 payment_method, amount, notes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id_payment;
            """,
            (id_sales_orders, id_payment_plan, id_client, id_payment_installment,
             payment_method, float(monto_a_pagar), notes)
        )
        payment_row = cur.fetchone()
        if not payment_row:
            conn.rollback()
            cur.close()
            conn.close()
            return "Error al insertar el pago en la tabla payments."

        id_payment_inserted = payment_row[0]

        # --- insertar en tablas según método ---
        if payment_method == "Transferencia":
            # Validaciones mínimas
            if not proof_number or not emission_bank or not emission_date or trans_value is None or not destiny_bank:
                conn.rollback()
                cur.close()
                conn.close()
                return "Faltan campos obligatorios para Transferencia (proof_number, emission_bank, emission_date, trans_value, destiny_bank)."

            cur.execute(
                """
                INSERT INTO public.transfers
                    (id_payment, id_payment_installment, proof_number, emission_bank, emission_date, trans_value, destiny_bank, observations, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
                """,
                (id_payment_inserted, id_payment_installment, proof_number, emission_bank, emission_date,
                 float(trans_value), destiny_bank, observations)
            )

        elif payment_method == "Cheque":
            if not cheque_number or not bank or not emision_date_cheque or cheque_value is None:
                conn.rollback()
                cur.close()
                conn.close()
                return "Faltan campos obligatorios para Cheque (cheque_number, bank, emision_date_cheque, cheque_value)."

            cur.execute(
                """
                INSERT INTO public.cheques
                    (id_payment, id_payment_installment, cheque_number, bank, emision_date, stimate_collection_date, cheque_value, observations, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
                """,
                (id_payment_inserted, id_payment_installment, cheque_number, bank, emision_date_cheque,
                 stimate_collection_date, float(cheque_value), observations)
            )

        # --- actualizar pay_amount de la cuota de forma segura y obtener el nuevo acumulado ---
        cur.execute(
            """
            UPDATE public.payment_installment
            SET pay_amount = COALESCE(pay_amount, 0) + %s,
                status = CASE WHEN COALESCE(pay_amount, 0) + %s >= amount THEN 'Pagado' ELSE 'Pendiente' END
            WHERE id_payment_installment = %s
            RETURNING COALESCE(pay_amount, 0) AS nuevo_acumulado, amount;
            """,
            (float(monto_a_pagar), float(monto_a_pagar), id_payment_installment)
        )
        updated = cur.fetchone()
        if not updated:
            conn.rollback()
            cur.close()
            conn.close()
            return "Error al actualizar la cuota."

        nuevo_acumulado, cuota_total = updated

        # Opcional: si quisiéramos actualizar pending_amount en payment_plan, aquí se puede hacer.
        # (No lo hago automáticamente porque la lógica de pending_amount puede depender de otras reglas.)

        conn.commit()
        cur.close()
        conn.close()

        return (
            f"✅ Pago registrado correctamente.\n"
            f"ID Payment: {id_payment_inserted}\n"
            f"Cuota ID (id_payment_installment): {id_payment_installment}\n"
            f"Nuevo acumulado en la cuota: {Decimal(str(nuevo_acumulado)):,.2f} / {Decimal(str(cuota_total)):,.2f}\n"
            f"Estado cuota: {'Pagado' if Decimal(str(nuevo_acumulado)) >= Decimal(str(cuota_total)) else 'Pendiente'}"
        )

    except Exception as e:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except:
                pass
        return f"❌ Error al registrar el pago: {str(e)}"
