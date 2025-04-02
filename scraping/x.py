from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from services.validator import extraer_emails, extraer_telefonos

async def scrape_x(username):
    print(f"🚀 Iniciando scraping de X para: {username}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            url = f"https://twitter.com/{username}"
            print(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)

            # Nombre del perfil
            nombre_locator = page.locator("div[data-testid='UserName'] span").first
            nombre = username  # Valor por defecto
            if await nombre_locator.is_visible():
                nombre = await nombre_locator.inner_text()

            # Bio
            bio_locator = page.locator("div[data-testid='UserDescription']")
            bio = ""
            if await bio_locator.count() > 0:
                bio = await bio_locator.inner_text()

            # 📩 Email y ☎️ Teléfono
            emails = extraer_emails(bio)
            email = emails[0] if emails else None
            email_fuente = url if email else None

            telefonos = extraer_telefonos(bio)
            telefono = telefonos[0] if telefonos else None

            origen = "bio" if email else "no_email"

            return {
                "nombre": nombre,
                "usuario": username,
                "bio": bio,
                "email": email,
                "fuente_email": email_fuente,
                "telefono": telefono,
                "origen": origen
            }

        except PlaywrightTimeoutError:
            print("❌ Timeout al acceder al perfil.")
            return {
                "nombre": None,
                "usuario": username,
                "bio": "",
                "email": None,
                "fuente_email": None,
                "telefono": None,
                "origen": "timeout"
            }

        except Exception as e:
            print("❌ Error general:", str(e))
            return {
                "nombre": None,
                "usuario": username,
                "bio": "",
                "email": None,
                "fuente_email": None,
                "telefono": None,
                "origen": "error"
            }

        finally:
            await page.close()
            await context.close()
            await browser.close()
