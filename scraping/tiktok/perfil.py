from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from utils.busqueda_username import buscar_perfiles_por_username
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from services.user_agents import random_user_agent

async def obtener_datos_perfil_tiktok(
    username: str,
    habilitar_busqueda_web: bool = False,
    redes_visitadas: set[str] = None
) -> dict:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("tiktok")

    urls = [
        f"https://www.tiktok.com/@{username}",
        f"https://www.tiktok.com/search?q={quote_plus(username)}"
    ]

    nombre = username
    email = None
    telefono = None
    hashtags = []

    try:
        user_agent = random_user_agent()
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_tiktok.json")

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para TikTok.")
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")

        page = await context.new_page()

        for url in urls:
            try:
                logger.info(f"🌐 Visitando: {url}")
                await page.goto(url, timeout=20000)
                await page.wait_for_timeout(3000)

                try:
                    bio = await page.locator('[data-e2e="user-bio"]').first.inner_text(timeout=3000)
                except PlaywrightTimeout:
                    bio = ""
                except Exception:
                    bio = ""

                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                nombre_tag = soup.find("h2")
                nombre = nombre_tag.get_text(strip=True) if nombre_tag else username

                emails = extraer_emails_validos(bio)
                email = emails[0] if emails else None

                telefonos = extraer_telefonos(bio)
                telefono = telefonos[0] if telefonos else None

                hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]

                if email or telefono:
                    break

            except Exception as e:
                logger.warning(f"⚠️ Error al procesar {url}: {e}")
                continue

        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

        if email or telefono:
            logger.info("✅ Email o teléfono encontrado en TikTok.")
            return normalizar_datos_scraper(
                nombre, username, email, url if email else None,
                telefono, None, None, hashtags, "bio"
            )

    except PlaywrightTimeout:
        logger.warning("❌ Timeout al cargar TikTok. Proxy marcado como bloqueado.")
        ProxyPool().reportar_bloqueo(proxy, "tiktok")
    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de TikTok: {e}")
        email = None
        telefono = None

    if not email and not telefono:
        logger.info("🔁 No se encontraron datos en TikTok. Buscando en otras redes por username...")
        resultado_multired = await buscar_perfiles_por_username(username, excluir=["tiktok"], redes_visitadas=redes_visitadas)
        if resultado_multired:
            return resultado_multired

    logger.warning("⚠️ Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=nombre,
        origen_actual="tiktok",
        habilitar_busqueda_web=True
    )

    if resultado_cruzado:
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or nombre,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_resultado")
