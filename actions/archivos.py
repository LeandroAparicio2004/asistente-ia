import os
import shutil
from config import SANDBOX_PATH

# ─── DIRECTORIO ACTIVO ────────────────────────────────────────────────────────

_directorio_activo = ""

def entrar_carpeta(nombre: str = "", **kwargs) -> str:
    global _directorio_activo
    nombre = nombre or kwargs.get("carpeta") or kwargs.get("directorio") or ""
    if not nombre:
        return "❌ No especificaste a qué carpeta entrar."
    ruta = os.path.abspath(os.path.join(SANDBOX_PATH, nombre))
    if not ruta.startswith(os.path.abspath(SANDBOX_PATH)):
        return "❌ Acceso fuera del sandbox bloqueado."
    if not os.path.exists(ruta):
        return f"❌ La carpeta '{nombre}' no existe."
    if not os.path.isdir(ruta):
        return f"❌ '{nombre}' no es una carpeta."
    _directorio_activo = nombre
    contenido = os.listdir(ruta)
    if not contenido:
        return f"📁 Entraste a '{nombre}'. La carpeta está vacía."
    items = ""
    for item in contenido:
        tipo = "📁" if os.path.isdir(os.path.join(ruta, item)) else "📄"
        items += f"\n  {tipo} {item}"
    return f"📁 Entraste a '{nombre}'. Contenido:{items}"

def salir_carpeta() -> str:
    global _directorio_activo
    if not _directorio_activo:
        return "ℹ️ No estás dentro de ninguna carpeta."
    nombre = _directorio_activo
    _directorio_activo = ""
    return f"✅ Saliste de '{nombre}'. Ahora estás en la raíz del sandbox."

def obtener_directorio_activo() -> str:
    return _directorio_activo

# ─── SEGURIDAD SANDBOX ────────────────────────────────────────────────────────

def ruta_segura(nombre: str) -> str:
    if _directorio_activo and not os.path.isabs(nombre):
        ruta = os.path.abspath(os.path.join(SANDBOX_PATH, _directorio_activo, nombre))
    else:
        ruta = os.path.abspath(os.path.join(SANDBOX_PATH, nombre))
    if not ruta.startswith(os.path.abspath(SANDBOX_PATH)):
        raise ValueError("❌ Intento de acceso fuera del sandbox bloqueado.")
    return ruta

def buscar_nombre_real(nombre: str) -> str:
    ruta = ruta_segura(nombre)
    if os.path.exists(ruta):
        return nombre
    directorio = os.path.dirname(ruta)
    nombre_base = os.path.basename(nombre)
    if os.path.exists(directorio):
        for item in os.listdir(directorio):
            if os.path.splitext(item)[0].lower() == nombre_base.lower():
                return os.path.join(os.path.dirname(nombre), item) if os.path.dirname(nombre) else item
    return nombre

# ─── CARPETAS ─────────────────────────────────────────────────────────────────

def crear_carpeta(nombre: str) -> str:
    ruta = ruta_segura(nombre)
    os.makedirs(ruta, exist_ok=True)
    ubicacion = f" dentro de '{_directorio_activo}'" if _directorio_activo else ""
    return f"✅ Carpeta '{nombre}' creada{ubicacion}."

def eliminar_carpeta(nombre: str) -> str:
    ruta = ruta_segura(nombre)
    if not os.path.exists(ruta):
        return f"❌ La carpeta '{nombre}' no existe."
    shutil.rmtree(ruta)
    return f"✅ Carpeta '{nombre}' eliminada."

def listar_contenido(subcarpeta: str = "") -> str:
    if subcarpeta:
        ruta = ruta_segura(subcarpeta)
    elif _directorio_activo:
        ruta = os.path.abspath(os.path.join(SANDBOX_PATH, _directorio_activo))
    else:
        ruta = SANDBOX_PATH
    if not os.path.exists(ruta):
        return f"❌ La carpeta no existe."
    items = os.listdir(ruta)
    if not items:
        return "📂 La carpeta está vacía."
    resultado = f"📂 Contenido de '{_directorio_activo or 'sandbox'}':\n"
    for item in items:
        ruta_item = os.path.join(ruta, item)
        tipo = "📁" if os.path.isdir(ruta_item) else "📄"
        resultado += f"  {tipo} {item}\n"
    return resultado

# ─── ARCHIVOS ─────────────────────────────────────────────────────────────────

def crear_archivo(nombre: str, contenido: str = "") -> str:
    ruta = ruta_segura(nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    ubicacion = f" dentro de '{_directorio_activo}'" if _directorio_activo else ""
    return f"✅ Archivo '{nombre}' creado{ubicacion}."

def eliminar_archivo(nombre: str) -> str:
    nombre = buscar_nombre_real(nombre)
    ruta = ruta_segura(nombre)
    if not os.path.exists(ruta):
        return f"❌ El archivo '{nombre}' no existe."
    os.remove(ruta)
    return f"✅ Archivo '{nombre}' eliminado."

def leer_archivo(nombre: str) -> str:
    nombre = buscar_nombre_real(nombre)
    ruta = ruta_segura(nombre)
    if not os.path.exists(ruta):
        return f"❌ El archivo '{nombre}' no existe."
    with open(ruta, "r", encoding="utf-8") as f:
        contenido = f.read()
    if not contenido.strip():
        return f"📄 El archivo '{nombre}' está vacío."
    return f"📄 Contenido de '{nombre}':\n{contenido}"

def mover(origen: str, destino: str) -> str:
    origen = buscar_nombre_real(origen)
    ruta_origen = ruta_segura(origen)
    ruta_destino = ruta_segura(destino)
    if not os.path.exists(ruta_origen):
        return f"❌ '{origen}' no existe."
    if os.path.isdir(ruta_destino):
        ruta_destino = os.path.join(ruta_destino, os.path.basename(ruta_origen))
    else:
        _, ext_origen = os.path.splitext(ruta_origen)
        _, ext_destino = os.path.splitext(ruta_destino)
        if ext_origen and not ext_destino:
            ruta_destino = ruta_destino + ext_origen
    shutil.move(ruta_origen, ruta_destino)
    return f"✅ '{origen}' movido a '{destino}'."

def copiar(origen: str, destino: str) -> str:
    origen = buscar_nombre_real(origen)
    ruta_origen = ruta_segura(origen)
    ruta_destino = ruta_segura(destino)
    if not os.path.exists(ruta_origen):
        return f"❌ '{origen}' no existe."
    if os.path.isdir(ruta_origen):
        shutil.copytree(ruta_origen, ruta_destino)
    else:
        if os.path.isdir(ruta_destino):
            ruta_destino = os.path.join(ruta_destino, os.path.basename(ruta_origen))
        shutil.copy2(ruta_origen, ruta_destino)
    return f"✅ '{origen}' copiado a '{destino}'."

def renombrar(nombre_actual: str, nombre_nuevo: str) -> str:
    nombre_actual = buscar_nombre_real(nombre_actual)
    ruta_actual = ruta_segura(nombre_actual)
    ruta_nueva = ruta_segura(nombre_nuevo)
    if not os.path.exists(ruta_actual):
        return f"❌ '{nombre_actual}' no existe."
    os.rename(ruta_actual, ruta_nueva)
    return f"✅ '{nombre_actual}' renombrado a '{nombre_nuevo}'."

def buscar(termino: str) -> str:
    base = os.path.join(SANDBOX_PATH, _directorio_activo) if _directorio_activo else SANDBOX_PATH
    resultados = []
    for raiz, dirs, archivos in os.walk(base):
        for nombre in dirs + archivos:
            if termino.lower() in nombre.lower():
                ruta_completa = os.path.join(raiz, nombre)
                tipo = "📁" if os.path.isdir(ruta_completa) else "📄"
                resultados.append(f"  {tipo} {ruta_completa}")
    if not resultados:
        return f"🔍 No se encontró nada con '{termino}'."
    return f"🔍 Resultados para '{termino}':\n" + "\n".join(resultados)

def abrir_archivo(nombre: str) -> str:
    nombre = buscar_nombre_real(nombre)
    ruta = ruta_segura(nombre)
    if not os.path.exists(ruta):
        return f"❌ '{nombre}' no existe."
    os.startfile(ruta)
    return f"✅ Abriendo '{nombre}'..."