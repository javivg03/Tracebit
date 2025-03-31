import requests
import re
from bs4 import BeautifulSoup
from services.validator import validar_email, validar_telefono
from services.busqueda_cruzada import buscar_email

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

def scrape_telegram(channel_username):
    url = f"https://t.me/s/{channel_username}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception("No se pudo acceder al canal público.")

    soup = BeautifulSoup(res.text, "html.parser")

    title = soup.select_one(".tgme_channel_info_header_title")
    description = soup.select_one(".tgme_channel_info_description")
    subs = soup.select_one(".tgme_channel_info_counter")

    raw_text = soup.get_text()

    # Buscar email
    emails = list({e for e in re.findall(EMAIL_REGEX, raw_text) if validar_email(e)})
    email = emails[0] if emails else None
    email_fuente = "bio" if email else None

    # Buscar teléfono
    phones = list({t for t in re.findall(PHONE_REGEX, raw_text) if validar_telefono(t)})
    telefono = phones[0] if phones else None

    origen = "bio"

    # Búsqueda cruzada si no hay email
    if not email:
        resultado = buscar_email(channel_username, title.text.strip() if title else None)
        email = resultado["email"]
        email_fuente = resultado["url_fuente"]
        origen = resultado["origen"]

    return {
        "username": channel_username,
        "nombre": title.text.strip() if title else "N/A",
        "descripcion": description.text.strip() if description else "N/A",
        "suscriptores": subs.text.strip() if subs else "N/A",
        "email": email,
        "fuente_email": email_fuente,
        "telefono": telefono,
        "origen": origen
    }