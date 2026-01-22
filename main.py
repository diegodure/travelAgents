from fastapi import FastAPI, Request
import uvicorn
# Aquí importarás tu lógica de agente luego
# from agent import travel_agent_executor

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    # 1. Recibir los datos de WPPConnect
    data = await request.json()
    
    # 2. Extraer información básica
    # WPPConnect envía mucha info, lo que nos importa es el texto y quién lo envía
    message_text = data.get("body")
    sender_number = data.get("from")
    
    if not message_text:
        return {"status": "ignored", "reason": "no text body"}

    print(f"Mensaje recibido de {sender_number}: {message_text}")

    # 3. AQUÍ LLAMAREMOS A TU AGENTE (PRÓXIMO PASO)
    # response = travel_agent_executor.invoke({"input": message_text})
    
    # Por ahora, una respuesta de prueba
    response_text = "¡Hola! Soy tu asistente de viajes. Recibí tu mensaje: " + message_text
    
    # 4. Enviar la respuesta de vuelta a WhatsApp vía WPPConnect API
    # (Usaremos la librería requests para pegarle al puerto 21465 del server)
    
    return {"status": "success", "reply": response_text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)