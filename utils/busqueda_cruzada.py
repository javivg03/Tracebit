import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS
from utils.validator import extraer_emails, extraer_telefonos
from services.proxy_pool import ProxyPool
from services.logging_config import logger

# =========================
# FUNCIONES DE EXTRACCIÓN
# =========================

def analizar_url_contacto(url, origen="externo", timeout=5):
    try:
        if not url or not url.startswith("http"):
            logger.warning("⚠️ URL vacía o inválida. Saltando...")
            return None

        logger.info(f"🔗 Analizando URL: {url} (origen: {origen})")

        pool = ProxyPool()
        proxy = pool.get_random_proxy()

        proxies = {"http": proxy, "https": proxy} if proxy else None

        res = requests.get(url, timeout=timeout, proxies=proxies)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text(separator=" ", strip=True)
            emails = extraer_emails(text)
            telefonos = extraer_telefonos(text)
            if emails or telefonos:
                return {
                    "email": emails[0] if emails else None,
                    "telefono": telefonos[0] if telefonos else None,
                    "url_fuente": url,
                    "origen": origen,
                    "nombre": None
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
                if not url or not url.startswith("http"):
                    logger.warning("⚠️ URL vacía o inválida en DuckDuckGo. Saltando...")
                    continue
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
            if not url or not url.startswith("http"):
                logger.warning("⚠️ URL vacía o inválida en Google. Saltando...")
                continue
            datos = analizar_url_contacto(url, "google")
            if datos:
                return datos
    except Exception as e:
        logger.warning(f"❌ Google error: {e}")
    return None

# =========================
# REDES SOCIALES (sin circular import)
# =========================

def buscar_contacto_en_red_social(username, nombre, red):
    try:
        if red == "instagram":
            from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback as insta
            datos = insta(username, forzar_solo_bio=True)
        elif red == "tiktok":
            from scraping.tiktok.perfil import obtener_datos_perfil_tiktok as tiktok
            datos = tiktok(username, forzar_solo_bio=True)
        elif red == "telegram":
            from scraping.telegram.canal import obtener_datos_canal_telegram as telegram
            datos = telegram(username)
        else:
            return None

        if datos and (datos.get("email") or datos.get("telefono")):
            return {
                "email": datos.get("email"),
                "telefono": datos.get("telefono"),
                "url_fuente": datos.get("fuente_email"),
                "origen": red,
                "nombre": datos.get("nombre")
            }

    except Exception as e:
        logger.warning(f"⚠️ Error buscando en {red}: {e}")

    return None

# =========================
# FLUJO ESCALONADO PRINCIPAL
# =========================

def buscar_contacto(username, nombre_completo=None, origen_actual=None):
    logger.info(f"🔎 Iniciando búsqueda cruzada para: {username} (origen actual: {origen_actual})")

    # 1️⃣ Redes sociales
    for red in ["instagram", "tiktok", "telegram"]:
        if red == origen_actual:
            continue
        datos = buscar_contacto_en_red_social(username, nombre_completo or username, red)
        if datos:
            return datos

    # 2️⃣ Plataformas personales
    for buscador in [buscar_contacto_en_github, buscar_contacto_en_aboutme, buscar_contacto_en_medium]:
        try:
            datos = buscador(username)
            if datos:
                return datos
        except Exception as e:
            logger.warning(f"⚠️ Error en {buscador.__name__}: {e}")

    # 3️⃣ Buscadores generales
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    for buscador in [buscar_contacto_en_duckduckgo, buscar_contacto_en_google]:
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
