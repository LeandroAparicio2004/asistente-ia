import os
import json
from datetime import datetime, timedelta

AGENDA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "agenda.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> list:
    os.makedirs(os.path.dirname(AGENDA_FILE), exist_ok=True)
    if not os.path.exists(AGENDA_FILE):
        return []
    with open(AGENDA_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return []
        return json.loads(contenido)

def _guardar(data: list):
    os.makedirs(os.path.dirname(AGENDA_FILE), exist_ok=True)
    with open(AGENDA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _parsear_fecha(texto: str) -> datetime:
    """Convierte texto a datetime."""
    texto = texto.lower().strip()
    ahora = datetime.now()

    if texto in ("hoy", "today"):
        return ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    if texto in ("mañana", "manana", "tomorrow"):
        return (ahora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    if texto in ("pasado mañana", "pasado manana"):
        return (ahora + timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)

    DIAS = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    for dia, num in DIAS.items():
        if dia in texto:
            hoy = ahora.weekday()
            diff = (num - hoy) % 7
            if diff == 0:
                diff = 7
            return (ahora + timedelta(days=diff)).replace(hour=0, minute=0, second=0, microsecond=0)

    # DD/MM/YYYY
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(texto, fmt)
        except ValueError:
            continue

    raise ValueError(f"No pude interpretar la fecha '{texto}'")

def _parsear_hora(texto: str) -> tuple[int, int]:
    """Extrae hora y minutos de un texto como '18:30' o '18hs'."""
    texto = texto.strip().lower()
    texto = texto.replace("hs", "").replace("h", "").replace(":", " ").strip()
    partes = texto.split()
    if len(partes) >= 2:
        return int(partes[0]), int(partes[1])
    if len(partes) == 1:
        return int(partes[0]), 0
    return 0, 0

# ─── EVENTOS ──────────────────────────────────────────────────────────────────

def agregar_evento(titulo: str, fecha: str, hora: str = "", descripcion: str = "") -> str:
    try:
        fecha_dt = _parsear_fecha(fecha)
        if hora:
            h, m = _parsear_hora(hora)
            fecha_dt = fecha_dt.replace(hour=h, minute=m)

        data = _cargar()
        evento = {
            "id": int(datetime.now().timestamp()),
            "titulo": titulo,
            "fecha": fecha_dt.strftime("%Y-%m-%d"),
            "hora": fecha_dt.strftime("%H:%M") if hora else "",
            "descripcion": descripcion,
            "creado": datetime.now().isoformat()
        }
        data.append(evento)
        data.sort(key=lambda x: x["fecha"] + x["hora"])
        _guardar(data)

        fecha_str = fecha_dt.strftime("%d/%m/%Y")
        hora_str = f" a las {fecha_dt.strftime('%H:%M')}" if hora else ""
        return f"📅 Evento agregado: '{titulo}' el {fecha_str}{hora_str}"
    except ValueError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def ver_eventos_hoy() -> str:
    data = _cargar()
    hoy = datetime.now().strftime("%Y-%m-%d")
    eventos = [e for e in data if e["fecha"] == hoy]
    if not eventos:
        return "📅 No tenés eventos para hoy."
    resultado = f"📅 Eventos de hoy ({len(eventos)}):\n"
    for e in eventos:
        hora_str = f" a las {e['hora']}" if e["hora"] else ""
        desc_str = f"\n     📝 {e['descripcion']}" if e["descripcion"] else ""
        resultado += f"  • {e['titulo']}{hora_str}{desc_str}\n"
    return resultado.strip()

def ver_eventos_manana() -> str:
    data = _cargar()
    manana = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    eventos = [e for e in data if e["fecha"] == manana]
    if not eventos:
        return "📅 No tenés eventos para mañana."
    resultado = f"📅 Eventos de mañana ({len(eventos)}):\n"
    for e in eventos:
        hora_str = f" a las {e['hora']}" if e["hora"] else ""
        desc_str = f"\n     📝 {e['descripcion']}" if e["descripcion"] else ""
        resultado += f"  • {e['titulo']}{hora_str}{desc_str}\n"
    return resultado.strip()

def ver_eventos_semana() -> str:
    data = _cargar()
    hoy = datetime.now()
    fin_semana = hoy + timedelta(days=7)
    eventos = [
        e for e in data
        if hoy.strftime("%Y-%m-%d") <= e["fecha"] <= fin_semana.strftime("%Y-%m-%d")
    ]
    if not eventos:
        return "📅 No tenés eventos esta semana."
    resultado = f"📅 Eventos próximos 7 días ({len(eventos)}):\n"
    for e in eventos:
        fecha_dt = datetime.strptime(e["fecha"], "%Y-%m-%d")
        fecha_str = fecha_dt.strftime("%d/%m/%Y")
        hora_str = f" a las {e['hora']}" if e["hora"] else ""
        resultado += f"  • {fecha_str}{hora_str}: {e['titulo']}\n"
    return resultado.strip()

def ver_todos_eventos() -> str:
    data = _cargar()
    hoy = datetime.now().strftime("%Y-%m-%d")
    futuros = [e for e in data if e["fecha"] >= hoy]
    if not futuros:
        return "📅 No tenés eventos futuros."
    resultado = f"📅 Todos tus eventos ({len(futuros)}):\n"
    for e in futuros:
        fecha_dt = datetime.strptime(e["fecha"], "%Y-%m-%d")
        fecha_str = fecha_dt.strftime("%d/%m/%Y")
        hora_str = f" a las {e['hora']}" if e["hora"] else ""
        resultado += f"  • {fecha_str}{hora_str}: {e['titulo']}\n"
    return resultado.strip()

def _normalizar(texto: str) -> str:
    """Elimina tildes y pasa a minúsculas para comparar."""
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'ñ': 'n'
    }
    texto = texto.lower()
    for orig, reemplazo in reemplazos.items():
        texto = texto.replace(orig, reemplazo)
    return texto

def eliminar_evento(identificador: str) -> str:
    data = _cargar()
    identificador_norm = _normalizar(identificador.strip())
    eliminados = []
    nuevos = []
    for e in data:
        titulo_norm = _normalizar(e["titulo"])
        if identificador_norm in titulo_norm or str(e["id"]) == identificador.strip():
            eliminados.append(e["titulo"])
        else:
            nuevos.append(e)
    if not eliminados:
        return f"❌ No encontré evento con '{identificador}'."
    _guardar(nuevos)
    return f"✅ Evento eliminado: '{eliminados[0]}'"

def ver_eventos_fecha(fecha: str) -> str:
    try:
        fecha_dt = _parsear_fecha(fecha)
        fecha_str = fecha_dt.strftime("%Y-%m-%d")
        data = _cargar()
        eventos = [e for e in data if e["fecha"] == fecha_str]
        if not eventos:
            return f"📅 No tenés eventos para el {fecha_dt.strftime('%d/%m/%Y')}."
        resultado = f"📅 Eventos del {fecha_dt.strftime('%d/%m/%Y')} ({len(eventos)}):\n"
        for e in eventos:
            hora_str = f" a las {e['hora']}" if e["hora"] else ""
            resultado += f"  • {e['titulo']}{hora_str}\n"
        return resultado.strip()
    except ValueError as e:
        return f"❌ {str(e)}"