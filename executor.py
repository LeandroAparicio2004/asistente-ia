from actions.archivos import (
    crear_carpeta, eliminar_carpeta, listar_contenido,
    crear_archivo, eliminar_archivo, leer_archivo,
    mover, copiar, renombrar, buscar, abrir_archivo,
    entrar_carpeta, salir_carpeta

)
from actions.editor import (
    establecer_archivo_activo, salir_archivo_activo,
    leer_archivo_completo, agregar_contenido,
    reemplazar_contenido, borrar_linea, buscar_en_archivo,
    generar_y_escribir
)

from actions.programas import (
    abrir_programa, listar_programas_instalados,
    actualizar_cache_apps, cerrar_programa, listar_procesos_activos
)
from actions.sistema import (
    obtener_volumen, ajustar_volumen, silenciar, activar_sonido,
    subir_volumen, bajar_volumen, obtener_brillo, ajustar_brillo,
    subir_brillo, bajar_brillo, captura_pantalla,
    apagar_pc, reiniciar_pc, suspender_pc, cancelar_apagado,
    bloquear_pc, cancelar_bloqueo
)
from actions.info_sistema import (
    obtener_info_sistema, obtener_ram, obtener_cpu,
    obtener_disco, obtener_bateria, obtener_procesos_pesados
)
from actions.internet import (
    buscar_en_internet, obtener_clima, obtener_ip,
    obtener_red, hacer_speedtest, verificar_conexion
)
from actions.archivos_avanzados import (
    comprimir_zip, descomprimir_zip, ver_contenido_zip,
    convertir_txt_a_pdf, convertir_imagen, convertir_csv_a_txt
)
from reminders import (
    agregar_recordatorio, listar_recordatorios,
    cancelar_recordatorio, cancelar_todos_recordatorios
)
from modes import (
    crear_modo, agregar_app_a_modo, quitar_app_de_modo,
    activar_modo, ver_modo, listar_modos, eliminar_modo
)
from history import ver_historial
from memory import limpiar_memoria

from actions.utilidades import (
    generar_qr, calcular, calcular_porcentaje,
    traducir, corregir_texto, analizar_imagen,
    reproducir_musica, buscar_musica,
    generar_contrasena, abrir_url
)

from actions.notas import (
    agregar_nota, ver_notas, eliminar_nota, limpiar_notas,
    agregar_tarea, ver_tareas, completar_tarea,
    eliminar_tarea, limpiar_tareas_completadas
)

from actions.pomodoro import (
    iniciar_pomodoro, cancelar_pomodoro,
    estado_pomodoro, iniciar_temporizador
)

from actions.portapapeles import (
    copiar_texto, obtener_portapapeles, guardar_portapapeles,
    ver_historial_portapapeles, recuperar_de_historial,
    limpiar_historial_portapapeles
)

from actions.agenda import (
    agregar_evento, ver_eventos_hoy, ver_eventos_manana,
    ver_eventos_semana, ver_todos_eventos,
    eliminar_evento, ver_eventos_fecha
)

from actions.programadas import (
    programar_accion, listar_programadas,
    cancelar_programada, iniciar_monitor_programadas
)

from diagnostico import ejecutar_diagnostico 

# ─── ALIAS — traduce acciones inventadas por la IA a las reales ───────────────

ACCIONES_ALIAS = {
    "abrir": "abrir_programa",
    "abrir_app": "abrir_programa",
    "ejecutar": "abrir_programa",
    "editar": "establecer_archivo_activo",
    "editar_archivo": "establecer_archivo_activo",
    "abrir_editor": "establecer_archivo_activo",
    "cerrar": "cerrar_programa",
    "mostrar_contenido": "listar_contenido",
    "mostrar": "listar_contenido",
    "listar": "listar_contenido",
    "ver_contenido": "listar_contenido",
    "ver": "listar_contenido",
    "mover_archivo": "mover",
    "copiar_archivo": "copiar",
    "crear": "crear_archivo",
    "borrar": "eliminar_archivo",
    "borrar_archivo": "eliminar_archivo",
    "borrar_carpeta": "eliminar_carpeta",
    "comprimir": "comprimir_zip",
    "descomprimir": "descomprimir_zip",
    "screenshot": "captura_pantalla",
    "captura": "captura_pantalla",
    "volumen": "obtener_volumen",
    "ip": "obtener_ip",
    "red": "obtener_red",
    "internet": "verificar_conexion",
    "buscar_internet": "buscar_en_internet",
    "clima": "obtener_clima",
    "sistema": "obtener_info_sistema",
    "ram": "obtener_ram",
    "cpu": "obtener_cpu",
    "disco": "obtener_disco",
    "bateria": "obtener_bateria",
    "recordatorio": "agregar_recordatorio",
    "alarma": "agregar_recordatorio",
    "modo": "activar_modo",
    "escribir": "agregar_contenido",
    "escribe": "agregar_contenido",
    "agregar": "agregar_contenido",
    "agrega": "agregar_contenido",
    "añadir": "agregar_contenido",
    "trabajar": "establecer_archivo_activo",
    "entrar": "entrar_carpeta",
    "ir_a": "entrar_carpeta",
    "abrir_carpeta": "entrar_carpeta",
    "salir_de_carpeta": "salir_carpeta",
    "volver": "salir_carpeta",
    #Forzar
    "analizar": "analizar_imagen",
    "analiza": "analizar_imagen",
    "analizá": "analizar_imagen",
    "describir imagen": "analizar_imagen",
    "leer imagen": "analizar_imagen",
    "qué hay en": "analizar_imagen",
    #Diagnostico
    "diagnostico": "ejecutar_diagnostico",
    "diagnóstico": "ejecutar_diagnostico",
}

# ─── MAPA DE ACCIONES ─────────────────────────────────────────────────────────

ACCIONES = {
    # Archivos y carpetas
    "crear_carpeta": crear_carpeta,
    "eliminar_carpeta": eliminar_carpeta,
    "listar_contenido": listar_contenido,
    "crear_archivo": crear_archivo,
    "eliminar_archivo": eliminar_archivo,
    "leer_archivo": leer_archivo,
    "mover": mover,
    "copiar": copiar,
    "renombrar": renombrar,
    "buscar": buscar,
    "abrir_archivo": abrir_archivo,
    "entrar_carpeta": entrar_carpeta,
    "salir_carpeta": salir_carpeta,
    # Editor
    "trabajar_con_archivo": establecer_archivo_activo,
    "salir_archivo": salir_archivo_activo,
    "leer_archivo_completo": leer_archivo_completo,
    "agregar_contenido": agregar_contenido,
    "reemplazar_contenido": reemplazar_contenido,
    "borrar_linea": borrar_linea,
    "buscar_en_archivo": buscar_en_archivo,
    "generar_y_escribir": generar_y_escribir,
    # Programas
    "abrir_programa": abrir_programa,
    "listar_programas_instalados": listar_programas_instalados,
    "actualizar_cache_apps": actualizar_cache_apps,
    "cerrar_programa": cerrar_programa,
    "listar_procesos_activos": listar_procesos_activos,
    # Sistema
    "obtener_volumen": obtener_volumen,
    "ajustar_volumen": ajustar_volumen,
    "silenciar": silenciar,
    "activar_sonido": activar_sonido,
    "subir_volumen": subir_volumen,
    "bajar_volumen": bajar_volumen,
    "obtener_brillo": obtener_brillo,
    "ajustar_brillo": ajustar_brillo,
    "subir_brillo": subir_brillo,
    "bajar_brillo": bajar_brillo,
    "captura_pantalla": captura_pantalla,
    "apagar_pc": apagar_pc,
    "reiniciar_pc": reiniciar_pc,
    "suspender_pc": suspender_pc,
    "cancelar_apagado": cancelar_apagado,
    "bloquear_pc": bloquear_pc,
    "cancelar_bloqueo": cancelar_bloqueo,
    # Info sistema
    "obtener_info_sistema": obtener_info_sistema,
    "obtener_ram": obtener_ram,
    "obtener_cpu": obtener_cpu,
    "obtener_disco": obtener_disco,
    "obtener_bateria": obtener_bateria,
    "obtener_procesos_pesados": obtener_procesos_pesados,
    # Internet
    "buscar_en_internet": buscar_en_internet,
    "obtener_clima": obtener_clima,
    "obtener_ip": obtener_ip,
    "obtener_red": obtener_red,
    "hacer_speedtest": hacer_speedtest,
    "verificar_conexion": verificar_conexion,
    # Archivos avanzados
    "comprimir_zip": comprimir_zip,
    "descomprimir_zip": descomprimir_zip,
    "ver_contenido_zip": ver_contenido_zip,
    "convertir_txt_a_pdf": convertir_txt_a_pdf,
    "convertir_imagen": convertir_imagen,
    "convertir_csv_a_txt": convertir_csv_a_txt,
    "analizar_imagen": analizar_imagen,
    # Recordatorios
    "agregar_recordatorio": agregar_recordatorio,
    "listar_recordatorios": listar_recordatorios,
    "cancelar_recordatorio": cancelar_recordatorio,
    "cancelar_todos_recordatorios": cancelar_todos_recordatorios,
    # Modos
    "crear_modo": crear_modo,
    "agregar_app_a_modo": agregar_app_a_modo,
    "quitar_app_de_modo": quitar_app_de_modo,
    "activar_modo": activar_modo,
    "ver_modo": ver_modo,
    "listar_modos": listar_modos,
    "eliminar_modo": eliminar_modo,
    # Memoria e historial
    "ver_historial": ver_historial,
    "limpiar_memoria": limpiar_memoria,
    # Utilidades
    "generar_qr": generar_qr,
    "calcular": calcular,
    "calcular_porcentaje": calcular_porcentaje,
    "traducir": traducir,
    "corregir_texto": corregir_texto,
    #notas
    "agregar_nota": agregar_nota,
    "ver_notas": ver_notas,
    "eliminar_nota": eliminar_nota,
    "limpiar_notas": limpiar_notas,
    "agregar_tarea": agregar_tarea,
    "ver_tareas": ver_tareas,
    "completar_tarea": completar_tarea,
    "eliminar_tarea": eliminar_tarea,
    "limpiar_tareas_completadas": limpiar_tareas_completadas,
    #pomodoro
    "iniciar_pomodoro": iniciar_pomodoro,
    "cancelar_pomodoro": cancelar_pomodoro,
    "estado_pomodoro": estado_pomodoro,
    "iniciar_temporizador": iniciar_temporizador,
    #portapapeles
    "copiar_texto": copiar_texto,
    "obtener_portapapeles": obtener_portapapeles,
    "guardar_portapapeles": guardar_portapapeles,
    "ver_historial_portapapeles": ver_historial_portapapeles,
    "recuperar_de_historial": recuperar_de_historial,
    "limpiar_historial_portapapeles": limpiar_historial_portapapeles,
    #agenda
    "agregar_evento": agregar_evento,
    "ver_eventos_hoy": ver_eventos_hoy,
    "ver_eventos_manana": ver_eventos_manana,
    "ver_eventos_semana": ver_eventos_semana,
    "ver_todos_eventos": ver_todos_eventos,
    "eliminar_evento": eliminar_evento,
    "ver_eventos_fecha": ver_eventos_fecha,
    #programadas
    "programar_accion": programar_accion,
    "listar_programadas": listar_programadas,
    "cancelar_programada": cancelar_programada,
    #musica
    "reproducir_musica": reproducir_musica,
    "reproducir_musica": reproducir_musica,
    "buscar_musica": buscar_musica,
    #Accesos
    "generar_contrasena": generar_contrasena,
    "abrir_url": abrir_url,
    #Diagnostico
    "ejecutar_diagnostico": ejecutar_diagnostico,
}