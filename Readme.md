# Asistente IA Personal

Asistente de inteligencia artificial para Windows que controla tu PC mediante lenguaje natural — texto o voz.

---

## Requisitos

- Windows 10 / 11
- Python 3.10 o superior
- Micrófono (para modo voz)
- Conexión a internet

---

## Instalación en otra PC

### 1 — Instalar Python

### 2 — Copiar la carpeta del proyecto
Copiá toda la carpeta `asistente-ia` a la nueva PC.

### 3 — Instalar dependencias
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
GEMINI_API_KEY=tu_key_de_gemini
OPENWEATHER_API_KEY=tu_key_de_openweather
SANDBOX_PATH=C:\Users\TuUsuario\Desktop\sandbox
```

> ⚠️ Cambiá `SANDBOX_PATH` por la carpeta donde querés que el asistente trabaje.

### 5 — Conseguir las API Keys (todas gratuitas)

| Servicio | Para qué | Dónde conseguirla |
|---|---|---|
| **Groq** | IA principal (LLaMA) | console.groq.com |
| **Gemini** | IA de respaldo (Google) | aistudio.google.com |
| **OpenWeatherMap** | Clima en tiempo real | openweathermap.org/api |

> ⚠️ La key de OpenWeatherMap tarda hasta 2 horas en activarse la primera vez.

### 6 — Ejecutar
```bash
python main.py - Consola
python app.py - Interfaz
```

---

## 🚀 Cómo usarlo

Escribí tu mensaje en la terminal o escribí `voz` para hablar por micrófono.

Comandos especiales:
- `voz` — activa el micrófono
- `historial` — muestra las últimas acciones
- `salir` — cierra el asistente

---

## ✅ Todo lo que puede hacer (A modo de ejemplo, no se limita a lo anotado)

### 📁 Archivos y Carpetas
Crea una carpeta llamada Proyectos
Eliminá la carpeta Test
Crea un archivo llamado notas.txt con el contenido "Hola mundo"
Eliminá el archivo notas.txt
Leé el archivo notas.txt
Mové el archivo notas.txt a la carpeta Proyectos
Copiá el archivo notas.txt como copia.txt
Listá el contenido de la carpeta Proyectos
Renombrá notas.txt a apuntes.txt
Buscá archivos que contengan la palabra "proyecto"
Abrí el archivo notas.txt

### 📝 Editor de Archivos (modo contexto)
Trabajemos con notas.txt
Qué dice el archivo?
Agregá "Esta es una línea nueva"
Reemplazá todo el contenido con "Nuevo contenido"
Borrá la línea 3
Buscá la palabra "proyecto" en el archivo
Terminamos con el archivo

### 💻 Programas
Abrí Spotify
Abrí Chrome
Abrí VSCode
Cerrá Spotify
Qué programas tengo abiertos?
Qué programas tengo instalados?
Actualizá el cache de apps

### 🔊 Volumen y Audio
Qué volumen tengo?
Poné el volumen al 50%
Subí el volumen
Bajá el volumen
Silenciá
Activá el sonido

### 💡 Brillo
Qué brillo tengo?
Poné el brillo al 80%
Subí el brillo
Bajá el brillo
> ⚠️ El brillo solo funciona en monitores que soporten control por software (no funciona en TVs externas).

### 📸 Captura de Pantalla
Sacá una captura de pantalla
Guardá lo que tengo en pantalla como "mi_captura"

### ⏻ Control de PC
Apagá la PC
Apagá la PC en 10 minutos
Cancelá el apagado
Reiniciá la PC
Reiniciá en 5 minutos
Suspendé la PC
Bloqueá la pantalla
Bloqueá la pantalla en 5 minutos
Cancelá el bloqueo

### 📊 Info del Sistema
Cómo está el sistema?
Cuánta RAM tengo libre?
Cómo está el CPU?
Cuánto espacio libre tengo en disco?
Cómo está la batería?
Qué procesos están consumiendo más recursos?

### ⏰ Recordatorios y Alarmas
Recordame en 10 minutos que tengo una reunión
Poneme una alarma para las 18:00 que diga "hora de descansar"
Recordame el 25/12/2025 a las 09:00 que es Navidad
Qué recordatorios tengo?
Cancelá el recordatorio de la reunión
Cancelá todos los recordatorios

### 🎮 Modos Personalizados
Crear Modo Trabajo
Agregá VSCode al Modo Trabajo
Agregá Spotify al Modo Trabajo
Agregá Chrome al Modo Trabajo
Activar Modo Trabajo
Ver Modo Trabajo
Listar modos
Quitar Spotify del Modo Trabajo
Eliminar Modo Trabajo

### 🌐 Internet y Red
Buscá qué es la inteligencia artificial
Buscá sobre Argentina
Qué clima hace en Buenos Aires?
Cuál es mi IP?
A qué red estoy conectado?
Hacé un speedtest
Hay internet?

### 📦 Archivos Avanzados
Comprimí la carpeta Proyectos
Comprimí el archivo notas.txt como backup.zip
Ver contenido del archivo backup.zip
Descomprimí backup.zip
Convertí notas.txt a PDF
Convertí imagen.png a jpg
Convertí datos.csv a txt

### 🧠 Memoria e Historial
Qué recordás que te pedí?
Mostrá el historial
Limpiá la memoria

---

## ⚠️ Seguridad

- El asistente **solo puede actuar dentro del sandbox** definido en `.env`
- Antes de ejecutar cualquier acción, **siempre pide confirmación**
- Procesos del sistema están **bloqueados permanentemente** y no pueden cerrarse

---

## 🔄 Si instalás una app nueva y no la encuentra
Actualizá el cache de apps

---

## 💰 Costos

| Servicio | Límite gratuito |
|---|---|
| Groq | 100,000 tokens por día |
| Gemini | 1,500 requests por día |
| OpenWeatherMap | 1,000 requests por día |

Todo gratuito para uso personal normal.