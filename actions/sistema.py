import os
import subprocess
import threading
import time
from config import SANDBOX_PATH

# ─── VOLUMEN ──────────────────────────────────────────────────────────────────

def _get_volume_interface():
    from pycaw.pycaw import AudioUtilities
    devices = AudioUtilities.GetSpeakers()
    return devices.EndpointVolume

def obtener_volumen() -> str:
    try:
        volume = _get_volume_interface()
        nivel = round(volume.GetMasterVolumeLevelScalar() * 100)
        muted = volume.GetMute()
        estado = " (silenciado)" if muted else ""
        return f"🔊 Volumen actual: {nivel}%{estado}"
    except Exception as e:
        return f"❌ Error al obtener volumen: {str(e)}"

def ajustar_volumen(nivel: int) -> str:
    try:
        nivel = max(0, min(100, nivel))
        volume = _get_volume_interface()
        volume.SetMasterVolumeLevelScalar(nivel / 100, None)
        return f"🔊 Volumen ajustado a {nivel}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def silenciar() -> str:
    try:
        volume = _get_volume_interface()
        volume.SetMute(1, None)
        return "🔇 PC silenciada."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def activar_sonido() -> str:
    try:
        volume = _get_volume_interface()
        volume.SetMute(0, None)
        return "🔊 Sonido activado."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def subir_volumen(cantidad: int = 10) -> str:
    try:
        volume = _get_volume_interface()
        actual = round(volume.GetMasterVolumeLevelScalar() * 100)
        nuevo = min(100, actual + cantidad)
        volume.SetMasterVolumeLevelScalar(nuevo / 100, None)
        return f"🔊 Volumen subido a {nuevo}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def bajar_volumen(cantidad: int = 10) -> str:
    try:
        volume = _get_volume_interface()
        actual = round(volume.GetMasterVolumeLevelScalar() * 100)
        nuevo = max(0, actual - cantidad)
        volume.SetMasterVolumeLevelScalar(nuevo / 100, None)
        return f"🔊 Volumen bajado a {nuevo}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── BRILLO ───────────────────────────────────────────────────────────────────

def obtener_brillo() -> str:
    try:
        import screen_brightness_control as sbc
        brillo = sbc.get_brightness()
        if isinstance(brillo, list):
            brillo = brillo[0]
        return f"💡 Brillo actual: {brillo}%"
    except Exception as e:
        return f"❌ Error al obtener brillo: {str(e)}"

def ajustar_brillo(nivel: int) -> str:
    try:
        import screen_brightness_control as sbc
        nivel = max(0, min(100, nivel))
        sbc.set_brightness(nivel)
        return f"💡 Brillo ajustado a {nivel}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def subir_brillo(cantidad: int = 10) -> str:
    try:
        import screen_brightness_control as sbc
        actual = sbc.get_brightness()
        if isinstance(actual, list):
            actual = actual[0]
        nuevo = min(100, actual + cantidad)
        sbc.set_brightness(nuevo)
        return f"💡 Brillo subido a {nuevo}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def bajar_brillo(cantidad: int = 10) -> str:
    try:
        import screen_brightness_control as sbc
        actual = sbc.get_brightness()
        if isinstance(actual, list):
            actual = actual[0]
        nuevo = max(0, actual - cantidad)
        sbc.set_brightness(nuevo)
        return f"💡 Brillo bajado a {nuevo}%"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── CAPTURA DE PANTALLA ──────────────────────────────────────────────────────

def captura_pantalla(nombre: str = "") -> str:
    try:
        from PIL import ImageGrab
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = nombre if nombre else f"captura_{timestamp}.png"
        if not nombre_archivo.endswith(".png"):
            nombre_archivo += ".png"
        ruta = os.path.join(SANDBOX_PATH, nombre_archivo)
        img = ImageGrab.grab()
        img.save(ruta)
        return f"📸 Captura guardada como '{nombre_archivo}'."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── APAGAR / REINICIAR / SUSPENDER / BLOQUEAR ───────────────────────────────

def apagar_pc(minutos: int = 0) -> str:
    try:
        segundos = minutos * 60
        os.system(f"shutdown /s /t {segundos}")
        return f"⏻ PC se apagará en {minutos} minuto(s)." if minutos > 0 else "⏻ Apagando ahora..."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def reiniciar_pc(minutos: int = 0) -> str:
    try:
        segundos = minutos * 60
        os.system(f"shutdown /r /t {segundos}")
        return f"🔄 PC se reiniciará en {minutos} minuto(s)." if minutos > 0 else "🔄 Reiniciando ahora..."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def suspender_pc() -> str:
    try:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "💤 Suspendiendo la PC..."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def cancelar_apagado() -> str:
    try:
        os.system("shutdown /a")
        return "✅ Apagado/reinicio cancelado."
    except Exception as e:
        return f"❌ Error: {str(e)}"

_bloqueo_cancelado = False

def bloquear_pc(minutos: int = 0) -> str:
    global _bloqueo_cancelado
    try:
        if minutos > 0:
            _bloqueo_cancelado = False
            def _bloquear():
                for _ in range(minutos * 60):
                    if _bloqueo_cancelado:
                        return
                    time.sleep(1)
                os.system("rundll32.exe user32.dll,LockWorkStation")
            threading.Thread(target=_bloquear, daemon=True).start()
            return f"🔒 PC se bloqueará en {minutos} minuto(s). Decí 'cancelar bloqueo' para cancelar."
        else:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "🔒 PC bloqueada."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def cancelar_bloqueo() -> str:
    global _bloqueo_cancelado
    _bloqueo_cancelado = True
    return "✅ Bloqueo cancelado."

def bloquear_pantalla() -> str:
    return bloquear_pc(0)