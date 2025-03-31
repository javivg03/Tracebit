from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from services.validator import extraer_emails, extraer_telefonos

def scrape_tiktok(entrada):
    print(f"🚀 Iniciando scraping de TikTok con Playwright para: {entrada}")
    urls = [
        f"https://www.tiktok.com/@{entrada}",
        f"https://www.tiktok.com/search?q={quote_plus(entrada)}"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for url in urls:
            try:
                print(f"🌐 Visitando: {url}")
                page.goto(url, timeout=15000)
                page.wait_for_timeout(4000)

                # Bio (si existe)
                try:
                    bio_element = page.locator('[data-e2e="user-bio"]')
                    bio_element.wait_for(timeout=5000)
                    bio = bio_element.inner_text()
                except PlaywrightTimeoutError:
                    bio = ""

                # HTML y nombre
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else entrada

                # 📩 Email y ☎️ Teléfono
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                fuente_email = url if email else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                # Hashtags
                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")] if bio else []

                origen = "bio" if email else "no_email"

                browser.close()
                return {
                    "nombre": nombre,
                    "usuario": entrada,
                    "email": email,
                    "fuente_email": fuente_email,
                    "telefono": telefono,
                    "seguidores": None,
                    "seguidos": None,
                    "hashtags": hashtags,
                    "origen": origen
                }

            except Exception as e:
                print(f"⚠️ Error al procesar {url}: {e}")
                continue

        browser.close()

    return {
        "nombre": None,
        "usuario": entrada,
        "email": None,
        "fuente_email": None,
        "telefono": None,
        "seguidores": None,
        "seguidos": None,
        "hashtags": [],
        "origen": "error"
    }
