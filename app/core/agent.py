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
    limpiar_memoria,
    obtener_administradores,
    obtener_telefono_usuario_id2,
    cambiar_status_usuario,
    crear_usuario_agent,
    procesar_devolucion,
    abrir_caja,
    cerrar_caja,
    crear_recibo_caja,
    crear_cliente,
    crear_producto,
    crear_proveedor,
    actualizar_estado_cheque,
    consultar_cuotas_por_cobrar,
    consultar_clientes_endeudados,
    consultar_estado_caja,
    crear_plan_financiamiento,
    crear_plan_letras,
    crear_plan_cheque
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
   obtener_administradores,
   obtener_telefono_usuario_id2,
   cambiar_status_usuario,
   crear_usuario_agent,
   procesar_devolucion,
   abrir_caja,
   cerrar_caja,
   crear_recibo_caja,
   crear_cliente,
   crear_producto,
   crear_proveedor,
   actualizar_estado_cheque,
   consultar_cuotas_por_cobrar,
   consultar_clientes_endeudados,
   consultar_estado_caja,
   crear_plan_financiamiento,
   crear_plan_letras,
   crear_plan_cheque
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
        max_iterations=8,          
        max_execution_time=60,     
        early_stopping_method="generate",
        return_intermediate_steps=True,  
        handle_parsing_errors=True       
    )
    
    return executor