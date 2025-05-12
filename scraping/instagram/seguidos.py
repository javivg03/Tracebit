from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from playwright.sync_api import TimeoutError
from services.playwright_tools import iniciar_browser_con_proxy
from services.logging_config import logger
import concurrent.futures


def obtener_seguidos(username: str, max_seguidos: int = 3):
    seguidos = []
    logger.info(f"🚀 Iniciando extracción de seguidos para: {username}")

    try:
        playwright, browser, context, proxy = iniciar_browser_con_proxy("state_instagram.json")
        logger.info(f"🧩 Proxy elegido para seguidos: {proxy}")
        page = context.new_page()

        logger.info("🌐 Accediendo al perfil...")
        page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        page.wait_for_timeout(3000)
        logger.info("✅ Perfil cargado")

        logger.info("🧭 Buscando botón de seguidos...")
        page.click('a[href$="/following/"]', timeout=10000)
        logger.info("✅ Clic en botón de seguidos")
        page.wait_for_timeout(6000)

        logger.info("🔄 Comenzando scroll y extracción de seguidos...")
        intentos_sin_nuevos = 0
        max_intentos = 12

        while len(seguidos) < max_seguidos and intentos_sin_nuevos < max_intentos:
            page.evaluate('''() => {
                const ul = document.querySelector('div[role="dialog"] ul');
                if (ul && ul.parentElement) {
                    ul.parentElement.scrollTop = ul.parentElement.scrollHeight;
                }
            }''')
            page.wait_for_timeout(1500)

            items = page.evaluate('''() => {
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
                if user not in seguidos and len(seguidos) < max_seguidos:
                    seguidos.append(user)
                    nuevos += 1
                    logger.info(f"👤 Seguido #{len(seguidos)}: {user}")

            if nuevos == 0:
                intentos_sin_nuevos += 1
                logger.warning(f"⚠️ Sin nuevos seguidos. Intento {intentos_sin_nuevos}/{max_intentos}")
            else:
                intentos_sin_nuevos = 0

        logger.info(f"✅ Total de seguidos extraídos: {len(seguidos)}")

    except TimeoutError as e:
        logger.error(f"❌ Timeout al interactuar con la página: {e}")
    except Exception as e:
        logger.error(f"❌ Error general durante el scraping de seguidos: {e}")
    finally:
        logger.info("🪩 Cerrando navegador...")
        try:
            browser.close()
            playwright.stop()
        except Exception:
            pass

    return seguidos


def scrape_followees_info(username: str, max_seguidos: int = 3, timeout_por_usuario: int = 30):
    logger.info(f"🚀 Scraping de seguidos para: {username}")
    todos_los_datos = []

    seguidos = obtener_seguidos(username, max_seguidos=max_seguidos)

    if not seguidos:
        logger.warning("⚠️ No se encontraron seguidos.")
        return []

    for i, usuario in enumerate(seguidos):
        logger.info(f"🔍 ({i+1}/{len(seguidos)}) Scrapeando seguido: {usuario}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(obtener_datos_perfil_instagram_con_fallback, usuario)
            try:
                datos = future.result(timeout=timeout_por_usuario)
                todos_los_datos.append(datos)
                logger.info(f"✅ Finalizado scraping de seguido {usuario}")
            except concurrent.futures.TimeoutError:
                logger.warning(f"⚠️ Timeout al scrapear seguido {usuario} (>{timeout_por_usuario}s)")
            except Exception as e:
                logger.error(f"❌ Error al scrapear seguido {usuario}: {e}")

    logger.info(f"📦 Scraping completado. Seguidos procesados: {len(todos_los_datos)}")
    return todos_los_datos
