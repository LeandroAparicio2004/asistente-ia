import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "data", "memory.json")

def _cargar() -> dict:
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        return {"conversaciones": [], "contexto": {}}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return {"conversaciones": [], "contexto": {}}
        return json.loads(contenido)

def _guardar(data: dict):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def agregar_mensaje(rol: str, contenido: str):
    """Guarda un mensaje en la memoria (rol: 'user' o 'assistant')."""
    data = _cargar()
    data["conversaciones"].append({
        "rol": rol,
        "contenido": contenido,
        "timestamp": datetime.now().isoformat()
    })
    # Mantener solo los últimos 20 mensajes para no crecer infinito
    data["conversaciones"] = data["conversaciones"][-20:]
    _guardar(data)

def obtener_historial_chat() -> list:
    """Devuelve los mensajes en formato que entiende Groq."""
    data = _cargar()
    return [
        {"role": m["rol"], "content": m["contenido"]}
        for m in data["conversaciones"]
    ]

def guardar_contexto(clave: str, valor: str):
    """Guarda un dato de contexto (ej: nombre del usuario)."""
    data = _cargar()
    data["contexto"][clave] = valor
    _guardar(data)

def obtener_contexto(clave: str) -> str:
    data = _cargar()
    return data["contexto"].get(clave, "")

def limpiar_memoria():
    _guardar({"conversaciones": [], "contexto": {}})
    return "🧹 Memoria limpiada."