from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
# from utils.playwright_tools import iniciar_browser_con_proxy
from services.validator import extraer_emails, extraer_telefonos
from services.busqueda_cruzada import buscar_contacto


def obtener_datos_perfil_tiktok(username: str) -> dict:
    print(f"🚀 Iniciando scraping de perfil TikTok para: {username}")

    urls = [
        f"https://www.tiktok.com/@{username}",
        f"https://www.tiktok.com/search?q={quote_plus(username)}"
    ]

    resultado = None

    try:
        # ⛔ Desactivado proxy temporalmente
        # playwright, browser, context, proxy = iniciar_browser_con_proxy()
        # print(f"🧩 Proxy elegido: {proxy}")

        # ✅ Modo sin proxy
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        for url in urls:
            try:
                print(f"🌐 Visitando: {url}")
                page.goto(url, timeout=20000)
                page.wait_for_timeout(3000)

                # Extraer bio
                try:
                    bio = page.locator('[data-e2e="user-bio"]').first.inner_text(timeout=3000)
                except PlaywrightTimeout:
                    bio = ""

                # Extraer nombre
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else username

                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                fuente_email = url if email else None
                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None
                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
                origen = "bio" if email else "no_email"

                resultado = {
                    "nombre": nombre,
                    "usuario": username,
                    "email": email,
                    "fuente_email": fuente_email,
                    "telefono": telefono,
                    "seguidores": None,
                    "seguidos": None,
                    "hashtags": hashtags,
                    "origen": origen
                }

                if email:
                    print("✅ Email encontrado, saliendo del bucle de URLs.")
                    break

            except Exception as e:
                print(f"⚠️ Error al procesar {url}: {e}")
                continue

        browser.close()
        playwright.stop()

    except Exception as e:
        print(f"❌ Error general durante scraping de TikTok: {e}")
        resultado = None

    if resultado and resultado.get("email"):
        return resultado

    return fallback_tiktok(username, resultado.get("nombre") if resultado else None)


def fallback_tiktok(username: str, nombre: str = None) -> dict:
    print("🔍 Lanzando búsqueda cruzada...")
    resultado = buscar_contacto(username, nombre or username)

    if resultado:
        return {
            "nombre": resultado.get("nombre") or username,
            "usuario": username,
            "email": resultado.get("email"),
            "telefono": resultado.get("telefono"),
            "fuente_email": resultado.get("url_fuente"),
            "seguidores": None,
            "seguidos": None,
            "hashtags": [],
            "origen": f"búsqueda cruzada ({resultado.get('origen')})"
        }

    return {
        "nombre": None,
        "usuario": username,
        "email": None,
        "fuente_email": None,
        "telefono": None,
        "seguidores": None,
        "seguidos": None,
        "hashtags": [],
        "origen": "error"
    }
