import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeout
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool
from utils.flujo_scraping import flujo_scraping_multired
import pandas as pd


async def obtener_seguidos(username: str, max_seguidos: int = 3) -> list[str]:
    seguidos = []
    logger.info(f"🚀 Iniciando extracción de seguidos para: {username}")

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_instagram.json")
        logger.info(f"🧩 Proxy usado para seguidos: {proxy}")
        page = await context.new_page()

        logger.info("🌐 Accediendo al perfil...")
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_timeout(3000)

        logger.info("🧭 Buscando botón de seguidos...")
        await page.click('a[href$="/following/"]', timeout=10000)
        await page.wait_for_timeout(6000)

        logger.info("🔄 Comenzando scroll y extracción de seguidos...")
        intentos_sin_nuevos = 0
        max_intentos = 12

        while len(seguidos) < max_seguidos and intentos_sin_nuevos < max_intentos:
            await page.evaluate('''() => {
                const ul = document.querySelector('div[role="dialog"] ul');
                if (ul && ul.parentElement) {
                    ul.parentElement.scrollTop = ul.parentElement.scrollHeight;
                }
            }''')
            await page.wait_for_timeout(1500)

            items = await page.evaluate('''() => {
                const lista = [];
                const links = document.querySelectorAll('div[role="dialog"] a[href^="/"]');
                for (const link of links) {
                    const href = link.getAttribute("href");
                    if (href && /^\\/[^\\/]+\\/$/.test(href)) {
                        lista.push(href.replace(/\\//g, ""));
                    }
                }
                return lista;
            }''')

            nuevos = 0
            for user in items:
                if user not in seguidos:
                    seguidos.append(user)
                    nuevos += 1
                    logger.info(f"👤 Seguido #{len(seguidos)}: {user}")
                    if len(seguidos) >= max_seguidos:
                        break

            if nuevos == 0:
                intentos_sin_nuevos += 1
                logger.warning(f"⚠️ Sin nuevos seguidos. Intento {intentos_sin_nuevos}/{max_intentos}")
            else:
                intentos_sin_nuevos = 0

        logger.info(f"✅ Total de seguidos extraídos: {len(seguidos)}")

    except PlaywrightTimeout as e:
        logger.error(f"❌ Timeout durante el scraping: {e}")
        ProxyPool().reportar_bloqueo(proxy, "instagram")
    except Exception as e:
        logger.error(f"❌ Error inesperado durante el scraping: {e}")
    finally:
        logger.info("🪩 Cerrando navegador...")
        try:
            await browser.close()
            await playwright.stop()
        except Exception:
            pass

    return seguidos


async def scrape_followees_info(username: str, max_seguidos: int = 3, timeout_por_usuario: int = 30) -> list[dict]:
    logger.info(f"🚀 Scraping de seguidos para: {username}")
    resultados = []

    seguidos = await obtener_seguidos(username, max_seguidos=max_seguidos)

    if not seguidos:
        logger.warning("⚠️ No se encontraron seguidos.")
        return []

    for i, usuario in enumerate(seguidos):
        logger.info(f"🔍 ({i+1}/{len(seguidos)}) Scrapeando seguido: {usuario}")
        try:
            datos = await asyncio.wait_for(
                flujo_scraping_multired(usuario, redes=["instagram"], habilitar_busqueda_web=False),
                timeout=timeout_por_usuario
            )
            resultados.append(datos)
            logger.info(f"✅ Finalizado scraping de seguido {usuario}")
        except asyncio.TimeoutError:
            logger.warning(f"⚠️ Timeout al scrapear seguido {usuario} (>{timeout_por_usuario}s)")
        except Exception as e:
            logger.error(f"❌ Error inesperado con {usuario}: {e}")

    logger.info(f"📦 Scraping completado. Seguidos procesados: {len(resultados)}")

    # Exportar a Excel
    ruta = f"exports/seguidos_{username}.xlsx"
    try:
        pd.DataFrame(resultados).to_excel(ruta, index=False)
        logger.info(f"📁 Archivo exportado: {ruta}")
    except Exception as e:
        logger.warning(f"❌ No se pudo exportar el Excel: {e}")

    return resultados
