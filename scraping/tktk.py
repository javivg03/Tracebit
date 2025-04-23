from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

from utils.validator import extraer_emails, extraer_telefonos

async def scrape_tiktok(entrada):
    print(f"🚀 Iniciando scraping de TikTok con Playwright para: {entrada}")
    urls = [
        f"https://www.tiktok.com/@{entrada}",
        f"https://www.tiktok.com/search?q={quote_plus(entrada)}"
    ]
    resultado = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for url in urls:
            try:
                print(f"🌐 Visitando: {url}")
                await page.goto(url, timeout=15000)
                await page.wait_for_timeout(4000)

                # Intentar extraer la bio, si existe
                bio = ""
                try:
                    bio_element = page.locator('[data-e2e="user-bio"]')
                    await bio_element.wait_for(timeout=5000)
                    bio = await bio_element.inner_text()
                except PlaywrightTimeoutError:
                    bio = ""

                # Obtener el HTML y extraer el nombre usando BeautifulSoup
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else entrada

                # Extraer email y teléfono desde la bio
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                fuente_email = url if email else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                # Extraer hashtags (si los hay)
                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")] if bio else []

                origen = "bio" if email else "no_email"

                # Crear el diccionario de resultado
                resultado = {
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

                # Si se encuentra un email válido, se interrumpe el bucle
                if email:
                    print("✅ Email encontrado, terminando búsqueda en TikTok.")
                    break
            except Exception as e:
                print(f"⚠️ Error al procesar {url}: {e}")
                continue

        await browser.close()

    # Si no se obtuvo ningún resultado, se retorna un diccionario con error
    if resultado is None:
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
    return resultado
