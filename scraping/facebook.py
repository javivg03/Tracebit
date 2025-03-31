import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from services.validator import validar_email, validar_telefono
from services.busqueda_cruzada import buscar_email

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

def scrape_facebook(input_text):
    print(f"🚀 Iniciando scraping de Facebook para: {input_text}")

    urls = []

    # Detectamos si es username (sin espacios) o nombre completo
    if " " in input_text:
        nombre_codificado = quote_plus(input_text)
        urls.append(f"https://www.facebook.com/public?q={nombre_codificado}")
        modo = "nombre"
    else:
        urls.append(f"https://www.facebook.com/{input_text}")
        modo = "username"

    for url in urls:
        print(f"🌐 Accediendo a: {url}")
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8)
            if res.status_code != 200:
                print(f"⚠️ No se pudo acceder a: {url}")
                continue

            text = BeautifulSoup(res.text, "html.parser").get_text()

            # Email
            matches = re.findall(EMAIL_REGEX, text)
            email = None
            for m in matches:
                if validar_email(m):
                    email = m
                    break

            # Teléfono
            matches_tel = re.findall(PHONE_REGEX, text)
            telefono = None
            for t in matches_tel:
                if validar_telefono(t):
                    telefono = t
                    break

            nombre = input_text  # Lo devolvemos igualmente
            origen = "facebook"

            # Si no hay email, hacemos búsqueda cruzada
            if not email:
                resultado = buscar_email(input_text, input_text)
                email = resultado["email"]
                url_fuente = resultado["url_fuente"]
                origen = resultado["origen"]
            else:
                url_fuente = url

            return {
                "nombre": input_text,
                "usuario": input_text,
                "email": email or "No encontrado",
                "fuente_email": url_fuente if email else None,
                "telefono": telefono,
                "origen": origen,
                "url_perfil": url
            }

        except Exception as e:
            print(f"❌ Error accediendo a {url}: {e}")
            continue

    return {
        "nombre": input_text,
        "usuario": input_text,
        "email": "No encontrado",
        "fuente_email": None,
        "telefono": None,
        "origen": "no_encontrado",
        "url_perfil": None
    }
