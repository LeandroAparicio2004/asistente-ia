import os
from config import SANDBOX_PATH

# ─── QR CODES ─────────────────────────────────────────────────────────────────

def generar_qr(contenido: str, nombre: str = "") -> str:
    try:
        import qrcode
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = nombre if nombre else f"qr_{timestamp}.png"
        if not nombre_archivo.endswith(".png"):
            nombre_archivo += ".png"
        ruta = os.path.join(SANDBOX_PATH, nombre_archivo)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(contenido)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(ruta)
        return f"✅ QR generado como '{nombre_archivo}' en el sandbox.\n   Contenido: {contenido}"
    except Exception as e:
        return f"❌ Error al generar QR: {str(e)}"

# ─── CALCULADORA AVANZADA ─────────────────────────────────────────────────────

def calcular(expresion: str) -> str:
    try:
        import sympy
        # Limpiar la expresión
        expresion = expresion.strip()
        expresion = expresion.replace("^", "**")
        expresion = expresion.replace("x", "*")
        expresion = expresion.replace("×", "*")
        expresion = expresion.replace("÷", "/")
        expresion = expresion.replace("%", "/100")
        # Agregar estas líneas:
        expresion = expresion.replace("raiz(", "sqrt(")
        expresion = expresion.replace("raíz(", "sqrt(")
        expresion = expresion.replace("raiz de ", "sqrt(") 
        expresion = expresion.replace("raíz de ", "sqrt(")

        # Evaluar con sympy
        resultado = sympy.sympify(expresion, locals={"sqrt": sympy.sqrt, "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan, "log": sympy.log, "pi": sympy.pi})
        resultado_eval = float(resultado.evalf())

        # Si es entero, mostrar sin decimales
        if resultado_eval == int(resultado_eval):
            return f"🧮 {expresion} = {int(resultado_eval)}"
        else:
            return f"🧮 {expresion} = {round(resultado_eval, 6)}"
    except Exception as e:
        return f"❌ No pude calcular '{expresion}': {str(e)}"

def calcular_porcentaje(valor: float, porcentaje: float) -> str:
    try:
        resultado = valor * porcentaje / 100
        return f"🧮 El {porcentaje}% de {valor} = {round(resultado, 2)}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ─── TRADUCTOR ────────────────────────────────────────────────────────────────

IDIOMAS = {
    "español": "es", "inglés": "en", "ingles": "en",
    "francés": "fr", "frances": "fr", "alemán": "de",
    "aleman": "de", "italiano": "it", "portugués": "pt",
    "portugues": "pt", "chino": "zh-CN", "japonés": "ja",
    "japones": "ja", "ruso": "ru", "árabe": "ar", "arabe": "ar",
    "coreano": "ko", "holandés": "nl", "holandes": "nl",
    "es": "es", "en": "en", "fr": "fr", "de": "de",
    "it": "it", "pt": "pt", "ja": "ja", "ru": "ru",
}

def traducir(texto: str, idioma_destino: str, idioma_origen: str = "auto") -> str:
    try:
        from deep_translator import GoogleTranslator

        # Resolver código de idioma
        destino = IDIOMAS.get(idioma_destino.lower(), idioma_destino.lower())
        origen = IDIOMAS.get(idioma_origen.lower(), idioma_origen.lower())

        translator = GoogleTranslator(source=origen, target=destino)
        resultado = translator.translate(texto)

        return f"🌍 Traducción ({idioma_destino}):\n{resultado}"
    except Exception as e:
        return f"❌ Error al traducir: {str(e)}"

# ─── CORRECTOR DE TEXTO ───────────────────────────────────────────────────────

def corregir_texto(texto: str) -> str:
    """Usa la IA directamente para corregir el texto."""
    try:
        from groq import Groq
        from config import GROQ_API_KEY

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Sos un corrector de texto. Corregí el texto que te den: ortografía, gramática y puntuación. Devolvé SOLO el texto corregido, sin explicaciones ni comentarios."
                },
                {
                    "role": "user",
                    "content": texto
                }
            ],
            temperature=0.1,
            max_tokens=1000
        )
        corregido = response.choices[0].message.content.strip()
        return f"✅ Texto corregido:\n{corregido}"
    except Exception as e:
        return f"❌ Error al corregir: {str(e)}"
    
    # ─── ANALISIS DE IMG ─────────────────────────────────────────────────────

def analizar_imagen(nombre_imagen: str, pregunta: str = "") -> str:
    """Analiza una imagen usando Gemini Vision."""
    try:
        import base64
        from google import genai
        from google.genai import types
        from config import GEMINI_API_KEY, SANDBOX_PATH

        # Buscar imagen en sandbox
        ruta = os.path.join(SANDBOX_PATH, nombre_imagen)

        # Buscar sin extensión si no existe
        if not os.path.exists(ruta):
            for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]:
                ruta_ext = os.path.join(SANDBOX_PATH, nombre_imagen + ext)
                if os.path.exists(ruta_ext):
                    ruta = ruta_ext
                    nombre_imagen = nombre_imagen + ext
                    break

        if not os.path.exists(ruta):
            return f"❌ No encontré la imagen '{nombre_imagen}' en el sandbox."

        # Detectar tipo de imagen
        ext = os.path.splitext(ruta)[1].lower()
        tipos_mime = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
            ".bmp": "image/bmp"
        }
        mime_type = tipos_mime.get(ext, "image/jpeg")

        # Leer imagen en base64
        with open(ruta, "rb") as f:
            imagen_bytes = f.read()
        imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

        print(f"   🔍 Analizando imagen '{nombre_imagen}'...")

        # Preparar pregunta
        texto_pregunta = pregunta if pregunta else "Describí detalladamente qué ves en esta imagen. Si hay texto, leélo. Si hay código, analizálo."

        # Llamar a Gemini Vision
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Content(
                    parts=[
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=imagen_base64
                            )
                        ),
                        types.Part(text=texto_pregunta)
                    ]
                )
            ]
        )

        resultado = response.text.strip()
        return f"🖼️ Análisis de '{nombre_imagen}':\n\n{resultado}"

    except Exception as e:
        return f"❌ Error al analizar imagen: {str(e)}"
    
    # ─── MÚSICA ───────────────────────────────────────────────────────────────────

def reproducir_musica(consulta: str, plataforma: str = "youtube", tipo: str = "musica") -> str:
    """Busca la canción y abre el primer resultado directo."""
    try:
        import webbrowser
        from urllib.parse import quote
        from config import YOUTUBE_API_KEY

        plataforma_lower = plataforma.lower().strip()

        if "spotify" in plataforma_lower:
            webbrowser.open(f"spotify:search:{consulta}")
            return f"🎵 Abriendo '{consulta}' en Spotify..."

        # Ajustar búsqueda según tipo
        if tipo == "musica":
            consulta_busqueda = f"{consulta} official audio"
        else:
            consulta_busqueda = consulta

        # YouTube — buscar con la API
        if YOUTUBE_API_KEY:
            import requests
            import random
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": consulta_busqueda,
                "type": "video",
                "maxResults": 5,
                "key": YOUTUBE_API_KEY
            }
            response = requests.get(url, params=params, timeout=8)
            data = response.json()

            if data.get("items"):
                item = random.choice(data["items"])
                video_id = item["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(video_url)
                titulo = item["snippet"]["title"]
                return f"🎵 Reproduciendo: '{titulo}'"

        # Fallback sin API
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote(consulta_busqueda)}")
        return f"🎵 Buscando '{consulta}' en YouTube..."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# YouTube — buscar primer video con la API
        if YOUTUBE_API_KEY:
            import requests
            import random
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": consulta,
                "type": "video",
                "maxResults": 5,
                "key": YOUTUBE_API_KEY
            }
            response = requests.get(url, params=params, timeout=8)
            data = response.json()

            if data.get("items"):
                item = random.choice(data["items"])
                video_id = item["id"]["videoId"]
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(video_url)
                titulo = item["snippet"]["title"]
                return f"🎵 Reproduciendo: '{titulo}'"

        # Fallback sin API
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote(consulta)}")
        return f"🎵 Buscando '{consulta}' en YouTube..."

    except Exception as e:
        return f"❌ Error: {str(e)}"
    
def buscar_musica(consulta: str, plataforma: str = "youtube") -> str:
    """Busca música abriendo el buscador."""
    try:
        import webbrowser
        from urllib.parse import quote

        consulta_encoded = quote(consulta)
        plataforma_lower = plataforma.lower().strip()

        if "spotify" in plataforma_lower:
            url = f"https://open.spotify.com/search/{consulta_encoded}"
            webbrowser.open(url)
            return f"🔍 Buscando '{consulta}' en Spotify web..."
        else:
            url = f"https://www.youtube.com/results?search_query={consulta_encoded}"
            webbrowser.open(url)
            return f"🔍 Buscando '{consulta}' en YouTube..."

    except Exception as e:
        return f"❌ Error: {str(e)}"