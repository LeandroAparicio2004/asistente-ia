import os
import shutil
import zipfile
from config import SANDBOX_PATH

# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def _ruta_segura(nombre: str) -> str:
    ruta = os.path.abspath(os.path.join(SANDBOX_PATH, nombre))
    if not ruta.startswith(os.path.abspath(SANDBOX_PATH)):
        raise ValueError("❌ Acceso fuera del sandbox bloqueado.")
    return ruta

def _buscar_nombre_real(nombre: str) -> str:
    ruta = _ruta_segura(nombre)
    if os.path.exists(ruta):
        return nombre
    directorio = os.path.dirname(ruta)
    nombre_base = os.path.basename(nombre)
    if os.path.exists(directorio):
        for item in os.listdir(directorio):
            if os.path.splitext(item)[0].lower() == nombre_base.lower():
                return os.path.join(os.path.dirname(nombre), item) if os.path.dirname(nombre) else item
    return nombre

# ─── COMPRIMIR ────────────────────────────────────────────────────────────────

def comprimir_zip(nombre_origen: str = "", nombre_zip: str = "", **kwargs) -> str:
    # Aceptar 'nombre' o 'carpeta' como alias de 'nombre_origen'
    nombre_origen = nombre_origen or kwargs.get("nombre") or kwargs.get("carpeta") or ""
    if not nombre_origen:
        return "❌ No especificaste qué comprimir."

    nombre_origen = _buscar_nombre_real(nombre_origen)
    ruta_origen = _ruta_segura(nombre_origen)

    if not os.path.exists(ruta_origen):
        return f"❌ '{nombre_origen}' no existe."

    if not nombre_zip:
        nombre_zip = os.path.splitext(nombre_origen)[0] + ".zip"
    if not nombre_zip.endswith(".zip"):
        nombre_zip += ".zip"

    ruta_zip = _ruta_segura(nombre_zip)

    try:
        with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            if os.path.isdir(ruta_origen):
                for raiz, dirs, archivos in os.walk(ruta_origen):
                    for archivo in archivos:
                        ruta_archivo = os.path.join(raiz, archivo)
                        arcname = os.path.relpath(ruta_archivo, SANDBOX_PATH)
                        zf.write(ruta_archivo, arcname)
            else:
                zf.write(ruta_origen, os.path.basename(ruta_origen))
        tamaño = os.path.getsize(ruta_zip) / 1024
        return f"✅ '{nombre_origen}' comprimido como '{nombre_zip}' ({tamaño:.1f} KB)"
    except Exception as e:
        return f"❌ Error al comprimir: {str(e)}"

def descomprimir_zip(nombre_zip: str, carpeta_destino: str = "") -> str:
    nombre_zip = _buscar_nombre_real(nombre_zip)
    ruta_zip = _ruta_segura(nombre_zip)

    if not os.path.exists(ruta_zip):
        return f"❌ '{nombre_zip}' no existe."

    if not carpeta_destino:
        carpeta_destino = os.path.splitext(nombre_zip)[0] + "_descomprimido"

    ruta_destino = _ruta_segura(carpeta_destino)

    try:
        with zipfile.ZipFile(ruta_zip, "r") as zf:
            zf.extractall(ruta_destino)
        return f"✅ '{nombre_zip}' descomprimido en '{carpeta_destino}'"
    except Exception as e:
        return f"❌ Error al descomprimir: {str(e)}"

def ver_contenido_zip(nombre_zip: str) -> str:
    nombre_zip = _buscar_nombre_real(nombre_zip)
    ruta_zip = _ruta_segura(nombre_zip)

    if not os.path.exists(ruta_zip):
        return f"❌ '{nombre_zip}' no existe."

    try:
        with zipfile.ZipFile(ruta_zip, "r") as zf:
            archivos = zf.namelist()
        if not archivos:
            return f"📦 '{nombre_zip}' está vacío."
        lista = "\n".join(f"  • {a}" for a in archivos[:30])
        extra = f"\n  ... y {len(archivos)-30} archivos más." if len(archivos) > 30 else ""
        return f"📦 Contenido de '{nombre_zip}' ({len(archivos)} archivos):\n{lista}{extra}"
    except Exception as e:
        return f"❌ Error al leer ZIP: {str(e)}"

# ─── CONVERTIR ────────────────────────────────────────────────────────────────

def convertir_txt_a_pdf(nombre_txt: str, nombre_pdf: str = "") -> str:
    try:
        from fpdf import FPDF
    except ImportError:
        return "❌ Necesitás instalar fpdf2: pip install fpdf2"

    nombre_txt = _buscar_nombre_real(nombre_txt)
    ruta_txt = _ruta_segura(nombre_txt)

    if not os.path.exists(ruta_txt):
        return f"❌ '{nombre_txt}' no existe."

    if not nombre_pdf:
        nombre_pdf = os.path.splitext(nombre_txt)[0] + ".pdf"
    ruta_pdf = _ruta_segura(nombre_pdf)

    try:
        with open(ruta_txt, "r", encoding="utf-8") as f:
            contenido = f.read()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.set_auto_page_break(auto=True, margin=15)

        for linea in contenido.split("\n"):
            pdf.cell(0, 8, linea.encode("latin-1", "replace").decode("latin-1"), ln=True)

        pdf.output(ruta_pdf)
        return f"✅ '{nombre_txt}' convertido a '{nombre_pdf}'"
    except Exception as e:
        return f"❌ Error al convertir: {str(e)}"

def convertir_imagen(nombre_origen: str, formato_destino: str) -> str:
    try:
        from PIL import Image
    except ImportError:
        return "❌ Necesitás instalar Pillow: pip install pillow"

    nombre_origen = _buscar_nombre_real(nombre_origen)
    ruta_origen = _ruta_segura(nombre_origen)

    if not os.path.exists(ruta_origen):
        return f"❌ '{nombre_origen}' no existe."

    formato_destino = formato_destino.lower().strip().replace(".", "")
    nombre_destino = os.path.splitext(nombre_origen)[0] + "." + formato_destino
    ruta_destino = _ruta_segura(nombre_destino)

    try:
        img = Image.open(ruta_origen)
        if formato_destino in ("jpg", "jpeg"):
            img = img.convert("RGB")
        img.save(ruta_destino)
        return f"✅ '{nombre_origen}' convertido a '{nombre_destino}'"
    except Exception as e:
        return f"❌ Error al convertir imagen: {str(e)}"

def convertir_csv_a_txt(nombre_csv: str, nombre_txt: str = "") -> str:
    import csv
    nombre_csv = _buscar_nombre_real(nombre_csv)
    ruta_csv = _ruta_segura(nombre_csv)

    if not os.path.exists(ruta_csv):
        return f"❌ '{nombre_csv}' no existe."

    if not nombre_txt:
        nombre_txt = os.path.splitext(nombre_csv)[0] + ".txt"
    ruta_txt = _ruta_segura(nombre_txt)

    try:
        with open(ruta_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            filas = list(reader)
        with open(ruta_txt, "w", encoding="utf-8") as f:
            for fila in filas:
                f.write(" | ".join(fila) + "\n")
        return f"✅ '{nombre_csv}' convertido a '{nombre_txt}' ({len(filas)} filas)"
    except Exception as e:
        return f"❌ Error al convertir: {str(e)}"