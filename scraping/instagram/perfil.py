from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool
from services.user_agents import random_user_agent


async def obtener_datos_perfil_instagram(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("instagram")

    try:
        user_agent = random_user_agent()
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_instagram.json")

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para Instagram.")
            return None

        page = await context.new_page()
        logger.info(f"🌐 Visitando perfil: https://www.instagram.com/{username}/")

        try:
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            logger.warning("❌ Timeout al cargar el perfil. Proxy marcado como bloqueado.")
            ProxyPool().reportar_bloqueo(proxy, "instagram")
            await browser.close()
            await playwright.stop()
            return None

        logger.info("🔍 Extrayendo datos del perfil...")

        nombre_raw = await page.locator('meta[property="og:title"]').get_attribute("content")
        nombre = nombre_raw.split("(@")[0].strip() if nombre_raw else username

        bio = await page.locator('meta[name="description"]').get_attribute("content") or ""
        if not bio:
            bio = await page.locator('meta[property="og:description"]').get_attribute("content") or ""

        emails = extraer_emails_validos(bio)
        telefonos = extraer_telefonos(bio)

        email = emails[0] if emails else None
        telefono = telefonos[0] if telefonos else None
        origen = construir_origen("Instagram", email, telefono)

        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

        if email or telefono:
            logger.info(f"✅ Contacto encontrado en Instagram: {username}")
            return normalizar_datos_scraper(
                nombre=nombre,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=origen
            )

    except Exception as e:
        logger.error(f"❌ Error general en scraping de Instagram: {e}")

    logger.info(f"🔁 No se encontraron datos en Instagram para {username}")
    return None
