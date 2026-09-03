import psutil
import platform
from datetime import datetime

def obtener_info_sistema() -> str:
    partes = []

    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_hilos = psutil.cpu_count(logical=True)
    partes.append(f"⚙️  CPU: {cpu_percent}% de uso | {cpu_cores} núcleos / {cpu_hilos} hilos")

    # RAM
    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024**3), 1)
    ram_usada = round(ram.used / (1024**3), 1)
    ram_libre = round(ram.available / (1024**3), 1)
    partes.append(f"🧠  RAM: {ram_usada}GB usados / {ram_libre}GB libres / {ram_total}GB total ({ram.percent}%)")

    # Disco
    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            total = round(uso.total / (1024**3), 1)
            usado = round(uso.used / (1024**3), 1)
            libre = round(uso.free / (1024**3), 1)
            partes.append(f"💾  Disco {particion.mountpoint}: {usado}GB usados / {libre}GB libres / {total}GB total ({uso.percent}%)")
        except PermissionError:
            continue

    # Temperatura
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for nombre, entradas in temps.items():
                for entrada in entradas[:1]:
                    partes.append(f"🌡️  Temperatura ({nombre}): {entrada.current}°C")
        else:
            partes.append("🌡️  Temperatura: no disponible en este sistema")
    except AttributeError:
        partes.append("🌡️  Temperatura: no disponible en Windows via psutil")

    # Batería
    try:
        bateria = psutil.sensors_battery()
        if bateria:
            estado = "🔌 Cargando" if bateria.power_plugged else "🔋 Descargando"
            partes.append(f"🔋  Batería: {round(bateria.percent)}% — {estado}")
        else:
            partes.append("🔋  Batería: PC de escritorio (sin batería)")
    except Exception:
        pass

    # Uptime
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    tiempo_encendida = datetime.now() - boot_time
    horas = int(tiempo_encendida.total_seconds() // 3600)
    minutos = int((tiempo_encendida.total_seconds() % 3600) // 60)
    partes.append(f"⏱️  Encendida hace: {horas}h {minutos}m (desde las {boot_time.strftime('%H:%M')})")

    # SO
    so = platform.system()
    arquitectura = platform.machine()
    version = platform.version()
    partes.append(f"🖥️  Sistema: {so} {arquitectura} | {version}")

    return "📊 Estado del sistema:\n\n" + "\n".join(partes)

def obtener_ram() -> str:
    ram = psutil.virtual_memory()
    total = round(ram.total / (1024**3), 1)
    usada = round(ram.used / (1024**3), 1)
    libre = round(ram.available / (1024**3), 1)
    return f"🧠 RAM: {usada}GB usados / {libre}GB libres / {total}GB total ({ram.percent}%)"

def obtener_cpu() -> str:
    percent = psutil.cpu_percent(interval=1)
    cores = psutil.cpu_count(logical=False)
    hilos = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    freq_str = f" | {round(freq.current)}MHz" if freq else ""
    return f"⚙️ CPU: {percent}% de uso | {cores} núcleos físicos / {hilos} hilos lógicos{freq_str}"

def obtener_disco() -> str:
    resultado = "💾 Discos:\n"
    for particion in psutil.disk_partitions():
        try:
            uso = psutil.disk_usage(particion.mountpoint)
            total = round(uso.total / (1024**3), 1)
            usado = round(uso.used / (1024**3), 1)
            libre = round(uso.free / (1024**3), 1)
            resultado += f"  {particion.mountpoint}: {usado}GB usados / {libre}GB libres / {total}GB total ({uso.percent}%)\n"
        except PermissionError:
            continue
    return resultado.strip()

def obtener_bateria() -> str:
    try:
        bateria = psutil.sensors_battery()
        if not bateria:
            return "🔋 Esta PC no tiene batería (escritorio)."
        estado = "🔌 Cargando" if bateria.power_plugged else "🔋 Descargando"
        mins = bateria.secsleft // 60 if bateria.secsleft > 0 else 0
        tiempo = f" | ~{mins // 60}h {mins % 60}m restantes" if not bateria.power_plugged and mins > 0 else ""
        return f"🔋 Batería: {round(bateria.percent)}% — {estado}{tiempo}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def obtener_procesos_pesados() -> str:
    procesos = []
    for proc in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
        try:
            if proc.info["cpu_percent"] is not None:
                procesos.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_cpu = sorted(procesos, key=lambda x: x["cpu_percent"], reverse=True)[:5]
    top_ram = sorted(procesos, key=lambda x: x["memory_percent"] or 0, reverse=True)[:5]

    resultado = "🏋️ Procesos más pesados:\n\n  Por CPU:\n"
    for p in top_cpu:
        resultado += f"    • {p['name']}: {round(p['cpu_percent'], 1)}%\n"
    resultado += "\n  Por RAM:\n"
    for p in top_ram:
        resultado += f"    • {p['name']}: {round(p['memory_percent'] or 0, 1)}%\n"
    return resultado.strip()