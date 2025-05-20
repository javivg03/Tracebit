from playwright.async_api import TimeoutError as PlaywrightTimeout
from utils.validator import extraer_emails_validos, extraer_telefonos, extraer_dominios
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto, buscar_contacto_por_dominio
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.user_agents import random_user_agent

async def obtener_datos_perfil_instagram(username: str, forzar_solo_bio: bool = False, habilitar_busqueda_web: bool = False) -> dict:
    logger.info(f"🚀 Iniciando scraping de perfil de Instagram para: {username}")

    try:
        user_agent = random_user_agent()
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_instagram.json")

        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para Instagram.")
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")

        page = await context.new_page()

        try:
            logger.info(f"🌐 Visitando perfil: https://www.instagram.com/{username}/")
            await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            logger.warning("❌ Timeout al cargar el perfil. Proxy marcado como bloqueado.")
            from services.proxy_pool import ProxyPool
            ProxyPool().reportar_bloqueo(proxy, "instagram")
            await browser.close()
            await playwright.stop()
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout")

        logger.info("🔍 Extrayendo datos...")

        nombre_raw = await page.locator('meta[property="og:title"]').get_attribute("content")
        nombre = nombre_raw.split("(@")[0].strip() if nombre_raw else username

        bio = await page.locator('meta[name="description"]').get_attribute("content") or ""
        if not bio:
            bio = await page.locator('meta[property="og:description"]').get_attribute("content") or ""

        hashtags = [tag.strip("#") for tag in bio.split() if tag.startswith("#")]
        emails = extraer_emails_validos(bio)
        email = emails[0] if emails else None
        fuente_email = "bio" if email else None
        telefonos = extraer_telefonos(bio)
        telefono = telefonos[0] if telefonos else None
        origen = "bio" if email or telefono else "no_email"

        await browser.close()
        await playwright.stop()

        if email or telefono:
            return normalizar_datos_scraper(
                nombre, username, email, fuente_email,
                telefono, None, None, hashtags, origen
            )

        # Scraping dirigido a dominios si no hay email/teléfono
        dominios = extraer_dominios(bio)
        for dominio in dominios:
            datos_dominio = await buscar_contacto_por_dominio(dominio)
            if datos_dominio:
                return normalizar_datos_scraper(
                    nombre, username,
                    datos_dominio.get("email"),
                    datos_dominio.get("url_fuente"),
                    datos_dominio.get("telefono"),
                    None, None,
                    hashtags,
                    "scraping_dominio"
                )

    except Exception as e:
        logger.error(f"❌ Error general en scraping de Instagram: {e}")

    # 🔁 Búsqueda cruzada si está habilitada
    logger.warning("⚠️ No se encontró información útil. Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=nombre if 'nombre' in locals() else username,
        origen_actual="instagram",
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
