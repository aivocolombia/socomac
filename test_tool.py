from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_ollama import ChatOllama  # actualizado
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage  # para reconstrucción manual
import os, json


def get_my_name_func(input=None):
    return "Camilo Mora"

get_my_name = Tool(
    name="get_my_name",
    func=get_my_name_func,
    description="Devuelve el nombre del usuario si se le pregunta cómo se llama"
)

# Modelo
llm = ChatOllama(model="qwen3:8b")

# Memoria conversacional
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Cargar historial si existe
if os.path.exists("chat_memory.json"):
    with open("chat_memory.json", "r", encoding="utf-8") as f:
        data = json.load(f)

        messages = []
        for msg in data["messages"]:
            msg_type = msg["type"]
            content = msg["content"]
            kwargs = msg.get("additional_kwargs", {})

            if msg_type == "human":
                messages.append(HumanMessage(content=content, additional_kwargs=kwargs))
            elif msg_type == "ai":
                messages.append(AIMessage(content=content, additional_kwargs=kwargs))
            else:
                print(f"[!] Tipo de mensaje no soportado: {msg_type}")

        memory.chat_memory.messages = messages

# Inicializar agente
agent = initialize_agent(
    tools=[get_my_name],
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)

# Consulta del usuario
query = input(": ")
respuesta = agent.invoke({"input": query})
print(respuesta["output"])

# Guardar la conversación actual
with open("chat_memory.json", "w", encoding="utf-8") as f:
    json.dump(memory.chat_memory.dict(), f, ensure_ascii=False, indent=2)
