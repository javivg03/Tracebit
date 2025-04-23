from playwright.async_api import async_playwright
from utils.validator import extraer_emails, extraer_telefonos

async def scrape_youtube(username):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            url = f"https://www.youtube.com/@{username}/about"
            print(f"🌐 Navegando a {url}")
            await page.goto(url, timeout=60000)

            # Aceptar cookies si aparecen
            try:
                await page.wait_for_timeout(3000)
                boton = await page.query_selector("button:has-text('Aceptar todo')")
                if boton and await boton.is_visible():
                    await boton.click()
                    print("✅ Cookies aceptadas")
            except Exception as e:
                print(f"(i) No se encontró botón de cookies o fallo: {e}")

            await page.wait_for_timeout(3000)

            nombre = (await page.title()).replace(" - YouTube", "")

            # Descripción del canal
            try:
                desc_elem = await page.query_selector("#description-container")
                descripcion = await desc_elem.inner_text() if desc_elem else ""
            except:
                descripcion = ""

            # 📩 Email y ☎️ Teléfono
            emails = extraer_emails(descripcion)
            email = emails[0] if emails else None
            email_fuente = url if email else None

            telefonos = extraer_telefonos(descripcion)
            telefono = telefonos[0] if telefonos else None

            origen = "bio" if email else "no_email"

            # 🌐 Extraer enlaces externos
            enlaces = []
            try:
                links = await page.query_selector_all("a[href^='http']")
                for link in links:
                    href = await link.get_attribute("href")
                    if href and "youtube.com" not in href:
                        enlaces.append(str(href))
            except:
                pass

            return {
                "nombre": str(nombre),
                "usuario": str(username),
                "email": str(email) if email else None,
                "fuente_email": str(email_fuente) if email_fuente else None,
                "telefono": str(telefono) if telefono else None,
                "enlaces_web": enlaces,
                "origen": str(origen)
            }

        finally:
            await page.close()
            await context.close()
            await browser.close()
