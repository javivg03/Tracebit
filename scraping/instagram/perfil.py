from services.busqueda_cruzada import buscar_contacto
from services.validator import extraer_emails, extraer_telefonos
from utils.user_agents import random_user_agent
from utils.proxy_pool import ProxyPool
from utils.playwright_tools import iniciar_browser_con_proxy
import instaloader

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
    # ⚠️ Acceso a _session porque Instaloader no permite configurar proxies de otra forma
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


def scrapear_perfil_instagram_playwright(username: str, max_intentos: int = 5):
    print(f"🔍 Intentando scraping de perfil con Playwright: {username}")

    for intento in range(max_intentos):
        print(f"🔁 Intento {intento+1}/{max_intentos} para acceder al perfil...")

        try:
            playwright, browser, context, proxy = iniciar_browser_con_proxy("state_instagram.json")
            print(f"🧩 Proxy elegido: {proxy}")

            page = context.new_page()

            try:
                page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
                page.wait_for_timeout(3000)

                nombre = page.locator("header h2, header h1").first.inner_text(timeout=3000)
                bio = page.locator("section div.-vDIg span").first.inner_text(timeout=3000)

                seguidores_text = page.locator("ul li:nth-child(2) span").first.get_attribute("title")
                seguidos_text = page.locator("ul li:nth-child(3) span").first.inner_text()

                try:
                    seguidores = int(seguidores_text.replace(",", "").replace(".", ""))
                except (ValueError, TypeError):
                    seguidores = None
                try:
                    seguidos = int(seguidos_text.replace(",", "").replace(".", ""))
                except (ValueError, TypeError):
                    seguidos = None

                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                email_fuente = "bio" if email else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None
                origen = "bio" if email else "no_email"

                browser.close()
                playwright.stop()

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
                print(f"❌ Fallo en navegación o extracción: {e}")
                browser.close()
                playwright.stop()
                continue  # Probar con otro proxy

        except Exception as e:
            print(f"❌ Error general al lanzar Playwright: {e}")
            continue  # Probar con otro proxy

    print("❌ Todos los intentos de acceso fallaron con los proxies disponibles.")
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
