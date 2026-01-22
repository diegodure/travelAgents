from agent import ask_agent

try:
    print("🚀 Iniciando prueba del agente de viajes...")
    # Usamos un ID de sesión cualquiera para la prueba
    respuesta = ask_agent("Hola Fly IA, ¿qué paquetes tienes para Cancún?", "session_123")
    
    print("\n🤖 RESPUESTA DEL AGENTE:")
    print(respuesta)
    print("\n✅ Prueba finalizada. Revisa Langfuse para ver la traza.")

except Exception as e:
    print(f"\n❌ Error durante la prueba: {e}")
    print("Asegúrate de que Ollama esté corriendo (`ollama serve`) y el modelo descargado.")