from fastapi import FastAPI, Request
import uvicorn
import os
import base64
from faster_whisper import WhisperModel
from agent import ask_agent

app = FastAPI()

# --- CARGA DEL MODELO AL INICIO ---
# Usamos 'base' para velocidad y 'int8' para cuidar tus 12GB de RAM
print("🚀 Cargando modelo de transcripción (Faster-Whisper)...")
stt_model = WhisperModel("base", device="cpu", compute_type="int8")

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    try:
        data = await request.json()

        # 1. Validaciones iniciales
        sender_number = data.get("from")
        sender_name = data.get("name", "viajero")
        
        if not sender_number or "status@broadcast" in sender_number:
            return {"status": "ignored"}

        event = data.get("event")
        if event != "onMessage":
            return {"status": "event_ignored"}

        # --- 2. LÓGICA DE PROCESAMIENTO (AUDIO O TEXTO) ---
        message_text = ""

        if data.get("type") == "audio":
            print(f"🎤 Procesando audio de {sender_name}...")
            try:
                # Decodificar el base64 que viene de Node.js
                audio_buffer = base64.b64decode(data.get("audio_buffer"))
                temp_filename = f"temp_{sender_number}.ogg"
                
                # Guardar temporalmente para que Whisper lo lea
                with open(temp_filename, "wb") as f:
                    f.write(audio_buffer)

                # Transcribir
                segments, info = stt_model.transcribe(temp_filename, beam_size=5)
                message_text = " ".join([segment.text for segment in segments])
                
                # Limpiar archivo temporal
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
                
                print(f"📝 Transcripción: {message_text}")
                
            except Exception as audio_err:
                print(f"❌ Error procesando audio: {audio_err}")
                return {"status": "error", "message": "No se pudo procesar el audio"}
        else:
            # Es un mensaje de texto normal
            message_text = data.get("body")
            print(f"📩 Mensaje de {sender_name}: {message_text}")

        # 3. Validar si hay texto para procesar
        if not message_text or message_text.strip() == "":
            return {"status": "data_incomplete"}

        # 4. LLAMAR A FLY IA (agent.py)
        response_text = ask_agent(message_text, sender_number, sender_name)
        
        print(f"🤖 Fly IA responde: {response_text}")

        # 5. Respuesta final al bot de Node.js
        return {
            "status": "success",
            "reply": response_text
        }

    except Exception as e:
        print(f"❌ Error crítico en webhook: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("🚀 Servidor Fly IA Webhook iniciado en puerto 8000...")
    # Cambiamos reload=False para que no recargue el modelo Whisper cada vez que tocas el código
    uvicorn.run(app, host="0.0.0.0", port=8000)