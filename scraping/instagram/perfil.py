from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from services.busqueda_cruzada import buscar_contacto
from services.validator import extraer_emails, extraer_telefonos
from utils.user_agents import random_user_agent
from services import history
from exports.exporter import export_to_excel
import instaloader
from utils.proxy_pool import ProxyPool

def scrapear_perfil_instagram_instaloader(username: str):
    print(f"📅 Intentando scrapear perfil con Instaloader: {username}")

    user_agent = random_user_agent()
    print(f"🕵️ User-Agent elegido: {user_agent}")

    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        print("❌ No hay proxies disponibles para Instaloader.")
        return None

    print(f"🧩 Proxy elegido para Instaloader: {proxy}")

    insta_loader = instaloader.Instaloader(user_agent=user_agent)
    insta_loader.context._session.proxies = {
        "http": proxy,
        "https": proxy
    }

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        print("✅ Sesión de Instagram cargada")
    except Exception as e:
        print(f"⚠️ No se pudo cargar la sesión: {e}")
        pool.remove_proxy(proxy)

    try:
        profile = instaloader.Profile.from_username(insta_loader.context, username)

        nombre = profile.full_name
        bio = profile.biography or ""
        seguidores = profile.followers
        seguidos = profile.followees
        hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

        emails = extraer_emails(bio)
        email = emails[0] if emails else None
        email_fuente = "bio" if email else None

        telefonos = extraer_telefonos(bio)
        telefono = telefonos[0] if telefonos else None

        origen = "bio" if email else "no_email"

        datos = {
            "nombre": nombre,
            "usuario": username,
            "email": email,
            "fuente_email": email_fuente,
            "telefono": telefono,
            "seguidores": seguidores,
            "seguidos": seguidos,
            "hashtags": hashtags,
            "origen": origen
        }

        return datos

    except Exception as e:
        print(f"❌ Error al obtener el perfil con Instaloader: {e}")
        return None

def scrapear_perfil_instagram_playwright(username: str):
    print(f"🔍 Intentando scraping de perfil con Playwright: {username}")
    pool = ProxyPool()
    proxy = pool.get_random_proxy()
    print(f"🧩 Proxy elegido: {proxy}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                proxy={"server": proxy}
            )
            context = browser.new_context(storage_state="state_instagram.json")
            page = context.new_page()

            page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            page.wait_for_timeout(3000)

            nombre = page.locator("header h2, header h1").first.inner_text(timeout=3000)
            bio = page.locator("section div.-vDIg span").first.inner_text(timeout=3000)

            seguidores_text = page.locator("ul li:nth-child(2) span").first.get_attribute("title")
            seguidos_text = page.locator("ul li:nth-child(3) span").first.inner_text()

            try:
                seguidores = int(seguidores_text.replace(",", "").replace(".", ""))
            except:
                seguidores = None
            try:
                seguidos = int(seguidos_text.replace(",", "").replace(".", ""))
            except:
                seguidos = None

            hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
            emails = extraer_emails(bio)
            email = emails[0] if emails else None
            email_fuente = "bio" if email else None

            telefonos = extraer_telefonos(bio)
            telefono = telefonos[0] if telefonos else None
            origen = "bio" if email else "no_email"

            browser.close()

            return {
                "nombre": nombre,
                "usuario": username,
                "email": email,
                "fuente_email": email_fuente,
                "telefono": telefono,
                "seguidores": seguidores,
                "seguidos": seguidos,
                "hashtags": hashtags,
                "origen": origen
            }

    except Exception as e:
        print(f"❌ Error al obtener el perfil con Playwright: {e}")
        return None

def obtener_datos_perfil_instagram_con_fallback(username: str) -> dict:
    print(f"📅 Intentando scrapear perfil con Instaloader: {username}")
    datos = scrapear_perfil_instagram_instaloader(username)

    if datos and datos.get("email"):
        return datos

    print("⚠️ Instaloader falló o sin email. Probando con Playwright...")
    datos = scrapear_perfil_instagram_playwright(username)

    if datos and datos.get("email"):
        return datos

    print("🔍 Lanzando búsqueda cruzada...")
    resultado_cruzado = buscar_contacto(username, datos.get("nombre") if datos else username)

    if resultado_cruzado:
        return {
            "nombre": resultado_cruzado.get("nombre") or username,
            "usuario": username,
            "email": resultado_cruzado.get("email"),
            "telefono": resultado_cruzado.get("telefono"),
            "fuente_email": resultado_cruzado.get("url_fuente"),
            "seguidores": None,
            "seguidos": None,
            "hashtags": [],
            "origen": f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        }

    print("⚠️ No se encontró ningún dato en búsqueda cruzada.")
    return {
        "nombre": None,
        "usuario": username,
        "email": None,
        "telefono": None,
        "fuente_email": None,
        "seguidores": None,
        "seguidos": None,
        "hashtags": [],
        "origen": "error"
    }
