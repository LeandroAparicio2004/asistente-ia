import re

# ─── COMANDOS DIRECTOS ────────────────────────────────────────────────────────
# Mapeo exacto: frase → acción + parámetros
# Sin IA, sin red, respuesta instantánea

COMANDOS_EXACTOS = {
    # Volumen
    "sube el volumen": ("subir_volumen", {}),
    "subí el volumen": ("subir_volumen", {}),
    "subi el volumen": ("subir_volumen", {}),
    "subir volumen": ("subir_volumen", {}),
    "baja el volumen": ("bajar_volumen", {}),
    "bajá el volumen": ("bajar_volumen", {}),
    "baja volumen": ("bajar_volumen", {}),
    "silencia": ("silenciar", {}),
    "silenciar": ("silenciar", {}),
    "silencio": ("silenciar", {}),
    "sin sonido": ("silenciar", {}),
    "activa el sonido": ("activar_sonido", {}),
    "activar sonido": ("activar_sonido", {}),
    "quitar silencio": ("activar_sonido", {}),
    "cuanto volumen tengo": ("obtener_volumen", {}),
    "cuánto volumen tengo": ("obtener_volumen", {}),
    "que volumen tengo": ("obtener_volumen", {}),
    "qué volumen tengo": ("obtener_volumen", {}),
    "volumen actual": ("obtener_volumen", {}),

    # Brillo
    "sube el brillo": ("subir_brillo", {}),
    "subí el brillo": ("subir_brillo", {}),
    "subi el brillo": ("subir_brillo", {}),
    "subir brillo": ("subir_brillo", {}),
    "baja el brillo": ("bajar_brillo", {}),
    "bajá el brillo": ("bajar_brillo", {}),
    "baja brillo": ("bajar_brillo", {}),
    "cuanto brillo tengo": ("obtener_brillo", {}),
    "cuánto brillo tengo": ("obtener_brillo", {}),
    "brillo actual": ("obtener_brillo", {}),

    # Sistema
    "como esta el sistema": ("obtener_info_sistema", {}),
    "cómo está el sistema": ("obtener_info_sistema", {}),
    "estado del sistema": ("obtener_info_sistema", {}),
    "cuanta ram tengo": ("obtener_ram", {}),
    "cuánta ram tengo": ("obtener_ram", {}),
    "cuanta memoria tengo": ("obtener_ram", {}),
    "ram disponible": ("obtener_ram", {}),
    "como esta la ram": ("obtener_ram", {}),
    "como esta el cpu": ("obtener_cpu", {}),
    "cómo está el cpu": ("obtener_cpu", {}),
    "uso del cpu": ("obtener_cpu", {}),
    "uso del procesador": ("obtener_cpu", {}),
    "cuanto espacio tengo": ("obtener_disco", {}),
    "cuánto espacio tengo": ("obtener_disco", {}),
    "espacio en disco": ("obtener_disco", {}),
    "como esta el disco": ("obtener_disco", {}),
    "procesos pesados": ("obtener_procesos_pesados", {}),
    "que procesos consumen mas": ("obtener_procesos_pesados", {}),
    "qué procesos consumen más": ("obtener_procesos_pesados", {}),

    # Red
    "cual es mi ip": ("obtener_ip", {}),
    "cuál es mi ip": ("obtener_ip", {}),
    "mi ip": ("obtener_ip", {}),
    "que red tengo": ("obtener_red", {}),
    "qué red tengo": ("obtener_red", {}),
    "a que red estoy conectado": ("obtener_red", {}),
    "hay internet": ("verificar_conexion", {}),
    "tengo internet": ("verificar_conexion", {}),
    "verificar conexion": ("verificar_conexion", {}),

    # Sandbox
    "que hay en el sandbox": ("listar_contenido", {}),
    "qué hay en el sandbox": ("listar_contenido", {}),
    "listar contenido": ("listar_contenido", {}),
    "mostrar contenido": ("listar_contenido", {}),

    # Recordatorios
    "que recordatorios tengo": ("listar_recordatorios", {}),
    "qué recordatorios tengo": ("listar_recordatorios", {}),
    "mis recordatorios": ("listar_recordatorios", {}),
    "listar recordatorios": ("listar_recordatorios", {}),
    "cancelar todos los recordatorios": ("cancelar_todos_recordatorios", {}),

    # Notas
    "mis notas": ("ver_notas", {}),
    "ver notas": ("ver_notas", {}),
    "que notas tengo": ("ver_notas", {}),
    "qué notas tengo": ("ver_notas", {}),

    # Tareas
    "mis tareas": ("ver_tareas", {}),
    "ver tareas": ("ver_tareas", {}),
    "que tareas tengo": ("ver_tareas", {}),
    "qué tareas tengo": ("ver_tareas", {}),
    "tareas pendientes": ("ver_tareas", {}),

    # Modos
    "listar modos": ("listar_modos", {}),
    "que modos tengo": ("listar_modos", {}),
    "qué modos tengo": ("listar_modos", {}),
    "mis modos": ("listar_modos", {}),

    # Captura
    "captura de pantalla": ("captura_pantalla", {}),
    "sacar captura": ("captura_pantalla", {}),
    "sacá una captura": ("captura_pantalla", {}),
    "screenshot": ("captura_pantalla", {}),

    # Programas activos
    "que programas tengo abiertos": ("listar_procesos_activos", {}),
    "qué programas tengo abiertos": ("listar_procesos_activos", {}),
    "programas abiertos": ("listar_procesos_activos", {}),
    "procesos activos": ("listar_procesos_activos", {}),

    # Historial
    "ver historial": ("ver_historial", {}),
    "mostrar historial": ("ver_historial", {}),
    "historial de acciones": ("ver_historial", {}),

    # Agenda
    "eventos de hoy": ("ver_eventos_hoy", {}),
    "que tengo hoy": ("ver_eventos_hoy", {}),
    "qué tengo hoy": ("ver_eventos_hoy", {}),
    "eventos de mañana": ("ver_eventos_manana", {}),
    "que tengo mañana": ("ver_eventos_manana", {}),
    "qué tengo mañana": ("ver_eventos_manana", {}),
    "eventos de esta semana": ("ver_eventos_semana", {}),
    "que tengo esta semana": ("ver_eventos_semana", {}),
    "qué tengo esta semana": ("ver_eventos_semana", {}),
    "todos mis eventos": ("ver_todos_eventos", {}),
    "ver todos los eventos": ("ver_todos_eventos", {}),

    # Portapapeles
    "que tengo en el portapapeles": ("obtener_portapapeles", {}),
    "qué tengo en el portapapeles": ("obtener_portapapeles", {}),
    "contenido del portapapeles": ("obtener_portapapeles", {}),
    "historial del portapapeles": ("ver_historial_portapapeles", {}),

    # Acciones programadas
    "acciones programadas": ("listar_programadas", {}),
    "que acciones tengo programadas": ("listar_programadas", {}),
    "qué acciones tengo programadas": ("listar_programadas", {}),

    # Batería
    "bateria": ("obtener_bateria", {}),
    "batería": ("obtener_bateria", {}),
    "como esta la bateria": ("obtener_bateria", {}),
    "cómo está la batería": ("obtener_bateria", {}),
    "cuanta bateria tengo": ("obtener_bateria", {}),
    "cuánta batería tengo": ("obtener_bateria", {}),

    # Pomodoro
    "iniciar pomodoro": ("iniciar_pomodoro", {}),
    "empezar pomodoro": ("iniciar_pomodoro", {}),
    "cancelar pomodoro": ("cancelar_pomodoro", {}),
    "estado pomodoro": ("estado_pomodoro", {}),
    "como esta el pomodoro": ("estado_pomodoro", {}),

    # Programas instalados
    "que programas tengo instalados": ("listar_programas_instalados", {}),
    "qué programas tengo instalados": ("listar_programas_instalados", {}),
    "programas instalados": ("listar_programas_instalados", {}),
    "actualizar cache": ("actualizar_cache_apps", {}),
    "actualizar cache de apps": ("actualizar_cache_apps", {}),

    # Acciones programadas
    "listar programadas": ("listar_programadas", {}),

    # Agenda extra
    "mi agenda": ("ver_todos_eventos", {}),
    "ver agenda": ("ver_todos_eventos", {}),

    # Sistema extra
    "reiniciar pc": ("reiniciar_pc", {}),
    "cancelar apagado": ("cancelar_apagado", {}),
    "cancelar bloqueo": ("cancelar_bloqueo", {}),

    # Notas extra
    "limpiar notas": ("limpiar_notas", {}),
    "borrar notas": ("limpiar_notas", {}),
    "limpiar tareas completadas": ("limpiar_tareas_completadas", {}),

    # Portapapeles extra
    "limpiar portapapeles": ("limpiar_historial_portapapeles", {}),
    "borrar historial portapapeles": ("limpiar_historial_portapapeles", {}),
    "guardar portapapeles": ("guardar_portapapeles", {}),

    # PC
    "bloquear pc": ("bloquear_pc", {}),
    "bloquear pantalla": ("bloquear_pc", {}),
    "bloqueá la pc": ("bloquear_pc", {}),
    "suspender pc": ("suspender_pc", {}),
    "suspendé la pc": ("suspender_pc", {}),
}

# ─── PATRONES CON PARÁMETROS ─────────────────────────────────────────────────
# Para comandos que necesitan extraer un valor

PATRONES = [
    # Volumen con nivel exacto
    (r"(?:poné|pon|poner|ajustar|ajustá)\s+(?:el\s+)?volumen\s+(?:al?\s+)?(\d+)%?",
     "ajustar_volumen", lambda m: {"nivel": int(m.group(1))}),

    # Subir volumen con cantidad
    (r"(?:subí|subi|sube|subir)\s+(?:el\s+)?volumen\s+(\d+)",
     "subir_volumen", lambda m: {"cantidad": int(m.group(1))}),

    # Bajar volumen con cantidad
    (r"(?:bajá|baja|bajar)\s+(?:el\s+)?volumen\s+(\d+)",
     "bajar_volumen", lambda m: {"cantidad": int(m.group(1))}),

    # Brillo con nivel
    (r"(?:poné|pon|poner|ajustar|ajustá)\s+(?:el\s+)?brillo\s+(?:al?\s+)?(\d+)%?",
     "ajustar_brillo", lambda m: {"nivel": int(m.group(1))}),

    # Abrir programa
    (r"(?:abrí|abri|abre|abrir|ejecutar|ejecutá)\s+(?:el\s+|la\s+|los\s+)?(.+)",
     "abrir_programa", lambda m: {"nombre": m.group(1).strip().strip('"')}),

    # Cerrar programa
    (r"(?:cerrá|cerra|cierra|cerrar)\s+(?:el\s+|la\s+)?(.+)",
     "cerrar_programa", lambda m: {"nombre": m.group(1).strip().strip('"')}),

    # Clima
    (r"(?:clima|tiempo|temperatura)\s+(?:en|de)\s+(.+)",
     "obtener_clima", lambda m: {"ciudad": m.group(1).strip()}),
    (r"(?:cómo|como)\s+(?:está|esta)\s+(?:el\s+)?(?:clima|tiempo)\s+en\s+(.+)",
     "obtener_clima", lambda m: {"ciudad": m.group(1).strip()}),
    (r"(?:qué|que)\s+clima\s+(?:hace|hay)\s+en\s+(.+)",
     "obtener_clima", lambda m: {"ciudad": m.group(1).strip()}),

    # Buscar en internet
    (r"(?:buscá|busca|buscar)\s+(?:sobre\s+|información\s+sobre\s+|info\s+de\s+)?(.+)",
     "buscar_en_internet", lambda m: {"consulta": m.group(1).strip().strip('"')}),

    # Crear carpeta
    (r'(?:creá|crea|crear)\s+(?:una\s+)?carpeta\s+(?:llamada\s+|con\s+nombre\s+)?"?([^"]+)"?',
     "crear_carpeta", lambda m: {"nombre": m.group(1).strip()}),

    # Crear archivo
    (r'(?:creá|crea|crear)\s+(?:un\s+)?archivo\s+(?:llamado\s+|con\s+nombre\s+)?"?([^"]+)"?',
     "crear_archivo", lambda m: {"nombre": m.group(1).strip()}),

    # Activar modo
    (r"(?:activar?\s+modo|modo)\s+(.+)",
     "activar_modo", lambda m: {"nombre": m.group(1).strip()}),

    # Recordatorio en X minutos
    (r"recordame\s+en\s+(\d+)\s+minutos?",
     "agregar_recordatorio", lambda m: {"mensaje": "", "cuando": f"en {m.group(1)} minutos"}),

    # Apagar PC en X minutos
    (r"(?:apagar?|apagá)\s+(?:la\s+)?pc\s+en\s+(\d+)\s+minutos?",
     "apagar_pc", lambda m: {"minutos": int(m.group(1))}),

    # Traducir
    (r'(?:traducí|traduce|traducir)\s+"?(.+?)"?\s+al?\s+(\w+)',
     "traducir", lambda m: {"texto": m.group(1).strip(), "idioma_destino": m.group(2).strip()}),

    # Calcular
    (r"(?:calculá|calcula|calcular|cuánto\s+es|cuanto\s+es)\s+(.+)",
     "calcular", lambda m: {"expresion": m.group(1).strip()}),

    # QR
    (r'(?:generá|genera|generar)\s+(?:un\s+)?qr\s+(?:con\s+)?"?(.+)"?',
     "generar_qr", lambda m: {"contenido": m.group(1).strip()}),

# ─── REPRODUCIR MÚSICA (YOUTUBE - SPOTIFY) _ REPRODUCIR VIDEOS (YOUTUBE) ────────────────────────────────────────────────────────

    # Reproducir VIDEO (YOUTUBE) — excluye palabras musicales
    (r"(?:reproducí|reproduce|reproduci)\s+(?:un\s+)?video\s+de\s+(.+)",
     "reproducir_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "youtube", "tipo": "video"}),

    # Reproducir MÚSICA en YouTube — con "en youtube" al final
    (r"(?:reproducí|reproduce|reproduci|poné|pone|pon|escuchar?)\s+(.+?)\s+en\s+youtube",
     "reproducir_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "youtube", "tipo": "musica"}),

    # Reproducir MÚSICA en Spotify — con "en spotify" al final
    (r"(?:reproducí|reproduce|reproduci|poné|pone|pon|escuchar?)\s+(.+?)\s+en\s+spotify",
     "reproducir_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "spotify", "tipo": "musica"}),

    # Reproducir MÚSICA genérico sin plataforma
    (r"(?:reproducí|reproduce|reproduci|poné|pone|pon)\s+(?:una?\s+canción\s+de\s+|una?\s+cancion\s+de\s+|música\s+de\s+|musica\s+de\s+|canciones?\s+de\s+|algo\s+de\s+)(.+)",
     "reproducir_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "spotify", "tipo": "musica"}),

    # Buscar música en Spotify
    (r"(?:buscá|busca)\s+(.+?)\s+en\s+spotify",
     "buscar_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "spotify"}),

    # Buscar música en YouTube
    (r"(?:buscá|busca)\s+(.+?)\s+en\s+youtube",
     "buscar_musica", lambda m: {"consulta": m.group(1).strip(), "plataforma": "youtube"}),
]

# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────

def pre_parsear(mensaje: str) -> dict | None:
    """
    Intenta resolver el mensaje sin llamar a la IA.
    Retorna dict con accion+parametros, o None si no puede resolverlo.
    """
    msg = mensaje.lower().strip()

    # Limpiar signos de puntuación al final
    msg = msg.rstrip("?.!")

    # 1 — Búsqueda exacta
    if msg in COMANDOS_EXACTOS:
        accion, params = COMANDOS_EXACTOS[msg]
        return {
            "accion": accion,
            "parametros": params,
            "descripcion": f"Ejecutar {accion}",
            "fast": True
        }

    # 2 — Patrones con regex
    for patron, accion, extractor in PATRONES:
        match = re.match(patron, msg, re.IGNORECASE)
        if match:
            try:
                params = extractor(match)
                return {
                    "accion": accion,
                    "parametros": params,
                    "descripcion": f"Ejecutar {accion}",
                    "fast": True
                }
            except Exception:
                continue

    # No pudo resolver → delegar a la IA
    return None