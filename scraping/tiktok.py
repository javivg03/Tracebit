from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from services.validator import extraer_emails, extraer_telefonos
from services.busqueda_cruzada import buscar_email

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

                # Obtener HTML completo (por si queremos más adelante scraping visual)
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Nombre del perfil
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else entrada

                # 📩 Email y ☎️ teléfono
                emails = extraer_emails(bio)
                email = emails[0] if emails else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                # 🏷️ Hashtags
                hashtags = []
                if bio:
                    hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

                if not email:
                    print("🔁 No se encontró email directo, probando búsqueda cruzada...")
                    resultado = buscar_email(entrada, nombre)
                    email = resultado["email"]
                    fuente_email = resultado["url_fuente"]
                    origen = resultado["origen"]
                else:
                    fuente_email = url
                    origen = "bio"

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
