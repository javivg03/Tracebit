import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from utils.validator import extraer_emails, extraer_telefonos
from services.proxy_pool import ProxyPool
from services.logging_config import logger
from services.proxy_format import formatear_proxy_requests

# =========================
# FUNCIONES DE EXTRACCIÓN WEB
# =========================

def analizar_url_contacto(url, origen="externo", timeout=5):
    try:
        if not url or not url.startswith("http"):
            logger.warning("⚠️ URL vacía o inválida. Saltando...")
            return None

        logger.info(f"🔗 Analizando URL: {url} (origen: {origen})")

        pool = ProxyPool()
        proxy = pool.get_random_proxy()
        proxy_url = formatear_proxy_requests(proxy) if proxy else None
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None

        res = requests.get(url, timeout=timeout, proxies=proxies)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
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
        # pool.remove_proxy(proxy)  # opcional
    return None

# =========================
# FUNCIONES PLATAFORMAS PERSONALES
# =========================

def buscar_contacto_en_github(username):
    return analizar_url_contacto(f"https://github.com/{username}", "github")

def buscar_contacto_en_aboutme(username):
    return analizar_url_contacto(f"https://about.me/{username}", "aboutme")

def buscar_contacto_en_medium(username):
    return analizar_url_contacto(f"https://medium.com/@{username}", "medium")

# =========================
# FUNCIONES BUSCADOR DUCKDUCKGO
# =========================

def buscar_contacto_en_duckduckgo(query, max_urls=5):
    logger.info(f"🧆 DuckDuckGo → {query}")
    try:
        with DDGS() as ddgs:
            for resultado in ddgs.text(query, max_results=max_urls):
                url = resultado.get("href") or resultado.get("url")
                if not url or not url.startswith("http"):
                    continue
                datos = analizar_url_contacto(url, "duckduckgo")
                if datos:
                    return datos
    except Exception as e:
        logger.warning(f"❌ DuckDuckGo error: {e}")
    return None

# =========================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA CRUZADA
# =========================

def buscar_contacto(username, nombre_completo=None, origen_actual=None):
    logger.info(f"🔎 Iniciando búsqueda cruzada para {username} (origen: {origen_actual})")

    # 1️⃣ Plataformas Personales
    for buscador in [buscar_contacto_en_github, buscar_contacto_en_aboutme, buscar_contacto_en_medium]:
        try:
            datos = buscador(username)
            if datos:
                logger.info(f"✅ Contacto encontrado en plataforma personal: {datos}")
                return datos
        except Exception as e:
            logger.warning(f"⚠️ Error en plataforma personal {buscador.__name__}: {e}")

    # 2️⃣ DuckDuckGo como único buscador general
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    try:
        datos = buscar_contacto_en_duckduckgo(query)
        if datos:
            logger.info(f"✅ Contacto encontrado en buscador: {datos}")
            return datos
    except Exception as e:
        logger.warning(f"⚠️ Error en DuckDuckGo: {e}")

    logger.warning("❌ No se encontró información de contacto relevante.")
    return None
