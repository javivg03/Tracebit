from playwright.sync_api import sync_playwright, Playwright
from services.proxy_pool import ProxyPool
from services.proxy_format import formatear_proxy_playwright
from services.logging_config import logger

def iniciar_browser_con_proxy(state_path: str = None, max_reintentos: int = 5):
    pool = ProxyPool()
    intentos = 0

    while intentos < max_reintentos:
        proxy = pool.get_random_proxy()
        if not proxy:
            raise Exception("❌ No hay proxies disponibles en el pool")

        try:
            proxy_config = formatear_proxy_playwright(proxy)
            logger.info(f"🌐 Intentando lanzar navegador con proxy: {proxy_config['server']}")

            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(proxy=proxy_config, headless=True)

            if state_path:
                context = browser.new_context(storage_state=state_path)
            else:
                context = browser.new_context()

            logger.info(f"✅ Navegador lanzado con proxy: {proxy_config['server']}")
            return playwright, browser, context, proxy

        except Exception as e:
            logger.warning(f"❌ Error al lanzar navegador con proxy {proxy['ip']}:{proxy['port']}: {e}")
            pool.remove_proxy(proxy)
            intentos += 1

    raise Exception("❌ No se pudo lanzar navegador con ningún proxy válido.")
