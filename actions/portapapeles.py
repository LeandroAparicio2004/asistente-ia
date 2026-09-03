import os
import json
from datetime import datetime

CLIPBOARD_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "portapapeles.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> list:
    os.makedirs(os.path.dirname(CLIPBOARD_FILE), exist_ok=True)
    if not os.path.exists(CLIPBOARD_FILE):
        return []
    with open(CLIPBOARD_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return []
        return json.loads(contenido)

def _guardar(data: list):
    os.makedirs(os.path.dirname(CLIPBOARD_FILE), exist_ok=True)
    with open(CLIPBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── PORTAPAPELES ─────────────────────────────────────────────────────────────

def copiar_texto(texto: str) -> str:
    """Copia texto al portapapeles."""
    try:
        import pyperclip
        pyperclip.copy(texto)
        return f"📋 Copiado al portapapeles: '{texto[:50]}{'...' if len(texto) > 50 else ''}'"
    except Exception as e:
        return f"❌ Error al copiar: {str(e)}"

def obtener_portapapeles() -> str:
    """Lee lo que hay actualmente en el portapapeles."""
    try:
        import pyperclip
        contenido = pyperclip.paste()
        if not contenido.strip():
            return "📋 El portapapeles está vacío."
        return f"📋 Portapapeles actual:\n{contenido}"
    except Exception as e:
        return f"❌ Error al leer portapapeles: {str(e)}"

def guardar_portapapeles(etiqueta: str = "") -> str:
    """Guarda el contenido actual del portapapeles en el historial."""
    try:
        import pyperclip
        contenido = pyperclip.paste()
        if not contenido.strip():
            return "📋 El portapapeles está vacío, nada que guardar."

        data = _cargar()
        entrada = {
            "id": int(datetime.now().timestamp()),
            "texto": contenido,
            "etiqueta": etiqueta if etiqueta else "",
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        data.append(entrada)
        # Mantener solo los últimos 30
        data = data[-30:]
        _guardar(data)

        label = f" como '{etiqueta}'" if etiqueta else ""
        return f"✅ Portapapeles guardado{label}: '{contenido[:50]}{'...' if len(contenido) > 50 else ''}'"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def ver_historial_portapapeles() -> str:
    """Muestra el historial guardado del portapapeles."""
    data = _cargar()
    if not data:
        return "📋 No hay nada guardado en el historial del portapapeles."
    resultado = f"📋 Historial del portapapeles ({len(data)} entradas):\n"
    for i, entrada in enumerate(reversed(data[-10:]), 1):
        etiqueta = f" [{entrada['etiqueta']}]" if entrada.get("etiqueta") else ""
        texto_corto = entrada['texto'][:60] + "..." if len(entrada['texto']) > 60 else entrada['texto']
        resultado += f"  {i}. {entrada['fecha']}{etiqueta}: {texto_corto}\n"
    return resultado.strip()

def recuperar_de_historial(identificador: str) -> str:
    """Recupera una entrada del historial y la pone en el portapapeles."""
    try:
        import pyperclip
        data = _cargar()
        if not data:
            return "📋 El historial está vacío."

        identificador = identificador.strip()

        # Buscar por número (posición)
        if identificador.isdigit():
            idx = int(identificador) - 1
            invertido = list(reversed(data))
            if 0 <= idx < len(invertido):
                texto = invertido[idx]["texto"]
                pyperclip.copy(texto)
                return f"✅ Recuperado al portapapeles: '{texto[:50]}{'...' if len(texto) > 50 else ''}'"

        # Buscar por etiqueta o contenido
        for entrada in reversed(data):
            if (identificador.lower() in entrada.get("etiqueta", "").lower() or
                identificador.lower() in entrada["texto"].lower()):
                pyperclip.copy(entrada["texto"])
                return f"✅ Recuperado al portapapeles: '{entrada['texto'][:50]}{'...' if len(entrada['texto']) > 50 else ''}'"

        return f"❌ No encontré '{identificador}' en el historial."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def limpiar_historial_portapapeles() -> str:
    """Limpia el historial guardado."""
    data = _cargar()
    cantidad = len(data)
    _guardar([])
    return f"✅ Historial del portapapeles limpiado ({cantidad} entradas eliminadas)."