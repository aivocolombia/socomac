from langchain_community.chat_models import ChatOllama
from langchain.agents import initialize_agent, AgentType
from test_tool import get_my_name

# Inicializar el modelo
llm = ChatOllama(model="qwen3:8b")

# Lista de tools disponibles
tools = [get_my_name]

# Inicializar el agente
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True
)

message = input(": ")
respuesta = agent.run(message)
print(respuesta)
