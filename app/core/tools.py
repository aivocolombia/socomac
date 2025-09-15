# app/core/tools.py
from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import get_db_connection
from app.db.mongo import MongoChatMessageHistory
from app.db.supabase import get_supabase_client
from typing import List, Dict, Any, Optional
import json

def get_bank_id(bank_name: str) -> Optional[int]:
    """
    Obtiene el ID de un banco por su nombre.
    
    Args:
        bank_name (str): Nombre del banco (Bancolombia, Davivienda, etc.)
    
    Returns:
        Optional[int]: ID del banco o None si no se encuentra
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_bank FROM banks WHERE name ILIKE %s", (f"%{bank_name}%",))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"❌ Error obteniendo ID del banco {bank_name}: {str(e)}")
        return None

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
                c.department AS departamento,
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
                pp.type_payment_plan
            FROM public.payment_plan pp
            JOIN public.sales_orders so 
                ON so.id_sales_orders = pp.id_sales_orders
            WHERE so.id_client = %s
            ORDER BY pp.created_at DESC;
        """

        cursor.execute(query, (id_cliente,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron planes de pago pendientes para el cliente con ID {id_cliente}."

        # Formato de salida
        lines = []
        for rid_plan, rid_order, num_inst, total_amt, type_plan in rows:
            lines.append(
                f"📋 Plan: {rid_plan} | 🛒 Orden: {rid_order} | "
                f"Cuotas: {num_inst} | 💰 Total: {total_amt} | "
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
                pp.total_amount,
                COALESCE(SUM(p.amount), 0) as total_paid
            FROM public.payment_plan pp
            JOIN public.sales_orders so 
                ON so.id_sales_orders = pp.id_sales_orders
            LEFT JOIN public.payments p 
                ON p.id_payment_installment IN (
                    SELECT pi.id_payment_installment 
                    FROM public.payment_installment pi 
                    WHERE pi.id_payment_plan = pp.id_payment_plan
                )
            WHERE so.id_client = %s
            GROUP BY pp.id_payment_plan, pp.id_sales_orders, pp.total_amount
            HAVING COALESCE(SUM(p.amount), 0) > pp.total_amount
            ORDER BY pp.created_at DESC;
        """

        cursor.execute(query, (id_cliente,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return f"No se encontraron montos a favor para el cliente con ID {id_cliente}."

        # Formato de salida
        lines = []
        for rid_plan, rid_order, total_amount, total_paid in rows:
            amount_favor = total_paid - total_amount
            lines.append(
                f"📋 Plan: {rid_plan} | 🛒 Orden: {rid_order} | 💵 Monto a favor: {amount_favor}"
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
                TO_CHAR(pi.due_date, 'DD/MM/YYYY')
            FROM public.payment_installment AS pi
            WHERE pi.id_payment_plan = %s
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
        for num_installment, id_real, id_plan, amount, pay_amount, due_date in rows:
            cuotas_map[num_installment] = {
                "id_payment_installment": id_real,
                "id_payment_plan": id_plan
            }
            lines.append(
                f"Nro: {num_installment} | 🆔 ID real (id_payment_installment): {id_real} "
                f"| 🪙 ID plan: {id_plan} | 💰 Monto total: {amount} | "
                f"💵 Pagado: {pay_amount} | 📅 Vence: {due_date}"
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
            destiny_bank_name = bancos_validos[destiny_bank_normalizado]
            
            # Obtener ID del banco destino
            id_destiny_bank = get_bank_id(destiny_bank_name)
            if not id_destiny_bank:
                return f"❌ No se encontró el banco destino '{destiny_bank_name}' en la base de datos."
            
            # Para transferencias, el banco de emisión puede ser cualquiera
            # No se valida contra la tabla banks ya que puede ser cualquier banco
            id_emission_bank = None
            
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
            INSERT INTO payments (id_sales_orders, id_payment_installment, amount, type, payment_date, id_destiny_bank, caja_receipt, id_client)
            VALUES (%s, %s, %s, %s, CURRENT_DATE, %s, %s, %s)
            RETURNING id_payment;
        """, (
            id_sales_orders, id_payment_installment, amount, metodo_pago.capitalize(), 
            id_destiny_bank if metodo_pago == "transferencia" else None, caja_receipt, id_client
        ))
        id_payment = cursor.fetchone()[0]

        # === Insertar en tabla específica según método ===
        if metodo_pago == "transferencia":
            cursor.execute("""
                INSERT INTO transfers (id_payment, proof_number, id_emission_bank, emission_date, trans_value, id_destiny_bank, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, proof_number, id_emission_bank, emission_date, trans_value, id_destiny_bank, observations
            ))

        elif metodo_pago == "cheque":
            cursor.execute("""
                INSERT INTO checks (id_payment, check_number, id_emission_bank, emission_date, stimate_collection_date, amount, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, cheque_number, id_emission_bank, emission_date, stimate_collection_date, amount, observations
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
            destiny_bank_name = bancos_validos[destiny_bank_normalizado]
            
            # Obtener ID del banco destino
            id_destiny_bank = get_bank_id(destiny_bank_name)
            if not id_destiny_bank:
                return f"❌ No se encontró el banco destino '{destiny_bank_name}' en la base de datos."
            
            # Para transferencias asociadas a órdenes de venta, el banco de emisión puede ser cualquiera
            # No se valida contra la tabla banks ya que puede ser cualquier banco
            id_emission_bank = None
            
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
            INSERT INTO payments (id_sales_orders, id_payment_installment, amount, type, payment_date, id_destiny_bank, caja_receipt, id_client)
            VALUES (%s, NULL, %s, %s, CURRENT_DATE, %s, %s, %s)
            RETURNING id_payment;
        """, (
            id_sales_orders, amount, metodo_pago.capitalize(), 
            id_destiny_bank if metodo_pago == "transferencia" else None, caja_receipt, id_client
        ))
        id_payment = cursor.fetchone()[0]

        # === Insertar en tabla específica según método ===
        if metodo_pago == "transferencia":
            cursor.execute("""
                INSERT INTO transfers (id_payment, proof_number, id_emission_bank, emission_date, trans_value, id_destiny_bank, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, proof_number, id_emission_bank, emission_date, trans_value, id_destiny_bank, observations
            ))

        elif metodo_pago == "cheque":
            cursor.execute("""
                INSERT INTO checks (id_payment, check_number, id_emission_bank, emission_date, stimate_collection_date, amount, observations)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (
                id_payment, cheque_number, id_emission_bank, emission_date, stimate_collection_date, amount, observations
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
    type_payment_plan: str = "Financiamiento"
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
        type_payment_plan (str, optional): Tipo de plan de pago. Default "Financiamiento"
    
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
                type_payment_plan,
                id_status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id_payment_plan;
        """
        
        # Cambiar "Otro plan de financiamiento" por "Financiamiento"
        if type_payment_plan == "Otro plan de financiamiento":
            type_payment_plan = "Financiamiento"
        
        cursor.execute(query, (
            id_sales_orders, num_installments, total_amount, start_date, 
            frequency, notes, type_payment_plan, 9
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
                    due_date
                )
                VALUES (
                    %s, %s, %s, %s
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
                department,
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
    letter_number: int,
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
        letter_number (int): Número de la letra
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
        
        # Validar letter_number
        if not isinstance(letter_number, int) or letter_number <= 0:
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
                type_payment_plan,
                id_status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id_payment_plan;
        """
        
        type_payment_plan = "Letra"
        
        cursor.execute(query, (
            id_sales_orders, num_installments, total_amount, start_date, 
            frequency, notes, type_payment_plan, 9
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
                    due_date
                )
                VALUES (
                    %s, %s, %s, %s
                );
            """, (id_payment_plan, i, amount_per_installment, due_date.strftime('%Y-%m-%d')))
        
        # Crear la letra
        cursor.execute("""
            INSERT INTO letters (
                id_payment_plan,
                letter_number,
                due_date,
                amount,
                id_status
            )
            VALUES (
                %s, %s, %s, %s, %s
            );
        """, (id_payment_plan, letter_number, due_date.strftime('%Y-%m-%d'), total_amount, 9))
        
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
            f"📄 Número de letra: {letter_number}\n"
            f"📋 Estado: Pendiente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al crear el plan de letras: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_plan_cheque(
    id_sales_orders: int,
    num_installments: int,
    total_amount: float,
    start_date: str,
    frequency: str,
    check_number: str,
    stimate_collection_date: str,
    notes: str = None
) -> str:
    """
    Crea un plan de financiamiento tipo "Cheque" para una orden de venta específica.
    Crea el payment_plan, los payment_installment y el cheque correspondiente.
    
    Args:
        id_sales_orders (int): ID de la orden de venta
        num_installments (int): Número de cuotas
        total_amount (float): Monto total del plan
        start_date (str): Fecha de inicio en formato YYYY-MM-DD
        frequency (str): Frecuencia de pago (Mensual, Quincenal, Semanal, etc.)
        check_number (str): Número del cheque
        stimate_collection_date (str): Fecha estimada de cobro en formato YYYY-MM-DD
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
            datetime.strptime(stimate_collection_date, '%Y-%m-%d')
        except ValueError:
            return "❌ Las fechas deben estar en formato YYYY-MM-DD."
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar que la orden de venta existe
        cursor.execute("SELECT id_sales_orders FROM sales_orders WHERE id_sales_orders = %s", (id_sales_orders,))
        if not cursor.fetchone():
            conn.close()
            return f"❌ No se encontró la orden de venta con ID {id_sales_orders}."
        
        # Validar check_number
        if not check_number or not check_number.strip():
            return "❌ El número de cheque es obligatorio."
        
        # Calcular monto por cuota
        amount_per_installment = total_amount / num_installments
        
        # Insertar el plan de financiamiento tipo "Cheque"
        query = """
            INSERT INTO payment_plan (
                id_sales_orders,
                num_installments,
                total_amount,
                start_date,
                frequency,
                notes,
                type_payment_plan,
                id_status
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id_payment_plan;
        """
        
        type_payment_plan = "Cheque"
        
        cursor.execute(query, (
            id_sales_orders, num_installments, total_amount, start_date, 
            frequency, notes, type_payment_plan, 9
        ))
        
        id_payment_plan = cursor.fetchone()[0]
        
        # Crear las cuotas automáticamente
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        last_due_date = None
        
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
            
            # Guardar la última fecha de vencimiento
            last_due_date = due_date
            
            # Insertar la cuota
            cursor.execute("""
                INSERT INTO payment_installment (
                    id_payment_plan,
                    installment_number,
                    amount,
                    due_date
                )
                VALUES (
                    %s, %s, %s, %s
                );
            """, (id_payment_plan, i, amount_per_installment, due_date.strftime('%Y-%m-%d')))
        
        # Crear el cheque
        cursor.execute("""
            INSERT INTO checks (
                id_payment_plan,
                check_number,
                due_date,
                amount,
                stimate_collection_date,
                type
            )
            VALUES (
                %s, %s, %s, %s, %s, %s
            );
        """, (id_payment_plan, check_number, last_due_date.strftime('%Y-%m-%d'), total_amount, stimate_collection_date, "Financiado"))
        
        conn.commit()
        conn.close()
        
        return (
            f"✅ Plan de cheque creado exitosamente.\n"
            f"🆔 ID del plan: {id_payment_plan}\n"
            f"🛒 Orden de venta: {id_sales_orders}\n"
            f"📊 Número de cuotas: {num_installments}\n"
            f"💰 Monto total: {total_amount}\n"
            f"💵 Monto por cuota: {amount_per_installment:.2f}\n"
            f"📅 Fecha de inicio: {start_date}\n"
            f"🔄 Frecuencia: {frequency}\n"
            f"📝 Tipo: Cheque\n"
            f"📄 Número de cheque: {check_number}\n"
            f"📅 Fecha estimada de cobro: {stimate_collection_date}\n"
            f"📅 Fecha de vencimiento: {last_due_date.strftime('%Y-%m-%d')}\n"
            f"📋 Estado: Pendiente"
        )
        
    except Exception as e:
        error_msg = f"❌ Error al crear el plan de cheque: {str(e)}"
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
                query = "SELECT id, amount, status FROM status_caja WHERE id = 1"
                cursor.execute(query)
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    id_fila, amount, status = result
                    estado_texto = "Abierta" if status else "Cerrada"
                    return f"📊 Estado actual de la caja:\n🔧 Estado: {estado_texto}\n💰 Saldo inicial: ${amount:,.2f}"
                else:
                    return "❌ No se encontró información de la caja"
                    
            elif tipo.lower() == "conciliaciones":
                # Consultar filas 2 (Davivienda) y 3 (Bancolombia)
                query = "SELECT id, amount, status FROM status_caja WHERE id IN (2, 3) ORDER BY id"
                cursor.execute(query)
                results = cursor.fetchall()
                conn.close()
                
                if results:
                    response = "📊 Estado actual de las conciliaciones:\n"
                    for id_fila, amount, status in results:
                        banco = "Davivienda" if id_fila == 2 else "Bancolombia"
                        estado_texto = "Abierta" if status else "Cerrada"
                        response += f"🏦 {banco}:\n   🔧 Estado: {estado_texto}\n   💰 Saldo inicial: ${amount:,.2f}\n"
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
            status = True
        elif accion.lower() == "cerrar":
            status = False
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
        print(f"🔧 Estado final: {status}")
        
        # Ejecutar las actualizaciones
        for i, id_fila in enumerate(ids_to_update):
            query = """
                INSERT INTO status_caja
                (id, amount, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET 
                    amount = EXCLUDED.amount,
                    updated_at = NOW(),
                    status = EXCLUDED.status
            """
            
            print(f"🔧 Actualizando fila {id_fila} con saldo: {saldos[i]}, status: {status}")
            print(f"🔧 Query SQL: {query}")
            print(f"🔧 Parámetros: id={id_fila}, saldo={saldos[i]}, status={status}")
            
            cursor.execute(query, (id_fila, saldos[i], status))
            
            # Verificar que la actualización fue exitosa
            verify_query = "SELECT id, amount, status FROM status_caja WHERE id = %s"
            cursor.execute(verify_query, (id_fila,))
            result = cursor.fetchone()
            print(f"✅ Fila {id_fila} actualizada exitosamente - Verificación: {result}")
        
        conn.commit()
        conn.close()
        
        # Determinar el texto del estado para mostrar
        estado_texto = "Abierta" if status else "Cerrada"
        
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
def obtener_administradores() -> str:
    """
    Obtiene los usuarios con type "Administrador" desde la tabla user_agent, mostrando su número de teléfono y status.
    Esta herramienta consulta la base de datos para obtener información de todos los administradores.
    
    Returns:
        str: Lista de administradores con su teléfono y status, o mensaje de error.
    """
    try:
        print("🔍 Consultando usuarios administradores...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Consultar usuarios con type "Administrador"
        query = """
            SELECT phone, name, status, type
            FROM users_agent 
            WHERE type = 'Administrador' 
            AND phone IS NOT NULL 
            AND phone != ''
            ORDER BY name, phone
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        
        if not resultados:
            print("⚠️ No se encontraron administradores en la base de datos")
            return "No se encontraron usuarios administradores en la base de datos."
        
        # Formatear los resultados
        administradores_info = []
        for row in resultados:
            phone, name, status, user_type = row
            if phone:
                administradores_info.append({
                    'phone': str(phone),
                    'name': name or 'Sin nombre',
                    'status': status or 'Sin status',
                    'type': user_type or 'Sin tipo'
                })
        
        print(f"👑 Administradores encontrados: {len(administradores_info)}")
        
        if len(administradores_info) == 1:
            admin = administradores_info[0]
            return f"👑 Administrador encontrado:\n📱 Teléfono: {admin['phone']}\n👤 Nombre: {admin['name']}\n✅ Status: {admin['status']}\n🔧 Tipo: {admin['type']}"
        else:
            # Formatear múltiples administradores
            lines = ["👑 Usuarios Administradores:"]
            for i, admin in enumerate(administradores_info, 1):
                lines.append(f"{i}. 📱 {admin['phone']} - 👤 {admin['name']} - ✅ {admin['status']} - 🔧 {admin['type']}")
            return "\n".join(lines)
            
    except Exception as e:
        error_msg = f"Error obteniendo administradores: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def obtener_telefono_usuario_id2(nombre_o_telefono: str = "") -> str:
    """
    Obtiene el número de teléfono de un usuario activo desde la tabla users_agent.
    Permite al administrador seleccionar una persona por nombre o teléfono y verifica que su status esté activo.
    
    Args:
        nombre_o_telefono (str): Nombre completo o número de teléfono del usuario a buscar. Si está vacío, muestra todos los usuarios activos.
    
    Returns:
        str: Número de teléfono del usuario activo, o mensaje de error si no se encuentra.
    """
    try:
        print(f"🔍 Consultando teléfono del usuario: '{nombre_o_telefono}'")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if nombre_o_telefono:
            # Buscar usuario específico por nombre o teléfono
            query = """
                SELECT phone, name, status, type
                FROM users_agent 
                WHERE (name ILIKE %s OR phone = %s)
                AND name IS NOT NULL 
                AND name != ''
            """
            
            # Si es un número de teléfono, buscar exacto; si es nombre, buscar parcial
            search_term = nombre_o_telefono if nombre_o_telefono.isdigit() else f"%{nombre_o_telefono}%"
            
            cursor.execute(query, (search_term, nombre_o_telefono))
            resultados = cursor.fetchall()
            
            if not resultados:
                conn.close()
                return f"❌ No se encontró ningún usuario con nombre o teléfono: '{nombre_o_telefono}'"
            
            if len(resultados) > 1:
                # Mostrar opciones si hay múltiples resultados
                opciones = []
                for i, (phone, name, status, user_type) in enumerate(resultados, 1):
                    status_texto = "ACTIVO" if status == "TRUE" else "INACTIVO"
                    opciones.append(f"{i}. {name} | 📱 {phone} | Status: {status_texto} | Tipo: {user_type}")
                
                conn.close()
                return f"🔍 Múltiples usuarios encontrados. Por favor especifica:\n" + "\n".join(opciones)
            
            # Un solo resultado encontrado
            phone, name, status, user_type = resultados[0]
            
            if not phone:
                conn.close()
                return f"⚠️ El usuario {name} no tiene un número de teléfono registrado."
            
            # Verificar que el usuario esté activo, excepto si es administrador
            # Los administradores siempre pueden obtener su teléfono, independientemente del status
            if user_type != "Administrador" and status != "TRUE":
                conn.close()
                return f"⚠️ El usuario {name} no está activo (status: {status}). Solo se pueden obtener teléfonos de usuarios activos o administradores."
            
            conn.close()
            print(f"📱 Teléfono encontrado para usuario activo: {phone}")
            return str(phone)
        else:
            # Mostrar todos los usuarios activos y administradores (independientemente del status)
            query = """
                SELECT phone, name, status, type
                FROM users_agent 
                WHERE (status = 'TRUE' OR type = 'Administrador')
                AND phone IS NOT NULL 
                AND phone != ''
                ORDER BY name
            """
            
            cursor.execute(query)
            resultados = cursor.fetchall()
            conn.close()
            
            if not resultados:
                return "❌ No se encontraron usuarios activos o administradores con número de teléfono registrado."
            
            usuarios_info = ["📋 Usuarios activos y administradores disponibles:"]
            for phone, name, status, user_type in resultados:
                usuarios_info.append(f"👤 {name} | 📱 {phone} | Tipo: {user_type}")
            
            return "\n".join(usuarios_info)
            
    except Exception as e:
        error_msg = f"Error obteniendo teléfono del usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def cambiar_status_usuario(nombre_o_telefono: str, nuevo_status: str) -> str:
    """
    Cambia el status de un usuario en la tabla users_agent.
    Permite buscar al usuario por nombre o teléfono y cambiar su status a activo (TRUE) o inactivo (FALSE).
    IMPORTANTE: Solo puede haber un usuario activo a la vez. Al activar un usuario, se desactivan automáticamente todos los demás.
    
    Args:
        nombre_o_telefono (str): Nombre completo o número de teléfono del usuario a buscar
        nuevo_status (str): Nuevo status a asignar ("TRUE" para activo, "FALSE" para inactivo)
    
    Returns:
        str: Mensaje de confirmación del cambio o error si no se encuentra el usuario.
    """
    try:
        print(f"🔍 Buscando usuario: '{nombre_o_telefono}' para cambiar status a: {nuevo_status}")
        
        # Validar el nuevo status
        if nuevo_status.upper() not in ["TRUE", "FALSE"]:
            return "❌ Status inválido. Debe ser 'TRUE' (activo) o 'FALSE' (inactivo)."
        
        # Normalizar el status
        status_normalizado = "TRUE" if nuevo_status.upper() == "TRUE" else "FALSE"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar usuario por nombre o teléfono
        query = """
            SELECT id, name, phone, status, type
            FROM users_agent 
            WHERE (name ILIKE %s OR phone = %s)
            AND name IS NOT NULL 
            AND name != ''
        """
        
        # Si es un número de teléfono, buscar exacto; si es nombre, buscar parcial
        search_term = nombre_o_telefono if nombre_o_telefono.isdigit() else f"%{nombre_o_telefono}%"
        
        cursor.execute(query, (search_term, nombre_o_telefono))
        resultados = cursor.fetchall()
        
        if not resultados:
            conn.close()
            return f"❌ No se encontró ningún usuario con nombre o teléfono: '{nombre_o_telefono}'"
        
        if len(resultados) > 1:
            # Mostrar opciones si hay múltiples resultados
            opciones = []
            for i, (user_id, name, phone, status, user_type) in enumerate(resultados, 1):
                opciones.append(f"{i}. {name} | 📱 {phone} | Status: {status} | Tipo: {user_type}")
            
            conn.close()
            return f"🔍 Múltiples usuarios encontrados. Por favor especifica:\n" + "\n".join(opciones)
        
        # Un solo resultado encontrado
        user_id, name, phone, status_actual, user_type = resultados[0]
        

        
        # Si se va a activar el usuario, desactivar todos los demás primero
        if status_normalizado == "TRUE":
            # Desactivar todos los usuarios excepto el actual
            deactivate_query = """
                UPDATE users_agent 
                SET status = 'FALSE', updated_at = NOW()
                WHERE id != %s
            """
            cursor.execute(deactivate_query, (user_id,))
            print(f"🔒 Desactivados todos los demás usuarios")
        
        # Actualizar el status del usuario
        update_query = """
            UPDATE users_agent 
            SET status = %s, updated_at = NOW()
            WHERE id = %s
        """
        
        cursor.execute(update_query, (status_normalizado, user_id))
        conn.commit()
        
        # Verificar que la actualización fue exitosa
        verify_query = "SELECT status FROM users_agent WHERE id = %s"
        cursor.execute(verify_query, (user_id,))
        status_verificado = cursor.fetchone()[0]
        
        conn.close()
        
        if status_verificado == status_normalizado:
            status_texto = "ACTIVO" if status_normalizado == "TRUE" else "INACTIVO"
            if status_normalizado == "TRUE":
                return f"✅ Usuario activado exitosamente (todos los demás desactivados)\n👤 Usuario: {name}\n📱 Teléfono: {phone}\n🔄 Status anterior: {status_actual}\n✅ Status nuevo: {status_normalizado} ({status_texto})\n🔒 Nota: Todos los demás usuarios han sido desactivados automáticamente"
            else:
                return f"✅ Status actualizado exitosamente\n👤 Usuario: {name}\n📱 Teléfono: {phone}\n🔄 Status anterior: {status_actual}\n✅ Status nuevo: {status_normalizado} ({status_texto})"
        else:
            return f"❌ Error al actualizar el status. Status actual: {status_verificado}"
            
    except Exception as e:
        error_msg = f"Error cambiando status del usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def crear_usuario_agent(nombre: str, telefono: str, tipo: str = "Secundario") -> str:
    """
    Crea un nuevo usuario en la tabla users_agent.
    Por defecto, el tipo es "Secundario" y el status es "FALSE" (inactivo).
    
    Args:
        nombre (str): Nombre completo del usuario
        telefono (str): Número de teléfono del usuario
        tipo (str): Tipo de usuario ("Administrador", "Secundario", etc.). Por defecto es "Secundario"
    
    Returns:
        str: Mensaje de confirmación del usuario creado o error si no se puede crear.
    """
    try:
        print(f"👤 Creando nuevo usuario: {nombre} | 📱 {telefono} | 🔧 {tipo} | ✅ FALSE")
        
        # Validar campos obligatorios
        if not nombre or not nombre.strip():
            return "❌ El nombre del usuario es obligatorio."
        
        if not telefono or not telefono.strip():
            return "❌ El teléfono del usuario es obligatorio."
        
        # Validar formato del teléfono (debe ser numérico y tener al menos 10 dígitos)
        if not telefono.isdigit() or len(telefono) < 10:
            return "❌ El teléfono debe ser numérico y tener al menos 10 dígitos."
        
        # Validar tipo de usuario
        tipos_validos = ["Administrador", "Secundario"]
        if tipo not in tipos_validos:
            return f"❌ Tipo de usuario inválido. Debe ser uno de: {', '.join(tipos_validos)}"
        
        # Normalizar valores
        nombre_normalizado = nombre.strip()
        telefono_normalizado = telefono.strip()
        tipo_normalizado = tipo
        status_normalizado = "FALSE"  # Siempre FALSE para nuevos usuarios
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si ya existe un usuario con ese teléfono
        check_query = """
            SELECT id, name, type, status
            FROM users_agent 
            WHERE phone = %s
        """
        cursor.execute(check_query, (telefono_normalizado,))
        usuario_existente = cursor.fetchone()
        
        if usuario_existente:
            user_id, name, user_type, user_status = usuario_existente
            conn.close()
            return f"❌ Ya existe un usuario con el teléfono {telefono_normalizado}:\n👤 Nombre: {name}\n🔧 Tipo: {user_type}\n✅ Status: {user_status}"
        
        # Verificar si ya existe un usuario con ese nombre
        check_name_query = """
            SELECT id, phone, type, status
            FROM users_agent 
            WHERE name = %s
        """
        cursor.execute(check_name_query, (nombre_normalizado,))
        usuario_nombre_existente = cursor.fetchone()
        
        if usuario_nombre_existente:
            user_id, phone, user_type, user_status = usuario_nombre_existente
            conn.close()
            return f"❌ Ya existe un usuario con el nombre '{nombre_normalizado}':\n📱 Teléfono: {phone}\n🔧 Tipo: {user_type}\n✅ Status: {user_status}"
        

        
        # Crear el nuevo usuario
        insert_query = """
            INSERT INTO users_agent (name, phone, type, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, NOW(), NOW())
            RETURNING id
        """
        
        cursor.execute(insert_query, (nombre_normalizado, telefono_normalizado, tipo_normalizado, status_normalizado))
        nuevo_user_id = cursor.fetchone()[0]
        conn.commit()
        
        # Verificar que el usuario fue creado exitosamente
        verify_query = """
            SELECT name, phone, type, status
            FROM users_agent 
            WHERE id = %s
        """
        cursor.execute(verify_query, (nuevo_user_id,))
        usuario_verificado = cursor.fetchone()
        
        conn.close()
        
        if usuario_verificado:
            name_verificado, phone_verificado, type_verificado, status_verificado = usuario_verificado
            status_texto = "ACTIVO" if status_verificado == "TRUE" else "INACTIVO"
            
            mensaje = f"✅ Usuario creado exitosamente\n🆔 ID: {nuevo_user_id}\n👤 Nombre: {name_verificado}\n📱 Teléfono: {phone_verificado}\n🔧 Tipo: {type_verificado}\n✅ Status: {status_verificado} ({status_texto})"
            
            return mensaje
        else:
            return "❌ Error al crear el usuario. No se pudo verificar la creación."
            
    except Exception as e:
        error_msg = f"Error creando usuario: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg
