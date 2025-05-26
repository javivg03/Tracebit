import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS

from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.logging_config import logger


def analizar_url_contacto(url: str, username: str, origen: str = "web", timeout: int = 6) -> dict | None:
    try:
        logger.info(f"✪ Analizando URL: {url} (origen: {origen})")
        res = requests.get(url, timeout=timeout)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)

            emails = extraer_emails(text)
            telefonos = extraer_telefonos(text)

            email = emails[0] if emails else None
            telefono = telefonos[0] if telefonos else None
            origen_real = construir_origen(origen, email, telefono)

            if email or telefono:
                return normalizar_datos_scraper(
                    nombre=None,
                    usuario=username,
                    email=email,
                    telefono=telefono,
                    origen=origen_real,
                    url_fuente=url
                )
    except Exception as e:
        logger.warning(f"❌ Error accediendo a {url}: {e}")
    return None


def buscar_en_duckduckgo(query: str, max_urls: int = 5) -> list:
    logger.info(f"🧆 DuckDuckGo → {query}")
    resultados = []
    try:
        with DDGS() as ddgs:
            for resultado in ddgs.text(query, max_results=max_urls):
                url = resultado.get("href") or resultado.get("url")
                if url:
                    resultados.append(url)
    except Exception as e:
        logger.warning(f"❌ DuckDuckGo error: {e}")
    return resultados


def buscar_en_google(query: str, max_urls: int = 5) -> list:
    logger.info(f"🔍 Google → {query}")
    resultados = []
    try:
        urls = google_search(query, num_results=max_urls, lang="es")
        resultados = [url for url in urls if url]
    except Exception as e:
        logger.warning(f"❌ Google error: {e}")
    return resultados


# 1️⃣ Búsqueda web por nombre o username (devuelve un resultado útil o vacío)
def buscar_por_nombre(username: str, nombre_completo: str | None = None) -> dict:
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    motores = [buscar_en_duckduckgo, buscar_en_google]

    for motor in motores:
        urls = motor(query)
        for url in urls:
            datos = analizar_url_contacto(url, username=username, origen="web")
            if datos:
                return datos

    logger.warning("❌ No se encontró información web relevante.")
    return normalizar_datos_scraper(
        nombre=None,
        usuario=username,
        email=None,
        telefono=None,
        origen="no_encontrado"
    )


# 2️⃣ Búsqueda genérica por palabra clave (devuelve lista de contactos útiles)
def buscar_por_palabra_clave(query: str, max_resultados: int = 5) -> list:
    motores = [buscar_en_duckduckgo, buscar_en_google]
    resultados_utiles = []

    for motor in motores:
        urls = motor(query, max_urls=max_resultados)
        for url in urls:
            datos = analizar_url_contacto(url, username=query, origen="web")
            if datos:
                resultados_utiles.append(datos)
            if len(resultados_utiles) >= max_resultados:
                return resultados_utiles

    logger.warning("❌ No se encontraron resultados útiles por palabra clave.")
    return resultados_utiles
