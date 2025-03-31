import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from googlesearch import search as google_search
from duckduckgo_search import DDGS

from services.validator import extraer_emails
from scraping.instagram import extraer_datos_relevantes as scrape_instagram
from scraping.youtube import scrape_youtube
from scraping.tiktok import scrape_tiktok
from scraping.telegram import scrape_telegram
from scraping.facebook import scrape_facebook
from scraping.x import scrape_x

# ===============================
# FUNCIONES QUE USAN TUS SCRAPERS
# ===============================

def buscar_email_en_instagram(username):
    try:
        resultado = scrape_instagram(username)
        if resultado["email"]:
            return {
                "email": resultado["email"],
                "origen": "instagram",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

def buscar_email_en_youtube(username):
    try:
        resultado = scrape_youtube(username)
        if resultado["email"]:
            return {
                "email": resultado["email"],
                "origen": "youtube",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

def buscar_email_en_tiktok(username):
    try:
        resultado = scrape_tiktok(username)
        if resultado["email"]:
            return {
                "email": resultado["email"],
                "origen": "tiktok",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

def buscar_email_en_telegram(username):
    try:
        resultado = scrape_telegram(username)
        if resultado["email"]:
            return {
                "email": resultado["email"],
                "origen": "telegram",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

def buscar_email_en_facebook(username):
    try:
        resultado = scrape_facebook(username)
        if resultado["email"]:
            return {
                "email": resultado["email"],
                "origen": "facebook",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

def buscar_email_en_x(username):
    try:
        resultado = scrape_x(username)
        if resultado["email"] and resultado["email"] != "No encontrado":
            return {
                "email": resultado["email"],
                "origen": "x",
                "url_fuente": resultado["fuente_email"]
            }
    except:
        pass
    return None

# ===============================
# FUENTES EXTERNAS (NO SCRAPERS PROPIOS)
# ===============================

def buscar_email_en_github(username):
    url = f"https://github.com/{username}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text()
            emails = extraer_emails(text)
            if emails:
                return {"email": emails[0], "origen": "github", "url_fuente": url}
    except:
        pass
    return None

def buscar_email_en_aboutme(username):
    url = f"https://about.me/{username}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text()
            emails = extraer_emails(text)
            if emails:
                return {"email": emails[0], "origen": "aboutme", "url_fuente": url}
    except:
        pass
    return None

def buscar_email_en_medium(username):
    url = f"https://medium.com/@{username}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            text = BeautifulSoup(res.text, "html.parser").get_text()
            emails = extraer_emails(text)
            if emails:
                return {"email": emails[0], "origen": "medium", "url_fuente": url}
    except:
        pass
    return None

# ===============================
# MOTORES DE BÚSQUEDA EXTERNOS
# ===============================

def buscar_email_en_duckduckgo(query, max_urls=5):
    print(f"🔍 DuckDuckGo → {query}")
    with DDGS() as ddgs:
        resultados = ddgs.text(query, region="es-es", safesearch="Moderate", max_results=max_urls)
        for resultado in resultados:
            url = resultado.get("href") or resultado.get("url")
            if not url:
                continue
            try:
                html = requests.get(url, timeout=5).text
                text = BeautifulSoup(html, "html.parser").get_text()
                emails = extraer_emails(text)
                if emails:
                    return {"email": emails[0], "url_fuente": url, "origen": "duckduckgo"}
            except:
                continue
    return None

def buscar_email_en_google(username, nombre_completo=None, max_urls=5):
    query = f'"{nombre_completo or username}" contacto OR email OR sitio web'
    print(f"🔍 Google → {query}")
    resultados = google_search(query, num_results=max_urls, lang="es")
    for url in resultados:
        try:
            html = requests.get(url, timeout=5).text
            text = BeautifulSoup(html, "html.parser").get_text()
            emails = extraer_emails(text)
            if emails:
                return {"email": emails[0], "url_fuente": url, "origen": "google"}
        except:
            continue
    return {"email": None, "url_fuente": None, "origen": "no_encontrado"}

# ===============================
# FUNCIÓN PRINCIPAL
# ===============================

def buscar_email(username, nombre_completo=None):
    print("🔎 Iniciando búsqueda cruzada...")

    estrategias = [
        buscar_email_en_instagram,
        buscar_email_en_youtube,
        buscar_email_en_tiktok,
        buscar_email_en_telegram,
        buscar_email_en_x,
        buscar_email_en_facebook,
        buscar_email_en_github,
        buscar_email_en_aboutme,
        buscar_email_en_medium,
        lambda u: buscar_email_en_duckduckgo(nombre_completo or username),
        lambda u: buscar_email_en_google(u, nombre_completo)
    ]

    for estrategia in estrategias:
        resultado = estrategia(username)
        if resultado and resultado["email"]:
            return resultado

    return {"email": None, "url_fuente": None, "origen": "no_encontrado"}
