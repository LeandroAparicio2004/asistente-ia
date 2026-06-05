import speech_recognition as sr
import pyttsx3

# Inicializar motor de voz
engine = pyttsx3.init()
engine.setProperty("rate", 160)
engine.setProperty("volume", 1.0)

def hablar(texto: str):
    """El asistente habla en voz alta."""
    print(f"🤖 Asistente: {texto}")
    engine.say(texto)
    engine.runAndWait()

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