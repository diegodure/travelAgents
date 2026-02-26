import os
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler
from langchain_ollama import ChatOllama
from langchain_ollama import ChatOllama

from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from tools import tools_list

from langgraph.prebuilt import create_react_agent

# Cargar variables de entorno (.env)
load_dotenv()

# 1. Configurar el observador de Langfuse
langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)

# 2. Configurar el modelo LLM Ollama
llm = ChatOllama(
    model="qwen2.5:7b", 
    temperature=0
)
# 3. Prompt de ReAct PERSONALIZADO para Qwen 2.5
fly_ia_instructions = """
<identity>
Eres 'Fly IA', un asistente de ventas experto para una agencia de viajes paraguaya. 
Tu objetivo es ayudar a viajeros de todo el país a encontrar su mejor opción, 
ya sea saliendo desde Asunción, Ciudad del Este/Foz o cualquier punto fronterizo.
</identity>

<rules>
1. PRECIOS DINÁMICOS: Los precios pueden variar según el mes. Si el usuario menciona una fecha, inclúyela en tu búsqueda.
2. FLEXIBILIDAD: Si el usuario es de CDE o frontera, menciona que podemos cotizar salidas desde Foz de Iguazú si le resulta más cómodo.
3. PROHIBIDO INVENTAR: Si un paquete no está en 'search_packages', no existe.
</rules>

<workflow>
- Si mencionan un destino: Usa 'search_packages' incluyendo el mes si lo sabes.
- Si el destino no existe o quieren algo a medida: Pide Origen (ej. ASU o CDE), Fechas y Presupuesto.
- Si el presupuesto es insuficiente: Ofrece cotización personalizada.
- Cierre: Usa 'agend_call' cuando tengas Nombre, Destino y Presupuesto.
</workflow>
"""

# 4. Configurar la Memoria
memory = MemorySaver() # Esto guardará los chats en RAM

# 5. Crear el Agente (Basado en la nueva arquitectura LangGraph)
# create_agent detecta las herramientas y configura el loop de ReAct solo
agent = create_react_agent(
    model=llm,
    tools=tools_list,
    prompt=fly_ia_instructions, # Cambiado de state_modifier a prompt
    checkpointer=memory
)

# 6. Función de ejecución simplificada
def ask_agent(user_input, session_id, user_name=None):
    config = {
        "configurable": {"thread_id": session_id},
        "callbacks": [langfuse_handler],
    }

    # Si es el primer mensaje, el modelo ya sabe el nombre por el contexto, 
    # pero no satures el input si no es necesario.
    content = user_input 

    response = agent.invoke(
        {"messages": [{"role": "user", "content": content}]},
        config=config
    )
    return response["messages"][-1].content