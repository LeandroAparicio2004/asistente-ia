import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SANDBOX_PATH = os.getenv("SANDBOX_PATH")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Validaciones
if not GROQ_API_KEY:
    raise ValueError("❌ No se encontró GROQ_API_KEY en el archivo .env")

if not SANDBOX_PATH:
    raise ValueError("❌ No se encontró SANDBOX_PATH en el archivo .env")

# Crear sandbox si no existe
os.makedirs(SANDBOX_PATH, exist_ok=True)

print(f"✅ Configuración cargada. Sandbox: {SANDBOX_PATH}")