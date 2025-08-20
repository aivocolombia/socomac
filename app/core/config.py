# Configuración de optimización de rendimiento para el agente

# Configuración del LLM
LLM_CONFIG = {
    "temperature": 0.3,  # Baja temperatura para respuestas más directas
    "model": "gpt-4o-mini",  # Modelo más rápido
    "request_timeout": 15,  # Timeout corto
    "max_retries": 1,  # Menos reintentos
    "streaming": False,  # Sin streaming para mayor velocidad
}

# Configuración del AgentExecutor
AGENT_CONFIG = {
    "verbose": False,  # Sin logging detallado
    "max_iterations": 3,  # Menos iteraciones
    "max_execution_time": 20,  # Tiempo máximo reducido
    "return_intermediate_steps": False,  # Sin pasos intermedios
    "handle_parsing_errors": True,
}

# Configuración de memoria
MEMORY_CONFIG = {
    "max_token_limit": 1000,  # Limitar tokens en memoria
}

# Configuración de caché
CACHE_CONFIG = {
    "enabled": True,
    "type": "InMemoryCache",
}

# Configuración de herramientas (priorizar las más usadas)
TOOL_PRIORITY = [
    "nombre_cliente",
    "buscar_producto_por_nombre", 
    "crear_orden_venta",
    "agregar_detalle_orden_venta",
    "registrar_pago",
    "crear_plan_financiamiento",
    "crear_plan_letras",
    "consultar_productos",
    "planes_pago_pendientes_por_cliente",
    "cuotas_pendientes_por_plan",
    "nombre_empresa",
    "buscar_clasificacion",
    "crear_nuevo_cliente",
    "registrar_pago_directo_orden",
    "obtener_id_sales_orders_por_plan",
    "obtener_id_client_por_orden",
    "consultar_detalles_ordenes_cliente",
    "montos_a_favor_por_cliente",
    "procesar_devolucion",
    "limpiar_memoria",
]
