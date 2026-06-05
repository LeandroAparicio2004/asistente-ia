import requests
import socket
import subprocess

# ─── BÚSQUEDA EN INTERNET ─────────────────────────────────────────────────────

def buscar_en_internet(consulta: str) -> str:
    """Busca en Wikipedia API y devuelve un resumen."""
    try:
        headers = {"User-Agent": "AsistenteIA/1.0"}

        url = "https://es.wikipedia.org/api/rest_v1/page/summary/" + consulta.replace(" ", "_")
        response = requests.get(url, headers=headers, timeout=8)

        if response.status_code == 200:
            data = response.json()
            titulo = data.get("title", "")
            resumen = data.get("extract", "")
            if resumen:
                if len(resumen) > 500:
                    resumen = resumen[:500] + "..."
                return f"🌐 {titulo}:\n\n{resumen}"

        url2 = "https://es.wikipedia.org/w/api.php"
        params = {
            "action": "opensearch",
            "search": consulta,
            "limit": 3,
            "format": "json",
            "lang": "es"
        }
        response2 = requests.get(url2, params=params, headers=headers, timeout=8)
        data2 = response2.json()

        if data2[1]:
            resultados = []
            for titulo, desc in zip(data2[1][:3], data2[2][:3]):
                if desc:
                    resultados.append(f"• {titulo}: {desc[:200]}")
                else:
                    resultados.append(f"• {titulo}")
            return f"🌐 Resultados para '{consulta}':\n\n" + "\n\n".join(resultados)

        return f"❌ No encontré resultados para '{consulta}'."

    except requests.Timeout:
        return "❌ La búsqueda tardó demasiado. Revisá tu conexión."
    except Exception as e:
        return f"❌ Error al buscar: {str(e)}"

# ─── CLIMA ────────────────────────────────────────────────────────────────────

def obtener_clima(ciudad: str) -> str:
    try:
        from config import OPENWEATHER_API_KEY
        if not OPENWEATHER_API_KEY:
            return "❌ No hay API key de OpenWeatherMap en el .env"

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": ciudad,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "es",
        }
        response = requests.get(url, params=params, timeout=8)
        data = response.json()

        if data.get("cod") != 200:
            return f"❌ Error {data.get('cod')}: {data.get('message', 'desconocido')}"

        nombre_ciudad = data["name"]
        pais = data["sys"]["country"]
        descripcion = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        sensacion = data["main"]["feels_like"]
        humedad = data["main"]["humidity"]
        viento = data["wind"]["speed"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]

        return (
            f"🌤️ Clima en {nombre_ciudad}, {pais}:\n"
            f"  • Estado: {descripcion}\n"
            f"  • Temperatura: {temp}°C (sensación {sensacion}°C)\n"
            f"  • Mín/Máx: {temp_min}°C / {temp_max}°C\n"
            f"  • Humedad: {humedad}%\n"
            f"  • Viento: {viento} m/s"
        )

    except requests.Timeout:
        return "❌ La consulta tardó demasiado. Revisá tu conexión."
    except Exception as e:
        return f"❌ Error al obtener el clima: {str(e)}"

# ─── IP Y RED ─────────────────────────────────────────────────────────────────

def obtener_ip() -> str:
    resultado = ""
    try:
        hostname = socket.gethostname()
        ip_local = socket.gethostbyname(hostname)
        resultado += f"🌐 IP local: {ip_local}\n"
    except Exception as e:
        resultado += f"❌ Error IP local: {str(e)}\n"
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        ip_publica = response.json()["ip"]
        resultado += f"🌍 IP pública: {ip_publica}"
    except Exception as e:
        resultado += f"❌ Error IP pública: {str(e)}"
    return resultado.strip()

def obtener_red() -> str:
    try:
        result = subprocess.run(
            ["netsh", "wlan", "show", "interfaces"],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout

        if "No hay ninguna" in output or not output.strip():
            result2 = subprocess.run(
                ["ipconfig"],
                capture_output=True, text=True, timeout=10
            )
            lineas = result2.stdout.split("\n")
            adaptador = ""
            info = []
            for linea in lineas:
                if "Adaptador" in linea:
                    adaptador = linea.strip()
                if "Dirección IPv4" in linea and "169.254" not in linea:
                    ip = linea.split(":")[-1].strip()
                    info.append(f"  📡 {adaptador}: {ip}")
            if info:
                return "🔌 Conexiones activas:\n" + "\n".join(info)
            return "❌ No se detectó conexión de red activa."

        nombre = ""
        estado = ""
        senal = ""
        for linea in output.split("\n"):
            if "SSID" in linea and "BSSID" not in linea:
                nombre = linea.split(":")[-1].strip()
            if "Estado" in linea:
                estado = linea.split(":")[-1].strip()
            if "Señal" in linea:
                senal = linea.split(":")[-1].strip()

        return f"📶 Red WiFi:\n  • Nombre: {nombre}\n  • Estado: {estado}\n  • Señal: {senal}"

    except Exception as e:
        return f"❌ Error al obtener red: {str(e)}"

def hacer_speedtest() -> str:
    try:
        print("   ⏳ Midiendo velocidad... (puede tardar 15-30 segundos)")
        import speedtest
        st = speedtest.Speedtest()
        st.get_best_server()
        descarga = st.download() / 1_000_000
        subida = st.upload() / 1_000_000
        ping = st.results.ping
        servidor = st.results.server.get("name", "desconocido")
        return (
            f"🚀 Resultado del speedtest:\n"
            f"  • Descarga: {descarga:.1f} Mbps\n"
            f"  • Subida: {subida:.1f} Mbps\n"
            f"  • Ping: {ping:.0f} ms\n"
            f"  • Servidor: {servidor}"
        )
    except Exception as e:
        return f"❌ Error al medir velocidad: {str(e)}"

def verificar_conexion() -> str:
    try:
        requests.get("https://www.google.com", timeout=5)
        return "✅ Hay conexión a internet."
    except Exception:
        return "❌ No hay conexión a internet."