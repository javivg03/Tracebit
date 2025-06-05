import asyncio
from utils.flujo_scraping import flujo_scraping_multired
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from services.logging_config import logger
from playwright.async_api import TimeoutError as PlaywrightTimeout

async def obtener_seguidores_tiktok(username: str, max_seguidores: int = 3):
    seguidores = []
    logger.info(f"🚀 Iniciando extracción de seguidores TikTok para: {username}")

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_tiktok.json")
        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para TikTok.")
            return []

        logger.info(f"🧩 Proxy usado para seguidores TikTok: {proxy}")
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
                    if user not in seguidores and len(seguidores) < max_seguidores:
                        seguidores.append(user)
                        logger.info(f"👤 Seguidor #{len(seguidores)}: {user}")

                if len(seguidores) >= max_seguidores:
                    break

        except PlaywrightTimeout:
            logger.error("❌ Timeout durante la carga de la sección de seguidores")
            ProxyPool().reportar_bloqueo(proxy, "tiktok")
        except Exception as e:
            logger.error(f"❌ Error al extraer seguidores de TikTok: {e}")

        finally:
            logger.info("🧹 Cerrando navegador de TikTok...")
            try:
                await context.close()
                await browser.close()
                await playwright.stop()
            except Exception as e:
                logger.warning(f"⚠️ Error al cerrar navegador: {e}")

    except Exception as e:
        logger.error(f"❌ Error general en Playwright: {e}")

    logger.info(f"✅ Seguidores extraídos de TikTok: {len(seguidores)}")
    return seguidores


async def scrape_followers_info_tiktok(username: str, max_seguidores: int = 3, timeout_por_usuario: int = 30):
    logger.info(f"🔍 Scrapeando seguidores de TikTok para: {username}")
    todos_los_datos = []

    seguidores = await obtener_seguidores_tiktok(username, max_seguidores=max_seguidores)
    if not seguidores:
        logger.warning("⚠️ No se encontraron seguidores.")
        return []

    for i, usuario in enumerate(seguidores):
        logger.info(f"🔍 ({i+1}/{len(seguidores)}) Scrapeando perfil del seguidor: {usuario}")
        try:
            datos = await asyncio.wait_for(
                flujo_scraping_multired(usuario, redes=["tiktok", "instagram", "facebook", "x"], habilitar_busqueda_web=False),
                timeout=timeout_por_usuario
            )
            todos_los_datos.append(datos)
        except asyncio.TimeoutError:
            logger.warning(f"⏱ Timeout al scrapear {usuario} (>{timeout_por_usuario}s)")
        except Exception as e:
            logger.error(f"❌ Error con seguidor {usuario}: {e}")

    logger.info(f"✅ Seguidores de TikTok procesados: {len(todos_los_datos)}")
    return todos_los_datos
