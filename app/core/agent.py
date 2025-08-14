from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories.file import FileChatMessageHistory
from langchain_core.messages import SystemMessage
from app.db.mongo import MongoChatMessageHistory
from langchain.prompts import MessagesPlaceholder
from app.core.prompts import build_system_prompt
from app.core.tools import (
    nombre_cliente,
    limpiar_memoria,
    nombre_empresa,
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
    crear_nuevo_cliente
)
import os
import json

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(
    temperature=0.3,
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [
   limpiar_memoria,
   nombre_empresa,
   nombre_cliente,
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
   crear_nuevo_cliente
]


def get_agent(phone: str):
    print("telefono entrante", phone)
    mongo_history = MongoChatMessageHistory(phone=phone)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=mongo_history
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
        verbose=True,
        max_iterations=4,          
        max_execution_time=30,     
        early_stopping_method="generate",
        return_intermediate_steps=True,  
        handle_parsing_errors=True       
    )
    
    return executor