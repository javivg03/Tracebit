from bs4 import BeautifulSoup
from utils.validator import extraer_emails, extraer_telefonos
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy


async def analizar_url_contacto_playwright(page, url: str, origen: str = "duckduckgo") -> dict | None:
    try:
        await page.goto(url, timeout=10000)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        texto = soup.get_text(separator=" ", strip=True)
        emails = extraer_emails(texto)
        telefonos = extraer_telefonos(texto)

        if emails or telefonos:
            return {
                "email": emails[0] if emails else None,
                "telefono": telefonos[0] if telefonos else None,
                "url_fuente": url,
                "origen": origen,
                "nombre": None
            }
    except Exception as e:
        logger.warning(f"❌ Error accediendo a {url}: {e}")
    return None


async def buscar_contacto(username: str, nombre_completo: str = None, origen_actual: str = None, habilitar_busqueda_web: bool = False) -> dict | None:
    logger.info(f"🔎 Búsqueda cruzada iniciada para {username} (origen: {origen_actual})")

    if not habilitar_busqueda_web:
        logger.info("⛔ Búsqueda web desactivada por configuración.")
        return None

    query = f'"{nombre_completo or username}" contacto OR email OR teléfono OR "sitio web"'
    intentos = 0
    max_intentos = 3

    while intentos < max_intentos:
        intentos += 1
        logger.info(f"🦆 Intento {intentos}/{max_intentos} de búsqueda DuckDuckGo para query: {query}")

        try:
            playwright, browser, context, proxy = await iniciar_browser_con_proxy()
            if not context or not browser or not playwright:
                logger.warning("⚠️ No se pudo iniciar el navegador correctamente. Reintentando...")
                try:
                    if browser:
                        await browser.close()
                    if playwright:
                        await playwright.stop()
                except:
                    pass
                continue

            page = await context.new_page()
            page.set_default_timeout(20000)

            await page.goto("https://duckduckgo.com/")
            await page.wait_for_selector("input[name='q']")
            await page.click("input[name='q']")
            await page.keyboard.type(query, delay=100)
            await page.keyboard.press("Enter")

            try:
                await page.wait_for_selector("#links", timeout=20000)
            except:
                if "418" in page.url or "static-pages/418.html" in page.url:
                    logger.warning("🚫 DuckDuckGo bloqueó esta sesión (418.html). Reintentando con otro proxy...")
                    await browser.close()
                    await playwright.stop()
                    continue
                raise

            await page.mouse.wheel(0, 500)
            await page.wait_for_timeout(1500)

            soup = BeautifulSoup(await page.content(), "html.parser")
            enlaces = soup.select("a.result__a, a[data-testid='result-title-a']")

            for enlace in enlaces:
                href = enlace.get("href")
                if href and href.startswith("http"):
                    logger.info(f"🔗 Analizando resultado: {href}")
                    subpage = await context.new_page()
                    datos = await analizar_url_contacto_playwright(subpage, href)
                    await subpage.close()
                    if datos:
                        await browser.close()
                        await playwright.stop()
                        logger.info(f"✅ Contacto encontrado en búsqueda cruzada: {datos}")
                        return datos

            await browser.close()
            await playwright.stop()
            logger.info("❌ No se encontró información de contacto relevante en los resultados.")

        except Exception as e:
            logger.warning(f"❌ Error en búsqueda cruzada con Playwright: {e}")
            try:
                await browser.close()
                await playwright.stop()
            except:
                pass

    logger.warning("🚫 Todos los intentos fallaron para DuckDuckGo con Playwright.")
    return None
