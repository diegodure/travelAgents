import os
from dotenv import load_dotenv
from langfuse.callback import CallbackHandler
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

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
    model="llama3.2:latest", 
    temperature=0
)

# 3. Prompt de sistema simplificado para el test
system_message = """
Eres 'Fly IA', el asistente virtual experto de 'Travel Premiun'. 
Responde de forma concisa y usa negritas para destacar destinos.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", "{input}"),
])

# 4. Función de ejecución con observabilidad
def ask_agent(user_input, session_id):
    # Creamos la cadena simple
    chain = prompt | llm
    
    # Invocamos con el callback de Langfuse
    response = chain.invoke(
        {"input": user_input},
        config={
            "callbacks": [langfuse_handler], 
            "run_name": f"Travel_Chat_{session_id}"
        }
    )
    return response.content