# Asistente IA Personal

Asistente de inteligencia artificial para Windows que controla tu PC mediante lenguaje natural — texto o voz.

---

### Instalar dependencias
Abrí una terminal en la carpeta del proyecto y ejecutá:

```bash
pip install groq speechrecognition pyttsx3 python-dotenv pyaudio google-genai psutil requests beautifulsoup4 python-docx schedule pycaw screen-brightness-control pillow speedtest-cli fpdf2
```

Si `pyaudio` da error:
```bash
pip install pipwin
pipwin install pyaudio
```

### 4 — Configurar el archivo `.env`
Creá un archivo `.env` en la raíz del proyecto con este contenido:

```env
GROQ_API_KEY=tu_key_de_groq
SANDBOX_PATH=C:\Users\TuUsuario\Desktop\sandbox
OPENWEATHER_API_KEY=tu_key_de_openweather
GEMINI_API_KEY=tu_key_de_gemini
YOUTUBE_API_KEY=tu_key_de_youtube

```

> ⚠️ Cambiá `SANDBOX_PATH` por la carpeta donde querés que el asistente trabaje.

### 6 — Ejecutar
```bash
python main.py - Consola
python app.py - Interfaz
```
