import instaloader
import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from utils.validator import extraer_emails, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from services.user_agents import random_user_agent
from services.proxy_format import formatear_proxy_requests
from services.proxy_pool import ProxyPool
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger


def scrapear_perfil_instagram_instaloader(username: str, forzar_solo_bio: bool = False):
    logger.info(f"📅 Intentando scrapear perfil con Instaloader: {username}")
    user_agent = random_user_agent()
    logger.info(f"🕵️ User-Agent elegido: {user_agent}")

    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        logger.error("❌ No hay proxies disponibles para Instaloader.")
        return None

    logger.info(f"🧩 Proxy elegido para Instaloader: {proxy}")
    proxy_url = formatear_proxy_requests(proxy)

    insta_loader = instaloader.Instaloader(user_agent=user_agent)
    insta_loader.context._session.proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    try:
        insta_loader.load_session_from_file("pruebasrc1")
        logger.info("✅ Sesión de Instagram cargada")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo cargar la sesión (no se elimina proxy): {e}")

    try:
        profile = instaloader.Profile.from_username(insta_loader.context, username)
        nombre = profile.full_name
        bio = profile.biography or ""
        hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
        emails = extraer_emails(bio)
        email = emails[0] if emails else None
        email_fuente = "bio" if email else None
        telefonos = extraer_telefonos(bio)
        telefono = telefonos[0] if telefonos else None
        seguidores = profile.followers if not forzar_solo_bio else None
        seguidos = profile.followees if not forzar_solo_bio else None
        origen = "bio" if email or telefono else "no_email"

        return normalizar_datos_scraper(
            nombre, username, email, email_fuente,
            telefono, seguidores, seguidos, hashtags, origen
        )

    except Exception as e:
        logger.error(f"❌ Error al obtener el perfil con Instaloader: {e}")
        pool.reportar_bloqueo(proxy, "instagram")
        return None


def convertir_numero(texto):
    texto = texto.replace(",", "").replace(".", "")
    if "M" in texto:
        return int(float(texto.replace("M", "")) * 1_000_000)
    elif "K" in texto:
        return int(float(texto.replace("K", "")) * 1_000)
    else:
        try:
            return int(texto)
        except:
            return None


def scrapear_perfil_instagram_playwright(username: str, max_intentos: int = 1, forzar_solo_bio: bool = False):
    logger.info(f"🔍 Intentando scraping de perfil con Playwright: {username}")

    for intento in range(max_intentos):
        logger.info(f"🔁 Intento {intento + 1}/{max_intentos} para acceder al perfil...")

        try:
            user_agent = random_user_agent()
            playwright, browser, _, proxy = iniciar_browser_con_proxy()
            context = browser.new_context(
                storage_state="state_instagram.json",
                user_agent=user_agent
            )
            page = context.new_page()

            try:
                logger.info("🌐 Visitando perfil en Instagram con proxy...")
                page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
                page.wait_for_timeout(3000)
            except PlaywrightTimeoutError:
                logger.warning("❌ Timeout: página no cargó correctamente, se marcará proxy como bloqueado")
                ProxyPool().reportar_bloqueo(proxy, "instagram")
                try:
                    browser.close()
                    playwright.stop()
                except:
                    pass
                continue

            try:
                logger.info("🔎 Extrayendo datos del perfil...")
                nombre_raw = page.locator('meta[property="og:title"]').get_attribute("content")
                nombre = nombre_raw.split("(@")[0].strip() if nombre_raw else "Sin nombre"

                bio = page.locator('meta[name="description"]').get_attribute("content") or ""
                if not bio:
                    bio = page.locator('meta[property="og:description"]').get_attribute("content") or ""

                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
                emails = extraer_emails(bio)
                email = emails[0] if emails else None
                email_fuente = "bio" if email else None
                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None
                origen = "bio" if email or telefono else "no_email"

                seguidores = None
                seguidos = None
                if not forzar_solo_bio:
                    match = re.search(r"(\d[\d.,MK]*) seguidores", bio)
                    if match:
                        seguidores = convertir_numero(match.group(1))
                    match = re.search(r"(\d[\d.,MK]*) siguiendo", bio)
                    if match:
                        seguidos = convertir_numero(match.group(1))

                logger.info("🪩 Cerrando navegador y devolviendo datos...")
                browser.close()
                playwright.stop()

                return normalizar_datos_scraper(
                    nombre, username, email, email_fuente,
                    telefono, seguidores, seguidos, hashtags, origen
                )

            except Exception as e:
                logger.error(f"❌ Fallo en extracción de datos: {e}")
                browser.close()
                playwright.stop()
                continue

        except Exception as e:
            logger.error(f"❌ Error general al lanzar Playwright: {e}")
            continue

    logger.error("❌ Todos los intentos fallaron. No se pudo acceder al perfil.")
    return None


def obtener_datos_perfil_instagram_con_fallback(username: str, forzar_solo_bio: bool = False, habilitar_busqueda_web: bool = False) -> dict:
    logger.info(f"🚀 Iniciando scraping de perfil de Instagram para: {username}")

    datos = scrapear_perfil_instagram_instaloader(username, forzar_solo_bio=forzar_solo_bio)
    if datos and (datos.get("email") or datos.get("telefono")):
        return datos

    logger.warning("⚠️ Instaloader falló o sin datos. Probando con Playwright...")
    datos = scrapear_perfil_instagram_playwright(username, forzar_solo_bio=forzar_solo_bio)
    if datos and (datos.get("email") or datos.get("telefono")):
        return datos

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    logger.warning("⚠️ Playwright también falló o no encontró datos. Lanzando búsqueda cruzada web...")
    resultado_cruzado = buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="instagram",
        habilitar_busqueda_web=True
    )

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

    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")
