from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from services.proxy_pool import ProxyPool
from services.proxy_format import formatear_proxy_playwright
from services.logging_config import logger
from utils.validator import extraer_emails_validos, extraer_telefonos, extraer_dominios
from utils.normalizador import normalizar_datos_scraper
from utils.busqueda_cruzada import buscar_contacto, buscar_contacto_por_dominio
from services.user_agents import random_user_agent
from urllib.parse import quote_plus

async def obtener_datos_perfil_facebook(username: str, habilitar_busqueda_web: bool = False) -> dict:
    pool = ProxyPool()
    proxy = pool.get_random_proxy()

    if not proxy:
        logger.error("❌ No hay proxies disponibles para Facebook.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_proxy")

    try:
        user_agent = random_user_agent()
        proxy_config = formatear_proxy_playwright(proxy)
        logger.info(f"🌐 Lanzando navegador con proxy: {proxy_config['server']} y User-Agent: {user_agent}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(proxy=proxy_config, headless=True)
            context = await browser.new_context(
                storage_state="state_facebook.json",
                user_agent=user_agent
            )
            page = await context.new_page()

            # Búsqueda general (personas + páginas)
            search_url = f"https://www.facebook.com/search/top/?q={quote_plus(username)}"
            try:
                logger.info(f"🌍 Accediendo a resultados de búsqueda: {search_url}")
                await page.goto(search_url, timeout=20000)
                await page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                logger.warning("⏱️ Timeout en búsqueda general.")
                pool.reportar_bloqueo(proxy, "facebook")
                return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout")

            # Buscar primer resultado con enlace a perfil/página
            perfil_encontrado = await page.locator('a[href*="facebook.com/"]').nth(0).get_attribute("href")
            if not perfil_encontrado:
                logger.warning("⚠️ No se encontró un perfil o página válido en los resultados.")
                return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_perfil")

            perfil_url = perfil_encontrado if perfil_encontrado.startswith("http") else f"https://www.facebook.com{perfil_encontrado}"
            logger.info(f"➡️ Navegando al perfil/página: {perfil_url}")
            try:
                await page.goto(perfil_url, timeout=20000)
                await page.wait_for_timeout(3000)
            except PlaywrightTimeout:
                logger.warning("⏱️ Timeout accediendo al perfil seleccionado.")
                pool.reportar_bloqueo(proxy, "facebook")
                return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "timeout_perfil")

            # Extraer contenido del perfil/página
            logger.info("🔎 Extrayendo contenido...")
            html = await page.content()
            emails = extraer_emails_validos(html)
            email = emails[0] if emails else None
            telefonos = extraer_telefonos(html)
            telefono = telefonos[0] if telefonos else None
            origen = "html" if email or telefono else "no_email"

            await context.close()
            await browser.close()

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
                    origen=origen
                )

            # Scraping dirigido a dominios detectados en el HTML
            dominios = extraer_dominios(html)
            for dominio in dominios:
                datos_dominio = await buscar_contacto_por_dominio(dominio)
                if datos_dominio:
                    logger.info(f"🌐 Datos encontrados desde dominio: {dominio}")
                    return normalizar_datos_scraper(
                        nombre=username,
                        usuario=username,
                        email=datos_dominio.get("email"),
                        fuente_email=datos_dominio.get("url_fuente"),
                        telefono=datos_dominio.get("telefono"),
                        seguidores=None,
                        seguidos=None,
                        hashtags=[],
                        origen="scraping_dominio"
                    )

    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de Facebook: {e}")
        pool.reportar_bloqueo(proxy, "facebook")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "error")

    # Búsqueda cruzada (si está habilitada)
    logger.warning("⚠️ No se encontraron datos útiles. Evaluando búsqueda cruzada...")
    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda cruzada desactivada por configuración del usuario.")
        return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_email")

    resultado_cruzado = await buscar_contacto(
        username=username,
        nombre_completo=username,
        origen_actual="facebook",
        habilitar_busqueda_web=True
    )

    if resultado_cruzado:
        logger.info(f"🔄 Resultado cruzado encontrado: {resultado_cruzado}")
        return normalizar_datos_scraper(
            resultado_cruzado.get("nombre") or username,
            username,
            resultado_cruzado.get("email"),
            resultado_cruzado.get("url_fuente"),
            resultado_cruzado.get("telefono"),
            None, None, [],
            f"búsqueda cruzada ({resultado_cruzado.get('origen')})"
        )

    logger.warning(f"❌ No se encontró ningún dato útil para {username} tras scraping + búsqueda cruzada.")
    return normalizar_datos_scraper(None, username, None, None, None, None, None, [], "sin_resultado")
