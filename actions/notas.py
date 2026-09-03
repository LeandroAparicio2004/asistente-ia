import os
import json
from datetime import datetime
from config import SANDBOX_PATH

NOTAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "notas.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> dict:
    os.makedirs(os.path.dirname(NOTAS_FILE), exist_ok=True)
    if not os.path.exists(NOTAS_FILE):
        return {"notas": [], "tareas": []}
    with open(NOTAS_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return {"notas": [], "tareas": []}
        return json.loads(contenido)

def _guardar(data: dict):
    os.makedirs(os.path.dirname(NOTAS_FILE), exist_ok=True)
    with open(NOTAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── NOTAS RÁPIDAS ────────────────────────────────────────────────────────────

def agregar_nota(texto: str) -> str:
    data = _cargar()
    nota = {
        "id": int(datetime.now().timestamp()),
        "texto": texto,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    data["notas"].append(nota)
    _guardar(data)
    return f"📝 Nota guardada: '{texto}'"

def ver_notas() -> str:
    data = _cargar()
    notas = data["notas"]
    if not notas:
        return "📝 No tenés notas guardadas."
    resultado = f"📝 Tus notas ({len(notas)}):\n"
    for n in notas:
        resultado += f"  [{n['fecha']}] {n['texto']}\n"
    return resultado.strip()

def eliminar_nota(identificador: str) -> str:
    data = _cargar()
    identificador = identificador.strip()
    eliminadas = []
    nuevas = []
    for n in data["notas"]:
        if identificador.lower() in n["texto"].lower() or str(n["id"]) == identificador:
            eliminadas.append(n["texto"])
        else:
            nuevas.append(n)
    if not eliminadas:
        return f"❌ No encontré nota con '{identificador}'."
    data["notas"] = nuevas
    _guardar(data)
    return f"✅ Nota eliminada: '{eliminadas[0]}'"

def limpiar_notas() -> str:
    data = _cargar()
    cantidad = len(data["notas"])
    data["notas"] = []
    _guardar(data)
    return f"✅ {cantidad} nota(s) eliminada(s)."

# ─── LISTA DE TAREAS (TODO) ───────────────────────────────────────────────────

def agregar_tarea(texto: str) -> str:
    data = _cargar()
    tarea = {
        "id": int(datetime.now().timestamp()),
        "texto": texto,
        "completada": False,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    data["tareas"].append(tarea)
    _guardar(data)
    return f"✅ Tarea agregada: '{texto}'"

def ver_tareas(solo_pendientes: bool = True) -> str:
    data = _cargar()
    tareas = data["tareas"]
    if solo_pendientes:
        tareas = [t for t in tareas if not t["completada"]]
    if not tareas:
        return "📋 No tenés tareas pendientes." if solo_pendientes else "📋 No tenés tareas."
    resultado = f"📋 Tareas {'pendientes' if solo_pendientes else 'todas'} ({len(tareas)}):\n"
    for t in tareas:
        estado = "✅" if t["completada"] else "⬜"
        resultado += f"  {estado} [{t['fecha']}] {t['texto']}\n"
    return resultado.strip()

def completar_tarea(identificador: str) -> str:
    data = _cargar()
    identificador = identificador.strip()
    completadas = []
    for t in data["tareas"]:
        if (identificador.lower() in t["texto"].lower() or str(t["id"]) == identificador) and not t["completada"]:
            t["completada"] = True
            completadas.append(t["texto"])
    if not completadas:
        return f"❌ No encontré tarea pendiente con '{identificador}'."
    _guardar(data)
    return f"✅ Tarea completada: '{completadas[0]}'"

def eliminar_tarea(identificador: str) -> str:
    data = _cargar()
    identificador = identificador.strip()
    eliminadas = []
    nuevas = []
    for t in data["tareas"]:
        if identificador.lower() in t["texto"].lower() or str(t["id"]) == identificador:
            eliminadas.append(t["texto"])
        else:
            nuevas.append(t)
    if not eliminadas:
        return f"❌ No encontré tarea con '{identificador}'."
    data["tareas"] = nuevas
    _guardar(data)
    return f"✅ Tarea eliminada: '{eliminadas[0]}'"

def limpiar_tareas_completadas() -> str:
    data = _cargar()
    antes = len(data["tareas"])
    data["tareas"] = [t for t in data["tareas"] if not t["completada"]]
    eliminadas = antes - len(data["tareas"])
    _guardar(data)
    return f"✅ {eliminadas} tarea(s) completada(s) eliminada(s)."