# app/core/tools.py
from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import get_db_connection
from app.db.mongo import MongoChatMessageHistory
from app.db.supabase import get_supabase_client

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
    La búsqueda es flexible y encuentra nombres similares.

    Args:
        nombre (str): Nombre o parte del nombre del cliente a buscar. Vacío = todos.
        offset (int): Posición inicial de los resultados (para paginación).
        limit (int): Número máximo de resultados a devolver.

    Returns:
        str: Lista de clientes encontrados con información completa.
    """
    try:
        print(f"👤 Buscando clientes con nombre: '{nombre}'")
        
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
                c.full_name AS nombre,
                c.company AS empresa,
                c.unique_id AS documento,
                c.address AS direccion,
                c.city AS ciudad,
                c.deparment AS departamento,
                c.phone AS telefono
            FROM public.clients c
            WHERE COALESCE(NULLIF(c.full_name, ''), '') <> ''
              AND (
                c.full_name ILIKE %s 
                OR c.company ILIKE %s 
                OR c.unique_id ILIKE %s
              )
            ORDER BY c.full_name
            OFFSET %s
            LIMIT %s
        """
        
        patron_busqueda = f"%{nombre}%" if nombre else "%%"

        cursor.execute(query, (patron_busqueda, patron_busqueda, patron_busqueda, offset, limit))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return "No se encontraron clientes con los criterios especificados."

        # Si se busca un nombre específico y hay pocos resultados, mostrar información detallada
        if nombre and len(resultados) <= 3:
            respuesta = []
            for id_cliente, nombre_cliente, empresa, documento, direccion, ciudad, departamento, telefono in resultados:
                # Formatear información de manera clara
                info_cliente = f"🆔 ID: {id_cliente} | 👤 Nombre: {nombre_cliente}"
                
                # Agregar información adicional si está disponible
                if empresa:
                    info_cliente += f" | 🏢 Empresa: {empresa}"
                if documento:
                    info_cliente += f" | 📄 Documento: {documento}"
                if direccion:
                    info_cliente += f" | 📍 Dirección: {direccion}"
                if ciudad:
                    info_cliente += f" | 🏙️ Ciudad: {ciudad}"
                if departamento:
                    info_cliente += f" | 🗺️ Departamento: {departamento}"
                if telefono:
                    info_cliente += f" | 📞 Teléfono: {telefono}"
                
                respuesta.append(info_cliente)
            
            if len(resultados) == 1:
                respuesta.insert(0, "✅ Cliente encontrado:")
            else:
                respuesta.insert(0, f"👥 Se encontraron {len(resultados)} clientes similares:")
                
            print(f"✅ Encontrados {len(resultados)} clientes")
            return "\n".join(respuesta)
        else:
            # Para búsquedas generales o muchos resultados, mostrar información básica
            respuesta = []
            for id_cliente, nombre_cliente, empresa, documento, direccion, ciudad, departamento, telefono in resultados:
                # Formatear información básica
                info_cliente = f"🆔 ID: {id_cliente} | 👤 Nombre: {nombre_cliente}"
                
                # Agregar información adicional si está disponible
                if empresa:
                    info_cliente += f" | 🏢 Empresa: {empresa}"
                if documento:
                    info_cliente += f" | 📄 Documento: {documento}"
                if direccion:
                    info_cliente += f" | 📍 Dirección: {direccion}"
                if ciudad:
                    info_cliente += f" | 🏙️ Ciudad: {ciudad}"
                if departamento:
                    info_cliente += f" | 🗺️ Departamento: {departamento}"
                if telefono:
                    info_cliente += f" | 📞 Teléfono: {telefono}"
                
                respuesta.append(info_cliente)

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
        error_msg = f"❌ Error al consultar cuotas pendientes: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

from decimal import Decimal
from datetime import datetime, timedelta

@tool
def consultar_productos(nombre: str = "", offset: int = 0, limit: int = 10) -> str:
    """
    Devuelve una lista de productos filtrados por nombre (opcional) con paginación.

    Args:
        nombre (str): Nombre o parte del nombre del producto a buscar. Puede estar vacío para traer todos.
        offset (int): Posición inicial de los resultados (para paginación).
        limit (int): Número máximo de resultados a devolver.

    Returns:
        str: Lista de productos encontrados con su ID, nombre, descripción y categoría.
    """
    try:
        print(f"🔍 Buscando productos con nombre: '{nombre}'")
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                p.id_product,
                p.name_product,
                p.description,
                p.id_category,
                c.name_category AS category_name
            FROM 
                public.products p
            LEFT JOIN 
                public.category c
            ON 
                p.id_category = c.id_category
            WHERE p.name_product ILIKE %s
            ORDER BY p.name_product
            OFFSET %s
            LIMIT %s
        """
        
        patron_busqueda = f"%{nombre}%" if nombre else "%%"

        cursor.execute(query, (patron_busqueda, offset, limit))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return "No se encontraron productos con los criterios especificados."

        respuesta = []
        for id_producto, nombre_producto, descripcion, id_categoria, nombre_categoria in resultados:
            categoria = nombre_categoria if nombre_categoria else "Sin categoría"
            respuesta.append(f"🆔 ID: {id_producto} | 📦 Producto: {nombre_producto} | 📝 Descripción: {descripcion} | 🏷️ Categoría: {categoria}")

        print(f"✅ Encontrados {len(resultados)} productos")
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"Error al consultar productos: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"

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
        error_msg = f"❌ Error al obtener id_sales_orders: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def obtener_id_client_por_orden(id_sales_orders: int) -> str:
    """
    Obtiene el id_client asociado a una orden de venta específica.

    Args:
        id_sales_orders (int): ID de la orden de venta.

    Returns:
        str: El id_client asociado a la orden o mensaje de error.
    """
    try:
        if not isinstance(id_sales_orders, int) or id_sales_orders <= 0:
            return "El ID de la orden de venta debe ser un número entero positivo."

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT id_client
            FROM public.sales_orders
            WHERE id_sales_orders = %s;
        """
        cursor.execute(query, (id_sales_orders,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return f"No se encontró la orden de venta con ID {id_sales_orders}."

        id_client = result[0]
        return f"ID de cliente: {id_client}"

    except Exception as e:
        error_msg = f"❌ Error al obtener id_client: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def registrar_pago(
    id_sales_orders: int,
    id_payment_installment: int,
    amount: float,
    metodo_pago: str,
    id_client: int,
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
         id_client (int): ID del cliente
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

        # === Determinar valor de caja_receipt ===
        caja_receipt = 'Yes' if metodo_pago == "efectivo" else None
        
        # === Insertar en payments ===
        cursor.execute("""
            INSERT INTO payments (id_sales_orders, id_payment_installment, amount, payment_method, payment_date, destiny_bank, caja_receipt, id_client)
            VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s, %s)
            RETURNING id_payment;
        """, (
            id_sales_orders, id_payment_installment, amount, metodo_pago.capitalize(), destiny_bank, caja_receipt, id_client
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
            WHERE id_payment_installment = %s
            RETURNING pay_amount;
        """, (amount, id_payment_installment))
        
        nuevo_acumulado = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return (
            f"✅ Pago registrado correctamente.\n"
            f"ID Payment: {id_payment}\n"
            f"Nuevo acumulado en la cuota: {nuevo_acumulado}"
        )

    except Exception as e:
        error_msg = f"❌ Error al registrar el pago: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_orden_venta(
    id_client: int,
    id_classification: int,
    total: float,
    discount: float = 0.0,
    order_date: str = None
) -> str:
    """
    Crea una nueva orden de venta en la base de datos.

    Args:
        id_client (int): ID del cliente
        id_classification (int): ID de la clasificación
        total (float): Total de la orden
        discount (float, optional): Descuento aplicado. Default 0.0
        order_date (str, optional): Fecha de la orden en formato YYYY-MM-DD. Si no se proporciona, usa CURRENT_DATE

    Returns:
        str: ID de la orden creada o mensaje de error
    """
    try:
        if not isinstance(id_client, int) or id_client <= 0:
            return "❌ El ID del cliente debe ser un número entero positivo."
        
        if not isinstance(id_classification, int) or id_classification <= 0:
            return "❌ El ID de clasificación debe ser un número entero positivo."
        
        if not isinstance(total, (int, float)) or total <= 0:
            return "❌ El total debe ser un número mayor que 0."
        
        if not isinstance(discount, (int, float)) or discount < 0:
            return "❌ El descuento debe ser un número mayor o igual a 0."

        conn = get_db_connection()
        cursor = conn.cursor()

        # Si no se proporciona fecha, usar CURRENT_DATE
        if not order_date:
            order_date = "CURRENT_DATE"
            query = """
                INSERT INTO sales_orders (
                    id_client,
                    id_classification,
                    order_date,
                    total,
                    discount
                )
                VALUES (
                    %s, %s, CURRENT_DATE, %s, %s
                )
                RETURNING id_sales_orders;
            """
            cursor.execute(query, (id_client, id_classification, total, discount))
        else:
            query = """
                INSERT INTO sales_orders (
                    id_client,
                    id_classification,
                    order_date,
                    total,
                    discount
                )
                VALUES (
                    %s, %s, %s, %s, %s
                )
                RETURNING id_sales_orders;
            """
            cursor.execute(query, (id_client, id_classification, order_date, total, discount))

        id_sales_orders = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return f"✅ Orden de venta creada exitosamente.\n🆔 ID de la orden: {id_sales_orders}"

    except Exception as e:
        error_msg = f"❌ Error al crear la orden de venta: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def registrar_pago_directo_orden(
    id_sales_orders: int,
    amount: float,
    metodo_pago: str,
    id_client: int,
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
    Registra un pago directo a una orden de venta (sin payment_plan).
    Este pago se registra solo en la tabla payments con id_payment_installment = NULL.
    
         Args:
         id_sales_orders (int): ID de la orden de venta
         amount (float): Monto del pago
         metodo_pago (str): Método de pago (efectivo, transferencia, cheque)
         id_client (int): ID del cliente
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
            trans_value = amount  # Copiar automáticamente

        # === Ajustar amount en caso de cheque ===
        if metodo_pago == "cheque":
            if cheque_value is None:
                return "❌ Debes indicar el valor del cheque."
            amount = cheque_value

        # === Determinar valor de caja_receipt ===
        caja_receipt = 'Yes' if metodo_pago == "efectivo" else None
        
        # === Insertar en payments con id_payment_installment = NULL ===
        cursor.execute("""
            INSERT INTO payments (id_sales_orders, id_payment_installment, amount, payment_method, payment_date, destiny_bank, caja_receipt, id_client)
            VALUES (%s, NULL, %s, %s, CURRENT_DATE, %s, %s, %s)
            RETURNING id_payment;
        """, (
            id_sales_orders, amount, metodo_pago.capitalize(), destiny_bank, caja_receipt, id_client
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

        conn.commit()
        conn.close()

        return (
            f"✅ Pago directo registrado correctamente a la orden {id_sales_orders}.\n"
            f"ID Payment: {id_payment}\n"
            f"Monto: {amount}"
        )

    except Exception as e:
        error_msg = f"❌ Error al registrar el pago directo: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def agregar_detalle_orden_venta(
    id_sales_orders: int,
    id_product: int,
    quantity: int,
    unit_price: float
) -> str:
    """
    Agrega un detalle (producto) a una orden de venta existente.

    Args:
        id_sales_orders (int): ID de la orden de venta
        id_product (int): ID del producto
        quantity (int): Cantidad del producto
        unit_price (float): Precio unitario del producto

    Returns:
        str: Confirmación de la operación o mensaje de error
    """
    try:
        if not isinstance(id_sales_orders, int) or id_sales_orders <= 0:
            return "❌ El ID de la orden de venta debe ser un número entero positivo."
        
        if not isinstance(id_product, int) or id_product <= 0:
            return "❌ El ID del producto debe ser un número entero positivo."
        
        if not isinstance(quantity, int) or quantity <= 0:
            return "❌ La cantidad debe ser un número entero positivo."
        
        if not isinstance(unit_price, (int, float)) or unit_price <= 0:
            return "❌ El precio unitario debe ser un número mayor que 0."

        # Calcular subtotal
        subtotal = quantity * unit_price

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verificar que la orden de venta existe
        cursor.execute("SELECT id_sales_orders FROM sales_orders WHERE id_sales_orders = %s", (id_sales_orders,))
        if not cursor.fetchone():
            conn.close()
            return f"❌ No se encontró la orden de venta con ID {id_sales_orders}."

        # Verificar que el producto existe
        cursor.execute("SELECT name_product FROM products WHERE id_product = %s", (id_product,))
        producto = cursor.fetchone()
        if not producto:
            conn.close()
            return f"❌ No se encontró el producto con ID {id_product}."

        # Insertar el detalle
        query = """
            INSERT INTO sales_order_details (
                id_sales_orders,
                id_product,
                quantity,
                unit_price,
                subtotal
            )
            VALUES (
                %s, %s, %s, %s, %s
            )
            RETURNING id_sales_order_detail;
        """
        cursor.execute(query, (id_sales_orders, id_product, quantity, unit_price, subtotal))
        id_sales_order_detail = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return f"✅ Detalle agregado exitosamente a la orden {id_sales_orders}.\n📦 Producto: {producto[0]}\n📊 Cantidad: {quantity}\n💰 Precio unitario: {unit_price}\n💵 Subtotal: {subtotal}\n🆔 ID del detalle: {id_sales_order_detail}"

    except Exception as e:
        error_msg = f"❌ Error al agregar el detalle a la orden: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def buscar_producto_por_nombre(nombre_producto: str) -> str:
    """
    Busca un producto específico por nombre y devuelve su información completa.
    Esta herramienta es útil para obtener el ID correcto de un producto antes de crear sales_order_details.

    Args:
        nombre_producto (str): Nombre del producto a buscar (búsqueda flexible)

    Returns:
        str: Información completa del producto encontrado o mensaje de error
    """
    try:
        if not nombre_producto or not nombre_producto.strip():
            return "❌ Debes proporcionar el nombre del producto a buscar."

        print(f"🔍 Buscando producto específico: '{nombre_producto}'")
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            SELECT 
                p.id_product,
                p.name_product,
                p.description,
                p.id_category,
                c.name_category AS category_name
            FROM 
                public.products p
            LEFT JOIN 
                public.category c ON p.id_category = c.id_category
            WHERE p.name_product ILIKE %s
            ORDER BY p.name_product
            LIMIT 5
        """
        
        patron_busqueda = f"%{nombre_producto.strip()}%"
        cursor.execute(query, (patron_busqueda,))
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return f"❌ No se encontró ningún producto con el nombre '{nombre_producto}'."

        if len(resultados) == 1:
            # Producto único encontrado
            id_producto, nombre_producto, descripcion, id_categoria, nombre_categoria = resultados[0]
            categoria = nombre_categoria if nombre_categoria else "Sin categoría"
            return (
                f"✅ Producto encontrado:\n"
                f"🆔 ID: {id_producto}\n"
                f"📦 Nombre: {nombre_producto}\n"
                f"📝 Descripción: {descripcion}\n"
                f"🏷️ Categoría: {categoria}"
            )
        else:
            # Múltiples productos encontrados
            respuesta = [f"🔍 Se encontraron {len(resultados)} productos similares a '{nombre_producto}':"]
            for id_producto, nombre_producto, descripcion, id_categoria, nombre_categoria in resultados:
                categoria = nombre_categoria if nombre_categoria else "Sin categoría"
                respuesta.append(
                    f"🆔 ID: {id_producto} | 📦 {nombre_producto} | 📝 {descripcion} | 🏷️ {categoria}"
                )
            respuesta.append("\n💡 Por favor, especifica el nombre exacto del producto que deseas usar.")
            return "\n".join(respuesta)

    except Exception as e:
        error_msg = f"❌ Error al buscar el producto: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_plan_financiamiento(
    id_sales_orders: int,
    num_installments: int,
    total_amount: float,
    start_date: str,
    frequency: str,
    notes: str = None,
    type_payment_plan: str = "Otro plan de financiamiento"
) -> str:
    """
    Crea un plan de financiamiento para una orden de venta específica.
    
    Args:
        id_sales_orders (int): ID de la orden de venta
        num_installments (int): Número de cuotas
        total_amount (float): Monto total del plan
        start_date (str): Fecha de inicio en formato YYYY-MM-DD
        frequency (str): Frecuencia de pago (Mensual, Quincenal, Semanal, etc.)
        notes (str, optional): Notas adicionales del plan
        type_payment_plan (str, optional): Tipo de plan de pago. Default "Otro plan de financiamiento"
    
    Returns:
        str: ID del plan creado o mensaje de error
    """
    try:
        if not isinstance(id_sales_orders, int) or id_sales_orders <= 0:
            return "❌ El ID de la orden de venta debe ser un número entero positivo."
        
        if not isinstance(num_installments, int) or num_installments <= 0:
            return "❌ El número de cuotas debe ser un número entero positivo."
        
        if not isinstance(total_amount, (int, float)) or total_amount <= 0:
            return "❌ El monto total debe ser un número mayor que 0."
        
        # Validar formato de fecha
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return "❌ La fecha debe estar en formato YYYY-MM-DD."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la orden de venta existe
        cursor.execute("SELECT id_sales_orders FROM sales_orders WHERE id_sales_orders = %s", (id_sales_orders,))
        if not cursor.fetchone():
            conn.close()
            return f"❌ No se encontró la orden de venta con ID {id_sales_orders}."
        
        # Calcular monto por cuota
        amount_per_installment = total_amount / num_installments
        
        # Insertar el plan de financiamiento
        query = """
            INSERT INTO payment_plan (
                id_sales_orders,
                num_installments,
                total_amount,
                start_date,
                frequency,
                notes,
                pending_amount,
                type_payment_plan,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente'
            )
            RETURNING id_payment_plan;
        """
        
        pending_amount = total_amount * (-1)  # Monto pendiente negativo
        
        cursor.execute(query, (
            id_sales_orders, num_installments, total_amount, start_date, 
            frequency, notes, pending_amount, type_payment_plan
        ))
        
        id_payment_plan = cursor.fetchone()[0]
        
        # Crear las cuotas automáticamente
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(1, num_installments + 1):
            # Calcular fecha de vencimiento según la frecuencia
            if frequency.lower() == "mensual":
                due_date = start_date_obj + timedelta(days=30 * i)
            elif frequency.lower() == "quincenal":
                due_date = start_date_obj + timedelta(days=15 * i)
            elif frequency.lower() == "semanal":
                due_date = start_date_obj + timedelta(weeks=i)
            else:
                # Por defecto, mensual
                due_date = start_date_obj + timedelta(days=30 * i)
            
            # Insertar la cuota
            cursor.execute("""
                INSERT INTO payment_installment (
                    id_payment_plan,
                    installment_number,
                    amount,
                    due_date,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, 'Pendiente'
                );
            """, (id_payment_plan, i, amount_per_installment, due_date.strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        return (
            f"✅ Plan de financiamiento creado exitosamente.\n"
            f"🆔 ID del plan: {id_payment_plan}\n"
            f"🛒 Orden de venta: {id_sales_orders}\n"
            f"📊 Número de cuotas: {num_installments}\n"
            f"💰 Monto total: {total_amount}\n"
            f"💵 Monto por cuota: {amount_per_installment:.2f}\n"
            f"📅 Fecha de inicio: {start_date}\n"
            f"🔄 Frecuencia: {frequency}\n"
            f"📝 Tipo: {type_payment_plan}\n"
            f"📋 Estado: Pendiente"
        )

    except Exception as e:
        error_msg = f"❌ Error al crear el plan de financiamiento: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_nuevo_cliente(
    unique_id: str,
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    client_type: str,
    company: str = "",
    phone_2: str = "",
    city: str = "",
    department: str = "",
    address: str = ""
) -> str:
    """
    Crea un nuevo cliente en la base de datos con la información proporcionada.
    
    Args:
        unique_id (str): Número de documento único del cliente (obligatorio)
        first_name (str): Nombre del cliente (obligatorio)
        last_name (str): Apellido del cliente (obligatorio)
        email (str): Correo electrónico del cliente (obligatorio)
        phone (str): Número de teléfono principal (obligatorio)
        client_type (str): Tipo de cliente - "Empresa" o "Persona natural" (obligatorio)
        company (str): Nombre de la empresa (obligatorio solo si client_type es "Empresa")
        phone_2 (str): Número de teléfono secundario (opcional)
        city (str): Ciudad del cliente (obligatorio)
        department (str): Departamento del cliente (obligatorio)
        address (str): Dirección del cliente (obligatorio)
    
    Returns:
        str: Confirmación de la creación del cliente con su ID asignado
    """
    try:
        print(f"👤 Creando nuevo cliente: {first_name} {last_name}")
        
        # Validar campos obligatorios
        if not unique_id or not first_name or not last_name or not email or not phone or not client_type or not city or not department or not address:
            return "❌ Error: Los campos unique_id, first_name, last_name, email, phone, client_type, city, department y address son obligatorios."
        
        # Validar client_type
        if client_type not in ["Empresa", "Persona natural"]:
            return "❌ Error: El client_type debe ser 'Empresa' o 'Persona natural'."
        
        # Validar company según client_type
        if client_type == "Empresa" and not company:
            return "❌ Error: Si el tipo de cliente es 'Empresa', el nombre de la empresa es obligatorio."
        
        # Verificar si el cliente ya existe
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe un cliente con el mismo unique_id
        cursor.execute("""
            SELECT id_client, full_name FROM public.clients 
            WHERE unique_id = %s
        """, (unique_id,))
        
        existing_client = cursor.fetchone()
        if existing_client:
            conn.close()
            return f"❌ Ya existe un cliente con el documento {unique_id}: {existing_client[1]} (ID: {existing_client[0]})"
        
        # Usar el client_type proporcionado por el usuario
        
        # Construir el nombre completo
        full_name = f"{first_name} {last_name}".strip()
        
        # Insertar el nuevo cliente
        query = """
            INSERT INTO clients (
                unique_id,
                client_type,
                email,
                full_name,
                first_name,
                last_name,
                company,
                phone,
                phone_2,
                city,
                deparment,
                address
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id_client;
        """
        
        cursor.execute(query, (
            unique_id,
            client_type,
            email,
            full_name,
            first_name,
            last_name,
            company,
            phone,
            phone_2,
            city,
            department,
            address
        ))
        
        id_client = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        # Construir mensaje de confirmación
        confirmacion = f"✅ Cliente creado exitosamente.\n"
        confirmacion += f"🆔 ID del cliente: {id_client}\n"
        confirmacion += f"👤 Nombre: {full_name}\n"
        confirmacion += f"📄 Documento: {unique_id}\n"
        confirmacion += f"🏷️ Tipo: {client_type}\n"
        
        if company:
            confirmacion += f"🏢 Empresa: {company}\n"
        if email:
            confirmacion += f"📧 Email: {email}\n"
        if phone:
            confirmacion += f"📞 Teléfono: {phone}\n"
        if phone_2:
            confirmacion += f"📱 Teléfono 2: {phone_2}\n"
        if city:
            confirmacion += f"🏙️ Ciudad: {city}\n"
        if department:
            confirmacion += f"🗺️ Departamento: {department}\n"
        if address:
            confirmacion += f"📍 Dirección: {address}\n"
        
        print(f"✅ Cliente creado con ID: {id_client}")
        return confirmacion
        
    except Exception as e:
        error_msg = f"❌ Error al crear el cliente: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_plan_letras(
    id_sales_orders: int,
    num_installments: int,
    total_amount: float,
    start_date: str,
    frequency: str,
    letra_number: int,
    notes: str = None
) -> str:
    """
    Crea un plan de financiamiento tipo "Letras" para una orden de venta específica.
    Crea el payment_plan, los payment_installment y la letra correspondiente.
    
    Args:
        id_sales_orders (int): ID de la orden de venta
        num_installments (int): Número de cuotas
        total_amount (float): Monto total del plan
        start_date (str): Fecha de inicio en formato YYYY-MM-DD
        frequency (str): Frecuencia de pago (Mensual, Quincenal, Semanal, etc.)
        letra_number (int): Número de la letra
        notes (str, optional): Notas adicionales del plan
    
    Returns:
        str: ID del plan creado o mensaje de error
    """
    try:
        if not isinstance(id_sales_orders, int) or id_sales_orders <= 0:
            return "❌ El ID de la orden de venta debe ser un número entero positivo."
        
        if not isinstance(num_installments, int) or num_installments <= 0:
            return "❌ El número de cuotas debe ser un número entero positivo."
        
        if not isinstance(total_amount, (int, float)) or total_amount <= 0:
            return "❌ El monto total debe ser un número mayor que 0."
        
        # Validar formato de fecha
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            return "❌ La fecha debe estar en formato YYYY-MM-DD."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la orden de venta existe
        cursor.execute("SELECT id_sales_orders FROM sales_orders WHERE id_sales_orders = %s", (id_sales_orders,))
        if not cursor.fetchone():
            conn.close()
            return f"❌ No se encontró la orden de venta con ID {id_sales_orders}."
        
        # Validar letra_number
        if not isinstance(letra_number, int) or letra_number <= 0:
            return "❌ El número de letra debe ser un número entero positivo."
        
        # Calcular monto por cuota
        amount_per_installment = total_amount / num_installments
        
        # Insertar el plan de financiamiento tipo "Letra"
        query = """
            INSERT INTO payment_plan (
                id_sales_orders,
                num_installments,
                total_amount,
                start_date,
                frequency,
                notes,
                pending_amount,
                type_payment_plan,
                status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, 'Pendiente'
            )
            RETURNING id_payment_plan;
        """
        
        pending_amount = total_amount * (-1)  # Monto pendiente negativo
        type_payment_plan = "Letra"
        
        cursor.execute(query, (
            id_sales_orders, num_installments, total_amount, start_date, 
            frequency, notes, pending_amount, type_payment_plan
        ))
        
        id_payment_plan = cursor.fetchone()[0]
        
        # Crear las cuotas automáticamente
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        
        for i in range(1, num_installments + 1):
            # Calcular fecha de vencimiento según la frecuencia
            if frequency.lower() == "mensual":
                due_date = start_date_obj + timedelta(days=30 * i)
            elif frequency.lower() == "quincenal":
                due_date = start_date_obj + timedelta(days=15 * i)
            elif frequency.lower() == "semanal":
                due_date = start_date_obj + timedelta(weeks=i)
            else:
                # Por defecto, mensual
                due_date = start_date_obj + timedelta(days=30 * i)
            
            # Insertar la cuota
            cursor.execute("""
                INSERT INTO payment_installment (
                    id_payment_plan,
                    installment_number,
                    amount,
                    due_date,
                    status
                )
                VALUES (
                    %s, %s, %s, %s, 'Pendiente'
                );
            """, (id_payment_plan, i, amount_per_installment, due_date.strftime('%Y-%m-%d')))
        
        # Crear la letra
        cursor.execute("""
            INSERT INTO letras (
                id_payment_plan,
                letra_number,
                last_date,
                status
            )
            VALUES (
                %s, %s, %s, 'Pendiente'
            );
        """, (id_payment_plan, letra_number, due_date.strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()
        
        return (
            f"✅ Plan de letras creado exitosamente.\n"
            f"🆔 ID del plan: {id_payment_plan}\n"
            f"🛒 Orden de venta: {id_sales_orders}\n"
            f"📊 Número de cuotas: {num_installments}\n"
            f"💰 Monto total: {total_amount}\n"
            f"💵 Monto por cuota: {amount_per_installment:.2f}\n"
            f"📅 Fecha de inicio: {start_date}\n"
            f"🔄 Frecuencia: {frequency}\n"
            f"📝 Tipo: Letra\n"
            f"📄 Número de letra: {letra_number}\n"
            f"📋 Estado: Pendiente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al crear el plan de letras: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def consultar_detalles_ordenes_cliente(id_client: int) -> str:
    """
    Consulta todos los detalles de órdenes de venta de un cliente específico, mostrando información completa
    incluyendo productos, cantidades, precios y estado de devoluciones.
    
    Args:
        id_client (int): ID del cliente
        
    Returns:
        str: Lista de detalles de órdenes con información completa
    """
    try:
        if not isinstance(id_client, int) or id_client <= 0:
            return "❌ El ID del cliente debe ser un número entero positivo."
        
        print(f"🔍 Consultando detalles de órdenes para cliente: {id_client}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consultar detalles de órdenes del cliente
        query = """
            SELECT 
                sod.id_sales_order_detail,
                sod.id_sales_orders,
                sod.id_product,
                sod.quantity,
                sod.unit_price,
                sod.subtotal,
                COALESCE(sod.devolucion, 'normal') as estado_devolucion,
                p.name_product,
                p.description,
                c.full_name,
                so.order_date,
                so.total as total_orden
            FROM sales_order_details sod
            JOIN products p ON sod.id_product = p.id_product
            JOIN sales_orders so ON sod.id_sales_orders = so.id_sales_orders
            JOIN clients c ON so.id_client = c.id_client
            WHERE so.id_client = %s
            ORDER BY so.order_date DESC, sod.id_sales_order_detail DESC
        """
        
        cursor.execute(query, (id_client,))
        detalles = cursor.fetchall()
        conn.close()
        
        if not detalles:
            return f"❌ No se encontraron detalles de órdenes para el cliente con ID {id_client}."
        
        # Construir respuesta
        respuesta = [f"📋 Detalles de órdenes para cliente: {detalles[0][9]} (ID: {id_client})"]
        respuesta.append("=" * 80)
        
        for detalle in detalles:
            id_detail, id_order, id_product, quantity, unit_price, subtotal, estado_devolucion, product_name, description, client_name, order_date, total_orden = detalle
            
            # Determinar emoji según estado de devolución
            estado_emoji = "🔄" if estado_devolucion == 'devolucion' else "✅"
            estado_texto = "DEVUELTO" if estado_devolucion == 'devolucion' else "NORMAL"
            
            respuesta.append(f"{estado_emoji} Detalle ID: {id_detail}")
            respuesta.append(f"   🛒 Orden: {id_order} | 📅 Fecha: {order_date}")
            respuesta.append(f"   📦 Producto: {product_name} (ID: {id_product})")
            respuesta.append(f"   📝 Descripción: {description}")
            respuesta.append(f"   📊 Cantidad: {quantity} | 💰 Precio unitario: {unit_price}")
            respuesta.append(f"   💵 Subtotal: {subtotal} | 🏷️ Estado: {estado_texto}")
            respuesta.append("-" * 60)
        
        respuesta.append(f"\n📊 Total de detalles encontrados: {len(detalles)}")
        
        print(f"✅ Encontrados {len(detalles)} detalles de órdenes para cliente {id_client}")
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"❌ Error al consultar detalles de órdenes: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def procesar_devolucion(id_sales_order_detail: int) -> str:
    """
    Procesa una devolución marcando un detalle específico de una orden de venta como devuelto.
    
    Args:
        id_sales_order_detail (int): ID del detalle de la orden de venta a devolver
        
    Returns:
        str: Confirmación de la devolución procesada o mensaje de error
    """
    try:
        if not isinstance(id_sales_order_detail, int) or id_sales_order_detail <= 0:
            return "❌ El ID del detalle de la orden debe ser un número entero positivo."
        
        print(f"🔄 Procesando devolución para detalle de orden: {id_sales_order_detail}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que el detalle existe y obtener información
        cursor.execute("""
            SELECT 
                sod.id_sales_order_detail,
                sod.id_sales_orders,
                sod.id_product,
                sod.quantity,
                sod.unit_price,
                sod.subtotal,
                p.name_product,
                c.full_name,
                c.id_client
            FROM sales_order_details sod
            JOIN products p ON sod.id_product = p.id_product
            JOIN sales_orders so ON sod.id_sales_orders = so.id_sales_orders
            JOIN clients c ON so.id_client = c.id_client
            WHERE sod.id_sales_order_detail = %s
        """, (id_sales_order_detail,))
        
        detalle = cursor.fetchone()
        if not detalle:
            conn.close()
            return f"❌ No se encontró el detalle de orden con ID {id_sales_order_detail}."
        
        # Verificar si ya está marcado como devolución
        cursor.execute("""
            SELECT devolucion FROM sales_order_details 
            WHERE id_sales_order_detail = %s
        """, (id_sales_order_detail,))
        
        estado_actual = cursor.fetchone()[0]
        if estado_actual == 'devolucion':
            conn.close()
            return f"❌ El detalle {id_sales_order_detail} ya está marcado como devolución."
        
        # Procesar la devolución
        cursor.execute("""
            UPDATE sales_order_details
            SET devolucion = 'devolucion'
            WHERE id_sales_order_detail = %s
        """, (id_sales_order_detail,))
        
        conn.commit()
        conn.close()
        
        # Construir mensaje de confirmación
        id_detail, id_order, id_product, quantity, unit_price, subtotal, product_name, client_name, id_client = detalle
        
        confirmacion = f"✅ Devolución procesada exitosamente.\n"
        confirmacion += f"🆔 ID del detalle: {id_detail}\n"
        confirmacion += f"🛒 Orden de venta: {id_order}\n"
        confirmacion += f"👤 Cliente: {client_name} (ID: {id_client})\n"
        confirmacion += f"📦 Producto: {product_name} (ID: {id_product})\n"
        confirmacion += f"📊 Cantidad devuelta: {quantity}\n"
        confirmacion += f"💰 Precio unitario: {unit_price}\n"
        confirmacion += f"💵 Subtotal devuelto: {subtotal}\n"
        confirmacion += f"🔄 Estado: Devolución procesada"
        
        print(f"✅ Devolución procesada para detalle {id_sales_order_detail}")
        return confirmacion
        
    except Exception as e:
        error_msg = f"❌ Error al procesar la devolución: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def buscar_clasificacion_por_tipo(tipo: str = "") -> str:
    """
    Busca clasificaciones en la base de datos por tipo (venta de producto o venta de servicio).
    Venta de producto: ID 1-5, Venta de servicio: ID 6-10

    Args:
        tipo (str): Tipo de clasificación ("producto" o "servicio")

    Returns:
        str: Lista de clasificaciones encontradas con su ID, nombre y primer apellido
    """
    try:
        print(f"🔍 Buscando clasificaciones por tipo: '{tipo}'")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        if tipo.lower() == "venta producto":
            query = """
                SELECT 
                    id_classification,
                    nombre,
                    primer_apellido
                FROM public.classification
                WHERE id_classification BETWEEN 1 AND 5
                ORDER BY nombre, primer_apellido
            """
        elif tipo.lower() == "venta servicio":
            query = """
                SELECT 
                    id_classification,
                    nombre,
                    primer_apellido
                FROM public.classification
                WHERE id_classification BETWEEN 6 AND 10
                ORDER BY nombre, primer_apellido
            """
        else:
            return "❌ Tipo inválido. Debe ser 'producto' o 'servicio'."

        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            return f"No se encontraron clasificaciones de {tipo} en la base de datos."

        # Formatear resultados
        respuesta = [f"📋 Clasificaciones de {tipo}:"]
        for id_clasificacion, nombre_clas, primer_apellido_clas in resultados:
            respuesta.append(f"{id_clasificacion}. {nombre_clas} {primer_apellido_clas}")

        print(f"✅ Encontradas {len(resultados)} clasificaciones de {tipo}")
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"Error al consultar clasificaciones por tipo: {str(e)}"
        print(f"❌ {error_msg}")
        return f"Error al consultar la base de datos: {str(e)}"

@tool
def gestionar_caja_conciliaciones(accion: str, tipo: str, saldo_caja: float = None, saldo_davivienda: float = None, saldo_bancolombia: float = None) -> str:
    """
    Gestiona la apertura y cierre de caja y conciliaciones bancarias.
    
    Args:
        accion (str): "abrir", "cerrar" o "consultar"
        tipo (str): "caja" (solo fila 1) o "conciliaciones" (filas 2 y 3)
        saldo_caja (float): Monto para caja (solo cuando tipo="caja" y accion="abrir")
        saldo_davivienda (float): Monto para banco Davivienda (solo cuando tipo="conciliaciones" y accion="abrir")
        saldo_bancolombia (float): Monto para banco Bancolombia (solo cuando tipo="conciliaciones" y accion="abrir")
    
    Returns:
        str: Confirmación de la operación realizada o estado actual
    """
    try:
        print(f"🔧 gestionar_caja_conciliaciones - Acción: {accion}, Tipo: {tipo}")
        print(f"🔧 Parámetros - saldo_caja: {saldo_caja}, saldo_davivienda: {saldo_davivienda}, saldo_bancolombia: {saldo_bancolombia}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Si es consulta, solo leer el estado actual
        if accion.lower() == "consultar":
            if tipo.lower() == "caja":
                # Consultar solo fila 1 (caja)
                query = "SELECT id, saldo_inicial, estado_caj FROM estado_caja WHERE id = 1"
                cursor.execute(query)
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    id_fila, saldo_inicial, estado_caj = result
                    estado_texto = "Abierta" if estado_caj else "Cerrada"
                    return f"📊 Estado actual de la caja:\n🔧 Estado: {estado_texto}\n💰 Saldo inicial: ${saldo_inicial:,.2f}"
                else:
                    return "❌ No se encontró información de la caja"
                    
            elif tipo.lower() == "conciliaciones":
                # Consultar filas 2 (Davivienda) y 3 (Bancolombia)
                query = "SELECT id, saldo_inicial, estado_caj FROM estado_caja WHERE id IN (2, 3) ORDER BY id"
                cursor.execute(query)
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    response = "📊 Estado actual de las conciliaciones:\n"
                    for id_fila, saldo_inicial, estado_caj in results:
                        banco = "Davivienda" if id_fila == 2 else "Bancolombia"
                        estado_texto = "Abierta" if estado_caj else "Cerrada"
                        response += f"🏦 {banco}:\n   🔧 Estado: {estado_texto}\n   💰 Saldo inicial: ${saldo_inicial:,.2f}\n"
                    return response
                else:
                    return "❌ No se encontró información de las conciliaciones"
            else:
                conn.close()
                return "❌ Tipo inválido para consulta. Debe ser 'caja' o 'conciliaciones'."
        
        # Validar parámetros según el tipo y la acción
        if accion.lower() == "abrir":
            if tipo.lower() == "caja":
                if saldo_caja is None:
                    return "❌ Para abrir caja, debes proporcionar el saldo_caja."
                print(f"💰 Abriendo {tipo} con saldo: {saldo_caja}")
            elif tipo.lower() == "conciliaciones":
                if saldo_davivienda is None or saldo_bancolombia is None:
                    return "❌ Para abrir conciliaciones, debes proporcionar saldo_davivienda y saldo_bancolombia."
                print(f"💰 Abriendo {tipo} - Davivienda: {saldo_davivienda}, Bancolombia: {saldo_bancolombia}")
            else:
                return "❌ Tipo inválido. Debe ser 'caja' o 'conciliaciones'."
        elif accion.lower() == "cerrar":
            if tipo.lower() not in ["caja", "conciliaciones"]:
                return "❌ Tipo inválido. Debe ser 'caja' o 'conciliaciones'."
            print(f"🔒 Cerrando {tipo}")
        else:
            conn.close()
            return "❌ Acción inválida. Debe ser 'abrir', 'cerrar' o 'consultar'."
        
        # Determinar el estado según la acción
        if accion.lower() == "abrir":
            estado_caj = True
        elif accion.lower() == "cerrar":
            estado_caj = False
        else:
            conn.close()
            return "❌ Acción inválida. Debe ser 'abrir' o 'cerrar'."
        
        # Determinar qué filas actualizar según el tipo
        if tipo.lower() == "caja":
            # Solo actualizar fila 1 (caja)
            ids_to_update = [1]
            saldos = [saldo_caja if accion.lower() == "abrir" else 0]
        elif tipo.lower() == "conciliaciones":
            # Actualizar filas 2 (Davivienda) y 3 (Bancolombia)
            ids_to_update = [2, 3]
            saldos = [
                saldo_davivienda if accion.lower() == "abrir" else 0,
                saldo_bancolombia if accion.lower() == "abrir" else 0
            ]
        
        print(f"🔧 Filas a actualizar: {ids_to_update}")
        print(f"🔧 Saldos a usar: {saldos}")
        print(f"🔧 Estado final: {estado_caj}")
        
        # Ejecutar las actualizaciones
        for i, id_fila in enumerate(ids_to_update):
            query = """
                INSERT INTO estado_caja
                (id, saldo_inicial, estado_caj)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET 
                    saldo_inicial = EXCLUDED.saldo_inicial,
                    updated_at = NOW(),
                    estado_caj = EXCLUDED.estado_caj
            """
            
            print(f"🔧 Actualizando fila {id_fila} con saldo: {saldos[i]}, estado_caj: {estado_caj}")
            print(f"🔧 Query SQL: {query}")
            print(f"🔧 Parámetros: id={id_fila}, saldo={saldos[i]}, estado_caj={estado_caj}")
            
            cursor.execute(query, (id_fila, saldos[i], estado_caj))
            
            # Verificar que la actualización fue exitosa
            verify_query = "SELECT id, saldo_inicial, estado_caj FROM estado_caja WHERE id = %s"
            cursor.execute(verify_query, (id_fila,))
            result = cursor.fetchone()
            print(f"✅ Fila {id_fila} actualizada exitosamente - Verificación: {result}")
        
        conn.commit()
        conn.close()
        
        # Determinar el texto del estado para mostrar
        estado_texto = "Abierta" if estado_caj else "Cerrada"
        
        # Construir mensaje según el tipo y la acción
        if tipo.lower() == "caja":
            if accion.lower() == "abrir":
                return f"✅ Caja {estado_texto.lower()} exitosamente\n💰 Saldo inicial: ${saldo_caja:,.2f}\n🎯 Operación completada exitosamente."
            else:  # cerrar
                return f"✅ Caja {estado_texto.lower()} exitosamente\n🎯 Operación completada exitosamente."
        elif tipo.lower() == "conciliaciones":
            if accion.lower() == "abrir":
                return f"✅ Conciliaciones {estado_texto.lower()}s exitosamente\n💰 Saldo Davivienda: ${saldo_davivienda:,.2f}\n💰 Saldo Bancolombia: ${saldo_bancolombia:,.2f}\n🎯 Operación completada exitosamente."
            else:  # cerrar
                return f"✅ Conciliaciones {estado_texto.lower()}s exitosamente\n🎯 Operación completada exitosamente."
        
    except Exception as e:
        print(f"❌ Error en gestionar_caja_conciliaciones: {str(e)}")
        return f"❌ Error al gestionar {tipo}: {str(e)}"

@tool
def consultar_usuario_autorizado(phone: str) -> str:
    """
    Consulta si un número de teléfono está autorizado para usar el agente desde la tabla users_agent en Supabase.
    Verifica el tipo de usuario (Administrador o Secundario) y su estado activo.
    
    Args:
        phone (str): Número de teléfono a consultar (formato: 573195792747)
        
    Returns:
        str: Información del usuario autorizado o mensaje de no autorizado
    """
    try:
        print(f"🔍 Consultando autorización para teléfono: {phone}")
        
        # Validar formato del teléfono
        if not phone or not phone.isdigit() or len(phone) < 10:
            return "❌ Formato de teléfono inválido. Debe ser un número de al menos 10 dígitos."
        
        # Conectar a Supabase
        supabase = get_supabase_client()
        
        # Consultar en la tabla users_agent
        response = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("phone", phone).execute()
        
        if not response.data:
            print(f"❌ Usuario no encontrado para teléfono: {phone}")
            return f"❌ El número {phone} no está autorizado para usar el agente."
        
        user_data = response.data[0]
        phone_db = user_data.get("phone")
        name = user_data.get("name", "Sin nombre")
        user_type = user_data.get("type")
        status = user_data.get("status")
        
        print(f"✅ Usuario encontrado: {name} - Tipo: {user_type} - Status: {status}")
        
        # Verificar si el usuario está activo
        if not status:
            return f"❌ El usuario {name} ({phone}) no está activo en el sistema."
        
        # Construir respuesta según el tipo de usuario
        if user_type == "Administrador":
            return (
                f"✅ USUARIO AUTORIZADO - ADMINISTRADOR\n"
                f"👤 Nombre: {name}\n"
                f"📞 Teléfono: {phone}\n"
                f"🔑 Tipo: {user_type}\n"
                f"🟢 Estado: Activo\n"
                f"💬 Acceso completo al agente"
            )
        elif user_type == "Secundario":
            return (
                f"✅ USUARIO AUTORIZADO - SECUNDARIO\n"
                f"👤 Nombre: {name}\n"
                f"📞 Teléfono: {phone}\n"
                f"🔑 Tipo: {user_type}\n"
                f"🟢 Estado: Activo\n"
                f"💬 Acceso limitado al agente (asignado por administrador)"
            )
        else:
            return (
                f"⚠️ USUARIO CON TIPO DESCONOCIDO\n"
                f"👤 Nombre: {name}\n"
                f"📞 Teléfono: {phone}\n"
                f"🔑 Tipo: {user_type}\n"
                f"🟢 Estado: Activo\n"
                f"❓ Tipo de usuario no reconocido"
            )
        
    except Exception as e:
        error_msg = f"❌ Error al consultar usuario autorizado: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def listar_usuarios_autorizados() -> str:
    """
    Lista todos los usuarios autorizados en la tabla users_agent de Supabase.
    Muestra información de administradores y usuarios secundarios activos.
    
    Returns:
        str: Lista de todos los usuarios autorizados con su información
    """
    try:
        print("🔍 Listando todos los usuarios autorizados")
        
        # Conectar a Supabase
        supabase = get_supabase_client()
        
        # Consultar todos los usuarios activos
        response = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("status", True).order("type", desc=False).execute()
        
        if not response.data:
            return "❌ No se encontraron usuarios autorizados en el sistema."
        
        users = response.data
        print(f"✅ Encontrados {len(users)} usuarios autorizados")
        
        # Separar por tipo
        administradores = [user for user in users if user.get("type") == "Administrador"]
        secundarios = [user for user in users if user.get("type") == "Secundario"]
        otros = [user for user in users if user.get("type") not in ["Administrador", "Secundario"]]
        
        # Construir respuesta
        respuesta = ["📋 LISTA DE USUARIOS AUTORIZADOS"]
        respuesta.append("=" * 50)
        
        if administradores:
            respuesta.append(f"\n👑 ADMINISTRADORES ({len(administradores)}):")
            for user in administradores:
                respuesta.append(f"  👤 {user.get('name', 'Sin nombre')}")
                respuesta.append(f"  📞 {user.get('phone')}")
                respuesta.append("  🔑 Tipo: Administrador")
                respuesta.append("  🟢 Estado: Activo")
                respuesta.append("  " + "-" * 30)
        
        if secundarios:
            respuesta.append(f"\n👥 USUARIOS SECUNDARIOS ({len(secundarios)}):")
            for user in secundarios:
                respuesta.append(f"  👤 {user.get('name', 'Sin nombre')}")
                respuesta.append(f"  📞 {user.get('phone')}")
                respuesta.append("  🔑 Tipo: Secundario")
                respuesta.append("  🟢 Estado: Activo")
                respuesta.append("  " + "-" * 30)
        
        if otros:
            respuesta.append(f"\n❓ OTROS TIPOS ({len(otros)}):")
            for user in otros:
                respuesta.append(f"  👤 {user.get('name', 'Sin nombre')}")
                respuesta.append(f"  📞 {user.get('phone')}")
                respuesta.append(f"  🔑 Tipo: {user.get('type', 'Desconocido')}")
                respuesta.append("  🟢 Estado: Activo")
                respuesta.append("  " + "-" * 30)
        
        respuesta.append(f"\n📊 RESUMEN:")
        respuesta.append(f"  • Total de usuarios activos: {len(users)}")
        respuesta.append(f"  • Administradores: {len(administradores)}")
        respuesta.append(f"  • Usuarios secundarios: {len(secundarios)}")
        respuesta.append(f"  • Otros tipos: {len(otros)}")
        
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"❌ Error al listar usuarios autorizados: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def asignar_usuario_secundario(nombre: str, telefono: str, asignado_por: str) -> str:
    """
    Asigna un nuevo usuario secundario al agente. Solo los administradores pueden usar esta herramienta.
    Crea un nuevo registro en la tabla users_agent con tipo 'Secundario' y status activo.
    
    Args:
        nombre (str): Nombre completo del usuario a asignar
        telefono (str): Número de teléfono del usuario (formato: 573195792747)
        asignado_por (str): Número de teléfono del administrador que hace la asignación
        
    Returns:
        str: Confirmación de la asignación o mensaje de error
    """
    try:
        print(f"👤 Asignando usuario secundario: {nombre} - {telefono}")
        print(f"🔑 Asignado por administrador: {asignado_por}")
        
        # Validar que quien asigna sea administrador
        supabase = get_supabase_client()
        
        # Verificar que el asignador sea administrador
        admin_check = supabase.table("users_agent").select(
            "type, status"
        ).eq("phone", asignado_por).execute()
        
        if not admin_check.data:
            return f"❌ Error: El número {asignado_por} no está registrado en el sistema."
        
        admin_data = admin_check.data[0]
        if admin_data.get("type") != "Administrador":
            return f"❌ Error: Solo los administradores pueden asignar usuarios secundarios."
        
        if not admin_data.get("status"):
            return f"❌ Error: El administrador no está activo en el sistema."
        
        # Validar formato del teléfono
        if not telefono or not telefono.isdigit() or len(telefono) < 10:
            return "❌ Formato de teléfono inválido. Debe ser un número de al menos 10 dígitos."
        
        # Verificar si el usuario ya existe
        existing_user = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("phone", telefono).execute()
        
        if existing_user.data:
            user_data = existing_user.data[0]
            if user_data.get("status"):
                return f"❌ El número {telefono} ya está registrado como usuario activo: {user_data.get('name')} ({user_data.get('type')})"
            else:
                # Si existe pero está inactivo, reactivarlo como secundario
                supabase.table("users_agent").update({
                    "name": nombre,
                    "type": "Secundario",
                    "status": True
                }).eq("phone", telefono).execute()
                
                return (
                    f"✅ Usuario reactivado exitosamente.\n"
                    f"👤 Nombre: {nombre}\n"
                    f"📞 Teléfono: {telefono}\n"
                    f"🔑 Tipo: Secundario\n"
                    f"🟢 Estado: Activo\n"
                    f"👑 Asignado por: {asignado_por}\n"
                    f"💬 El usuario ahora puede interactuar con el agente"
                )
        
        # Crear nuevo usuario secundario
        new_user = {
            "phone": telefono,
            "name": nombre,
            "type": "Secundario",
            "status": True
        }
        
        supabase.table("users_agent").insert(new_user).execute()
        
        return (
            f"✅ Usuario secundario asignado exitosamente.\n"
            f"👤 Nombre: {nombre}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🔑 Tipo: Secundario\n"
            f"🟢 Estado: Activo\n"
            f"👑 Asignado por: {asignado_por}\n"
            f"💬 El usuario ahora puede interactuar con el agente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al asignar usuario secundario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def buscar_usuario_por_nombre(nombre: str) -> str:
    """
    Busca usuarios en la tabla users_agent por nombre (búsqueda flexible).
    
    Args:
        nombre (str): Nombre o parte del nombre del usuario a buscar
        
    Returns:
        str: Información de los usuarios encontrados
    """
    try:
        print(f"🔍 Buscando usuario por nombre: '{nombre}'")
        
        if not nombre or not nombre.strip():
            return "❌ Debes proporcionar un nombre para buscar."
        
        supabase = get_supabase_client()
        
        # Búsqueda flexible por nombre (ILIKE para PostgreSQL)
        response = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).ilike("name", f"%{nombre.strip()}%").execute()
        
        if not response.data:
            return f"❌ No se encontraron usuarios con el nombre '{nombre}'."
        
        users = response.data
        print(f"✅ Encontrados {len(users)} usuarios")
        
        # Construir respuesta
        respuesta = [f"🔍 RESULTADOS DE BÚSQUEDA: '{nombre}'"]
        respuesta.append("=" * 50)
        
        for user in users:
            phone = user.get("phone")
            name = user.get("name", "Sin nombre")
            user_type = user.get("type")
            status = user.get("status")
            
            estado_emoji = "🟢" if status else "🔴"
            estado_texto = "Activo" if status else "Inactivo"
            
            respuesta.append(f"\n{estado_emoji} {name}")
            respuesta.append(f"📞 Teléfono: {phone}")
            respuesta.append(f"🔑 Tipo: {user_type}")
            respuesta.append(f"📊 Estado: {estado_texto}")
            respuesta.append("-" * 30)
        
        respuesta.append(f"\n📊 Total encontrados: {len(users)}")
        
        return "\n".join(respuesta)
        
    except Exception as e:
        error_msg = f"❌ Error al buscar usuario por nombre: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def cambiar_status_usuario(telefono: str, nuevo_status: bool, modificado_por: str) -> str:
    """
    Cambia el status de un usuario (activar/desactivar). Solo los administradores pueden usar esta herramienta.
    
    Args:
        telefono (str): Número de teléfono del usuario a modificar
        nuevo_status (bool): True para activar, False para desactivar
        modificado_por (str): Número de teléfono del administrador que hace el cambio
        
    Returns:
        str: Confirmación del cambio o mensaje de error
    """
    try:
        print(f"🔄 Cambiando status de usuario: {telefono} -> {nuevo_status}")
        print(f"🔑 Modificado por administrador: {modificado_por}")
        
        # Validar que quien modifica sea administrador
        supabase = get_supabase_client()
        
        # Verificar que el modificador sea administrador
        admin_check = supabase.table("users_agent").select(
            "type, status"
        ).eq("phone", modificado_por).execute()
        
        if not admin_check.data:
            return f"❌ Error: El número {modificado_por} no está registrado en el sistema."
        
        admin_data = admin_check.data[0]
        if admin_data.get("type") != "Administrador":
            return f"❌ Error: Solo los administradores pueden cambiar el status de usuarios."
        
        if not admin_data.get("status"):
            return f"❌ Error: El administrador no está activo en el sistema."
        
        # Verificar que el usuario existe
        user_check = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("phone", telefono).execute()
        
        if not user_check.data:
            return f"❌ Error: El usuario con teléfono {telefono} no existe en el sistema."
        
        user_data = user_check.data[0]
        current_status = user_data.get("status")
        user_name = user_data.get("name", "Sin nombre")
        user_type = user_data.get("type")
        
        # No permitir desactivar administradores
        if user_type == "Administrador" and not nuevo_status:
            return f"❌ Error: No se puede desactivar un usuario administrador."
        
        # Si el status ya es el mismo, no hacer nada
        if current_status == nuevo_status:
            status_texto = "Activo" if nuevo_status else "Inactivo"
            return f"ℹ️ El usuario {user_name} ({telefono}) ya está {status_texto.lower()}."
        
        # Actualizar el status
        supabase.table("users_agent").update({
            "status": nuevo_status
        }).eq("phone", telefono).execute()
        
        # Construir mensaje de confirmación
        status_texto = "activado" if nuevo_status else "desactivado"
        accion_texto = "puede" if nuevo_status else "ya no puede"
        
        return (
            f"✅ Usuario {status_texto} exitosamente.\n"
            f"👤 Nombre: {user_name}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🔑 Tipo: {user_type}\n"
            f"📊 Estado: {'Activo' if nuevo_status else 'Inactivo'}\n"
            f"👑 Modificado por: {modificado_por}\n"
            f"💬 El usuario {accion_texto} interactuar con el agente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al cambiar status de usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def cambiar_tipo_usuario(telefono: str, nuevo_tipo: str, modificado_por: str) -> str:
    """
    Cambia el tipo de usuario (Administrador/Secundario). Solo los administradores pueden usar esta herramienta.
    
    Args:
        telefono (str): Número de teléfono del usuario a modificar
        nuevo_tipo (str): Nuevo tipo ("Administrador" o "Secundario")
        modificado_por (str): Número de teléfono del administrador que hace el cambio
        
    Returns:
        str: Confirmación del cambio o mensaje de error
    """
    try:
        print(f"🔄 Cambiando tipo de usuario: {telefono} -> {nuevo_tipo}")
        print(f"🔑 Modificado por administrador: {modificado_por}")
        
        # Validar tipo
        if nuevo_tipo not in ["Administrador", "Secundario"]:
            return "❌ Error: El tipo debe ser 'Administrador' o 'Secundario'."
        
        # Validar que quien modifica sea administrador
        supabase = get_supabase_client()
        
        # Verificar que el modificador sea administrador
        admin_check = supabase.table("users_agent").select(
            "type, status"
        ).eq("phone", modificado_por).execute()
        
        if not admin_check.data:
            return f"❌ Error: El número {modificado_por} no está registrado en el sistema."
        
        admin_data = admin_check.data[0]
        if admin_data.get("type") != "Administrador":
            return f"❌ Error: Solo los administradores pueden cambiar el tipo de usuarios."
        
        if not admin_data.get("status"):
            return f"❌ Error: El administrador no está activo en el sistema."
        
        # Verificar que el usuario existe
        user_check = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("phone", telefono).execute()
        
        if not user_check.data:
            return f"❌ Error: El usuario con teléfono {telefono} no existe en el sistema."
        
        user_data = user_check.data[0]
        current_type = user_data.get("type")
        user_name = user_data.get("name", "Sin nombre")
        
        # Si el tipo ya es el mismo, no hacer nada
        if current_type == nuevo_tipo:
            return f"ℹ️ El usuario {user_name} ({telefono}) ya es de tipo {nuevo_tipo}."
        
        # Actualizar el tipo
        supabase.table("users_agent").update({
            "type": nuevo_tipo
        }).eq("phone", telefono).execute()
        
        return (
            f"✅ Tipo de usuario cambiado exitosamente.\n"
            f"👤 Nombre: {user_name}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🔑 Tipo anterior: {current_type}\n"
            f"🔑 Tipo nuevo: {nuevo_tipo}\n"
            f"👑 Modificado por: {modificado_por}\n"
            f"💬 El usuario ahora tiene permisos de {nuevo_tipo.lower()}"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al cambiar tipo de usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def eliminar_usuario_secundario(telefono: str, eliminado_por: str) -> str:
    """
    Elimina un usuario secundario del sistema (cambia status a False). Solo los administradores pueden usar esta herramienta.
    
    Args:
        telefono (str): Número de teléfono del usuario a eliminar
        eliminado_por (str): Número de teléfono del administrador que hace la eliminación
        
    Returns:
        str: Confirmación de la eliminación o mensaje de error
    """
    try:
        print(f"🗑️ Eliminando usuario secundario: {telefono}")
        print(f"🔑 Eliminado por administrador: {eliminado_por}")
        
        # Validar que quien elimina sea administrador
        supabase = get_supabase_client()
        
        # Verificar que el eliminador sea administrador
        admin_check = supabase.table("users_agent").select(
            "type, status"
        ).eq("phone", eliminado_por).execute()
        
        if not admin_check.data:
            return f"❌ Error: El número {eliminado_por} no está registrado en el sistema."
        
        admin_data = admin_check.data[0]
        if admin_data.get("type") != "Administrador":
            return f"❌ Error: Solo los administradores pueden eliminar usuarios."
        
        if not admin_data.get("status"):
            return f"❌ Error: El administrador no está activo en el sistema."
        
        # Verificar que el usuario existe
        user_check = supabase.table("users_agent").select(
            "phone, name, type, status"
        ).eq("phone", telefono).execute()
        
        if not user_check.data:
            return f"❌ Error: El usuario con teléfono {telefono} no existe en el sistema."
        
        user_data = user_check.data[0]
        user_name = user_data.get("name", "Sin nombre")
        user_type = user_data.get("type")
        
        # No permitir eliminar administradores
        if user_type == "Administrador":
            return f"❌ Error: No se puede eliminar un usuario administrador."
        
        # Si ya está inactivo, no hacer nada
        if not user_data.get("status"):
            return f"ℹ️ El usuario {user_name} ({telefono}) ya está eliminado (inactivo)."
        
        # Desactivar el usuario (cambiar status a False)
        supabase.table("users_agent").update({
            "status": False
        }).eq("phone", telefono).execute()
        
        return (
            f"✅ Usuario eliminado exitosamente.\n"
            f"👤 Nombre: {user_name}\n"
            f"📞 Teléfono: {telefono}\n"
            f"🔑 Tipo: {user_type}\n"
            f"📊 Estado: Inactivo\n"
            f"👑 Eliminado por: {eliminado_por}\n"
            f"💬 El usuario ya no puede interactuar con el agente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al eliminar usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


