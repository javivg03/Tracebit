from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from scraping.tiktok.perfil import obtener_datos_perfil_tiktok
from services.logging_config import logger

# Función que extrae los usernames de los seguidores desde la interfaz de TikTok
async def obtener_seguidores_tiktok(username: str, max_seguidores: int = 3):
    seguidores = []
    logger.info(f"🚀 Iniciando extracción de seguidores TikTok para: {username}")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(storage_state="state_tiktok.json")  # <-- aquí
            page = await context.new_page()

            try:
                logger.info("🌐 Abriendo sección de seguidores...")
                await page.goto(f"https://www.tiktok.com/@{username}/followers", timeout=20000)
                await page.wait_for_timeout(3000)

                logger.info("🔄 Iniciando scroll para extraer seguidores...")
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
                                    let username = href.split("/@")[1].split("?")[0];  // limpia ?lang=en u otros params
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
                        if user not in seguidores and len(seguidores) < max_seguidores:
                            seguidores.append(user)
                            logger.info(f"👤 Seguidor #{len(seguidores)}: {user}")

                    if len(seguidores) >= max_seguidores:
                        break

            except Exception as e:
                logger.error(f"❌ Error durante navegación o extracción de seguidores: {e}")

            finally:
                logger.info("🧹 Cerrando navegador de TikTok...")
                try:
                    await context.close()
                    await browser.close()
                except Exception as e:
                    logger.warning(f"⚠️ Error al cerrar navegador: {e}")

    except Exception as e:
        logger.error(f"❌ Error general durante Playwright: {e}")

    return seguidores


# Función que llama al scraper de perfil para cada seguidor y acumula los datos
async def scrape_followers_info_tiktok(username: str, max_seguidores: int = 3):
    logger.info(f"🔍 Scrapeando seguidores de TikTok para: {username}")
    todos_los_datos = []

    seguidores = await obtener_seguidores_tiktok(username, max_seguidores=max_seguidores)
    if not seguidores:
        logger.warning("⚠️ No se encontraron seguidores.")
        return []

    for i, usuario in enumerate(seguidores):
        logger.info(f"🔍 ({i+1}/{len(seguidores)}) Scrapeando perfil del seguidor: {usuario}")
        try:
            datos = await obtener_datos_perfil_tiktok(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            logger.error(f"❌ Error al scrapear perfil del seguidor {usuario}: {e}")

    return todos_los_datos
