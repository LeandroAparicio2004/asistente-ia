import threading
import time
import os
from datetime import datetime

# ─── ESTADO ───────────────────────────────────────────────────────────────────

_pomodoro_activo = False
_pomodoro_cancelado = False

# ─── POMODORO ─────────────────────────────────────────────────────────────────

def iniciar_pomodoro(minutos_trabajo: int = 25, minutos_descanso: int = 5, ciclos: int = 4) -> str:
    global _pomodoro_activo, _pomodoro_cancelado

    if _pomodoro_activo:
        return "⚠️ Ya hay un Pomodoro en curso. Cancelalo primero con 'cancelar pomodoro'."

    _pomodoro_activo = True
    _pomodoro_cancelado = False

    def _correr():
        global _pomodoro_activo, _pomodoro_cancelado
        for ciclo in range(1, ciclos + 1):
            if _pomodoro_cancelado:
                break

            # Trabajo
            print(f"\n🍅 Pomodoro {ciclo}/{ciclos} — ¡A trabajar! ({minutos_trabajo} minutos)")
            print("─" * 40)
            try:
                import winsound
                winsound.Beep(800, 500)
            except Exception:
                pass

            for _ in range(minutos_trabajo * 60):
                if _pomodoro_cancelado:
                    break
                time.sleep(1)

            if _pomodoro_cancelado:
                break

            # Beep fin de trabajo
            try:
                import winsound
                for _ in range(3):
                    winsound.Beep(1000, 300)
                    time.sleep(0.1)
            except Exception:
                pass

            if ciclo == ciclos:
                print(f"\n🎉 ¡Completaste todos los {ciclos} pomodoros! Tomá un descanso largo.")
                print("─" * 40)
                break

            # Descanso
            print(f"\n☕ ¡Descanso! ({minutos_descanso} minutos)")
            print("─" * 40)
            for _ in range(minutos_descanso * 60):
                if _pomodoro_cancelado:
                    break
                time.sleep(1)

            if _pomodoro_cancelado:
                break

            # Beep fin de descanso
            try:
                import winsound
                for _ in range(2):
                    winsound.Beep(600, 400)
                    time.sleep(0.1)
            except Exception:
                pass

        _pomodoro_activo = False
        if not _pomodoro_cancelado:
            print("\n✅ Sesión Pomodoro finalizada.")
            print("─" * 40)

    threading.Thread(target=_correr, daemon=True).start()
    return f"🍅 Pomodoro iniciado: {ciclos} ciclos de {minutos_trabajo}min trabajo / {minutos_descanso}min descanso.\n   Sonará un beep cuando cambie cada etapa."

def cancelar_pomodoro() -> str:
    global _pomodoro_cancelado, _pomodoro_activo
    if not _pomodoro_activo:
        return "ℹ️ No hay ningún Pomodoro en curso."
    _pomodoro_cancelado = True
    _pomodoro_activo = False
    return "✅ Pomodoro cancelado."

def estado_pomodoro() -> str:
    if _pomodoro_activo:
        return "🍅 Hay un Pomodoro en curso."
    return "ℹ️ No hay ningún Pomodoro activo."

def iniciar_temporizador(minutos: int, mensaje: str = "") -> str:
    """Temporizador simple sin ciclos."""
    global _pomodoro_cancelado
    _pomodoro_cancelado = False

    def _correr():
        for _ in range(minutos * 60):
            if _pomodoro_cancelado:
                return
            time.sleep(1)
        aviso = mensaje if mensaje else f"¡Pasaron {minutos} minuto(s)!"
        print(f"\n⏱️  {aviso}")
        print("─" * 40)
        try:
            import winsound
            for _ in range(3):
                winsound.Beep(1000, 400)
                time.sleep(0.2)
        except Exception:
            pass

    threading.Thread(target=_correr, daemon=True).start()
    aviso = f" — '{mensaje}'" if mensaje else ""
    return f"⏱️ Temporizador iniciado: {minutos} minuto(s){aviso}."