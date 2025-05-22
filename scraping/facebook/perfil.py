from playwright.async_api import TimeoutError as PlaywrightTimeout
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from utils.validator import extraer_emails_validos, extraer_telefonos
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto
from utils.busqueda_username import buscar_perfiles_por_username
from urllib.parse import quote_plus

async def obtener_datos_perfil_facebook(
    username: str,
    habilitar_busqueda_web: bool = False,
    redes_visitadas: set[str] = None
) -> dict:
    if redes_visitadas is None:
        redes_visitadas = set()
    redes_visitadas.add("facebook")

    email = None
    telefono = None

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_facebook.json")

        if not context:
            logger.error("❌ No se pudo iniciar navegador con proxy para Facebook.")
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_proxy")

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
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout")

        perfil_encontrado = await page.locator('a[href*="facebook.com/"]').nth(0).get_attribute("href")
        if not perfil_encontrado:
            logger.warning("⚠️ No se encontró un perfil o página válido en los resultados.")
            await browser.close()
            await playwright.stop()
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_perfil")

        perfil_url = perfil_encontrado if perfil_encontrado.startswith("http") else f"https://www.facebook.com{perfil_encontrado}"
        logger.info(f"➡️ Navegando al perfil/página: {perfil_url}")

        try:
            await page.goto(perfil_url, timeout=20000)
            await page.wait_for_timeout(3000)
        except PlaywrightTimeout:
            logger.warning("⏱️ Timeout accediendo al perfil seleccionado.")
            ProxyPool().reportar_bloqueo(proxy, "facebook")
            await browser.close()
            await playwright.stop()
            return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout_perfil")

        logger.info("🔎 Extrayendo contenido...")
        html = await page.content()
        emails = extraer_emails_validos(html)
        email = emails[0] if emails else None
        telefonos = extraer_telefonos(html)
        telefono = telefonos[0] if telefonos else None

        await page.close()
        await context.close()
        await browser.close()
        await playwright.stop()

        if email or telefono:
            logger.info(f"✅ Datos encontrados directamente en Facebook para {username}")
            return normalizar_datos_scraper(
                nombre=username,
                usuario=username,
                email=email,
                fuente_email=perfil_url if email else None,
                telefono=telefono,
                seguidores=None,
                seguidos=None,
                hashtags=[],
                origen="bio"
            )

    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de Facebook: {e}")
        email = None
        telefono = None

    # 🔁 Buscar en otras redes si no se obtuvo contacto
    if not email and not telefono:
        logger.info("🔁 No se encontraron datos en Facebook")
        resultado_multired = await buscar_perfiles_por_username(username, excluir=["facebook"], redes_visitadas=redes_visitadas)
        if resultado_multired:
            return resultado_multired

    # 🔎 Búsqueda cruzada como último recurso
    logger.warning("⚠️ No se encontró información útil. Evaluando búsqueda cruzada...")

    if not habilitar_busqueda_web:
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="facebook",
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

    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_resultado")
