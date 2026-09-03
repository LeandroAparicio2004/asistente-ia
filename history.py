import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "data", "history.log")

def _asegurar_directorio():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

def registrar(accion: str, parametros: dict, resultado: str):
    """Registra una acción ejecutada en el log."""
    _asegurar_directorio()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    params_str = ", ".join(f"{k}={v}" for k, v in parametros.items())
    linea = f"[{timestamp}] ACCION: {accion} | PARAMS: {params_str} | RESULTADO: {resultado}\n"
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(linea)

def ver_historial(ultimas_n: int = 10) -> str:
    """Devuelve las últimas N entradas del historial."""
    _asegurar_directorio()
    if not os.path.exists(HISTORY_FILE):
        return "📋 El historial está vacío."
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    if not lineas:
        return "📋 El historial está vacío."
    ultimas = lineas[-ultimas_n:]
    return "📋 Últimas acciones:\n" + "".join(ultimas)

def limpiar_historial() -> str:
    _asegurar_directorio()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("")
    return "🧹 Historial limpiado."