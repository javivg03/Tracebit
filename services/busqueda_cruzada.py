import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS
import concurrent.futures

from services.validator import extraer_emails, extraer_telefonos
from scraping.insta import extraer_datos_relevantes as scrape_instagram
from scraping.telegram import scrape_telegram


# ===============================
# FUNCIONES QUE USAN TUS SCRAPERS (LOS QUE NO USAN PLAYWRIGHT)
# ===============================

def buscar_contacto_en_instagram(username):
    try:
        resultado = scrape_instagram(username)
        if resultado.get("email") or resultado.get("telefono"):
            return {
                "email": resultado.get("email"),
                "telefono": resultado.get("telefono"),
                "origen": "instagram",
                "url_fuente": resultado.get("fuente_email")
            }
    except Exception:
        pass
    return None


def buscar_contacto_en_telegram(username):
    try:
        resultado = scrape_telegram(username)
        if resultado.get("email") or resultado.get("telefono"):
            return {
                "email": resultado.get("email"),
                "telefono": resultado.get("telefono"),
                "origen": "telegram",
                "url_fuente": resultado.get("fuente_email")
            }
    except Exception:
        pass
    return None


# ===============================
# FUENTES EXTERNAS (NO SCRAPERS PROPIOS)
# ===============================

def buscar_contacto_en_github(username):
    url = f"https://github.com/{username}"
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
                    "origen": "github",
                    "url_fuente": url
                }
    except Exception:
        pass
    return None


def buscar_contacto_en_aboutme(username):
    url = f"https://about.me/{username}"
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
                    "origen": "aboutme",
                    "url_fuente": url
                }
    except Exception:
        pass
    return None


def buscar_contacto_en_medium(username):
    url = f"https://medium.com/@{username}"
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
                    "origen": "medium",
                    "url_fuente": url
                }
    except Exception:
        pass
    return None


# ===============================
# MOTORES DE BÚSQUEDA EXTERNOS
# ===============================

def buscar_contacto_en_duckduckgo(query, max_urls=5):
    print(f"🔍 DuckDuckGo → {query}")
    with DDGS() as ddgs:
        resultados = ddgs.text(query, region="es-es", safesearch="Moderate", max_results=max_urls)
        for resultado in resultados:
            url = resultado.get("href") or resultado.get("url")
            if not url:
                continue
            try:
                html = requests.get(url, timeout=5).text
                text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
                emails = extraer_emails(text)
                telefonos = extraer_telefonos(text)
                if emails or telefonos:
                    return {
                        "email": emails[0] if emails else None,
                        "telefono": telefonos[0] if telefonos else None,
                        "url_fuente": url,
                        "origen": "duckduckgo"
                    }
            except Exception:
                continue
    return None


def buscar_contacto_en_google(username, nombre_completo=None, max_urls=5):
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    print(f"🔍 Google → {query}")
    resultados = google_search(query, num_results=max_urls, lang="es")
    for url in resultados:
        try:
            html = requests.get(url, timeout=5).text
            text = BeautifulSoup(html, "html.parser").get_text(separator=" ", strip=True)
            emails = extraer_emails(text)
            telefonos = extraer_telefonos(text)
            if emails or telefonos:
                return {
                    "email": emails[0] if emails else None,
                    "telefono": telefonos[0] if telefonos else None,
                    "url_fuente": url,
                    "origen": "google"
                }
        except Exception:
            continue
    return {"email": None, "telefono": None, "url_fuente": None, "origen": "no_encontrado"}


def buscar_contacto_en_yahoo(username, nombre_completo=None, max_urls=5):
    # Ejemplo de integración con Yahoo search (se usa el motor de búsqueda de Yahoo mediante una query HTTP)
    query = f'"{nombre_completo or username}" contacto OR email OR teléfono'
    url_search = f"https://es.search.yahoo.com/search?p={quote_plus(query)}"
    print(f"🔍 Yahoo → {query}")
    try:
        res = requests.get(url_search, timeout=5)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text(separator=" ", strip=True)
            emails = extraer_emails(text)
            telefonos = extraer_telefonos(text)
            if emails or telefonos:
                return {
                    "email": emails[0] if emails else None,
                    "telefono": telefonos[0] if telefonos else None,
                    "url_fuente": url_search,
                    "origen": "yahoo"
                }
    except Exception:
        pass
    return None


# ===============================
# FUNCIÓN PRINCIPAL DE BÚSQUEDA CRUZADA CON EJECUCIÓN CONCURRENTE Y PRIORIDADES
# ===============================

# Asignamos prioridades (mayor valor indica mayor confiabilidad)
PRIORIDADES = {
    "instagram": 10,
    "telegram": 9,
    "github": 7,
    "aboutme": 6,
    "medium": 6,
    "duckduckgo": 4,
    "google": 4,
    "yahoo": 3
}


def buscar_contacto(username, nombre_completo=None):
    """
    Ejecuta varias estrategias de búsqueda cruzada concurrentemente para obtener email y teléfono.
    """
    print("🔎 Iniciando búsqueda cruzada (sin Playwright)...")

    estrategias = [
        buscar_contacto_en_instagram,
        buscar_contacto_en_telegram,
        buscar_contacto_en_github,
        buscar_contacto_en_aboutme,
        buscar_contacto_en_medium,
        lambda u: buscar_contacto_en_duckduckgo(nombre_completo or username),
        lambda u: buscar_contacto_en_google(u, nombre_completo),
        lambda u: buscar_contacto_en_yahoo(u, nombre_completo)
    ]

    resultados = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Lanzamos todas las estrategias en paralelo
        futures = {executor.submit(estrategia, username): estrategia for estrategia in estrategias}
        for future in concurrent.futures.as_completed(futures):
            try:
                res = future.result()
                if res and (res.get("email") or res.get("telefono")):
                    resultados.append(res)
            except Exception:
                continue

    if resultados:
        # Seleccionamos el resultado con la mayor prioridad
        resultados.sort(key=lambda r: PRIORIDADES.get(r.get("origen"), 0), reverse=True)
        mejor_resultado = resultados[0]
        print(f"✅ Resultado seleccionado: {mejor_resultado}")
        return mejor_resultado

    return {"email": None, "telefono": None, "url_fuente": None, "origen": "no_encontrado"}
