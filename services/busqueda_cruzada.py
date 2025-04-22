import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS

from services.validator import extraer_emails, extraer_telefonos


# ===============================
# FUNCIONES DE ANÁLISIS EXTERNAS
# ===============================

def analizar_url_contacto(url, origen="externo"):
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text(separator=" ", strip=True)
            emails = extraer_emails(text)
            telefonos = extraer_telefonos(text)
            if emails or telefonos:
                return {
                    "email": emails[0] if emails else None,
                    "telefono": telefonos[0] if telefonos else None,
                    "url_fuente": url,
                    "origen": origen
                }
    except Exception as e:
        print(f"❌ Error accediendo a {url}: {e}")
    return None


# ===============================
# PLATAFORMAS EXTERNAS PÚBLICAS
# ===============================

def buscar_contacto_en_github(username):
    return analizar_url_contacto(f"https://github.com/{username}", "github")

def buscar_contacto_en_aboutme(username):
    return analizar_url_contacto(f"https://about.me/{username}", "aboutme")

def buscar_contacto_en_medium(username):
    return analizar_url_contacto(f"https://medium.com/@{username}", "medium")


# ===============================
# BUSCADORES GENERALES
# ===============================

def buscar_contacto_en_duckduckgo(query, max_urls=5):
    print(f"🦆 DuckDuckGo → {query}")
    with DDGS() as ddgs:
        for resultado in ddgs.text(query, max_results=max_urls):
            url = resultado.get("href") or resultado.get("url")
            if url:
                datos = analizar_url_contacto(url, "duckduckgo")
                if datos:
                    return datos
    return None

def buscar_contacto_en_google(query, max_urls=5):
    print(f"🔍 Google → {query}")
    try:
        resultados = google_search(query, num_results=max_urls, lang="es")
        for url in resultados:
            datos = analizar_url_contacto(url, "google")
            if datos:
                return datos
    except Exception as e:
        print(f"❌ Error en Google Search: {e}")
    return None

def buscar_contacto_en_yahoo(query):
    print(f"🟣 Yahoo → {query}")
    url_search = f"https://es.search.yahoo.com/search?p={quote_plus(query)}"
    return analizar_url_contacto(url_search, "yahoo")


# ===============================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA CRUZADA
# ===============================

def buscar_contacto(username, nombre_completo=None, origen_actual=None):
    print(f"🔎 Iniciando búsqueda cruzada (origen: {origen_actual})")

    # Paso 1 – Redes sociales propias (excluyendo la actual)

    redes_propias = []

    # TikTok
    if origen_actual != "tiktok":
        try:
            from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
            redes_propias.append(obtener_datos_perfil_tiktok)
        except ImportError:
            print("ℹ️ Scraper TikTok no disponible.")

    # Telegram
    if origen_actual != "telegram":
        try:
            from scraping.telegram.perfil import obtener_datos_perfil_telegram
            redes_propias.append(obtener_datos_perfil_telegram)
        except ImportError:
            print("ℹ️ Scraper Telegram no disponible.")

    # Facebook
    if origen_actual != "facebook":
        try:
            from scraping.facebook.perfil import obtener_datos_perfil_facebook
            redes_propias.append(obtener_datos_perfil_facebook)
        except ImportError:
            print("ℹ️ Scraper Facebook no disponible.")

    # X (Twitter)
    if origen_actual != "x":
        try:
            from scraping.x.perfil import obtener_datos_perfil_x
            redes_propias.append(obtener_datos_perfil_x)
        except ImportError:
            print("ℹ️ Scraper X (Twitter) no disponible.")

    # YouTube
    if origen_actual != "youtube":
        try:
            from scraping.youtube.perfil import obtener_datos_perfil_youtube
            redes_propias.append(obtener_datos_perfil_youtube)
        except ImportError:
            print("ℹ️ Scraper YouTube no disponible.")


    for funcion in redes_propias:
        try:
            datos = funcion(username)
            if datos and (datos.get("email") or datos.get("telefono")):
                print(f"✅ Contacto encontrado en {funcion.__name__}")
                return {
                    "email": datos.get("email"),
                    "telefono": datos.get("telefono"),
                    "url_fuente": datos.get("fuente_email"),
                    "origen": datos.get("origen"),
                    "nombre": datos.get("nombre")
                }
        except Exception as e:
            print(f"⚠️ Error en fallback con {funcion.__name__}: {e}")

    # Paso 2 – Plataformas personales públicas
    for funcion in [buscar_contacto_en_github, buscar_contacto_en_aboutme, buscar_contacto_en_medium]:
        try:
            datos = funcion(username)
            if datos:
                return datos
        except Exception:
            continue

    # Paso 3 – Motores de búsqueda generales
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    for buscador in [buscar_contacto_en_duckduckgo, buscar_contacto_en_google, buscar_contacto_en_yahoo]:
        try:
            datos = buscador(query)
            if datos:
                return datos
        except Exception:
            continue

    print("❌ No se encontró información de contacto.")
    return {"email": None, "telefono": None, "url_fuente": None, "origen": "no_encontrado", "nombre": None}
