import requests
from bs4 import BeautifulSoup

from utils.validator import extraer_emails, extraer_telefonos

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

    raw_text = soup.get_text(separator=" ", strip=True)

    # 📩 Email y ☎️ Teléfono
    emails = extraer_emails(raw_text)
    email = emails[0] if emails else None
    email_fuente = "bio" if email else None

    telefonos = extraer_telefonos(raw_text)
    telefono = telefonos[0] if telefonos else None

    origen = "bio" if email else "no_email"

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
