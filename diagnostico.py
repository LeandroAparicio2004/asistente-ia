import os
import traceback
from datetime import datetime
from config import SANDBOX_PATH

# ─── PRUEBAS ──────────────────────────────────────────────────────────────────

PRUEBAS = [
    # (nombre, función, args, kwargs)

    # Archivos y carpetas
    ("Crear carpeta",           "crear_carpeta",        [], {"nombre": "_test_diag"}),
    ("Crear archivo",           "crear_archivo",        [], {"nombre": "_test_diag/prueba.txt", "contenido": "test"}),
    ("Leer archivo",            "leer_archivo",         [], {"nombre": "_test_diag/prueba.txt"}),
    ("Listar contenido",        "listar_contenido",     [], {"subcarpeta": "_test_diag"}),
    ("Renombrar archivo",       "renombrar",            [], {"nombre_actual": "_test_diag/prueba.txt", "nombre_nuevo": "_test_diag/prueba2.txt"}),
    ("Copiar archivo",          "copiar",               [], {"origen": "_test_diag/prueba2.txt", "destino": "_test_diag/copia.txt"}),
    ("Buscar archivo",          "buscar",               [], {"termino": "prueba2"}),
    ("Mover archivo",           "mover",                [], {"origen": "_test_diag/copia.txt", "destino": "_test_diag/movido.txt"}),
    ("Eliminar archivo",        "eliminar_archivo",     [], {"nombre": "_test_diag/prueba2.txt"}),
    ("Eliminar carpeta",        "eliminar_carpeta",     [], {"nombre": "_test_diag"}),

    # Sistema
    ("Info sistema",            "obtener_info_sistema", [], {}),
    ("RAM",                     "obtener_ram",          [], {}),
    ("CPU",                     "obtener_cpu",          [], {}),
    ("Disco",                   "obtener_disco",        [], {}),
    ("Batería",                 "obtener_bateria",      [], {}),
    ("Procesos pesados",        "obtener_procesos_pesados", [], {}),

    # Volumen
    ("Obtener volumen",         "obtener_volumen",      [], {}),

    # Red
    ("Verificar conexión",      "verificar_conexion",   [], {}),
    ("Obtener IP",              "obtener_ip",           [], {}),

    # Notas y tareas
    ("Agregar nota",            "agregar_nota",         [], {"texto": "nota de diagnóstico"}),
    ("Ver notas",               "ver_notas",            [], {}),
    ("Eliminar nota",           "eliminar_nota",        [], {"identificador": "diagnóstico"}),
    ("Agregar tarea",           "agregar_tarea",        [], {"texto": "tarea de diagnóstico"}),
    ("Ver tareas",              "ver_tareas",           [], {}),
    ("Completar tarea",         "completar_tarea",      [], {"identificador": "diagnóstico"}),
    ("Limpiar tareas comp.",    "limpiar_tareas_completadas", [], {}),

    # Recordatorios
    ("Agregar recordatorio",    "agregar_recordatorio", [], {"mensaje": "test diagnóstico", "cuando": "en 60 minutos"}),
    ("Listar recordatorios",    "listar_recordatorios", [], {}),
    ("Cancelar recordatorio",   "cancelar_recordatorio",[], {"identificador": "test diagnóstico"}),

    # Agenda
    ("Agregar evento",          "agregar_evento",       [], {"titulo": "Evento diagnóstico", "fecha": "mañana", "hora": "10:00"}),
    ("Ver eventos hoy",         "ver_eventos_hoy",      [], {}),
    ("Ver eventos mañana",      "ver_eventos_manana",   [], {}),
    ("Eliminar evento",         "eliminar_evento",      [], {"identificador": "diagnóstico"}),

    # Modos
    ("Listar modos",            "listar_modos",         [], {}),

    # Portapapeles
    ("Copiar texto",            "copiar_texto",         [], {"texto": "texto de prueba"}),
    ("Obtener portapapeles",    "obtener_portapapeles", [], {}),

    # Utilidades
    ("Calcular",                "calcular",             [], {"expresion": "2+2"}),
    ("Calcular porcentaje",     "calcular_porcentaje",  [], {"valor": 100, "porcentaje": 15}),
    ("Generar QR",              "generar_qr",           [], {"contenido": "https://test.com", "nombre": "_test_qr"}),
    ("Generar contraseña",      "generar_contrasena",   [], {"longitud": 16}),

    # Comprimir
    ("Crear archivo para ZIP",   "crear_archivo",    [], {"nombre": "_test_zip_src.txt", "contenido": "test zip"}),
    ("Comprimir ZIP",            "comprimir_zip",    [], {"nombre_origen": "_test_zip_src", "nombre_zip": "_test_diag_backup"}),
    ("Eliminar archivo ZIP src", "eliminar_archivo", [], {"nombre": "_test_zip_src.txt"}),

    # Clima (puede fallar si la key no está activa)
    ("Clima Buenos Aires",      "obtener_clima",        [], {"ciudad": "Buenos Aires"}),

    # Acciones programadas
    ("Listar programadas",      "listar_programadas",   [], {}),

    # Historial
    ("Ver historial",           "ver_historial",        [], {}),
]

# ─── EJECUTOR ─────────────────────────────────────────────────────────────────

def ejecutar_diagnostico(callback_progreso=None) -> str:
    """
    Ejecuta todas las pruebas y devuelve un reporte completo.
    callback_ progreso(actual, total, nombre) se llama en cada prueba
    """
    from executor import ACCIONES
    
    resultados = []
    ok = 0
    fail = 0
    total = len(PRUEBAS)
    
    inicio = datetime.now()
    
    for i, (nombre, accion, args, kwargs) in enumerate(PRUEBAS):
        if callback_progreso:
            callback_progreso(i, total, nombre)
            
        if accion not in ACCIONES:
            resultados.append(("⚠️", nombre, "Accion no encontrada en ACCIONES"))
            fail += 1
            continue
        
        try:
            resultado = ACCIONES[accion](*args, **kwargs)
            if resultado and str(resultado).startswith("❌"):
                resultados.append(("⚠️", nombre, str(resultado)[:80]))
                fail += 1
            else:
                resultados.append(("✅", nombre, str(resultado)[:60]))
                ok += 1
        except Exception as e:
            resultados.append(("❌", nombre, str(e)[:80]))
            fail += 1
            
    duracion = (datetime.now() - inicio).total_seconds()
    
    # ─── REPORTE ──────────────────────────────────────────────────────────────

    lineas = [
        f"╔═══════════════════════════════════════╗",
        f"║      DIAGNÓSTICO DEL ASISTENTE        ║",
        f"╚═══════════════════════════════════════╝",
        f"",
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        f"Duración: {duracion:.1f} segundos",
        f"Total: {total} pruebas  |  ✅ {ok} OK  |  ❌/⚠️ {fail} problemas",
        f"",
        f"─────────────────────────────────────────",
    ]
    
    #Errores
    errores = [(s, n, r) for s, n, r in resultados if s != "✅"]
    exitosos = [(s, n, r ) for s, n, r in resultados if s == "✅"]
    
    if errores:
        lineas.append("PROBLEMAS ENCONTRADOS:")
        for estado, nombre, resultado in errores:
            lineas.append(f" {estado} {nombre}")
            lineas.append(f"    →{resultado}")
        lineas.append("")

    #Exitos
    lineas.append("PRUBEAS EXITOSAS:")
    for estado, nombre, _ in exitosos:
        lineas.append(f" {estado} {nombre}")
        
    lineas.append("")
    lineas.append("─────────────────────────────────────────")
    
    if fail == 0:
        lineas.append("TODO FUNCIONA PERFECTAMENTE!")
    elif fail <= 3:
        lineas.append(f" {fail} problemas menores detectados")
    else:
        lineas.append(f" {fail} problemas detectados. Revisar!")

    # Limpiar archivos QR de prueba
    try:
        qr_test = os.path.join(SANDBOX_PATH, "_test_qr.png")
        if os.path.exists(qr_test):
            os.remove(qr_test)
        zip_test = os.path.join(SANDBOX_PATH, "_test_diag_backup.zip")
        if os.path.exists(zip_test):
            os.remove(zip_test)
    except Exception:
        pass

    return "\n".join(lineas)
