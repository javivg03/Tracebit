import requests
from bs4 import BeautifulSoup

from services.validator import extraer_emails, extraer_telefonos
from services.busqueda_cruzada import buscar_email

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

    # 🔁 Si no hay email, buscar por nombre real
    origen = "bio"
    if not email:
        nombre_completo = title.text.strip() if title else None
        resultado = buscar_email(channel_username, nombre_completo)
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
