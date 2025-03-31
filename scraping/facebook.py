from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from services.validator import extraer_emails, extraer_telefonos

def scrape_facebook(username_o_nombre):
    print(f"🚀 Iniciando scraping de Facebook con Playwright para: {username_o_nombre}")

    urls = [
        f"https://www.facebook.com/{username_o_nombre}",
        f"https://www.facebook.com/public?q={quote_plus(username_o_nombre)}"
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for url in urls:
            try:
                print(f"🌐 Visitando: {url}")
                page.goto(url, timeout=15000)
                page.wait_for_timeout(5000)

                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator=" ", strip=True)

                # 📩 Extraer email y ☎️ teléfono
                emails = extraer_emails(text)
                telefonos = extraer_telefonos(text)

                if emails:
                    email_valido = emails[0]
                    telefono_valido = telefonos[0] if telefonos else None

                    browser.close()
                    return {
                        "nombre": username_o_nombre,
                        "usuario": username_o_nombre,
                        "email": email_valido,
                        "fuente_email": url,
                        "telefono": telefono_valido,
                        "origen": "facebook"
                    }

            except Exception as e:
                print(f"⚠️ Error en URL: {url} → {e}")
                continue

        browser.close()

    # ❌ No se encontró email directo → se devuelve sin email y luego lo maneja `buscar_email`
    return {
        "nombre": username_o_nombre,
        "usuario": username_o_nombre,
        "email": None,
        "fuente_email": None,
        "telefono": None,
        "origen": "no_email"
    }
