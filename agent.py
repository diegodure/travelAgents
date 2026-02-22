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
    model="llama3.1:latest", 
    temperature=0
)
# 3. Prompt de ReAct PERSONALIZADO 
fly_ia_instructions = """Eres 'Fly IA', un asistente que SOLO vende lo que aparece en sus herramientas.

REGLAS DE ACERO (PROHIBIDO INVENTAR):
1. SI UN PRECIO O PAQUETE NO ESTÁ EN 'search_packages', NO EXISTE. No inventes descuentos ni tours (como el Museo del Prado o Retiro) si no están en el JSON.
2. Si el presupuesto del usuario es MENOR al del paquete, di: "No tengo paquetes por ese valor, pero puedo tomar tus datos para una cotización personalizada."
3. INSTRUCCIÓN DE ORO: Si encuentras el paquete, muestra Nombre, Precio y Descripción de inmediato.

EJEMPLO DE RESPUESTA CORRECTA:
Usuario: "Madrid"
Herramienta dice: "Paquete Madrid Real: $1200, incluye tour al Bernabéu."
Tu respuesta: "✈️ ¡Tengo una oferta! Paquete Madrid Real: $1200, incluye tour al Bernabéu. ¿Qué te parece?"

FLUJO:
- Si solo saludan: Pregunta el destino.
- Si el destino no está en el JSON: Pide Origen, Fechas, Personas y Presupuesto.
- Si ya tienes Nombre, Destino y Presupuesto: Usa 'agend_call'.
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