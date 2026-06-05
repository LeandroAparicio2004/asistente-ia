import json
import os
import threading
import time
from datetime import datetime, timedelta

REMINDERS_FILE = os.path.join(os.path.dirname(__file__), "data", "reminders.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> list:
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    if not os.path.exists(REMINDERS_FILE):
        return []
    with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return []
        return json.loads(contenido)

def _guardar(data: list):
    os.makedirs(os.path.dirname(REMINDERS_FILE), exist_ok=True)
    with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── GESTIÓN DE RECORDATORIOS ─────────────────────────────────────────────────

def agregar_recordatorio(mensaje: str, cuando: str) -> str:
    try:
        fecha_hora = _parsear_cuando(cuando)
    except ValueError as e:
        return f"❌ No entendí la hora: {str(e)}"

    # Si el mensaje es vacío o tiene placeholder, usar la hora real
    if not mensaje or mensaje.strip() == "" or "{hora}" in mensaje or mensaje == "Son las ":
        mensaje = f"Son las {fecha_hora.strftime('%H:%M')}"

    data = _cargar()
    nuevo = {
        "id": int(datetime.now().timestamp()),
        "mensaje": mensaje,
        "cuando": fecha_hora.isoformat(),
        "disparado": False
    }
    data.append(nuevo)
    _guardar(data)
    cuando_str = fecha_hora.strftime("%d/%m/%Y a las %H:%M")
    return f"⏰ Recordatorio guardado para el {cuando_str}: '{mensaje}'"

def _parsear_cuando(cuando: str) -> datetime:
    cuando = cuando.lower().strip()
    ahora = datetime.now()

    if "minuto" in cuando:
        for parte in cuando.split():
            if parte.isdigit():
                return ahora + timedelta(minutes=int(parte))
        raise ValueError("No encontré el número de minutos")

    if "hora" in cuando:
        for parte in cuando.split():
            if parte.isdigit():
                return ahora + timedelta(hours=int(parte))
        raise ValueError("No encontré el número de horas")

    if "segundo" in cuando:
        for parte in cuando.split():
            if parte.isdigit():
                return ahora + timedelta(seconds=int(parte))

    if ":" in cuando and len(cuando) <= 5:
        hora, minuto = cuando.split(":")
        resultado = ahora.replace(hour=int(hora), minute=int(minuto), second=0, microsecond=0)
        if resultado <= ahora:
            resultado += timedelta(days=1)
        return resultado

    try:
        return datetime.strptime(cuando, "%d/%m/%Y %H:%M")
    except ValueError:
        pass

    try:
        dt = datetime.strptime(cuando, "%d/%m %H:%M")
        return dt.replace(year=ahora.year)
    except ValueError:
        pass

    raise ValueError(f"Formato no reconocido: '{cuando}'")

def listar_recordatorios() -> str:
    data = _cargar()
    pendientes = [r for r in data if not r["disparado"]]
    if not pendientes:
        return "📋 No tenés recordatorios pendientes."
    resultado = f"📋 Tenés {len(pendientes)} recordatorio(s) pendiente(s):\n"
    for r in pendientes:
        dt = datetime.fromisoformat(r["cuando"])
        cuando_str = dt.strftime("%d/%m/%Y a las %H:%M")
        resultado += f"  ⏰ [{r['id']}] {cuando_str}: '{r['mensaje']}'\n"
    return resultado

def cancelar_recordatorio(identificador: str) -> str:
    data = _cargar()
    identificador = identificador.strip()
    cancelados = []
    for r in data:
        if str(r["id"]) == identificador:
            r["disparado"] = True
            cancelados.append(r["mensaje"])
            continue
        if identificador.lower() in r["mensaje"].lower() and not r["disparado"]:
            r["disparado"] = True
            cancelados.append(r["mensaje"])
    if not cancelados:
        return f"❌ No encontré recordatorio con '{identificador}'."
    _guardar(data)
    return f"✅ Cancelado(s): {', '.join(cancelados)}"

def cancelar_todos_recordatorios() -> str:
    data = _cargar()
    count = 0
    for r in data:
        if not r["disparado"]:
            r["disparado"] = True
            count += 1
    _guardar(data)
    return f"✅ {count} recordatorio(s) cancelado(s)."

# ─── HILO DE MONITOREO ────────────────────────────────────────────────────────

_monitor_activo = False

def _monitor_loop():
    """Corre en segundo plano y dispara recordatorios cuando llega la hora."""
    global _monitor_activo
    while _monitor_activo:
        try:
            data = _cargar()
            ahora = datetime.now()
            hubo_cambio = False

            for r in data:
                if r["disparado"]:
                    continue
                cuando = datetime.fromisoformat(r["cuando"])
                if ahora >= cuando:
                    r["disparado"] = True
                    hubo_cambio = True
                    mensaje = r["mensaje"]
                    print(f"\n{'='*40}")
                    print(f"🔔  ¡RECORDATORIO!  🔔")
                    print(f"   {mensaje}")
                    print(f"{'='*40}\n")
                    try:
                        import winsound
                        for _ in range(3):
                            winsound.Beep(1000, 400)
                            time.sleep(0.2)
                    except Exception:
                        pass

            if hubo_cambio:
                _guardar(data)

        except Exception:
            pass

        time.sleep(30)

def iniciar_monitor():
    global _monitor_activo
    if _monitor_activo:
        return
    _monitor_activo = True
    hilo = threading.Thread(target=_monitor_loop, daemon=True)
    hilo.start()

def detener_monitor():
    global _monitor_activo
    _monitor_activo = False