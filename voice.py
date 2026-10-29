import speech_recognition as sr
import pyttsx3

import threading

_lock_voz = threading.Lock()

def hablar(texto: str):
    """El asistente habla en voz alta (funciona también desde otros hilos)."""
    print(f"🤖 Asistente: {texto}")
    with _lock_voz:
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()   # necesario para usar la voz fuera del hilo principal
            except Exception:
                pass
            motor = pyttsx3.init()
            motor.setProperty("rate", 160)
            motor.setProperty("volume", 1.0)
            motor.say(texto)
            motor.runAndWait()
        except Exception as e:
            print(f"⚠️ No pude hablar: {e}")

def escuchar() -> str:
    """Escucha por el micrófono y devuelve texto."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Escuchando... (hablá ahora)")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            texto = recognizer.recognize_google(audio, language="es-AR")
            print(f"👤 Vos dijiste: {texto}")
            return texto
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("❓ No entendí lo que dijiste.")
            return ""
        except sr.RequestError:
            print("❌ Error con el servicio de reconocimiento de voz.")
            return ""