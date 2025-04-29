from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from services.logging_config import logger

# Función que extrae los usernames de los seguidos desde la interfaz de TikTok
async def obtener_seguidos_tiktok(username: str, max_seguidos: int = 3):
    seguidos = []
    logger.info(f"🚀 Iniciando extracción de seguidos TikTok para: {username}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state="state_tiktok.json")
            page = await context.new_page()

            try:
                logger.info("🌐 Abriendo sección de seguidos (following)...")
                await page.goto(f"https://www.tiktok.com/@{username}/following", timeout=20000)
                await page.wait_for_timeout(3000)

                logger.info("🔄 Iniciando scroll para extraer seguidos...")
                for _ in range(10):
                    await page.mouse.wheel(0, 5000)
                    await page.wait_for_timeout(1000)

                    items = await page.eval_on_selector_all(
                        'a[href^="/@"]',
                        '''
                        elements => {
                            const usernames = new Set();
                            elements.forEach(e => {
                                const href = e.getAttribute("href");
                                if (href && href.startsWith("/@")) {
                                    let username = href.split("/@")[1].split("?")[0];
                                    if (username && !username.includes("/")) {
                                        usernames.add(username);
                                    }
                                }
                            });
                            return [...usernames];
                        }
                        '''
                    )

                    for user in items:
                        if user not in seguidos and len(seguidos) < max_seguidos:
                            seguidos.append(user)
                            logger.info(f"👤 Seguido #{len(seguidos)}: {user}")

                    if len(seguidos) >= max_seguidos:
                        break

            except Exception as e:
                logger.error(f"❌ Error durante navegación o extracción de seguidos: {e}")

            finally:
                logger.info("🧹 Cerrando navegador de TikTok...")
                try:
                    await context.close()
                    await browser.close()
                except Exception as e:
                    logger.warning(f"⚠️ Error al cerrar navegador: {e}")

    except Exception as e:
        logger.error(f"❌ Error general durante Playwright: {e}")

    return seguidos


# Función que llama al scraper de perfil para cada seguido y acumula los datos
async def scrape_followees_info_tiktok(username: str, max_seguidos: int = 3):
    logger.info(f"🔍 Scrapeando seguidos de TikTok para: {username}")
    todos_los_datos = []

    seguidos = await obtener_seguidos_tiktok(username, max_seguidos=max_seguidos)
    if not seguidos:
        logger.warning("⚠️ No se encontraron seguidos.")
        return []

    for i, usuario in enumerate(seguidos):
        logger.info(f"🔍 ({i+1}/{len(seguidos)}) Scrapeando perfil del seguido: {usuario}")
        try:
            datos = await obtener_datos_perfil_tiktok(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            logger.error(f"❌ Error al scrapear perfil del seguido {usuario}: {e}")

    return todos_los_datos
