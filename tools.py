import unicodedata
import json
import os
from langchain_core.tools import tool

@tool
def search_packages(destination: str, month: str = None) -> str:
    """ÚSALA OBLIGATORIAMENTE para consultar precios reales. El mes es opcional."""

    def normalize_text(text):
        if not text: return ""
        return "".join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        ).lower().strip()

    print(f"DEBUG: Buscando destino: {destination} | Mes: {month}")
    
    file_path = os.path.join(os.path.dirname(__file__), 'packages.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            packages = json.load(f)

        dest_search = normalize_text(destination)
        mes_search = normalize_text(month) if month else "default"
        
        if dest_search in packages:
            p = packages[dest_search]
            
            # Obtener el diccionario de precios
            precios = p.get("precios_por_mes", {})
            
            # 1. Intentar el mes exacto 
            # 2. Si no está, intentar 'default'
            # 3. Si no hay 'default', usar el campo 'precio' antiguo (por compatibilidad)
            precio_final = precios.get(mes_search, precios.get("default", p.get("precio", 0)))
            
            msg_mes = f"para {month}" if month else "en tarifa base"
            return f"DATOS_DEL_PAQUETE: {p['nombre']} | Precio {msg_mes}: ${precio_final} USD | Descripción: {p['descripcion']}"
        
        else:
            disponibles = ", ".join([d.capitalize() for d in packages.keys()])
            return f"No tengo paquetes cerrados para {destination}. Actualmente solo cuento con: {disponibles}."
            
    except Exception as e:
        return f"Error al consultar la base de datos de paquetes: {str(e)}"

@tool
def baggage_policy(aeroline: str) -> str:
    """Consulta las políticas de equipaje de una aerolínea."""
    policys = {
        "latam": "Incluye bolso de mano (10kg) y maleta de bodega (23kg).",
        "copa": "Incluye solo bolso de mano (10kg) en tarifa económica.",
        "iberia": "Permite una maleta de cabina y un artículo personal."
    }

    return policys.get(aeroline.lower(), "La política varía según la tarifa. ¿Quieres que te comunique con un humano para confirmar?")

@tool
def agend_call(name: str, destination: str, budget: str) -> str:
    """
    REGISTRO FINAL: Úsala ÚNICAMENTE cuando ya tengas CONFIRMADOS el nombre, el destino y el presupuesto.
    """
    # VALIDACIÓN DE SEGURIDAD
    if not destination or not budget or "viajero" in name.lower():
        return "ERROR: No puedo registrar la llamada porque faltan datos. Debes preguntar al usuario el destino y su presupuesto primero."

    print(f"\n[SISTEMA]: 🚨 SOLICITUD DE VIAJE REGISTRADA 🚨")
    print(f"Cliente: {name} | Destino: {destination} | Presupuesto: {budget}")
    print(f"---------------------------------------------------\n")
    
    # En tools.py, dentro de agend_call:
    return f"¡Listo! Registro exitoso para {name}. Un agente experto te contactará pronto para coordinar tu viaje a {destination}."

tools_list = [search_packages, baggage_policy, agend_call]