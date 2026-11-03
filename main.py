import re

from agent import interpretar
from executor import ACCIONES, ACCIONES_ALIAS
from actions.sistema import cancelar_bloqueo
from voice import hablar, escuchar
from history import registrar, ver_historial
from memory import limpiar_memoria
from reminders import iniciar_monitor
from actions.programadas import iniciar_monitor_programadas
from pre_parser import pre_parsear

# Solo estas acciones piden confirmación (las que empiezan con estas palabras).
# Para quitar la confirmación de alguna, borrala de la lista.
PREFIJOS_PELIGROSOS = ("eliminar", "borrar", "limpiar", "apagar", "reiniciar",
                       "suspender", "cerrar", "formatear", "vaciar")

SEPARADORES = r"\s*(?:,|;|\by\b|\bluego\b|\bdespu[eé]s\b|\bademás\b)\s+"


def requiere_confirmacion(accion: str) -> bool:
    return accion.startswith(PREFIJOS_PELIGROSOS)


def confirmar_accion(descripcion: str) -> bool:
    print(f"\n⚡ Acción a ejecutar: {descripcion}")
    respuesta = input("   ¿Confirmás? (s/n): ").strip().lower()
    return respuesta == "s"


def dividir_comando(mensaje: str) -> list[str]:
    """Separa 'abrí la calculadora y subí el volumen' en pasos,
    solo si cada paso se entiende sin IA."""
    partes = [p.strip() for p in re.split(SEPARADORES, mensaje, flags=re.I) if p.strip()]
    if len(partes) > 1 and all(pre_parsear(p) for p in partes):
        return partes
    return [mensaje]


def procesar(mensaje: str):
    resultado = interpretar(mensaje)
    accion = resultado.get("accion")
    parametros = resultado.get("parametros", {})
    descripcion = resultado.get("descripcion", "")

    if accion == "ninguna":
        hablar(descripcion)
        return

    if accion == "error":
        hablar(f"Hubo un error: {descripcion}")
        return

    if accion == "ver_historial":
        print(ver_historial())
        hablar("Te mostré el historial en pantalla.")
        return

    if accion == "limpiar_memoria":
        if confirmar_accion("Limpiar toda la memoria del asistente"):
            hablar(limpiar_memoria())
        return

    # Corregir acción si es un alias
    if accion not in ACCIONES and accion in ACCIONES_ALIAS:
        accion = ACCIONES_ALIAS[accion]

    if accion not in ACCIONES:
        hablar(f"No conozco esa acción: {accion}")
        return

    if requiere_confirmacion(accion) and not confirmar_accion(descripcion):
        hablar("Acción cancelada.")
        registrar(accion, parametros, "Cancelado por el usuario")
        return

    try:
        resultado_ejecucion = ACCIONES[accion](**parametros)
        registrar(accion, parametros, resultado_ejecucion)
        hablar(resultado_ejecucion)
    except Exception as e:
        error_msg = f"❌ Error al ejecutar: {str(e)}"
        registrar(accion, parametros, error_msg)
        hablar(error_msg)


def main():
    iniciar_monitor()
    iniciar_monitor_programadas()
    hablar("¡Hola! Soy tu asistente. Escribí tu mensaje, 'voz' para hablar, o 'salir' para terminar.")

    while True:
        print("\n" + "─" * 40)
        modo = input("📝 Tu mensaje: ").strip()

        if not modo:
            continue

        if modo.lower() == "salir":
            hablar("¡Hasta luego!")
            break
        elif modo.lower() == "historial":
            print(ver_historial())
            continue
        elif modo.lower() == "voz":
            mensaje = escuchar()
            if not mensaje:
                continue
        else:
            mensaje = modo

        for parte in dividir_comando(mensaje):
            procesar(parte)


if __name__ == "__main__":
    main()