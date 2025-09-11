# app/core/tools.py
from langchain.tools import tool
from app.data.questions import question_list
from app.db.respositories import get_db_connection
from app.db.mongo import MongoChatMessageHistory
from app.db.supabase import get_supabase_client
from typing import List, Dict, Any, Optional
import json

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
def consultar_estado_caja() -> str:
    """Verifica si la caja está abierta para permitir transacciones en el sistema SOCOMAC."""
    try:
        print("🔍 Consultando estado de la caja...")
        
        supabase = get_supabase_client()
        
        # Consultar el estado más reciente de la caja
        response = supabase.table('status_caja').select('*').order('created_at', desc=True).limit(1).execute()
        
        if not response.data:
            return "❌ No se encontró información del estado de la caja."
        
        estado_caja = response.data[0]
        status = estado_caja.get('status', False)
        amount = estado_caja.get('amount', 0)
        
        if status:
            return f"✅ La caja está ABIERTA\n💰 Monto actual: ${amount:,.2f}"
        else:
            return f"❌ La caja está CERRADA\n💰 Último monto: ${amount:,.2f}\n💡 Debe abrir la caja antes de registrar pagos."
            
    except Exception as e:
        error_msg = f"Error al consultar estado de caja: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def consultar_clientes(filtro: str = "") -> str:
    """Consulta la lista de clientes disponibles en el sistema SOCOMAC. Opcionalmente filtra por nombre o identificación."""
    try:
        print(f"🔍 Consultando clientes con filtro: '{filtro}'")
        
        supabase = get_supabase_client()
        
        if filtro:
            # Buscar por nombre completo o identificación
            response = supabase.table('clients').select('*').or_(f'full_name.ilike.%{filtro}%,unique_id.ilike.%{filtro}%').execute()
        else:
            # Obtener todos los clientes
            response = supabase.table('clients').select('*').execute()
        
        if not response.data:
            return f"❌ No se encontraron clientes con el filtro '{filtro}'."
        
        clientes = response.data
        resultado = f"👥 Clientes encontrados ({len(clientes)}):\n\n"
        
        for cliente in clientes[:10]:  # Limitar a 10 resultados
            resultado += f"🆔 ID: {cliente['id_client']}\n"
            resultado += f"👤 Nombre: {cliente['full_name']}\n"
            resultado += f"📋 Identificación: {cliente['unique_id']}\n"
            resultado += f"📞 Teléfono: {cliente.get('phone', 'N/A')}\n"
            resultado += f"🏢 Empresa: {cliente.get('company', 'N/A')}\n"
            resultado += "─" * 30 + "\n"
        
        if len(clientes) > 10:
            resultado += f"... y {len(clientes) - 10} clientes más."
            
        return resultado
        
    except Exception as e:
        error_msg = f"Error al consultar clientes: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def consultar_cuotas_pendientes(cliente_id: int, plan_financiamiento_id: int = None) -> str:
    """Consulta las cuotas pendientes de pago para un cliente específico en el sistema SOCOMAC."""
    try:
        print(f"🔍 Consultando cuotas pendientes para cliente ID: {cliente_id}")
        
        supabase = get_supabase_client()
        
        # Construir la consulta base
        query = supabase.table('payment_installment').select('''
            *,
            payment_plan!inner(
                id_payment_plan,
                num_installments,
                total_amount,
                start_date,
                clients!inner(
                    id_client,
                    full_name,
                    unique_id
                )
            )
        ''')
        
        # Filtrar por cliente
        query = query.eq('payment_plan.clients.id_client', cliente_id)
        
        # Filtrar por plan específico si se proporciona
        if plan_financiamiento_id:
            query = query.eq('payment_plan.id_payment_plan', plan_financiamiento_id)
        
        # Filtrar solo cuotas pendientes (id_status != 6)
        query = query.neq('id_status', 6)
        
        # Ordenar por número de cuota
        query = query.order('installment_number')
        
        response = query.execute()
        
        if not response.data:
            return f"❌ No se encontraron cuotas pendientes para el cliente ID: {cliente_id}."
        
        cuotas = response.data
        resultado = f"📋 Cuotas pendientes encontradas ({len(cuotas)}):\n\n"
        
        for cuota in cuotas:
            plan = cuota['payment_plan']
            cliente = plan['clients']
            
            resultado += f"🆔 Cliente: {cliente['full_name']} (ID: {cliente['id_client']})\n"
            resultado += f"📋 Identificación: {cliente['unique_id']}\n"
            resultado += f"📊 Plan ID: {plan['id_payment_plan']}\n"
            resultado += f"🔢 Cuota #{cuota['installment_number']}\n"
            resultado += f"💰 Valor: ${cuota['amount']:,.2f}\n"
            resultado += f"💳 Pagado: ${cuota.get('pay_amount', 0):,.2f}\n"
            resultado += f"📅 Vencimiento: {cuota.get('due_date', 'N/A')}\n"
            resultado += f"📊 Estado: {cuota['id_status']}\n"
            resultado += "─" * 40 + "\n"
        
        return resultado
        
    except Exception as e:
        error_msg = f"Error al consultar cuotas pendientes: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg

@tool
def registrar_pago_cuota(cliente_id: int, plan_financiamiento_id: int, cuotas_seleccionadas: List[int], 
                        valor_pagar: float, metodo_pago: str, datos_adicionales: Dict[str, Any] = None) -> str:
    """Registra un pago de cuota o abono para un cliente específico en el sistema SOCOMAC."""
    try:
        print(f"💰 Registrando pago para cliente ID: {cliente_id}")
        print(f"📊 Plan ID: {plan_financiamiento_id}")
        print(f"🔢 Cuotas: {cuotas_seleccionadas}")
        print(f"💵 Valor: ${valor_pagar:,.2f}")
        print(f"💳 Método: {metodo_pago}")
        
        # Validar método de pago
        metodos_validos = ["efectivo", "transferencia", "cheque"]
        if metodo_pago not in metodos_validos:
            return f"❌ Método de pago inválido. Métodos válidos: {', '.join(metodos_validos)}"
        
        supabase = get_supabase_client()
        
        # Verificar que las cuotas existan y estén pendientes
        cuotas_response = supabase.table('payment_installment').select('*').eq('id_payment_plan', plan_financiamiento_id).in_('installment_number', cuotas_seleccionadas).execute()
        
        if not cuotas_response.data:
            return f"❌ No se encontraron las cuotas especificadas: {cuotas_seleccionadas}"
        
        cuotas = cuotas_response.data
        
        # Validar que las cuotas estén pendientes
        for cuota in cuotas:
            if cuota['id_status'] == 6:  # Ya pagada
                return f"❌ La cuota #{cuota['installment_number']} ya está pagada."
        
        # Calcular total de cuotas seleccionadas
        total_cuotas = sum(cuota['amount'] for cuota in cuotas)
        
        if abs(valor_pagar - total_cuotas) > 0.01:  # Tolerancia para decimales
            return f"❌ El valor a pagar (${valor_pagar:,.2f}) no coincide con el total de las cuotas (${total_cuotas:,.2f})"
        
        # Registrar el pago para cada cuota
        pagos_registrados = []
        
        for cuota in cuotas:
            # Crear registro de pago
            pago_data = {
                'id_client': cliente_id,
                'id_payment_installment': cuota['id_payment_installment'],
                'amount': cuota['amount'],
                'payment_date': 'now()',
                'type': metodo_pago,
                'notes': datos_adicionales.get('comentarios', '') if datos_adicionales else ''
            }
            
            # Agregar datos específicos según método de pago
            if metodo_pago == "transferencia" and datos_adicionales:
                pago_data['notes'] += f" | Comprobante: {datos_adicionales.get('numero_comprobante', '')}"
                pago_data['notes'] += f" | Banco emisión: {datos_adicionales.get('banco_emision', '')}"
                pago_data['notes'] += f" | Fecha emisión: {datos_adicionales.get('fecha_emision', '')}"
                pago_data['notes'] += f" | Banco destino: {datos_adicionales.get('banco_destino', '')}"
            
            elif metodo_pago == "cheque" and datos_adicionales:
                pago_data['notes'] += f" | Número cheque: {datos_adicionales.get('numero_cheque', '')}"
                pago_data['notes'] += f" | Fecha estimada cobro: {datos_adicionales.get('fecha_estimada_cobro', '')}"
                pago_data['notes'] += f" | Banco emisión: {datos_adicionales.get('banco_emision_cheque', '')}"
                pago_data['notes'] += f" | Fecha emisión: {datos_adicionales.get('fecha_emision_cheque', '')}"
            
            # Insertar pago
            pago_response = supabase.table('payments').insert(pago_data).execute()
            
            if pago_response.data:
                pagos_registrados.append(pago_response.data[0])
                
                # Actualizar estado de la cuota a pagada
                supabase.table('payment_installment').update({
                    'id_status': 6,  # Pagada
                    'pay_amount': cuota['amount'],
                    'payment_date': 'now()'
                }).eq('id_payment_installment', cuota['id_payment_installment']).execute()
        
        # Verificar si todas las cuotas del plan están pagadas
        cuotas_restantes = supabase.table('payment_installment').select('*').eq('id_payment_plan', plan_financiamiento_id).neq('id_status', 6).execute()
        
        if not cuotas_restantes.data:
            # Todas las cuotas están pagadas, finalizar el plan
            supabase.table('payment_plan').update({
                'id_status': 10  # Finalizado
            }).eq('id_payment_plan', plan_financiamiento_id).execute()
        
        resultado = f"✅ Pago registrado exitosamente\n"
        resultado += f"🆔 Cliente ID: {cliente_id}\n"
        resultado += f"📊 Plan ID: {plan_financiamiento_id}\n"
        resultado += f"💰 Monto total: ${valor_pagar:,.2f}\n"
        resultado += f"🔢 Cuotas pagadas: {', '.join(map(str, cuotas_seleccionadas))}\n"
        resultado += f"💳 Método: {metodo_pago.title()}\n"
        resultado += f"📝 Pagos registrados: {len(pagos_registrados)}\n"
        
        if datos_adicionales and datos_adicionales.get('comentarios'):
            resultado += f"💬 Comentarios: {datos_adicionales['comentarios']}\n"
        
        return resultado
        
    except Exception as e:
        error_msg = f"Error al registrar pago: {str(e)}"
        print(f"❌ {error_msg}")
        return error_msg


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