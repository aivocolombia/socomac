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
