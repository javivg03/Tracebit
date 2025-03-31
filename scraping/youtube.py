from playwright.sync_api import sync_playwright
from services.validator import extraer_emails, extraer_telefonos
from services.busqueda_cruzada import buscar_email

def scrape_youtube(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            url = f"https://www.youtube.com/@{username}/about"
            print(f"🌐 Navegando a {url}")
            page.goto(url, timeout=60000)

            # Aceptar cookies si aparecen
            try:
                page.wait_for_timeout(3000)
                boton = page.locator("button:has-text('Aceptar todo')").first
                if boton.is_visible():
                    boton.click()
                    print("✅ Cookies aceptadas")
            except:
                print("(i) No se encontró el botón de cookies")

            page.wait_for_timeout(3000)

            # Título de la página como nombre del canal
            nombre = page.title().replace(" - YouTube", "")

            # Descripción del canal (bio)
            try:
                descripcion = page.locator("#description-container").inner_text()
            except:
                descripcion = ""

            # 📩 Email y ☎️ Teléfono
            emails = extraer_emails(descripcion)
            email = emails[0] if emails else None
            email_fuente = "bio" if email else None

            telefonos = extraer_telefonos(descripcion)
            telefono = telefonos[0] if telefonos else None

            # 🔁 Búsqueda cruzada si no se encuentra email
            if not email:
                resultado = buscar_email(username, nombre)
                email = resultado["email"]
                email_fuente = resultado["url_fuente"]
                origen = resultado["origen"]
            else:
                origen = "bio"

            # 🌐 Extraer enlaces externos que no sean de YouTube
            enlaces = []
            try:
                links = page.locator("a[href^='http']").all()
                for link in links:
                    href = link.get_attribute("href")
                    if href and "youtube.com" not in href:
                        enlaces.append(href)
            except:
                pass

            return {
                "nombre": nombre,
                "usuario": username,
                "email": email,
                "fuente_email": email_fuente,
                "telefono": telefono,
                "enlaces_web": enlaces,
                "origen": origen
            }

        finally:
            page.close()
            context.close()
            browser.close()
