from services.busqueda_cruzada import buscar_contacto
from services.validator import extraer_emails, extraer_telefonos
from utils.user_agents import random_user_agent
import instaloader
from playwright.sync_api import sync_playwright
# from utils.proxy_pool import ProxyPool

# ⚠️ Proxies desactivados temporalmente para pruebas locales

def scrapear_perfil_instagram_instaloader(username: str):
    print(f"📅 Intentando scrapear perfil con Instaloader: {username}")

    user_agent = random_user_agent()
    print(f"🕵️ User-Agent elegido: {user_agent}")

    # proxy = None  # Desactivamos proxies
    # print("❌ No hay proxies disponibles para Instaloader.")
    # return None

    insta_loader = instaloader.Instaloader(user_agent=user_agent)

    # ❌ No usar proxy:
    # insta_loader.context._session.proxies = {
    #     "http": proxy,
    #     "https": proxy
    # }

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        print("✅ Sesión de Instagram cargada")
    except Exception as e:
        print(f"⚠️ No se pudo cargar la sesión: {e}")
        # pool.remove_proxy(proxy)

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


from playwright.sync_api import sync_playwright

def scrapear_perfil_instagram_playwright(username: str, max_intentos: int = 1):
    print(f"🔍 [Playwright] Intentando scraping de perfil: {username}", flush=True)

    for intento in range(max_intentos):
        print(f"🔁 Intento {intento+1}/{max_intentos}", flush=True)

        try:
            print("🚀 Lanzando Playwright...", flush=True)
            with sync_playwright() as playwright:
                print("✅ Playwright lanzado", flush=True)

                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(storage_state="state_instagram.json")
                page = context.new_page()

                print("🌐 Navegando a la URL del perfil...", flush=True)
                page.goto(f"https://www.instagram.com/{username}/", timeout=20000)
                print("✅ Página cargada correctamente", flush=True)

                page.wait_for_timeout(2000)

                print("🔍 Intentando localizar nombre", flush=True)
                nombre = page.locator("header h2, header h1").first.inner_text(timeout=3000)
                print(f"🧾 Nombre: {nombre}", flush=True)

                print("🔍 Intentando localizar bio", flush=True)
                bio = page.locator('span._ap3a').first.inner_text(timeout=3000)
                print(f"📜 Bio: {bio[:60]}...", flush=True)

                print("🧹 Cerrando navegador (automáticamente con 'with')", flush=True)

                return {
                    "nombre": nombre,
                    "usuario": username,
                    "email": None,
                    "fuente_email": None,
                    "telefono": None,
                    "seguidores": None,
                    "seguidos": None,
                    "hashtags": [],
                    "origen": "playwright"
                }

        except Exception as e:
            print(f"❌ Excepción en intento {intento+1}: {e}", flush=True)

    print("❌ Todos los intentos fallaron", flush=True)
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
