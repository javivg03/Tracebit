from playwright.async_api import TimeoutError as PlaywrightTimeout
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper, construir_origen
from urllib.parse import quote_plus

async def obtener_datos_perfil_facebook(
    username: str,
    redes_visitadas: set[str] = None
) -> dict | None:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("facebook")

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_facebook.json")

        if not context:
            logger.error("❌ No se pudo iniciar navegador con proxy para Facebook.")
            return None

        page = await context.new_page()
        search_url = f"https://www.facebook.com/search/top/?q={quote_plus(username)}"

        try:
            logger.info(f"🌍 Accediendo a resultados de búsqueda: {search_url}")
            await page.goto(search_url, timeout=20000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            logger.warning("⏱️ Timeout en búsqueda general.")
            ProxyPool().reportar_bloqueo(proxy, "facebook")
            await browser.close()
            await playwright.stop()
            return None

        perfil_encontrado = await page.locator('a[href*="facebook.com/"]').nth(0).get_attribute("href")
        if not perfil_encontrado:
            logger.warning("⚠️ No se encontró un perfil válido.")
            await browser.close()
            await playwright.stop()
            return None

        perfil_url = perfil_encontrado if perfil_encontrado.startswith("http") else f"https://www.facebook.com{perfil_encontrado}"
        logger.info(f"➡️ Navegando al perfil: {perfil_url}")

        try:
            await page.goto(perfil_url, timeout=20000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            logger.warning("⏱️ Timeout accediendo al perfil.")
            ProxyPool().reportar_bloqueo(proxy, "facebook")
            await browser.close()
            await playwright.stop()
            return None

        logger.info("🔎 Extrayendo contenido...")
        html = await page.content()
        emails = extraer_emails_validos(html)
        telefonos = extraer_telefonos(html)

        email = emails[0] if emails else None
        telefono = telefonos[0] if telefonos else None
        origen = construir_origen("Facebook", email, telefono)

        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

        if email or telefono:
            logger.info(f"✅ Contacto encontrado en Facebook: {username}")
            return normalizar_datos_scraper(
                nombre=username,
                usuario=username,
                email=email,
                telefono=telefono,
                origen=origen
            )

    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de Facebook: {e}")

    logger.info(f"🔁 No se encontraron datos útiles en Facebook para {username}")
    return None
