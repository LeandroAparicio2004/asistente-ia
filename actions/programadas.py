import os
import json
import threading
import time
from datetime import datetime, timedelta

PROGRAMADAS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "programadas.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> list:
    os.makedirs(os.path.dirname(PROGRAMADAS_FILE), exist_ok=True)
    if not os.path.exists(PROGRAMADAS_FILE):
        return []
    with open(PROGRAMADAS_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return []
        return json.loads(contenido)

def _guardar(data: list):
    os.makedirs(os.path.dirname(PROGRAMADAS_FILE), exist_ok=True)
    with open(PROGRAMADAS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _parsear_cuando(cuando: str) -> datetime:
    cuando = cuando.lower().strip()
    ahora = datetime.now()

    if "minuto" in cuando:
        for p in cuando.split():
            if p.isdigit():
                return ahora + timedelta(minutes=int(p))

    if "hora" in cuando:
        for p in cuando.split():
            if p.isdigit():
                return ahora + timedelta(hours=int(p))

    if ":" in cuando and len(cuando) <= 5:
        h, m = cuando.split(":")
        resultado = ahora.replace(hour=int(h), minute=int(m), second=0, microsecond=0)
        if resultado <= ahora:
            resultado += timedelta(days=1)
        return resultado

    try:
        return datetime.strptime(cuando, "%d/%m/%Y %H:%M")
    except ValueError:
        pass

    raise ValueError(f"No pude interpretar '{cuando}'")

# ─── ACCIONES PROGRAMADAS ─────────────────────────────────────────────────────

def programar_accion(accion: str, parametros: dict, cuando: str, descripcion: str = "") -> str:
    """Programa una acción para ejecutarse en un momento determinado."""
    try:
        fecha_hora = _parsear_cuando(cuando)
    except ValueError as e:
        return f"❌ {str(e)}"

    data = _cargar()
    nueva = {
        "id": int(datetime.now().timestamp()),
        "accion": accion,
        "parametros": parametros,
        "cuando": fecha_hora.isoformat(),
        "descripcion": descripcion or f"Ejecutar {accion}",
        "ejecutada": False
    }
    data.append(nueva)
    _guardar(data)

    cuando_str = fecha_hora.strftime("%d/%m/%Y a las %H:%M")
    return f"⏰ Acción programada para el {cuando_str}: '{nueva['descripcion']}'"

def listar_programadas() -> str:
    data = _cargar()
    pendientes = [a for a in data if not a["ejecutada"]]
    if not pendientes:
        return "📋 No hay acciones programadas pendientes."
    resultado = f"📋 Acciones programadas ({len(pendientes)}):\n"
    for a in pendientes:
        dt = datetime.fromisoformat(a["cuando"])
        cuando_str = dt.strftime("%d/%m/%Y a las %H:%M")
        resultado += f"  ⏰ [{a['id']}] {cuando_str}: {a['descripcion']}\n"
    return resultado.strip()

def cancelar_programada(identificador: str) -> str:
    data = _cargar()
    identificador = identificador.strip()
    canceladas = []
    for a in data:
        if (str(a["id"]) == identificador or
            identificador.lower() in a["descripcion"].lower()) and not a["ejecutada"]:
            a["ejecutada"] = True
            canceladas.append(a["descripcion"])
    if not canceladas:
        return f"❌ No encontré acción programada con '{identificador}'."
    _guardar(data)
    return f"✅ Cancelada: '{canceladas[0]}'"

# ─── MONITOR ──────────────────────────────────────────────────────────────────

_monitor_activo = False

def _monitor_loop():
    global _monitor_activo
    while _monitor_activo:
        try:
            data = _cargar()
            ahora = datetime.now()
            hubo_cambio = False

            for a in data:
                if a["ejecutada"]:
                    continue
                cuando = datetime.fromisoformat(a["cuando"])
                if ahora >= cuando:
                    a["ejecutada"] = True
                    hubo_cambio = True
                    try:
                        # Importar executor y ejecutar la acción
                        from executor import ACCIONES
                        accion = a["accion"]
                        parametros = a.get("parametros", {})
                        if accion in ACCIONES:
                            resultado = ACCIONES[accion](**parametros)
                            print(f"\n{'='*40}")
                            print(f"⚡ ACCIÓN PROGRAMADA: {a['descripcion']}")
                            print(f"   Resultado: {resultado}")
                            print(f"{'='*40}\n")
                            try:
                                import winsound
                                winsound.Beep(800, 300)
                            except Exception:
                                pass
                        else:
                            print(f"\n❌ Acción '{accion}' no encontrada.")
                    except Exception as e:
                        print(f"\n❌ Error al ejecutar acción programada: {str(e)}")

            if hubo_cambio:
                _guardar(data)

        except Exception:
            pass

        time.sleep(30)

def iniciar_monitor_programadas():
    global _monitor_activo
    if _monitor_activo:
        return
    _monitor_activo = True
    hilo = threading.Thread(target=_monitor_loop, daemon=True)
    hilo.start()