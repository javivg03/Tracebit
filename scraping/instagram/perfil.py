from utils.busqueda_cruzada import buscar_contacto
from utils.validator import extraer_emails, extraer_telefonos
from services.user_agents import random_user_agent
from services.proxy_pool import ProxyPool
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from utils.normalizador import normalizar_datos_scraper
import instaloader

def scrapear_perfil_instagram_instaloader(username: str):
    logger.info(f"📅 Intentando scrapear perfil con Instaloader: {username}")

    user_agent = random_user_agent()
    logger.info(f"🕵️ User-Agent elegido: {user_agent}")

    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        logger.error("❌ No hay proxies disponibles para Instaloader.")
        return None

    logger.info(f"🧩 Proxy elegido para Instaloader: {proxy}")

    insta_loader = instaloader.Instaloader(user_agent=user_agent)
    insta_loader.context._session.proxies = {
        "http": proxy,
        "https": proxy
    }

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        logger.info("✅ Sesión de Instagram cargada")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo cargar la sesión: {e}")
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

        return normalizar_datos_scraper(
            nombre, username, email, email_fuente,
            telefono, seguidores, seguidos, hashtags, origen
        )

    except Exception as e:
        logger.error(f"❌ Error al obtener el perfil con Instaloader: {e}")
        return None

def scrapear_perfil_instagram_playwright(username: str, max_intentos: int = 1):
    logger.info(f"🔍 Intentando scraping de perfil con Playwright: {username}")

    for intento in range(max_intentos):
        logger.info(f"🔁 Intento {intento + 1}/{max_intentos} para acceder al perfil...")

        try:
            playwright, browser, context, proxy = iniciar_browser_con_proxy("state_instagram.json")
            logger.info(f"🧩 Proxy elegido: {proxy}")

            page = context.new_page()

            try:
                logger.info("🌐 Visitando perfil en Instagram...")
                page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
                page.wait_for_timeout(3000)

                logger.info("🔎 Buscando nombre de perfil...")
                nombre = page.locator("header h2, header h1").first.inner_text(timeout=3000)

                logger.info("📜 Extrayendo descripción de perfil (bio)...")
                bio = page.locator('meta[name="description"]').get_attribute("content") or ""

                logger.info("👥 Extrayendo número de seguidores y seguidos...")
                seguidores_text = page.locator("ul li:nth-child(2) span").first.get_attribute("title") or ""
                seguidos_text = page.locator("ul li:nth-child(3) span").first.inner_text() or ""

                try:
                    seguidores = int(seguidores_text.replace(",", "").replace(".", ""))
                except (ValueError, TypeError, AttributeError):
                    seguidores = None
                try:
                    seguidos = int(seguidos_text.replace(",", "").replace(".", ""))
                except (ValueError, TypeError, AttributeError):
                    seguidos = None

                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                email_fuente = "bio" if email else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None
                origen = "bio" if email else "no_email"

                logger.info("🪩 Cerrando navegador y devolviendo datos extraídos...")
                browser.close()
                playwright.stop()

                return normalizar_datos_scraper(
                    nombre, username, email, email_fuente,
                    telefono, seguidores, seguidos, hashtags, origen
                )

            except Exception as e:
                logger.error(f"❌ Fallo en navegación o extracción: {e}")
                browser.close()
                playwright.stop()
                continue

        except Exception as e:
            logger.error(f"❌ Error general al lanzar Playwright: {e}")
            continue

    logger.error("❌ Todos los intentos de acceso fallaron. No se pudo acceder al perfil.")
    return None

def obtener_datos_perfil_instagram_con_fallback(username: str) -> dict:
    logger.info(f"📅 Intentando scrapear perfil con Instaloader: {username}")
    datos = scrapear_perfil_instagram_instaloader(username)

    if datos and datos.get("email"):
        return datos

    logger.warning("⚠️ Instaloader falló o sin email. Probando con Playwright...")
    datos = scrapear_perfil_instagram_playwright(username)

    if datos and datos.get("email"):
        return datos

    logger.info("🔍 Lanzando búsqueda cruzada...")
    resultado_cruzado = buscar_contacto(username, datos.get("nombre") if datos else username)

    if resultado_cruzado:
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or username,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning("⚠️ No se encontró ningún dato en búsqueda cruzada.")
    return normalizar_datos_scraper(
        None, username, None, None, None, None, None, [], "error"
    )
