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
        return f"❌ Error al consultar cuotas pendientes: {str(e)}"


from decimal import Decimal

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
        return f"❌ Error al obtener id_sales_orders: {str(e)}"


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
        return f"❌ Error al obtener id_client: {str(e)}"


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
        return f"❌ Error al registrar el pago: {str(e)}"


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
        return f"❌ Error al crear la orden de venta: {str(e)}"


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
        return f"❌ Error al registrar el pago directo: {str(e)}"


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
        return f"❌ Error al agregar el detalle a la orden: {str(e)}"


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
        return f"❌ Error al buscar el producto: {str(e)}"



