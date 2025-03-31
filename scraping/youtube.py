from playwright.sync_api import sync_playwright
import re
from services.validator import validar_email, validar_telefono
from services.busqueda_cruzada import buscar_email  # Aquí podrías integrar más adelante la búsqueda de teléfonos

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

def scrape_youtube(username):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            url = f"https://www.youtube.com/@{username}/about"
            print(f"🌐 Navegando a {url}")
            page.goto(url, timeout=60000)

            # Aceptar cookies
            try:
                page.wait_for_timeout(3000)
                boton = page.locator("button:has-text('Aceptar todo')").first
                if boton.is_visible():
                    boton.click()
                    print("✅ Cookies aceptadas")
            except:
                print("(i) No se encontró el botón de cookies")

            page.wait_for_timeout(3000)

            # Extraer nombre del canal desde el título
            nombre = page.title().replace(" - YouTube", "")

            # Extraer bio/descripción
            descripcion = ""
            try:
                descripcion = page.locator("#description-container").inner_text()
            except:
                pass

            # Buscar email en la descripción
            email = None
            email_fuente = None
            matches_email = re.findall(EMAIL_REGEX, descripcion)
            for e in matches_email:
                if validar_email(e):
                    email = e
                    email_fuente = "bio"
                    break

            # Buscar teléfono en la descripción
            telefono = None
            matches_tel = re.findall(PHONE_REGEX, descripcion)
            if matches_tel:
                telefono = validar_telefono(matches_tel[0])

            # Si no hay email → búsqueda cruzada
            if not email:
                resultado = buscar_email(username, nombre)
                email = resultado["email"]
                email_fuente = resultado["url_fuente"]
                origen = resultado["origen"]
            else:
                origen = "bio"

            # Buscar enlaces externos (que no sean de YouTube)
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
