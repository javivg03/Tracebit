import asyncio
from playwright.async_api import TimeoutError as PlaywrightTimeout
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
from services.proxy_pool import ProxyPool
from utils.flujo_scraping import flujo_scraping_multired
import pandas as pd


async def obtener_seguidores(username: str, max_seguidores: int = 3) -> list[str]:
    seguidores = []
    logger.info(f"🚀 Iniciando extracción de seguidores para: {username}")

    try:
        playwright, browser, context, proxy = await iniciar_browser_con_proxy("state_instagram.json")
        logger.info(f"🧩 Proxy usado para seguidores: {proxy}")
        page = await context.new_page()

        logger.info("🌐 Accediendo al perfil...")
        await page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        await page.wait_for_timeout(3000)

        logger.info("🕭 Buscando botón de seguidores...")
        await page.click('a[href$="/followers/"]', timeout=10000)
        await page.wait_for_timeout(6000)

        logger.info("🔄 Comenzando scroll y extracción de seguidores...")
        intentos_sin_nuevos = 0
        max_intentos = 12

        while len(seguidores) < max_seguidores and intentos_sin_nuevos < max_intentos:
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
                if user not in seguidores:
                    seguidores.append(user)
                    nuevos += 1
                    logger.info(f"👤 Seguidor #{len(seguidores)}: {user}")
                    if len(seguidores) >= max_seguidores:
                        break

            if nuevos == 0:
                intentos_sin_nuevos += 1
                logger.warning(f"⚠️ Sin nuevos seguidores. Intento {intentos_sin_nuevos}/{max_intentos}")
            else:
                intentos_sin_nuevos = 0

        logger.info(f"✅ Total de seguidores extraídos: {len(seguidores)}")

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

    return seguidores


async def scrape_followers_info(username: str, max_seguidores: int = 3, timeout_por_seguidor: int = 30) -> list[dict]:
    logger.info(f"🚀 Scraping de seguidores para: {username}")
    resultados = []

    seguidores = await obtener_seguidores(username, max_seguidores)
    if not seguidores:
        logger.warning("⚠️ No se encontraron seguidores.")
        return []

    for i, seguidor in enumerate(seguidores):
        logger.info(f"🔍 ({i+1}/{len(seguidores)}) Procesando seguidor: {seguidor}")
        try:
            datos = await asyncio.wait_for(
                flujo_scraping_multired(seguidor, redes=["instagram"], habilitar_busqueda_web=False),
                timeout=timeout_por_seguidor
            )
            resultados.append(datos)
            logger.info(f"✅ Datos obtenidos de {seguidor}")
        except asyncio.TimeoutError:
            logger.warning(f"⏱ Timeout en {seguidor} tras {timeout_por_seguidor}s")
        except Exception as e:
            logger.error(f"❌ Error inesperado con {seguidor}: {e}")

    logger.info(f"📦 Scraping completado. Seguidores procesados: {len(resultados)}")

    # (Opcional) Guardar en Excel aquí directamente si no se hace desde Celery
    ruta = f"exports/seguidores_{username}.xlsx"
    try:
        pd.DataFrame(resultados).to_excel(ruta, index=False)
        logger.info(f"📁 Archivo exportado: {ruta}")
    except Exception as e:
        logger.warning(f"❌ No se pudo exportar el Excel: {e}")

    return resultados
