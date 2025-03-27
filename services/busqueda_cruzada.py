import re
import requests
from bs4 import BeautifulSoup
from services.validator import validar_email
from googlesearch import search as google_search
from urllib.parse import quote_plus
from duckduckgo_search import DDGS

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

# =====================================
# SECCIÓN 1: Scraping directo en redes
# =====================================

def buscar_email_en_facebook(username, nombre_completo=None):
    urls = [f"https://www.facebook.com/{username}"]

    if nombre_completo:
        nombre_codificado = quote_plus(nombre_completo)
        urls.append(f"https://www.facebook.com/public?q={nombre_codificado}")

    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code != 200:
                continue
            text = BeautifulSoup(res.text, "html.parser").get_text()
            correos = re.findall(EMAIL_REGEX, text)
            for correo in correos:
                if validar_email(correo):
                    return {"email": correo, "origen": "facebook", "url_fuente": url}
        except Exception:
            continue
    return None

def buscar_email_en_twitter(username):
    url = f"https://twitter.com/{username}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None
        text = BeautifulSoup(res.text, "html.parser").get_text()
        correos = re.findall(EMAIL_REGEX, text)
        for correo in correos:
            if validar_email(correo):
                return {"email": correo, "origen": "twitter", "url_fuente": url}
    except Exception:
        return None

def buscar_email_en_github(username):
    url = f"https://github.com/{username}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code != 200:
            return None
        text = BeautifulSoup(res.text, "html.parser").get_text()
        correos = re.findall(EMAIL_REGEX, text)
        for correo in correos:
            if validar_email(correo):
                return {"email": correo, "origen": "github", "url_fuente": url}
    except Exception:
        return None

# ====================================================
# SECCIÓN 2: Búsqueda en DuckDuckGo (nuevo fallback)
# ====================================================

def buscar_email_en_duckduckgo(query, max_urls=5):
    print(f"🔍 Buscando con DuckDuckGo: {query}")
    with DDGS() as ddgs:
        resultados = ddgs.text(query, region="es-es", safesearch="Moderate", max_results=max_urls)
        if not resultados:
            return None

        for resultado in resultados:
            url = resultado.get("href") or resultado.get("url")
            if not url:
                continue
            try:
                print(f"🌐 Revisando: {url}")
                html = requests.get(url, timeout=5).text
                text = BeautifulSoup(html, "html.parser").get_text()
                correos = re.findall(EMAIL_REGEX, text)
                for correo in correos:
                    if validar_email(correo):
                        return {"email": correo, "url_fuente": url, "origen": "duckduckgo"}
            except Exception:
                continue
    return None


# ====================================================
# SECCIÓN 3: Búsqueda en Google (última opción)
# ====================================================

def buscar_email_en_google(username, nombre_completo=None, max_urls=5):
    if nombre_completo:
        query = f'"{nombre_completo}" contacto OR email OR sitio web'
    else:
        query = f'"{username}" contacto OR email OR sitio web'

    print(f"🔍 Búsqueda cruzada: {query}")
    resultados = google_search(query, num_results=max_urls, lang="es")

    for url in resultados:
        try:
            print(f"🌐 Revisando: {url}")
            html = requests.get(url, timeout=5).text
            text = BeautifulSoup(html, "html.parser").get_text()
            correos = re.findall(EMAIL_REGEX, text)
            for correo in correos:
                if validar_email(correo):
                    return {"email": correo, "url_fuente": url, "origen": "google"}
        except Exception:
            continue

    return {"email": None, "url_fuente": None, "origen": "no_encontrado"}

# ====================================================
# SECCIÓN 4: Función principal de búsqueda cruzada
# ====================================================

def buscar_email(username, nombre_completo=None):
    # 1. Buscar en Facebook (username y nombre)
    fb = buscar_email_en_facebook(username, nombre_completo)
    if fb:
        return fb

    # 2. Buscar en Twitter
    tw = buscar_email_en_twitter(username)
    if tw:
        return tw

    # 3. Buscar en GitHub
    gh = buscar_email_en_github(username)
    if gh:
        return gh

    # 4. Buscar con DuckDuckGo si no hay resultados anteriores
    query = nombre_completo if nombre_completo else username
    ddg_result = buscar_email_en_duckduckgo(query)
    if ddg_result:
        return ddg_result

    # 5. Búsqueda final por Google (última opción)
    return buscar_email_en_google(username, nombre_completo)

# NOTA:
# Si este archivo se hace demasiado largo, puedes separar así:
# - services/fuentes_directas.py → funciones facebook/twitter/github
# - services/google_fallback.py → buscar_email_en_google()
# - services/busqueda_cruzada.py → solo dejar buscar_email() y orquestar todo
