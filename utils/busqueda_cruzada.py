import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS
from utils.validator import extraer_emails, extraer_telefonos
import logging

logger = logging.getLogger("fct_scraper")

# =========================
# FUNCIONES DE EXTRACCIÓN
# =========================

def analizar_url_contacto(url, origen="externo", timeout=5):
    try:
        logger.info(f"🔗 Analizando URL: {url} (origen: {origen})")
        res = requests.get(url, timeout=timeout)
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
        logger.warning(f"❌ Error accediendo a {url}: {e}")
    return None

# =========================
# PLATAFORMAS DIRECTAS
# =========================

def buscar_contacto_en_github(username):
    return analizar_url_contacto(f"https://github.com/{username}", "github")

def buscar_contacto_en_aboutme(username):
    return analizar_url_contacto(f"https://about.me/{username}", "aboutme")

def buscar_contacto_en_medium(username):
    return analizar_url_contacto(f"https://medium.com/@{username}", "medium")

# =========================
# MOTORES DE BÚSQUEDA
# =========================

def buscar_contacto_en_duckduckgo(query, max_urls=5):
    logger.info(f"🧆 DuckDuckGo → {query}")
    try:
        with DDGS() as ddgs:
            for resultado in ddgs.text(query, max_results=max_urls):
                url = resultado.get("href") or resultado.get("url")
                if url:
                    datos = analizar_url_contacto(url, "duckduckgo")
                    if datos:
                        return datos
    except Exception as e:
        logger.warning(f"❌ DuckDuckGo error: {e}")
    return None

def buscar_contacto_en_google(query, max_urls=5):
    logger.info(f"🔍 Google → {query}")
    try:
        resultados = google_search(query, num_results=max_urls, lang="es")
        for url in resultados:
            datos = analizar_url_contacto(url, "google")
            if datos:
                return datos
    except Exception as e:
        logger.warning(f"❌ Google error: {e}")
    return None

def buscar_contacto_en_yahoo(query):
    logger.info(f"🔸 Yahoo → {query}")
    url_search = f"https://es.search.yahoo.com/search?p={quote_plus(query)}"
    return analizar_url_contacto(url_search, "yahoo")

# =========================
# BÚSQUEDA CRUZADA
# =========================

def buscar_contacto(username, nombre_completo=None, origen_actual=None):
    logger.info(f"🔎 Iniciando búsqueda cruzada para: {username} (origen actual: {origen_actual})")

    plataformas_personales = [
        buscar_contacto_en_github,
        buscar_contacto_en_aboutme,
        buscar_contacto_en_medium
    ]

    for funcion in plataformas_personales:
        try:
            datos = funcion(username)
            if datos:
                return datos
        except Exception as e:
            logger.warning(f"⚠️ Error en {funcion.__name__}: {e}")

    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    motores = [
        buscar_contacto_en_duckduckgo,
        buscar_contacto_en_google,
        buscar_contacto_en_yahoo
    ]

    for buscador in motores:
        try:
            datos = buscador(query)
            if datos:
                return datos
        except Exception as e:
            logger.warning(f"⚠️ Error en {buscador.__name__}: {e}")

    logger.warning("❌ No se encontró información de contacto relevante.")
    return {
        "email": None,
        "telefono": None,
        "url_fuente": None,
        "origen": "no_encontrado",
        "nombre": None
    }
