import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Validaciones
if not GROQ_API_KEY:
    raise ValueError("❌ No se encontró GROQ_API_KEY en el archivo .env")

# Sandbox: si no está definido o la ruta no sirve en esta PC, usa una carpeta junto al proyecto
_DEFAULT_SANDBOX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sandbox")
SANDBOX_PATH = os.getenv("SANDBOX_PATH") or _DEFAULT_SANDBOX
try:
    os.makedirs(SANDBOX_PATH, exist_ok=True)
except OSError:
    print(f"⚠️ No pude usar SANDBOX_PATH ({SANDBOX_PATH}). Uso: {_DEFAULT_SANDBOX}")
    SANDBOX_PATH = _DEFAULT_SANDBOX
    os.makedirs(SANDBOX_PATH, exist_ok=True)

print(f"✅ Configuración cargada. Sandbox: {SANDBOX_PATH}")