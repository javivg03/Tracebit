import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeout
from services.logging_config import logger
from services.playwright_tools import iniciar_browser_con_proxy
from services.proxy_pool import ProxyPool
from utils.flujo_scraping import flujo_scraping_multired

async def obtener_seguidos_tiktok(username: str, max_seguidos: int = 3):
    seguidos = []
    logger.info(f"🚀 Iniciando extracción de seguidos TikTok para: {username}")

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_tiktok.json")
        if not context:
            logger.warning("⚠️ No se pudo iniciar navegador con proxy para TikTok.")
            return []

        logger.info(f"🧩 Proxy usado para seguidos TikTok: {proxy}")
        page = await context.new_page()

        try:
            logger.info("🌐 Abriendo sección de seguidos...")
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

        except PlaywrightTimeout:
            logger.error("❌ Timeout durante la carga de la sección de seguidos")
            ProxyPool().reportar_bloqueo(proxy, "tiktok")
        except Exception as e:
            logger.error(f"❌ Error durante la navegación de seguidos: {e}")

        finally:
            logger.info("🧹 Cerrando navegador de TikTok...")
            try:
                await context.close()
                await browser.close()
                await playwright.stop()
            except Exception as e:
                logger.warning(f"⚠️ Error al cerrar navegador: {e}")

    except Exception as e:
        logger.error(f"❌ Error general durante Playwright: {e}")

    logger.info(f"✅ Total de seguidos extraídos: {len(seguidos)}")
    return seguidos


async def scrape_followees_info_tiktok(username: str, max_seguidos: int = 3, timeout_por_usuario: int = 30):
    logger.info(f"🔍 Scrapeando seguidos de TikTok para: {username}")
    resultados = []

    seguidos = await obtener_seguidos_tiktok(username, max_seguidos=max_seguidos)
    if not seguidos:
        logger.warning("⚠️ No se encontraron seguidos.")
        return []

    for i, usuario in enumerate(seguidos):
        logger.info(f"🔍 ({i+1}/{len(seguidos)}) Scrapeando perfil del seguido: {usuario}")
        try:
            datos = await asyncio.wait_for(
                flujo_scraping_multired(usuario, redes=["tiktok"]),
                timeout=timeout_por_usuario
            )
            resultados.append(datos)
            logger.info(f"✅ Datos obtenidos de seguido {usuario}")
        except asyncio.TimeoutError:
            logger.warning(f"⏱ Timeout en {usuario} tras {timeout_por_usuario}s")
        except Exception as e:
            logger.error(f"❌ Error inesperado con {usuario}: {e}")

    logger.info(f"📦 Scraping completado. Seguidos procesados: {len(resultados)}")
    return resultados
