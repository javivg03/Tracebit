import requests
from bs4 import BeautifulSoup

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

    return {
        "username": channel_username,
        "nombre": title.text.strip() if title else "N/A",
        "descripcion": description.text.strip() if description else "N/A",
        "suscriptores": subs.text.strip() if subs else "N/A"
    }
