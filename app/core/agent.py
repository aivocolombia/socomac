from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_core.messages import SystemMessage
from app.db.mongo import MongoChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from app.core.prompts import build_system_prompt
from app.core.config import LLM_CONFIG, AGENT_CONFIG, MEMORY_CONFIG, CACHE_CONFIG, TOOL_PRIORITY
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache
from app.core.tools import (
    nombre_cliente,
    limpiar_memoria,
    nombre_empresa,
    buscar_clasificacion,
    planes_pago_pendientes_por_cliente,
    montos_a_favor_por_cliente,
    cuotas_pendientes_por_plan,
    obtener_id_sales_orders_por_plan,
    obtener_id_client_por_orden,
    registrar_pago,
    registrar_pago_directo_orden,
    consultar_productos,
    buscar_producto_por_nombre,
    crear_orden_venta,
    agregar_detalle_orden_venta,
    crear_plan_financiamiento,
    crear_plan_letras,
    crear_nuevo_cliente,
    consultar_detalles_ordenes_cliente,
    procesar_devolucion
)
import os
import json

from dotenv import load_dotenv

load_dotenv()

# Configurar caché para respuestas más rápidas
if CACHE_CONFIG["enabled"]:
    set_llm_cache(InMemoryCache())

llm = ChatOpenAI(
    temperature=LLM_CONFIG["temperature"],
    model=LLM_CONFIG["model"],
    api_key=os.getenv("OPENAI_API_KEY"),
    request_timeout=LLM_CONFIG["request_timeout"],
    max_retries=LLM_CONFIG["max_retries"],
    streaming=LLM_CONFIG["streaming"]
)

# Ordenar herramientas por prioridad de uso para mayor velocidad
tools = [
   nombre_cliente,  # Más usada
   buscar_producto_por_nombre,  # Muy usada
   crear_orden_venta,  # Muy usada
   agregar_detalle_orden_venta,  # Muy usada
   registrar_pago,  # Muy usada
   crear_plan_financiamiento,  # Muy usada
   crear_plan_letras,  # Muy usada
   consultar_productos,  # Usada frecuentemente
   planes_pago_pendientes_por_cliente,  # Usada frecuentemente
   cuotas_pendientes_por_plan,  # Usada frecuentemente
   nombre_empresa,  # Usada ocasionalmente
   buscar_clasificacion,  # Usada ocasionalmente
   crear_nuevo_cliente,  # Usada ocasionalmente
   registrar_pago_directo_orden,  # Usada ocasionalmente
   obtener_id_sales_orders_por_plan,  # Usada ocasionalmente
   obtener_id_client_por_orden,  # Usada ocasionalmente
   consultar_detalles_ordenes_cliente,  # Usada ocasionalmente
   montos_a_favor_por_cliente,  # Usada ocasionalmente
   procesar_devolucion,  # Usada ocasionalmente
   limpiar_memoria  # Menos usada
]


def get_agent(phone: str):
    print("telefono entrante", phone)
    mongo_history = MongoChatMessageHistory(phone=phone)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=mongo_history,
        max_token_limit=MEMORY_CONFIG["max_token_limit"]
    )
    prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=build_system_prompt(phone)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,
    )

    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=AGENT_CONFIG["verbose"],
        max_iterations=AGENT_CONFIG["max_iterations"],
        max_execution_time=AGENT_CONFIG["max_execution_time"],
        early_stopping_method="generate",
        return_intermediate_steps=AGENT_CONFIG["return_intermediate_steps"],
        handle_parsing_errors=AGENT_CONFIG["handle_parsing_errors"]
    )
    
    return executor