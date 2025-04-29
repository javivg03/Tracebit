from playwright.sync_api import sync_playwright, TimeoutError
from scraping.instagram.perfil import obtener_datos_perfil_instagram_con_fallback
from services.logging_config import logger
# from services.proxy_pool import ProxyPool
# from services.playwright_tools import iniciar_browser_con_proxy

def obtener_seguidores(username: str, max_seguidores: int = 3):
    seguidores = []
    logger.info(f"🚀 Iniciando extracción de seguidores para: {username}")

    try:
        # ⛔ Uso de proxy desactivado temporalmente
        # playwright, browser, context, proxy = iniciar_browser_con_proxy("state_instagram.json")

        # ✅ Modo sin proxy (con tu IP)
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state="state_instagram.json")
        page = context.new_page()

        logger.info("🌐 Accediendo al perfil...")
        page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
        page.wait_for_timeout(3000)
        logger.info("✅ Perfil cargado")

        logger.info("🕭 Buscando botón de seguidores...")
        page.click('a[href$="/followers/"]', timeout=10000)
        logger.info("✅ Clic en botón de seguidores")
        page.wait_for_timeout(6000)

        logger.info("🔄 Comenzando scroll + extracción sin esperar a visibilidad...")
        intentos_sin_nuevos = 0
        max_intentos = 12

        while len(seguidores) < max_seguidores and intentos_sin_nuevos < max_intentos:
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
                if user not in seguidores and len(seguidores) < max_seguidores:
                    seguidores.append(user)
                    nuevos += 1
                    logger.info(f"👤 Seguidor #{len(seguidores)}: {user}")

            if nuevos == 0:
                intentos_sin_nuevos += 1
                logger.warning(f"⚠️ Sin nuevos seguidores. Intento {intentos_sin_nuevos}/{max_intentos}")
            else:
                intentos_sin_nuevos = 0

        logger.info(f"✅ Total de seguidores extraídos: {len(seguidores)}")

    except TimeoutError as e:
        logger.error(f"❌ Timeout al interactuar con la página: {e}")
    except Exception as e:
        logger.error(f"❌ Error inesperado durante el scraping: {e}")
    finally:
        logger.info("🪩 Cerrando navegador...")
        browser.close()
        playwright.stop()

    return seguidores


def scrape_followers_info(username: str, max_seguidores: int = 3):
    logger.info(f"🚀 Scraping de seguidores para: {username}")
    todos_los_datos = []

    seguidores = obtener_seguidores(username, max_seguidores=max_seguidores)

    if not seguidores:
        logger.warning("⚠️ No se encontraron seguidores.")
        return []

    for i, usuario in enumerate(seguidores):
        logger.info(f"🔍 ({i+1}/{len(seguidores)}) Scrapeando seguidor: {usuario}")
        try:
            datos = obtener_datos_perfil_instagram_con_fallback(usuario)
            todos_los_datos.append(datos)
        except Exception as e:
            logger.error(f"❌ Error al scrapear seguidor {usuario}: {e}")

    return todos_los_datos
