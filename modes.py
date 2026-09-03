import json
import os
import subprocess

MODES_FILE = os.path.join(os.path.dirname(__file__), "data", "modes.json")

# ─── PERSISTENCIA ─────────────────────────────────────────────────────────────

def _cargar() -> dict:
    os.makedirs(os.path.dirname(MODES_FILE), exist_ok=True)
    if not os.path.exists(MODES_FILE):
        return {}
    with open(MODES_FILE, "r", encoding="utf-8") as f:
        contenido = f.read().strip()
        if not contenido:
            return {}
        return json.loads(contenido)

def _guardar(data: dict):
    os.makedirs(os.path.dirname(MODES_FILE), exist_ok=True)
    with open(MODES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── GESTIÓN DE MODOS ─────────────────────────────────────────────────────────

def crear_modo(nombre: str) -> str:
    """Crea un modo nuevo vacío."""
    data = _cargar()
    nombre_key = nombre.lower().strip()
    if nombre_key in data:
        apps = data[nombre_key]["apps"]
        return f"⚠️ El modo '{nombre}' ya existe con {len(apps)} app(s). Usá 'agregar app a modo' para agregarle más."
    data[nombre_key] = {
        "nombre_display": nombre,
        "apps": []
    }
    _guardar(data)
    return f"✅ Modo '{nombre}' creado. Ahora agregale apps con 'Agregá [app] al Modo {nombre}'."

def agregar_app_a_modo(modo: str, app: str) -> str:
    """Agrega una app a un modo existente."""
    data = _cargar()
    modo_key = modo.lower().strip()
    if modo_key not in data:
        return f"❌ El modo '{modo}' no existe. Crealo primero con 'Crear Modo {modo}'."
    app = app.strip()
    if app.lower() in [a.lower() for a in data[modo_key]["apps"]]:
        return f"⚠️ '{app}' ya está en el Modo '{modo}'."
    data[modo_key]["apps"].append(app)
    _guardar(data)
    apps_total = len(data[modo_key]["apps"])
    return f"✅ '{app}' agregado al Modo '{modo}'. Total: {apps_total} app(s): {', '.join(data[modo_key]['apps'])}"

def quitar_app_de_modo(modo: str, app: str) -> str:
    """Quita una app de un modo."""
    data = _cargar()
    modo_key = modo.lower().strip()
    if modo_key not in data:
        return f"❌ El modo '{modo}' no existe."
    apps = data[modo_key]["apps"]
    app_lower = app.lower()
    nueva_lista = [a for a in apps if a.lower() != app_lower]
    if len(nueva_lista) == len(apps):
        return f"❌ '{app}' no está en el Modo '{modo}'."
    data[modo_key]["apps"] = nueva_lista
    _guardar(data)
    return f"✅ '{app}' quitado del Modo '{modo}'."

def activar_modo(nombre: str) -> str:
    """Activa un modo abriendo todas sus apps."""
    data = _cargar()
    modo_key = nombre.lower().strip()
    if modo_key not in data:
        return f"❌ El modo '{nombre}' no existe. Crealo con 'Crear Modo {nombre}'."
    apps = data[modo_key]["apps"]
    if not apps:
        return f"⚠️ El Modo '{nombre}' no tiene apps. Agregale con 'Agregá [app] al Modo {nombre}'."

    from app_cache import obtener_cache
    cache = obtener_cache()
    abiertos = []
    no_encontrados = []

    for app in apps:
        app_lower = app.lower().strip().replace(".exe", "")
        exe_path = None

        # Buscar en cache exacto
        if app_lower in cache:
            exe_path = cache[app_lower]
        else:
            # Buscar parcial
            for clave, exe in cache.items():
                if app_lower in clave or clave in app_lower:
                    exe_path = exe
                    break

        if exe_path and os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path], shell=False)
                abiertos.append(app)
            except Exception:
                no_encontrados.append(app)
        else:
            # Último recurso
            try:
                subprocess.Popen(app, shell=True)
                abiertos.append(app)
            except Exception:
                no_encontrados.append(app)

    resultado = f"🚀 Modo '{nombre}' activado!\n"
    if abiertos:
        resultado += f"  ✅ Abiertos: {', '.join(abiertos)}\n"
    if no_encontrados:
        resultado += f"  ❌ No encontrados: {', '.join(no_encontrados)}\n"
    return resultado.strip()

def ver_modo(nombre: str) -> str:
    """Muestra las apps de un modo."""
    data = _cargar()
    modo_key = nombre.lower().strip()
    if modo_key not in data:
        return f"❌ El modo '{nombre}' no existe."
    apps = data[modo_key]["apps"]
    if not apps:
        return f"📋 Modo '{nombre}' está vacío. Agregale apps con 'Agregá [app] al Modo {nombre}'."
    lista = "\n".join(f"  • {a}" for a in apps)
    return f"📋 Modo '{nombre}' ({len(apps)} apps):\n{lista}"

def listar_modos() -> str:
    """Lista todos los modos disponibles."""
    data = _cargar()
    if not data:
        return "📋 No hay modos creados. Creá uno con 'Crear Modo [nombre]'."
    resultado = f"📋 Modos disponibles ({len(data)}):\n"
    for key, info in data.items():
        apps = info["apps"]
        resultado += f"  🎮 {info['nombre_display']}: {', '.join(apps) if apps else 'vacío'}\n"
    return resultado.strip()

def eliminar_modo(nombre: str) -> str:
    """Elimina un modo completo."""
    data = _cargar()
    modo_key = nombre.lower().strip()
    if modo_key not in data:
        return f"❌ El modo '{nombre}' no existe."
    del data[modo_key]
    _guardar(data)
    return f"✅ Modo '{nombre}' eliminado."