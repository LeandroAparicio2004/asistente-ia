import os
import glob
import winreg
import subprocess

# ─── CACHE ────────────────────────────────────────────────────────────────────

import json
from datetime import datetime, timedelta

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "app_cache.json")
CACHE_EXPIRA_HORAS = 24

def _cache_valido() -> bool:
    if not os.path.exists(CACHE_FILE):
        return False
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    generado = datetime.fromisoformat(data.get("generado", "2000-01-01"))
    return datetime.now() - generado < timedelta(hours=CACHE_EXPIRA_HORAS)

def _escanear_sistema() -> dict:
    print("   ⚙️  Construyendo cache de aplicaciones (solo la primera vez)...")
    encontrados = {}

    RUTAS_BUSQUEDA = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),
        os.environ.get("APPDATA", ""),
    ]

    CARPETAS_IGNORAR = {
        "windows", "system32", "syswow64", "winsxs",
        "microsoft.net", "windowsapps", "temp", "cache",
        "installer", "packages", "logs",
    }

    for base in RUTAS_BUSQUEDA:
        if not base or not os.path.exists(base):
            continue
        try:
            for raiz, dirs, archivos in os.walk(base):
                dirs[:] = [
                    d for d in dirs
                    if d.lower() not in CARPETAS_IGNORAR
                    and raiz.replace(base, "").count(os.sep) < 5
                ]
                for archivo in archivos:
                    if not archivo.lower().endswith(".exe"):
                        continue
                    nombre_sin_ext = os.path.splitext(archivo)[0].lower()
                    ruta_completa = os.path.join(raiz, archivo)
                    encontrados[nombre_sin_ext] = ruta_completa
        except PermissionError:
            continue

    # Desde el registro
    rutas_registro = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, ruta in rutas_registro:
        try:
            with winreg.OpenKey(hive, ruta) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                nombre = winreg.QueryValueEx(subkey, "DisplayName")[0].strip()
                            except Exception:
                                continue
                            for campo in ("DisplayIcon", "InstallLocation"):
                                try:
                                    val = winreg.QueryValueEx(subkey, campo)[0].strip()
                                    if campo == "DisplayIcon":
                                        val = val.split(",")[0].strip().strip('"')
                                    if val.lower().endswith(".exe") and os.path.exists(val):
                                        encontrados[nombre.lower()] = val
                                        break
                                except Exception:
                                    continue
                    except Exception:
                        continue
        except Exception:
            continue

    return encontrados

def obtener_cache() -> dict:
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    if _cache_valido():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["apps"]
    apps = _escanear_sistema()
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "generado": datetime.now().isoformat(),
            "apps": apps
        }, f, ensure_ascii=False, indent=2)
    print(f"   ✅ Cache generado con {len(apps)} aplicaciones.")
    return apps

def forzar_regenerar() -> str:
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    apps = obtener_cache()
    return f"✅ Cache regenerado con {len(apps)} aplicaciones."

# ─── ABRIR PROGRAMAS ──────────────────────────────────────────────────────────

def abrir_programa(nombre: str) -> str:
    nombre_lower = nombre.lower().strip().replace(".exe", "")
    cache = obtener_cache()

    if nombre_lower in cache:
        exe = cache[nombre_lower]
        if os.path.exists(exe):
            subprocess.Popen([exe], shell=False)
            return f"✅ Abriendo '{nombre}'..."

    for clave, exe in cache.items():
        if nombre_lower in clave or clave in nombre_lower:
            if os.path.exists(exe):
                subprocess.Popen([exe], shell=False)
                return f"✅ Abriendo '{clave}'..."

    try:
        subprocess.Popen(nombre, shell=True)
        return f"✅ Intentando abrir '{nombre}'..."
    except Exception:
        return f"❌ No encontré '{nombre}'. Probá 'actualizar cache de apps'."

def listar_programas_instalados() -> str:
    cache = obtener_cache()
    if not cache:
        return "❌ No pude encontrar programas."
    nombres = sorted(set(cache.keys()))
    lista = "\n".join(f"  • {n}" for n in nombres)
    return f"💻 {len(nombres)} aplicaciones encontradas:\n{lista}"

def actualizar_cache_apps() -> str:
    return forzar_regenerar()

# ─── CERRAR PROGRAMAS ─────────────────────────────────────────────────────────

import psutil

PROCESOS_BLOQUEADOS = {
    "explorer.exe", "svchost.exe", "lsass.exe", "csrss.exe",
    "winlogon.exe", "system", "smss.exe", "wininit.exe",
    "services.exe", "taskmgr.exe", "taskhost.exe", "dwm.exe",
    "spoolsv.exe", "audiodg.exe", "conhost.exe", "fontdrvhost.exe",
    "python.exe", "pythonw.exe",
    "avast.exe", "avastui.exe", "avastsvc.exe",
    "msmpeng.exe", "securityhealthservice.exe", "windefend.exe",
    "avgui.exe", "avguard.exe", "mbam.exe", "mbamservice.exe",
}

def es_proceso_bloqueado(nombre_proceso: str) -> bool:
    return nombre_proceso.lower().strip() in PROCESOS_BLOQUEADOS

def cerrar_programa(nombre: str) -> str:
    nombre_lower = nombre.lower().strip().replace(".exe", "")
    nombre_exe = nombre_lower + ".exe"

    if es_proceso_bloqueado(nombre_exe):
        return f"🚫 No puedo cerrar '{nombre}' porque es un proceso protegido."

    cerrados = []
    no_encontrados = True

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            proc_nombre = proc.info["name"].lower()
            proc_sin_ext = proc_nombre.replace(".exe", "")
            if proc_sin_ext == nombre_lower or proc_nombre == nombre_exe:
                no_encontrados = False
                if es_proceso_bloqueado(proc_nombre):
                    return f"🚫 '{nombre}' está protegido y no puede cerrarse."
                proc.terminate()
                cerrados.append(f"{proc.info['name']} (PID {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if no_encontrados:
        return f"❌ No encontré '{nombre}' en ejecución."
    if cerrados:
        return f"✅ Cerrado: {', '.join(cerrados)}"
    return f"❌ No se pudo cerrar '{nombre}'."

def listar_procesos_activos() -> str:
    procesos = set()
    for proc in psutil.process_iter(["name"]):
        try:
            nombre = proc.info["name"]
            if not es_proceso_bloqueado(nombre.lower()):
                procesos.add(nombre)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not procesos:
        return "📋 No hay procesos de usuario activos."
    lista = "\n".join(f"  • {p}" for p in sorted(procesos))
    return f"📋 Procesos activos:\n{lista}"