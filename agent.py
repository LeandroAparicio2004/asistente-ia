import json
from groq import Groq
from google import genai
from config import GROQ_API_KEY, GEMINI_API_KEY
from memory import agregar_mensaje, obtener_historial_chat

# ─── CLIENTES ─────────────────────────────────────────────────────────────────

groq_client = Groq(api_key=GROQ_API_KEY)
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)

# ─── MODELOS ──────────────────────────────────────────────────────────────────

MODELOS = [
    {"tipo": "groq",   "modelo": "llama-3.3-70b-versatile", "nombre": "LLaMA 3.3 70B"},
    {"tipo": "groq",   "modelo": "llama-3.1-8b-instant",    "nombre": "LLaMA 3.1 8B"},
    {"tipo": "gemini", "modelo": "gemini-1.5-flash",         "nombre": "Gemini Flash"},
]

# ─── CATEGORÍAS DE ACCIONES ───────────────────────────────────────────────────

CATEGORIAS = {
"archivos": {
    "palabras_clave": ["archivo", "carpeta", "crear", "eliminar", "borrar", "mover", "mové", "copiar", "copiá", "renombrar", "renombrá", "buscar", "buscá", "listar", "listá", "contenido", "leer", "leé", "abrir", "abrí", "trabajar", "guardar", "trabajemos", "entrar", "salir", "volver", "directorio", "informe", "redactá", "redacta", "escribí un", "genera", "generá", "documento"],
    "acciones": """crear_carpeta(nombre), eliminar_carpeta(nombre), crear_archivo(nombre,contenido?), eliminar_archivo(nombre), leer_archivo(nombre), mover(origen,destino), copiar(origen,destino), listar_contenido(subcarpeta?), renombrar(nombre_actual,nombre_nuevo), buscar(termino), abrir_archivo(nombre)
    trabajar_con_archivo(nombre), salir_archivo(), leer_archivo_completo(nombre?), agregar_contenido(texto), reemplazar_contenido(contenido_nuevo), borrar_linea(numero_linea), buscar_en_archivo(termino)
entrar_carpeta(nombre), salir_carpeta(), generar_y_escribir(tema, nombre_archivo, formato?="txt") — genera un informe/documento completo sobre un tema y lo guarda en un archivo"""

},
    "archivos_avanzados": {
        "palabras_clave": ["comprimir", "comprimí", "zip", "descomprimir", "convertir", "convertí", "pdf", "csv"],
        "acciones": """comprimir_zip(nombre_origen,nombre_zip?), descomprimir_zip(nombre_zip,carpeta_destino?), ver_contenido_zip(nombre_zip)
convertir_txt_a_pdf(nombre_txt,nombre_pdf?), convertir_imagen(nombre_origen,formato_destino), convertir_csv_a_txt(nombre_csv,nombre_txt?)"""
},
    
    "programas": {
        "palabras_clave": ["abrir", "abrí", "abre", "ejecutar", "cerrar", "cerrá", "cierra", "programa", "aplicación", "app", "proceso", "instalado"],
        "acciones": """abrir_programa(nombre), listar_programas_instalados(), actualizar_cache_apps()
cerrar_programa(nombre), listar_procesos_activos()"""
    },
    "sistema": {
        "palabras_clave": ["volumen", "sonido", "silenciar", "silencia", "silencio", "mute", "brillo", "captura", "pantalla", "apagar", "reiniciar", "suspender", "bloquear", "ram", "cpu", "disco", "bateria", "temperatura", "sistema", "memoria", "subí", "bajá", "subi", "baja", "almacenamiento", "espacio", "procesador", "rendimiento", "como esta", "cómo está", "estado", "procesos", "pesados", "recursos"],
        "acciones": """
— Volumen: obtener_volumen(), ajustar_volumen(nivel 0-100), silenciar(), activar_sonido(), subir_volumen(cantidad?=10), bajar_volumen(cantidad?=10)
— Brillo: obtener_brillo(), ajustar_brillo(nivel 0-100), subir_brillo(cantidad?=10), bajar_brillo(cantidad?=10)
— Pantalla/PC: captura_pantalla(nombre?), apagar_pc(minutos?=0), reiniciar_pc(minutos?=0), suspender_pc(), cancelar_apagado(), bloquear_pc(minutos?=0), cancelar_bloqueo()
— Info sistema:
  * obtener_info_sistema() → resumen completo: CPU%, núcleos, hilos, RAM usada/libre/total, discos, temperatura, batería, uptime, SO
  * obtener_ram() → RAM usada/libre/total en GB y porcentaje
  * obtener_cpu() → uso CPU en %, núcleos físicos, hilos lógicos, frecuencia MHz
  * obtener_disco() → espacio usado/libre/total por cada disco en GB
  * obtener_bateria() → porcentaje batería, estado carga, tiempo restante
  * obtener_procesos_pesados() → top 5 procesos por CPU y por RAM"""
    },
    "recordatorios": {
        "palabras_clave": ["recordar", "recordame", "recordatorio", "alarma", "aviso", "cuando", "minutos", "horas", "cancelar"],
        "acciones": """agregar_recordatorio(mensaje, cuando)
  — cuando: "en X minutos", "en X horas", "HH:MM", "DD/MM/YYYY HH:MM"
  — Si el usuario NO especificó mensaje, calculá la hora destino y usá "Son las HH:MM" con la hora real calculada
  — NUNCA uses "{hora}" como texto literal, siempre calculá la hora real
  — NUNCA inventes un mensaje que el usuario no dijo
listar_recordatorios(), cancelar_recordatorio(identificador), cancelar_todos_recordatorios()"""
    },
    "modos": {
        "palabras_clave": ["modo", "crear modo", "activar modo", "agregar", "configurar modo", "gamer", "trabajo", "programador"],
        "acciones": """crear_modo(nombre), agregar_app_a_modo(modo,app), quitar_app_de_modo(modo,app)
activar_modo(nombre), ver_modo(nombre), listar_modos(), eliminar_modo(nombre)"""
    },
    "internet": {
        "palabras_clave": ["buscar", "buscá", "internet", "web", "wikipedia", "clima", "tiempo", "ip", "red", "wifi", "velocidad", "speedtest", "conexion", "historia", "qué es", "que es", "información", "informacion"],
        "acciones": """buscar_en_internet(consulta) [1-3 palabras clave]
obtener_clima(ciudad), obtener_ip(), obtener_red(), hacer_speedtest(), verificar_conexion()"""
    },
    "memoria": {
        "palabras_clave": ["historial", "memoria", "recordas", "limpiar", "olvidar"],
        "acciones": """ver_historial(), limpiar_memoria()"""
    },
    "general": {
        "palabras_clave": [],
        "acciones": "ninguna acción — respondé la pregunta directamente como asistente"
    },
"utilidades": {
    "palabras_clave": ["qr", "calcul", "cuanto es", "cuánto es", "porcentaje", "traducir", "traducí", "traduce", "idioma", "inglés", "ingles", "corregir", "corregí", "corrección", "ortografía", "analizar", "analizá", "analiza", "describí", "describe", "imagen", "foto", "reproducir", "reproducí", "poné", "pon", "escuchar", "música", "musica", "cancion", "canción", "spotify", "youtube", "video", "famosa", "popular", "contraseña", "contrasena", "password", "url", "abrir pagina", "abrir web", "abrí", "abri", "abre", "abrir"],
    "acciones": """generar_qr(contenido, nombre?)
calcular(expresion)
calcular_porcentaje(valor, porcentaje)
traducir(texto, idioma_destino, idioma_origen?="auto")
corregir_texto(texto)
analizar_imagen(nombre_imagen, pregunta?="")
generar_contrasena(longitud?=16, incluir_simbolos?=True)
abrir_url(url) — abre cualquier URL en el navegador
reproducir_musica(consulta, plataforma, tipo) — REGLAS ESTRICTAS:
  * tipo="musica" cuando diga "canción", "música", "tema", "algo de", "lo más famoso", "la más famosa"
  * tipo="video" cuando diga "video", "gameplay", "clip"
  * plataforma="spotify" cuando no especifique plataforma
  * plataforma="youtube" cuando diga "youtube"
  * consulta = texto EXACTO para buscar. Ejemplos:
    - "Reproduce Come As You Are de Nirvana" → consulta="Come As You Are Nirvana", plataforma="spotify", tipo="musica"
    - "Reproduce Come As You Are de Nirvana en youtube" → consulta="Come As You Are Nirvana", plataforma="youtube", tipo="musica"
    - "Reproduce la canción más famosa de Nirvana en youtube" → consulta="Nirvana most popular song", plataforma="youtube", tipo="musica"
    - "Reproduce la canción más famosa de Nirvana" → consulta="Nirvana most popular song", plataforma="spotify", tipo="musica"
    - "Reproduce un video de ZarcortGames" → consulta="ZarcortGames", plataforma="youtube", tipo="video"
    - "Pon algo de Rock" → consulta="Rock", plataforma="spotify", tipo="musica"
  * NUNCA uses parámetros como "artista", "cancion", "nombre" — SOLO consulta, plataforma y tipo
buscar_musica(consulta, plataforma) — cuando diga "buscá" en vez de "reproducí/poné" """
},
    "notas": {
    "palabras_clave": ["nota", "notas", "anotá", "anota", "apuntá", "apunta", "tarea", "tareas", "todo", "pendiente", "completar", "completá", "terminar"],
    "acciones": """agregar_nota(texto), ver_notas(), eliminar_nota(identificador), limpiar_notas()
agregar_tarea(texto), ver_tareas(solo_pendientes?=True), completar_tarea(identificador), eliminar_tarea(identificador), limpiar_tareas_completadas()"""
    },
    "pomodoro": {
    "palabras_clave": ["pomodoro", "temporizador", "timer", "trabajar", "descanso", "ciclo", "concentración", "foco"],
    "acciones": """iniciar_pomodoro(minutos_trabajo?=25, minutos_descanso?=5, ciclos?=4)
    cancelar_pomodoro(), estado_pomodoro()
iniciar_temporizador(minutos, mensaje?) — temporizador simple sin ciclos"""
    },
    "portapapeles": {
    "palabras_clave": ["portapapeles", "copiar", "copiá", "clipboard", "pegar", "pegá", "copié", "guardá lo que copié"],
    "acciones": """copiar_texto(texto) — copia texto al portapapeles
    obtener_portapapeles() — lee lo que hay en el portapapeles
    guardar_portapapeles(etiqueta?) — guarda el portapapeles actual en el historial
    ver_historial_portapapeles() — muestra el historial guardado
    recuperar_de_historial(identificador) — recupera una entrada al portapapeles
limpiar_historial_portapapeles() — limpia el historial"""
},

"agenda": {
    "palabras_clave": ["agenda", "evento", "eventos", "reunión", "reunion", "cita", "turno", "hoy", "mañana", "manana", "semana", "calendario"],
    "acciones": """agregar_evento(titulo, fecha, hora?="", descripcion?="")
  — fecha puede ser: "hoy", "mañana", "lunes", "15/06/2026", etc.
  — hora puede ser: "18:00", "18hs", "9:30"
    ver_eventos_hoy(), ver_eventos_manana(), ver_eventos_semana(), ver_todos_eventos()
ver_eventos_fecha(fecha), eliminar_evento(identificador)"""
},
"programadas": {
    "palabras_clave": ["programar", "programá", "automatizar", "todos los", "cada dia", "cada semana", "cuando sean", "a las", "ejecutar automaticamente"],
    "acciones": """programar_accion(accion, parametros, cuando, descripcion?)
  — accion: nombre exacto de la acción (ej: "abrir_programa", "silenciar")
  — parametros: dict con los parámetros (ej: {"nombre": "spotify"})
  — cuando: "en X minutos", "HH:MM", "DD/MM/YYYY HH:MM"
  — Ejemplo: programar que se abra Spotify a las 8:00 → accion="abrir_programa", parametros={"nombre":"spotify"}, cuando="08:00"
    listar_programadas() — ver acciones pendientes
cancelar_programada(identificador) — cancelar una acción"""
},
    
}

SISTEMA_BASE = """Sos un asistente de IA para Windows. Respondé SOLO con JSON:
{"accion": "nombre", "parametros": {}, "descripcion": "qué vas a hacer"}
Si no hay acción: {"accion": "ninguna", "parametros": {}, "descripcion": "respuesta"}
Usá SOLO acciones de la lista. Si no hay acción exacta, usá la más cercana.
NUNCA digas que no podés hacer algo si hay una acción disponible para ello.
IMPORTANTE: Solo JSON puro, sin markdown, sin explicaciones, sin texto extra."""

# ─── DETECCIÓN DE CATEGORÍAS ──────────────────────────────────────────────────

def _detectar_categorias(mensaje: str) -> list[str]:
    mensaje_lower = mensaje.lower()
    categorias_relevantes = []
    for cat, info in CATEGORIAS.items():
        for palabra in info["palabras_clave"]:
            if palabra in mensaje_lower:
                categorias_relevantes.append(cat)
                break
    if not categorias_relevantes:
        categorias_relevantes = ["general"]
    return categorias_relevantes

def _construir_prompt(mensaje: str) -> str:
    categorias = _detectar_categorias(mensaje)
    acciones_relevantes = []
    for cat in categorias:
        acciones_relevantes.append(CATEGORIAS[cat]["acciones"])
    acciones_str = "\n".join(acciones_relevantes)
    return f"{SISTEMA_BASE}\n\nACCIONES DISPONIBLES:\n{acciones_str}"

# ─── LLAMADAS A CADA API ──────────────────────────────────────────────────────

def _llamar_groq(modelo: str, historial: list, system_prompt: str) -> str:
    messages = [{"role": "system", "content": system_prompt}] + historial
    response = groq_client.chat.completions.create(
        model=modelo,
        messages=messages,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()

def _llamar_gemini(modelo: str, historial: list, system_prompt: str) -> str:
    contenido = system_prompt + "\n\n"
    for msg in historial:
        rol = "Usuario" if msg["role"] == "user" else "Asistente"
        contenido += f"{rol}: {msg['content']}\n"
    response = genai_client.models.generate_content(
        model=modelo,
        contents=contenido
    )
    return response.text.strip()

def _intentar_con_fallback(historial: list, system_prompt: str) -> tuple[str, str]:
    errores = []
    for m in MODELOS:
        try:
            if m["tipo"] == "groq":
                texto = _llamar_groq(m["modelo"], historial, system_prompt)
            elif m["tipo"] == "gemini":
                texto = _llamar_gemini(m["modelo"], historial, system_prompt)
            else:
                continue
            return texto, m["nombre"]
        except Exception as e:
            errores.append(f"{m['nombre']}: {str(e)[:80]}")
            if len(errores) > 1:
                print(f"   ⚠️  {m['nombre']} falló, probando siguiente...")
            continue
    raise Exception("❌ Todos los modelos fallaron:\n" + "\n".join(errores))

# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

_modelo_actual = None

def interpretar(mensaje_usuario: str) -> dict:
    global _modelo_actual

    # ─── PRE-PARSER: intentar resolver sin IA ────────────────────────────────
    from pre_parser import pre_parsear
    resultado_rapido = pre_parsear(mensaje_usuario)
    if resultado_rapido:
        print(f"   ⚡ Pre-parser → {resultado_rapido['accion']}")
        agregar_mensaje("user", mensaje_usuario)
        agregar_mensaje("assistant", resultado_rapido.get("descripcion", ""))
        return resultado_rapido

    # ─── IA normal si el pre-parser no pudo ──────────────────────────────────
    agregar_mensaje("user", mensaje_usuario)
    historial = obtener_historial_chat()
    system_prompt = _construir_prompt(mensaje_usuario)

    try:
        texto, modelo_usado = _intentar_con_fallback(historial, system_prompt)

        if _modelo_actual and _modelo_actual != modelo_usado:
            print(f"   🔄 Usando: {modelo_usado}")
        _modelo_actual = modelo_usado

        texto = texto.strip()
        if "```" in texto:
            partes = texto.split("```")
            for parte in partes:
                parte = parte.strip()
                if parte.startswith("json"):
                    parte = parte[4:].strip()
                if parte.startswith("{"):
                    texto = parte
                    break
        if not texto.startswith("{"):
            inicio = texto.find("{")
            fin = texto.rfind("}") + 1
            if inicio != -1 and fin > 0:
                texto = texto[inicio:fin]

        resultado = json.loads(texto)
        agregar_mensaje("assistant", resultado.get("descripcion", texto))
        return resultado

    except json.JSONDecodeError:
        return {"accion": "error", "parametros": {}, "descripcion": "No pude interpretar la respuesta."}
    except Exception as e:
        return {"accion": "error", "parametros": {}, "descripcion": str(e)}