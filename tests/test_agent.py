from agent import ask_agent

try:
    print("🚀 Iniciando prueba de memoria de Fly IA...")
    session = "cliente_diego_1"

    # Primera interacción
    print("\n--- Mensaje 1 ---")
    res1 = ask_agent("Hola, soy Diego. ¿Qué paquetes tienes para Cancún?", session)
    print(f"🤖: {res1}")

    # Segunda interacción (sin repetir el nombre ni el destino)
    print("\n--- Mensaje 2 ---")
    res2 = ask_agent("¿Recuerdas mi nombre? ¿Y qué me dijiste que incluía el paquete?", session)
    print(f"🤖: {res2}")
    
    print("\n✅ Prueba de memoria finalizada.")

except Exception as e:
    print(f"\n❌ Error: {e}")