from playwright.sync_api import sync_playwright, TimeoutError
from services.validator import extraer_emails, extraer_telefonos
from services.busqueda_cruzada import buscar_email


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
            page.wait_for_timeout(3000)

            # Nombre del perfil
            nombre_element = page.locator("div[data-testid='UserName'] span").first
            nombre = nombre_element.inner_text() if nombre_element.is_visible() else username

            # Bio
            bio_element = page.locator("div[data-testid='UserDescription']")
            bio = bio_element.inner_text() if bio_element.count() > 0 else ""

            # 📩 Email y ☎️ Teléfono
            emails = extraer_emails(bio)
            email = emails[0] if emails else None
            email_fuente = "bio" if email else None

            telefonos = extraer_telefonos(bio)
            telefono = telefonos[0] if telefonos else None

            # 🔁 Búsqueda cruzada si no se encontró email
            if not email:
                print("🔁 Email no encontrado en bio. Buscando externamente...")
                resultado = buscar_email(username, nombre)
                email = resultado["email"]
                email_fuente = resultado["url_fuente"]
                origen = resultado["origen"]
            else:
                origen = "bio"

            return {
                "nombre": nombre,
                "usuario": username,
                "bio": bio,
                "email": email or "No encontrado",
                "fuente_email": email_fuente if email else None,
                "telefono": telefono,
                "origen": origen
            }

        except TimeoutError:
            print("❌ Timeout al acceder al perfil.")
            return None
        except Exception as e:
            print("❌ Error general:", str(e))
            return None
        finally:
            page.close()
            context.close()
            browser.close()
