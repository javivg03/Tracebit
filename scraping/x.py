from playwright.sync_api import sync_playwright
import re
from services.validator import validar_email, validar_telefono
from services.busqueda_cruzada import buscar_email

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d[\d\s().-]{7,}"

def scrape_x(username):
    print(f"🚀 Iniciando scraping de X para: {username}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            url = f"https://twitter.com/{username}"
            print(f"🌐 Navegando a {url}")
            page.goto(url, timeout=60000)
            print("⏳ Esperando que cargue el perfil...")
            page.wait_for_timeout(3000)

            # Extraer nombre
            nombre = page.locator("div[data-testid='UserName'] span").first
            nombre_texto = nombre.inner_text() if nombre.is_visible() else "No encontrado"
            print(f"✅ Nombre detectado: {nombre_texto}")

            # Extraer bio
            bio_locator = page.locator("div[data-testid='UserDescription']")
            bio = bio_locator.inner_text() if bio_locator.count() > 0 else ""
            print(f"🔍 Bio: {bio or 'No encontrada'}")

            # Email
            matches = re.findall(EMAIL_REGEX, bio)
            email = None
            for e in matches:
                if validar_email(e):
                    email = e
                    email_fuente = "bio"
                    break

            # Teléfono
            matches_tel = re.findall(PHONE_REGEX, bio)
            telefono = None
            for tel in matches_tel:
                if validar_telefono(tel):
                    telefono = tel
                    break

            # Si no hay email, buscar externamente
            if not email:
                resultado = buscar_email(username, nombre_texto)
                email = resultado["email"]
                email_fuente = resultado["url_fuente"]
                origen = resultado["origen"]
            else:
                origen = "bio"

            return {
                "nombre": nombre_texto,
                "usuario": username,
                "bio": bio,
                "email": email or "No encontrado",
                "fuente_email": email_fuente if email else None,
                "telefono": telefono,
                "origen": origen
            }

        except Exception as e:
            print("❌ Error en scraping:", str(e))
            return None

        finally:
            page.close()
            context.close()
            browser.close()